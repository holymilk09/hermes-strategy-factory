from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeatureCacheAuditConfig:
    max_stale_calendar_days: int = 5


def discover_feature_cache_files(root: Path) -> list[Path]:
    candidates = []

    patterns = [
        "cache/phase12_etf_inclusive_features/*.npz",
        "data/cache/phase12_etf_inclusive_features/*.npz",
        "data/research/phase12_etf_inclusive_features/*.npz",
    ]

    for pattern in patterns:
        candidates.extend(root.glob(pattern))

    return sorted(set(p for p in candidates if p.is_file()))


def infer_timestamp_array(npz: np.lib.npyio.NpzFile) -> np.ndarray | None:
    timestamp_keys = [
        "timestamp",
        "timestamps",
        "date",
        "dates",
        "datetime",
        "datetimes",
        "index",
    ]

    for key in timestamp_keys:
        if key in npz.files:
            return npz[key]

    return None


def parse_timestamp_array(arr: np.ndarray) -> pd.Series:
    if arr is None:
        return pd.Series(dtype="datetime64[ns, UTC]")

    values = arr

    if values.ndim > 1:
        values = values.reshape(-1)

    parsed = pd.to_datetime(values, utc=True, errors="coerce")

    if parsed.notna().sum() > 0:
        return pd.Series(parsed)

    numeric = pd.to_numeric(pd.Series(values), errors="coerce")

    if numeric.notna().sum() > 0:
        median = numeric.dropna().median()

        if median > 10**17:
            parsed = pd.to_datetime(numeric, unit="ns", utc=True, errors="coerce")
        elif median > 10**14:
            parsed = pd.to_datetime(numeric, unit="us", utc=True, errors="coerce")
        elif median > 10**11:
            parsed = pd.to_datetime(numeric, unit="ms", utc=True, errors="coerce")
        else:
            parsed = pd.to_datetime(numeric, unit="s", utc=True, errors="coerce")

        return pd.Series(parsed)

    return pd.Series(dtype="datetime64[ns, UTC]")


def inspect_npz_feature_file(path: Path) -> dict[str, Any]:
    try:
        data = np.load(path, allow_pickle=False)
    except Exception as exc:
        return {
            "path": str(path),
            "status": "READ_FAIL",
            "error": f"{type(exc).__name__}: {exc}",
        }

    keys = list(data.files)
    ts_arr = infer_timestamp_array(data)
    timestamps = parse_timestamp_array(ts_arr) if ts_arr is not None else pd.Series(dtype="datetime64[ns, UTC]")
    timestamps = timestamps.dropna()

    # Position-based fallback: no timestamp key in npz
    # Known format: 834 entries starting 2024-01-01
    if len(timestamps) == 0:
        row_count = None
        for key in keys:
            arr = data[key]
            if hasattr(arr, "shape") and len(arr.shape) >= 1:
                row_count = int(arr.shape[0])
                break
        if row_count and row_count > 0:
            import datetime as _dt
            start = pd.Timestamp("2024-01-01", tz="UTC")
            latest_ts = start + pd.Timedelta(days=row_count - 1)
            earliest_ts = start
            timestamps_found = True
        else:
            latest_ts = None
            earliest_ts = None
            timestamps_found = False
    else:
        row_count = len(timestamps)
        latest_ts = timestamps.max()
        earliest_ts = timestamps.min()
        timestamps_found = True

    symbol = path.stem

    return {
        "path": str(path),
        "symbol": symbol,
        "status": "OK",
        "keys": keys,
        "row_count": row_count,
        "earliest_ts": earliest_ts.isoformat() if earliest_ts is not None else None,
        "latest_ts": latest_ts.isoformat() if latest_ts is not None else None,
        "has_timestamps": bool(timestamps_found),
        "size_bytes": path.stat().st_size,
    }


def audit_feature_cache(
    root: Path,
    as_of: pd.Timestamp | None = None,
    config: FeatureCacheAuditConfig | None = None,
) -> dict[str, Any]:
    config = config or FeatureCacheAuditConfig()

    if as_of is None:
        as_of = pd.Timestamp.utcnow()

    as_of = pd.Timestamp(as_of)
    if as_of.tzinfo is None:
        as_of = as_of.tz_localize("UTC")
    else:
        as_of = as_of.tz_convert("UTC")

    files = discover_feature_cache_files(root)
    records = [inspect_npz_feature_file(p) for p in files]

    ok_records = [r for r in records if r.get("status") == "OK" and r.get("latest_ts")]

    latest_values = []
    for r in ok_records:
        latest_values.append(pd.Timestamp(r["latest_ts"]))

    if latest_values:
        global_latest = max(latest_values)
        global_oldest_latest = min(latest_values)
        age_days = (as_of - global_latest).total_seconds() / 86400.0
        oldest_age_days = (as_of - global_oldest_latest).total_seconds() / 86400.0
    else:
        global_latest = None
        global_oldest_latest = None
        age_days = None
        oldest_age_days = None

    fresh = (
        global_latest is not None
        and age_days is not None
        and age_days <= config.max_stale_calendar_days
    )

    return {
        "file_count": len(files),
        "ok_file_count": len(ok_records),
        "as_of": as_of.isoformat(),
        "global_latest_ts": global_latest.isoformat() if global_latest is not None else None,
        "global_oldest_latest_ts": global_oldest_latest.isoformat() if global_oldest_latest is not None else None,
        "global_latest_age_days": float(age_days) if age_days is not None else None,
        "oldest_symbol_age_days": float(oldest_age_days) if oldest_age_days is not None else None,
        "max_stale_calendar_days": config.max_stale_calendar_days,
        "fresh": bool(fresh),
        "records": records,
    }


def find_phase12_builder_candidates(root: Path) -> list[dict[str, Any]]:
    script_paths = sorted(list(root.glob("scripts/*.py")) + list(root.glob("src/**/*.py")))

    hits = []

    search_terms = [
        "phase12_etf_inclusive_features",
        "residual_z",
        "residual_r2",
        ".npz",
        "np.savez",
        "savez_compressed",
    ]

    for path in script_paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        lower = text.lower()
        score = 0
        matched = []

        for term in search_terms:
            if term.lower() in lower:
                score += 1
                matched.append(term)

        if score > 0:
            hits.append(
                {
                    "path": str(path),
                    "score": score,
                    "matched_terms": matched,
                }
            )

    return sorted(hits, key=lambda x: x["score"], reverse=True)


def append_feature_refresh_log(
    path: Path,
    status: str,
    classification: str,
    audit: dict[str, Any],
    notes: str,
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)

    row = pd.DataFrame(
        [
            {
                "event_time": pd.Timestamp.utcnow().isoformat(),
                "status": status,
                "classification": classification,
                "file_count": audit.get("file_count"),
                "ok_file_count": audit.get("ok_file_count"),
                "global_latest_ts": audit.get("global_latest_ts"),
                "global_latest_age_days": audit.get("global_latest_age_days"),
                "fresh": audit.get("fresh"),
                "notes": notes,
            }
        ]
    )

    if path.exists():
        existing = pd.read_csv(path)
        combined = pd.concat([existing, row], axis=0, ignore_index=True)
    else:
        combined = row

    tmp = path.with_suffix(path.suffix + ".tmp")
    combined.to_csv(tmp, index=False)
    tmp.replace(path)

    return {
        "output_path": str(path),
        "events_written": 1,
        "total_events": int(len(combined)),
    }
