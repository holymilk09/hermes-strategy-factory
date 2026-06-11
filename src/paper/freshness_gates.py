from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class FreshnessConfig:
    max_stale_calendar_days: int = 5
    require_selected_signal: bool = True


def normalize_candidate_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]

    if "timestamp" not in out.columns:
        raise ValueError("Candidate ledger missing timestamp column")

    if "selected" not in out.columns:
        raise ValueError("Candidate ledger missing selected column")

    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    out["selected"] = out["selected"].astype(bool)
    out = out.dropna(subset=["timestamp"])

    if out.empty:
        raise ValueError("Candidate ledger has no valid timestamps")

    return out


def evaluate_candidate_freshness(
    df: pd.DataFrame,
    as_of: pd.Timestamp | None = None,
    config: FreshnessConfig | None = None,
) -> dict[str, Any]:
    config = config or FreshnessConfig()
    data = normalize_candidate_timestamps(df)

    if as_of is None:
        as_of = pd.Timestamp.utcnow()

    as_of = pd.Timestamp(as_of)
    if as_of.tzinfo is None:
        as_of = as_of.tz_localize("UTC")
    else:
        as_of = as_of.tz_convert("UTC")

    latest_candidate_ts = data["timestamp"].max()

    selected = data[data["selected"]].copy()
    latest_selected_ts = selected["timestamp"].max() if not selected.empty else None

    candidate_age_days = (as_of - latest_candidate_ts).total_seconds() / 86400.0

    if latest_selected_ts is None:
        selected_age_days = None
    else:
        selected_age_days = (as_of - latest_selected_ts).total_seconds() / 86400.0

    candidate_fresh = candidate_age_days <= config.max_stale_calendar_days

    if config.require_selected_signal:
        selected_fresh = (
            latest_selected_ts is not None
            and selected_age_days is not None
            and selected_age_days <= config.max_stale_calendar_days
        )
    else:
        selected_fresh = True

    pass_gate = bool(candidate_fresh and selected_fresh)

    if not candidate_fresh:
        reason = "STALE_CANDIDATE_LEDGER"
    elif not selected_fresh:
        reason = "STALE_OR_MISSING_SELECTED_SIGNAL"
    else:
        reason = "FRESH"

    return {
        "pass": pass_gate,
        "reason": reason,
        "as_of": as_of.isoformat(),
        "latest_candidate_ts": latest_candidate_ts.isoformat(),
        "latest_selected_ts": latest_selected_ts.isoformat() if latest_selected_ts is not None else None,
        "candidate_age_days": float(candidate_age_days),
        "selected_age_days": float(selected_age_days) if selected_age_days is not None else None,
        "max_stale_calendar_days": config.max_stale_calendar_days,
        "candidate_rows": int(len(data)),
        "selected_rows": int(data["selected"].sum()),
    }


def filter_latest_fresh_selected_candidates(
    df: pd.DataFrame,
    as_of: pd.Timestamp | None = None,
    config: FreshnessConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    config = config or FreshnessConfig()
    data = normalize_candidate_timestamps(df)
    freshness = evaluate_candidate_freshness(data, as_of=as_of, config=config)

    if not freshness["pass"]:
        return data.iloc[0:0].copy(), freshness

    selected = data[data["selected"]].copy()

    if selected.empty:
        freshness["pass"] = False
        freshness["reason"] = "NO_SELECTED_SIGNAL"
        return selected, freshness

    latest_ts = selected["timestamp"].max()
    latest = selected[selected["timestamp"] == latest_ts].copy()

    return latest.sort_values("symbol").reset_index(drop=True), freshness
