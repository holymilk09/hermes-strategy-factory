from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RegimeConditionedConfig:
    ret_3d_z_threshold: float = -1.5
    volume_z_threshold: float = 1.0
    close_location_threshold: float = 0.50
    spy_drawdown_60d_threshold: float = -0.0146
    min_holdout_selected: int = 75

    @property
    def config_hash(self) -> str:
        return sha256(repr(self).encode("utf-8")).hexdigest()[:16]


def load_capitulation_v2_ledger(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]

    required = [
        "timestamp",
        "symbol",
        "ret_3d_z",
        "volume_z_20",
        "close_location",
        "forward_return",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Capitulation V2 ledger missing columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    for c in ["ret_3d_z", "volume_z_20", "close_location", "forward_return"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=required)
    df = df.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    return df


def load_spy_ohlcv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]

    time_col = None
    for c in ["timestamp", "date", "datetime", "time"]:
        if c in df.columns:
            time_col = c
            break

    if time_col is None:
        raise ValueError("SPY OHLCV missing timestamp/date column")

    if "close" not in df.columns:
        raise ValueError("SPY OHLCV missing close column")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    df = df.dropna(subset=["timestamp", "close"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")

    return df[["timestamp", "close"]].reset_index(drop=True)


def compute_spy_drawdown_60d(spy: pd.DataFrame) -> pd.DataFrame:
    out = spy.copy()

    rolling_high = out["close"].rolling(60, min_periods=20).max()
    out["spy_drawdown_60d"] = out["close"] / rolling_high - 1.0

    return out[["timestamp", "spy_drawdown_60d"]].dropna().reset_index(drop=True)


def attach_spy_drawdown(
    candidates: pd.DataFrame,
    spy_drawdown: pd.DataFrame,
) -> pd.DataFrame:
    merged = pd.merge_asof(
        candidates.sort_values("timestamp"),
        spy_drawdown.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
        allow_exact_matches=True,
    )

    return merged.dropna(subset=["spy_drawdown_60d"]).reset_index(drop=True)


def apply_regime_conditioned_rule(
    df: pd.DataFrame,
    config: RegimeConditionedConfig | None = None,
) -> pd.Series:
    config = config or RegimeConditionedConfig()

    return (
        (pd.to_numeric(df["ret_3d_z"], errors="coerce") <= config.ret_3d_z_threshold)
        & (pd.to_numeric(df["volume_z_20"], errors="coerce") >= config.volume_z_threshold)
        & (pd.to_numeric(df["close_location"], errors="coerce") >= config.close_location_threshold)
        & (pd.to_numeric(df["spy_drawdown_60d"], errors="coerce") <= config.spy_drawdown_60d_threshold)
    )


def build_regime_conditioned_ledger(
    capitulation_v2_path: Path,
    spy_path: Path,
    config: RegimeConditionedConfig | None = None,
) -> pd.DataFrame:
    config = config or RegimeConditionedConfig()

    base = load_capitulation_v2_ledger(capitulation_v2_path)
    spy = load_spy_ohlcv(spy_path)
    drawdown = compute_spy_drawdown_60d(spy)

    df = attach_spy_drawdown(base, drawdown)

    df["selected"] = apply_regime_conditioned_rule(df, config)
    df["strategy"] = "regime_conditioned_capitulation_v2"
    df["lineage"] = "regime_conditioned_capitulation_v2_phase25c"
    df["feature_config_hash"] = config.config_hash

    raw = (
        df["timestamp"].astype(str)
        + "|"
        + df["symbol"].astype(str)
        + "|regime_conditioned_capitulation_v2"
    )
    df["candidate_id"] = raw.map(lambda x: sha256(x.encode("utf-8")).hexdigest()[:24])

    if df["candidate_id"].duplicated().any():
        dupes = int(df["candidate_id"].duplicated().sum())
        raise ValueError(f"Duplicate candidate_id rows: {dupes}")

    return df.sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def audit_rule(df: pd.DataFrame, config: RegimeConditionedConfig | None = None) -> dict[str, Any]:
    config = config or RegimeConditionedConfig()

    expected = apply_regime_conditioned_rule(df, config)
    actual = df["selected"].astype(bool)
    mismatch = actual.ne(expected)

    return {
        "rule": (
            f"ret_3d_z <= {config.ret_3d_z_threshold} AND "
            f"volume_z_20 >= {config.volume_z_threshold} AND "
            f"close_location >= {config.close_location_threshold} AND "
            f"spy_drawdown_60d <= {config.spy_drawdown_60d_threshold}"
        ),
        "rows": int(len(df)),
        "selected_actual": int(actual.sum()),
        "selected_expected": int(expected.sum()),
        "mismatch_count": int(mismatch.sum()),
        "mismatch_rate": float(mismatch.mean()) if len(df) else None,
        "pass": int(mismatch.sum()) == 0,
    }


def build_time_folds(df: pd.DataFrame, n_folds: int = 4) -> pd.DataFrame:
    timestamps = sorted(df["timestamp"].dropna().unique())
    chunks = np.array_split(np.array(timestamps), n_folds)

    rows = []
    for i, chunk in enumerate(chunks, start=1):
        rows.append(
            {
                "fold": i,
                "start": pd.Timestamp(chunk[0]),
                "end": pd.Timestamp(chunk[-1]),
                "is_holdout": i in {3, 4},
            }
        )

    return pd.DataFrame(rows)


def summarize_returns(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"trades": 0, "mean": None, "hit_rate": None}

    r = pd.to_numeric(df["forward_return"], errors="coerce").dropna()

    if r.empty:
        return {"trades": 0, "mean": None, "hit_rate": None}

    return {
        "trades": int(len(r)),
        "mean": float(r.mean()),
        "hit_rate": float((r > 0).mean()),
    }


def evaluate_folds(df: pd.DataFrame) -> pd.DataFrame:
    folds = build_time_folds(df, 4)
    rows = []

    for _, fold in folds.iterrows():
        part = df[
            (df["timestamp"] >= fold["start"])
            & (df["timestamp"] <= fold["end"])
        ].copy()

        selected = part[part["selected"]].copy()
        rejected = part[~part["selected"]].copy()

        s = summarize_returns(selected)
        r = summarize_returns(rejected)

        spread = None
        if s["mean"] is not None and r["mean"] is not None:
            spread = s["mean"] - r["mean"]

        rows.append(
            {
                "fold": int(fold["fold"]),
                "is_holdout": bool(fold["is_holdout"]),
                "candidate_rows": int(len(part)),
                "selected_rows": s["trades"],
                "rejected_rows": r["trades"],
                "selected_mean": s["mean"],
                "selected_hit": s["hit_rate"],
                "rejected_mean": r["mean"],
                "rejected_hit": r["hit_rate"],
                "spread": spread,
            }
        )

    return pd.DataFrame(rows)


def random_baseline_holdout(
    df: pd.DataFrame,
    fold_df: pd.DataFrame,
    n: int = 500,
    seed: int = 42,
) -> dict[str, Any]:
    holdout_folds = fold_df[fold_df["is_holdout"]].copy()

    if holdout_folds.empty:
        return {"classification": "NO_HOLDOUT"}

    holdout_parts = []

    folds = build_time_folds(df, 4)
    for _, fold in folds[folds["is_holdout"]].iterrows():
        holdout_parts.append(
            df[(df["timestamp"] >= fold["start"]) & (df["timestamp"] <= fold["end"])]
        )

    holdout = pd.concat(holdout_parts, axis=0, ignore_index=True)

    selected = holdout[holdout["selected"]].copy()
    selected_count = int(len(selected))

    if selected_count == 0:
        return {"classification": "NO_SELECTED_ROWS"}

    observed_mean = float(selected["forward_return"].mean())

    rng = np.random.default_rng(seed)
    returns = pd.to_numeric(holdout["forward_return"], errors="coerce").fillna(0.0).to_numpy()
    idx_all = np.arange(len(holdout))

    means = []
    for _ in range(n):
        idx = rng.choice(idx_all, size=selected_count, replace=False)
        means.append(float(np.mean(returns[idx])))

    arr = np.array(means)
    pct = float(np.mean(arr <= observed_mean))

    if pct >= 0.95:
        cls = "STRONG_VS_RANDOM"
    elif pct >= 0.90:
        cls = "OK_VS_RANDOM"
    else:
        cls = "WEAK_VS_RANDOM"

    return {
        "runs": int(n),
        "selected_count": selected_count,
        "observed_mean": observed_mean,
        "random_mean_avg": float(arr.mean()),
        "random_p05": float(np.percentile(arr, 5)),
        "random_p50": float(np.percentile(arr, 50)),
        "random_p95": float(np.percentile(arr, 95)),
        "random_percentile": pct,
        "classification": cls,
    }


def classify_holdout(
    df: pd.DataFrame,
    rule_audit: dict[str, Any],
    fold_df: pd.DataFrame,
    random_baseline: dict[str, Any],
    config: RegimeConditionedConfig | None = None,
) -> str:
    config = config or RegimeConditionedConfig()

    if not rule_audit.get("pass"):
        return "RULE_AUDIT_FAIL"

    holdout = fold_df[fold_df["is_holdout"]].copy()

    if holdout.empty:
        return "REGIME_HOLDOUT_INCONCLUSIVE"

    total_selected = int(holdout["selected_rows"].sum())

    if total_selected < config.min_holdout_selected:
        return "REGIME_HOLDOUT_INCONCLUSIVE"

    if (holdout["selected_rows"] < 20).any():
        return "REGIME_HOLDOUT_INCONCLUSIVE"

    selected_mean = float(np.average(
        holdout["selected_mean"],
        weights=holdout["selected_rows"],
    ))

    selected_hit = float(np.average(
        holdout["selected_hit"],
        weights=holdout["selected_rows"],
    ))

    spread_mean = float(np.average(
        holdout["spread"],
        weights=holdout["selected_rows"],
    ))

    positive_spread_folds = int((holdout["spread"] > 0).sum())

    random_pct = random_baseline.get("random_percentile")

    if selected_mean < 0.0125:
        return "REGIME_HOLDOUT_FAIL"

    if selected_hit < 0.57:
        return "REGIME_HOLDOUT_FAIL"

    if spread_mean < 0.0075:
        return "REGIME_HOLDOUT_FAIL"

    if positive_spread_folds < 2:
        return "REGIME_HOLDOUT_FAIL"

    if random_pct is None or random_pct < 0.90:
        return "REGIME_HOLDOUT_FAIL"

    if random_pct >= 0.95:
        return "REGIME_HOLDOUT_PASS_RESEARCH_ONLY"

    return "REGIME_HOLDOUT_WEAK_PASS"


def build_trade_ledger(df: pd.DataFrame) -> pd.DataFrame:
    selected = df[df["selected"]].copy()
    selected = selected.rename(columns={"forward_return": "realized_return"})

    keep = [
        "timestamp",
        "symbol",
        "strategy",
        "realized_return",
        "ret_3d_z",
        "volume_z_20",
        "close_location",
        "spy_drawdown_60d",
        "candidate_id",
        "lineage",
        "feature_config_hash",
    ]

    existing = [c for c in keep if c in selected.columns]
    return selected[existing].sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def write_csv_atomic(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)
