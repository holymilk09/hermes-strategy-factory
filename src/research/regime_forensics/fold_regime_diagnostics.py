"""
Phase 25A — Regime Contingency Forensics.

Diagnoses whether the consistent fold-3 outperformance across multiple failed
feature families is caused by identifiable market regime conditions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def load_candidate_ledger(path: Path, family: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]

    required = ["timestamp", "symbol", "selected", "forward_return"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{family} missing columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["selected"] = df["selected"].astype(bool)
    df["forward_return"] = pd.to_numeric(df["forward_return"], errors="coerce")
    df["family"] = family

    df = df.dropna(subset=["timestamp", "symbol", "selected", "forward_return"])
    df = df.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    return df


def load_ohlcv(path: Path) -> pd.DataFrame:
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
        raise ValueError(f"Missing timestamp/date: {path}")

    required = ["open", "high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLC columns {missing}: {path}")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")
    return df.reset_index(drop=True)


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
            }
        )

    return pd.DataFrame(rows)


def summarize_selected_vs_rejected(df: pd.DataFrame, folds: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, fold in folds.iterrows():
        part = df[
            (df["timestamp"] >= fold["start"])
            & (df["timestamp"] <= fold["end"])
        ].copy()

        selected = part[part["selected"]].copy()
        rejected = part[~part["selected"]].copy()

        def stats(x: pd.DataFrame) -> dict[str, Any]:
            if x.empty:
                return {"n": 0, "mean": None, "hit": None}
            r = x["forward_return"].dropna()
            if r.empty:
                return {"n": 0, "mean": None, "hit": None}
            return {
                "n": int(len(r)),
                "mean": float(r.mean()),
                "hit": float((r > 0).mean()),
            }

        s = stats(selected)
        r = stats(rejected)

        spread = None
        if s["mean"] is not None and r["mean"] is not None:
            spread = s["mean"] - r["mean"]

        rows.append(
            {
                "family": df["family"].iloc[0],
                "fold": int(fold["fold"]),
                "start": fold["start"],
                "end": fold["end"],
                "candidates": int(len(part)),
                "selected": s["n"],
                "rejected": r["n"],
                "selected_mean": s["mean"],
                "selected_hit": s["hit"],
                "rejected_mean": r["mean"],
                "rejected_hit": r["hit"],
                "spread": spread,
            }
        )

    return pd.DataFrame(rows)


def compute_spy_regime_features(spy: pd.DataFrame) -> pd.DataFrame:
    out = spy.copy()
    close = out["close"]

    out["spy_ret_5d"] = close / close.shift(5) - 1.0
    out["spy_ret_20d"] = close / close.shift(20) - 1.0
    out["spy_ret_60d"] = close / close.shift(60) - 1.0

    ret = close.pct_change()
    out["spy_vol_20d"] = ret.rolling(20, min_periods=20).std()
    out["spy_vol_60d"] = ret.rolling(60, min_periods=60).std()

    out["spy_ma20"] = close.rolling(20, min_periods=20).mean()
    out["spy_ma50"] = close.rolling(50, min_periods=50).mean()
    out["spy_ma200"] = close.rolling(200, min_periods=100).mean()

    out["spy_above_ma20"] = close > out["spy_ma20"]
    out["spy_above_ma50"] = close > out["spy_ma50"]
    out["spy_above_ma200"] = close > out["spy_ma200"]

    rolling_high = close.rolling(60, min_periods=20).max()
    rolling_low = close.rolling(60, min_periods=20).min()
    out["spy_drawdown_60d"] = close / rolling_high - 1.0
    out["spy_position_60d"] = (close - rolling_low) / (rolling_high - rolling_low).replace(0, np.nan)

    return out


def compute_universe_breadth(candidate_df: pd.DataFrame) -> pd.DataFrame:
    d = candidate_df.copy()
    d["ret_positive"] = d["forward_return"] > 0

    rows = []
    for ts, group in d.groupby("timestamp"):
        rows.append(
            {
                "timestamp": ts,
                "universe_forward_mean": float(group["forward_return"].mean()),
                "universe_forward_hit": float(group["ret_positive"].mean()),
                "candidate_count": int(len(group)),
                "selected_count": int(group["selected"].sum()),
            }
        )

    return pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)


def summarize_regime_by_fold(
    folds: pd.DataFrame,
    spy_features: pd.DataFrame,
    breadth: pd.DataFrame,
) -> pd.DataFrame:
    merged = pd.merge_asof(
        breadth.sort_values("timestamp"),
        spy_features.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )

    rows = []

    for _, fold in folds.iterrows():
        part = merged[
            (merged["timestamp"] >= fold["start"])
            & (merged["timestamp"] <= fold["end"])
        ].copy()

        if part.empty:
            rows.append({"fold": int(fold["fold"]), "rows": 0})
            continue

        rows.append(
            {
                "fold": int(fold["fold"]),
                "start": fold["start"],
                "end": fold["end"],
                "rows": int(len(part)),
                "spy_ret_20d_mean": float(part["spy_ret_20d"].mean()),
                "spy_ret_60d_mean": float(part["spy_ret_60d"].mean()),
                "spy_vol_20d_mean": float(part["spy_vol_20d"].mean()),
                "spy_vol_60d_mean": float(part["spy_vol_60d"].mean()),
                "spy_drawdown_60d_mean": float(part["spy_drawdown_60d"].mean()),
                "spy_position_60d_mean": float(part["spy_position_60d"].mean()),
                "spy_above_ma20_rate": float(part["spy_above_ma20"].mean()),
                "spy_above_ma50_rate": float(part["spy_above_ma50"].mean()),
                "spy_above_ma200_rate": float(part["spy_above_ma200"].mean()),
                "universe_forward_mean": float(part["universe_forward_mean"].mean()),
                "universe_forward_hit": float(part["universe_forward_hit"].mean()),
                "selected_count_sum": int(part["selected_count"].sum()),
            }
        )

    return pd.DataFrame(rows)


def classify_regime_contingency(
    family_summary: pd.DataFrame,
    regime_summary: pd.DataFrame,
) -> str:
    if family_summary.empty or regime_summary.empty:
        return "REGIME_FORENSICS_INCONCLUSIVE"

    fold_spreads = (
        family_summary.groupby("fold")["spread"]
        .mean()
        .dropna()
        .sort_values(ascending=False)
    )

    if fold_spreads.empty:
        return "REGIME_FORENSICS_INCONCLUSIVE"

    best_fold = int(fold_spreads.index[0])

    if best_fold != 3:
        return "REGIME_PATTERN_NOT_CONSISTENT"

    best = regime_summary[regime_summary["fold"].eq(best_fold)]
    others = regime_summary[~regime_summary["fold"].eq(best_fold)]

    if best.empty or others.empty:
        return "REGIME_FORENSICS_INCONCLUSIVE"

    best_row = best.iloc[0]

    # Diagnostic only:
    # Fold 3 is considered distinct if it has clearly higher broad market forward behavior
    # or a materially different trend/position state.
    universe_advantage = (
        best_row["universe_forward_mean"] - others["universe_forward_mean"].mean()
    )

    position_advantage = (
        best_row["spy_position_60d_mean"] - others["spy_position_60d_mean"].mean()
    )

    trend_advantage = (
        best_row["spy_above_ma50_rate"] - others["spy_above_ma50_rate"].mean()
    )

    if universe_advantage > 0.005 or position_advantage > 0.15 or trend_advantage > 0.25:
        return "REGIME_DEPENDENCY_PLAUSIBLE"

    return "REGIME_PATTERN_WEAK_OR_RANDOM"


def build_diagnostic_decision(classification: str) -> str:
    if classification == "REGIME_DEPENDENCY_PLAUSIBLE":
        return (
            "Regime dependency is plausible. Next phase may define one pre-registered "
            "regime-conditioned hypothesis. Do not reuse failed rules without a holdout rule."
        )

    if classification == "REGIME_PATTERN_WEAK_OR_RANDOM":
        return (
            "Fold clustering exists but regime explanation is weak. Prefer a new orthogonal feature family."
        )

    if classification == "REGIME_PATTERN_NOT_CONSISTENT":
        return (
            "Fold 3 is not consistently the best fold across families. Do not pursue regime rescue."
        )

    return (
        "Regime forensics inconclusive. Do not create a trading rule from this result."
    )
