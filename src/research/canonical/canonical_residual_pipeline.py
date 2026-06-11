from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CanonicalResidualRule:
    residual_z_threshold: float = -2.0
    residual_r2_threshold: float = 0.20

    @property
    def description(self) -> str:
        return (
            f"residual_z <= {self.residual_z_threshold} "
            f"AND residual_r2 >= {self.residual_r2_threshold}"
        )


REQUIRED_KEYS = [
    "timestamp",
    "residual_z",
    "residual_r2",
    "rsi_2",
    "regime_score",
]


FORWARD_RETURN_KEYS = [
    "forward_return_5d",
    "forward_return_10d",
    "forward_return_20d",
]


def parse_npz_timestamp(values: np.ndarray) -> pd.Series:
    arr = values.reshape(-1)

    # Auto-detect timestamp unit.
    # If values ~1.7e15+, try nanoseconds first; if ~1.7e12+, try microseconds.
    numeric = pd.to_numeric(pd.Series(arr), errors="coerce")
    if numeric.max() > 1e17:
        # Nanoseconds (post-2000 values ~1.7e18)
        parsed = pd.to_datetime(numeric, unit="ns", utc=True, errors="coerce")
    elif numeric.max() > 1e13:
        # Microseconds (post-2000 values ~1.7e15)
        parsed = pd.to_datetime(numeric, unit="us", utc=True, errors="coerce")
    else:
        # Fallback: try both
        parsed = pd.to_datetime(numeric, unit="ns", utc=True, errors="coerce")
        if parsed.isna().sum() > len(parsed) // 2:
            parsed = pd.to_datetime(numeric, unit="us", utc=True, errors="coerce")

    return pd.Series(parsed)


def load_canonical_symbol_npz(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    data = np.load(path, allow_pickle=False)
    keys = set(data.files)

    missing = [k for k in REQUIRED_KEYS if k not in keys]
    if missing:
        raise ValueError(f"{path} missing canonical keys: {missing}")

    symbol = path.stem
    timestamps = parse_npz_timestamp(data["timestamp"])

    df = pd.DataFrame()
    df["timestamp"] = timestamps
    df["symbol"] = symbol

    for key in REQUIRED_KEYS:
        if key == "timestamp":
            continue
        df[key] = pd.to_numeric(pd.Series(data[key].reshape(-1)), errors="coerce")

    for key in FORWARD_RETURN_KEYS:
        if key in keys:
            df[key] = pd.to_numeric(pd.Series(data[key].reshape(-1)), errors="coerce")

    # canonical true_walk_forward expects forward_return
    if "forward_return_5d" in df.columns:
        df["forward_return"] = df["forward_return_5d"]
    else:
        raise ValueError(f"{path} missing forward_return_5d")

    df = df.dropna(
        subset=[
            "timestamp",
            "symbol",
            "residual_z",
            "residual_r2",
            "rsi_2",
            "regime_score",
            "forward_return",
        ]
    )

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def apply_canonical_residual_rule(
    df: pd.DataFrame,
    rule: CanonicalResidualRule | None = None,
) -> pd.Series:
    rule = rule or CanonicalResidualRule()

    return (
        (pd.to_numeric(df["residual_z"], errors="coerce") <= rule.residual_z_threshold)
        & (pd.to_numeric(df["residual_r2"], errors="coerce") >= rule.residual_r2_threshold)
    )


def assign_strategy(df: pd.DataFrame) -> pd.Series:
    rsi = pd.to_numeric(df["rsi_2"], errors="coerce")
    regime = pd.to_numeric(df["regime_score"], errors="coerce")

    return np.where(
        (rsi < 30.0) & (regime <= 1.0),
        "mean_reversion",
        "structural_mr",
    )


def build_candidate_id(df: pd.DataFrame) -> pd.Series:
    raw = (
        df["timestamp"].astype(str)
        + "|"
        + df["symbol"].astype(str)
        + "|"
        + df["strategy"].astype(str)
        + "|canonical"
    )

    return raw.map(lambda x: sha256(x.encode("utf-8")).hexdigest()[:24])


def build_canonical_candidate_ledger(
    cache_dir: Path,
    rule: CanonicalResidualRule | None = None,
) -> pd.DataFrame:
    rule = rule or CanonicalResidualRule()

    files = sorted(cache_dir.glob("*.npz"))
    if not files:
        raise FileNotFoundError(f"No canonical NPZ files found in {cache_dir}")

    frames = []
    for path in files:
        frames.append(load_canonical_symbol_npz(path))

    df = pd.concat(frames, axis=0, ignore_index=True)

    df["strategy"] = assign_strategy(df)
    df["selected"] = apply_canonical_residual_rule(df, rule)
    df["candidate_id"] = build_candidate_id(df)
    df["lineage"] = "canonical_spy_residual_phase22a"
    df["selection_rule"] = rule.description

    df = df.sort_values(["timestamp", "symbol", "strategy"]).reset_index(drop=True)

    if df["candidate_id"].duplicated().any():
        dupes = int(df["candidate_id"].duplicated().sum())
        raise ValueError(f"Duplicate candidate_id rows: {dupes}")

    return df


def summarize_candidate_ledger(df: pd.DataFrame) -> dict[str, Any]:
    selected = df[df["selected"]].copy()
    rejected = df[~df["selected"]].copy()

    def summary(part: pd.DataFrame) -> dict[str, Any]:
        if part.empty:
            return {"rows": 0, "mean": None, "hit": None}

        r = pd.to_numeric(part["forward_return"], errors="coerce").dropna()

        if r.empty:
            return {"rows": 0, "mean": None, "hit": None}

        return {
            "rows": int(len(r)),
            "mean": float(r.mean()),
            "hit": float((r > 0).mean()),
        }

    return {
        "candidate_rows": int(len(df)),
        "selected_rows": int(df["selected"].sum()),
        "rejected_rows": int((~df["selected"]).sum()),
        "latest_candidate_ts": df["timestamp"].max().isoformat(),
        "latest_selected_ts": selected["timestamp"].max().isoformat() if not selected.empty else None,
        "selected": summary(selected),
        "rejected": summary(rejected),
    }


def write_ledger_atomic(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)


def build_selected_trade_ledger(candidate_ledger: pd.DataFrame) -> pd.DataFrame:
    selected = candidate_ledger[candidate_ledger["selected"]].copy()

    selected = selected.rename(columns={"forward_return": "realized_return"})

    keep = [
        "timestamp",
        "symbol",
        "strategy",
        "realized_return",
        "residual_z",
        "residual_r2",
        "rsi_2",
        "regime_score",
        "candidate_id",
        "lineage",
    ]

    existing = [c for c in keep if c in selected.columns]
    return selected[existing].sort_values(["timestamp", "symbol"]).reset_index(drop=True)
