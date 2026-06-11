from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd


class EdgeRobustnessClass(str, Enum):
    ROBUST_EDGE_CANDIDATE = "ROBUST_EDGE_CANDIDATE"
    WEAK_EDGE = "WEAK_EDGE"
    CONCENTRATED_EDGE = "CONCENTRATED_EDGE"
    UNSTABLE_EDGE = "UNSTABLE_EDGE"
    NO_EDGE = "NO_EDGE"
    NO_POWER = "NO_POWER"


@dataclass(frozen=True)
class RobustnessThresholds:
    min_trades: int = 100
    min_hit_rate: float = 0.52
    min_mean_return: float = 0.005
    max_top_symbol_contribution: float = 0.35
    max_top_month_contribution: float = 0.45
    min_bootstrap_positive_rate: float = 0.70
    min_split_positive_rate: float = 0.60


def normalize_trade_ledger(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    time_col = None
    for c in ["entry_time", "timestamp", "date", "datetime"]:
        if c in df.columns:
            time_col = c
            break

    if time_col is None:
        raise ValueError("Missing time column: entry_time/timestamp/date/datetime")

    ret_col = None
    for c in ["return", "realized_return", "ret", "pnl_pct", "forward_return"]:
        if c in df.columns:
            ret_col = c
            break

    if ret_col is None:
        raise ValueError("Missing return column")

    if "symbol" not in df.columns:
        raise ValueError("Missing symbol column")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df["realized_return"] = pd.to_numeric(df[ret_col], errors="coerce")
    df["symbol"] = df["symbol"].astype(str)

    if "strategy" not in df.columns:
        df["strategy"] = "UNKNOWN"

    if "side" not in df.columns:
        df["side"] = "UNKNOWN"

    df = df.dropna(subset=["timestamp", "realized_return", "symbol"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    if df.empty:
        raise ValueError("Trade ledger normalized to zero rows")

    return df


def summarize_returns(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "trades": 0,
            "mean": None,
            "median": None,
            "hit_rate": None,
            "sum_return": 0.0,
            "std": None,
            "sharpe_proxy": None,
        }

    r = pd.to_numeric(df["realized_return"], errors="coerce").dropna()

    if r.empty:
        return {
            "trades": 0,
            "mean": None,
            "median": None,
            "hit_rate": None,
            "sum_return": 0.0,
            "std": None,
            "sharpe_proxy": None,
        }

    std = float(r.std(ddof=1)) if len(r) > 1 else 0.0

    return {
        "trades": int(len(r)),
        "mean": float(r.mean()),
        "median": float(r.median()),
        "hit_rate": float((r > 0).mean()),
        "sum_return": float(r.sum()),
        "std": std,
        "sharpe_proxy": None if std == 0 else float(r.mean() / std),
    }


def grouped_summary(
    df: pd.DataFrame,
    group_col: str,
) -> pd.DataFrame:
    rows = []

    for key, group in df.groupby(group_col, dropna=False):
        s = summarize_returns(group)
        s[group_col] = key
        rows.append(s)

    if not rows:
        return pd.DataFrame()

    out = pd.DataFrame(rows)
    return out.sort_values("trades", ascending=False).reset_index(drop=True)


def calendar_summary(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["year_month"] = d["timestamp"].dt.strftime("%Y-%m")
    return grouped_summary(d, "year_month")


def contribution_concentration(
    df: pd.DataFrame,
    group_col: str,
) -> dict[str, Any]:
    if df.empty:
        return {
            "group_col": group_col,
            "top_group": None,
            "top_abs_contribution_share": None,
            "groups": 0,
        }

    g = (
        df.groupby(group_col)["realized_return"]
        .sum()
        .sort_values(key=lambda x: x.abs(), ascending=False)
    )

    total_abs = float(g.abs().sum())

    if total_abs == 0:
        share = None
    else:
        share = float(abs(g.iloc[0]) / total_abs)

    return {
        "group_col": group_col,
        "top_group": str(g.index[0]),
        "top_group_sum_return": float(g.iloc[0]),
        "top_abs_contribution_share": share,
        "groups": int(len(g)),
    }


def leave_one_group_out(
    df: pd.DataFrame,
    group_col: str,
) -> pd.DataFrame:
    rows = []

    for key in sorted(df[group_col].dropna().unique()):
        subset = df[df[group_col] != key]
        s = summarize_returns(subset)
        s[f"removed_{group_col}"] = key
        rows.append(s)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values("mean", ascending=True).reset_index(drop=True)


def bootstrap_mean_returns(
    df: pd.DataFrame,
    n: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    r = pd.to_numeric(df["realized_return"], errors="coerce").dropna().to_numpy()

    if len(r) < 2:
        return {
            "runs": 0,
            "positive_rate": None,
            "mean_of_means": None,
            "p05": None,
            "p50": None,
            "p95": None,
        }

    rng = np.random.default_rng(seed)
    means = []

    for _ in range(n):
        sample = rng.choice(r, size=len(r), replace=True)
        means.append(float(np.mean(sample)))

    arr = np.array(means)

    return {
        "runs": int(n),
        "positive_rate": float(np.mean(arr > 0)),
        "mean_of_means": float(arr.mean()),
        "p05": float(np.percentile(arr, 5)),
        "p50": float(np.percentile(arr, 50)),
        "p95": float(np.percentile(arr, 95)),
    }


def chronological_split_summary(
    df: pd.DataFrame,
    splits: int = 4,
) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    d = df.sort_values("timestamp").reset_index(drop=True)
    indices = np.array_split(d.index, splits)

    rows = []
    for i, idx in enumerate(indices, start=1):
        chunk = d.loc[idx]
        s = summarize_returns(chunk)
        s["split"] = i
        s["start"] = chunk["timestamp"].min()
        s["end"] = chunk["timestamp"].max()
        rows.append(s)

    return pd.DataFrame(rows)


def classify_edge_robustness(
    baseline: dict[str, Any],
    symbol_concentration: dict[str, Any],
    month_concentration: dict[str, Any],
    bootstrap: dict[str, Any],
    chronological_splits: pd.DataFrame,
    thresholds: RobustnessThresholds | None = None,
) -> str:
    thresholds = thresholds or RobustnessThresholds()

    trades = baseline["trades"]
    mean = baseline["mean"]
    hit = baseline["hit_rate"]

    if trades < thresholds.min_trades:
        return EdgeRobustnessClass.NO_POWER.value

    if mean is None or hit is None:
        return EdgeRobustnessClass.NO_EDGE.value

    if mean < thresholds.min_mean_return or hit < thresholds.min_hit_rate:
        return EdgeRobustnessClass.NO_EDGE.value

    top_symbol_share = symbol_concentration.get("top_abs_contribution_share")
    top_month_share = month_concentration.get("top_abs_contribution_share")

    if top_symbol_share is not None and top_symbol_share > thresholds.max_top_symbol_contribution:
        return EdgeRobustnessClass.CONCENTRATED_EDGE.value

    if top_month_share is not None and top_month_share > thresholds.max_top_month_contribution:
        return EdgeRobustnessClass.CONCENTRATED_EDGE.value

    boot_positive = bootstrap.get("positive_rate")
    if boot_positive is None or boot_positive < thresholds.min_bootstrap_positive_rate:
        return EdgeRobustnessClass.WEAK_EDGE.value

    if chronological_splits.empty:
        return EdgeRobustnessClass.UNSTABLE_EDGE.value

    positive_split_rate = float((chronological_splits["mean"] > 0).mean())

    if positive_split_rate < thresholds.min_split_positive_rate:
        return EdgeRobustnessClass.UNSTABLE_EDGE.value

    return EdgeRobustnessClass.ROBUST_EDGE_CANDIDATE.value
