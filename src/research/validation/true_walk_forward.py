from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class TrueWalkForwardClass(str, Enum):
    TRUE_WALK_FORWARD_PASS = "TRUE_WALK_FORWARD_PASS"
    TRUE_WALK_FORWARD_WEAK_PASS = "TRUE_WALK_FORWARD_WEAK_PASS"
    TRUE_WALK_FORWARD_FAIL = "TRUE_WALK_FORWARD_FAIL"
    TRUE_WALK_FORWARD_INCONCLUSIVE = "TRUE_WALK_FORWARD_INCONCLUSIVE"
    RULE_AUDIT_FAIL = "RULE_AUDIT_FAIL"
    ARTIFACT_FAIL = "ARTIFACT_FAIL"


@dataclass(frozen=True)
class TrueWalkForwardThresholds:
    min_total_candidates: int = 1000
    min_total_selected: int = 100
    min_test_selected_per_fold: int = 20
    min_positive_test_folds_rate: float = 0.75
    min_avg_test_mean: float = 0.005
    min_avg_test_hit: float = 0.52
    min_selected_vs_rejected_spread: float = 0.005
    min_random_percentile: float = 0.75


@dataclass(frozen=True)
class ResidualSelectionRule:
    residual_z_threshold: float = -2.0
    residual_r2_threshold: float = 0.20

    @property
    def description(self) -> str:
        return (
            f"residual_z <= {self.residual_z_threshold} "
            f"AND residual_r2 >= {self.residual_r2_threshold}"
        )


def normalize_candidate_ledger(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    required = ["timestamp", "symbol", "selected", "residual_z", "residual_r2"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Candidate ledger missing required columns: {missing}")

    ret_col = None
    for c in ["forward_return", "realized_return", "return", "ret", "pnl_pct"]:
        if c in df.columns:
            ret_col = c
            break

    if ret_col is None:
        raise ValueError("Candidate ledger missing forward/realized return column")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["symbol"] = df["symbol"].astype(str)
    df["selected"] = df["selected"].astype(bool)
    df["residual_z"] = pd.to_numeric(df["residual_z"], errors="coerce")
    df["residual_r2"] = pd.to_numeric(df["residual_r2"], errors="coerce")
    df["forward_return"] = pd.to_numeric(df[ret_col], errors="coerce")

    if "strategy" not in df.columns:
        df["strategy"] = "residual_reversion"

    df = df.dropna(
        subset=[
            "timestamp",
            "symbol",
            "selected",
            "residual_z",
            "residual_r2",
            "forward_return",
        ]
    )

    df = df.sort_values(["timestamp", "symbol", "strategy"]).reset_index(drop=True)

    if df.empty:
        raise ValueError("Candidate ledger normalized to zero rows")

    return df


def apply_residual_rule(
    df: pd.DataFrame,
    rule: ResidualSelectionRule | None = None,
) -> pd.Series:
    rule = rule or ResidualSelectionRule()

    return (
        (pd.to_numeric(df["residual_z"], errors="coerce") <= rule.residual_z_threshold)
        & (pd.to_numeric(df["residual_r2"], errors="coerce") >= rule.residual_r2_threshold)
    )


def audit_selected_flag_matches_rule(
    df: pd.DataFrame,
    rule: ResidualSelectionRule | None = None,
) -> dict[str, Any]:
    expected = apply_residual_rule(df, rule)
    actual = df["selected"].astype(bool)

    mismatches = actual.ne(expected)
    mismatch_count = int(mismatches.sum())

    return {
        "rule": (rule or ResidualSelectionRule()).description,
        "rows": int(len(df)),
        "selected_actual": int(actual.sum()),
        "selected_expected": int(expected.sum()),
        "mismatch_count": mismatch_count,
        "mismatch_rate": float(mismatch_count / len(df)) if len(df) else None,
        "pass": mismatch_count == 0,
    }


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

    r = pd.to_numeric(df["forward_return"], errors="coerce").dropna()

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


def build_time_folds(
    df: pd.DataFrame,
    n_folds: int = 4,
) -> list[tuple[int, pd.Timestamp, pd.Timestamp]]:
    timestamps = sorted(df["timestamp"].dropna().unique())

    if len(timestamps) < n_folds:
        raise ValueError("Not enough unique timestamps for folds")

    chunks = np.array_split(np.array(timestamps), n_folds)

    folds = []
    for i, chunk in enumerate(chunks, start=1):
        folds.append((i, pd.Timestamp(chunk[0]), pd.Timestamp(chunk[-1])))

    return folds


def evaluate_true_walk_forward_folds(
    df: pd.DataFrame,
    n_folds: int = 4,
) -> pd.DataFrame:
    folds = build_time_folds(df, n_folds=n_folds)
    rows = []

    for fold, start, end in folds:
        test = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].copy()

        selected = test[test["selected"]].copy()
        rejected = test[~test["selected"]].copy()

        selected_summary = summarize_returns(selected)
        rejected_summary = summarize_returns(rejected)

        selected_mean = selected_summary["mean"]
        rejected_mean = rejected_summary["mean"]

        if selected_mean is None or rejected_mean is None:
            spread = None
        else:
            spread = float(selected_mean - rejected_mean)

        rows.append(
            {
                "fold": fold,
                "test_start": start,
                "test_end": end,
                "candidate_rows": int(len(test)),
                "selected_rows": int(len(selected)),
                "rejected_rows": int(len(rejected)),
                "selected_mean": selected_summary["mean"],
                "selected_hit": selected_summary["hit_rate"],
                "rejected_mean": rejected_summary["mean"],
                "rejected_hit": rejected_summary["hit_rate"],
                "selected_vs_rejected_spread": spread,
            }
        )

    return pd.DataFrame(rows)


def random_selection_baseline(
    df: pd.DataFrame,
    n: int = 500,
    seed: int = 42,
) -> dict[str, Any]:
    selected_count = int(df["selected"].sum())

    if selected_count <= 0:
        return {
            "runs": 0,
            "observed_mean": None,
            "random_mean_avg": None,
            "random_percentile": None,
            "classification": "NO_SELECTED_ROWS",
        }

    observed_mean = summarize_returns(df[df["selected"]])["mean"]

    if observed_mean is None:
        return {
            "runs": 0,
            "observed_mean": None,
            "random_mean_avg": None,
            "random_percentile": None,
            "classification": "NO_OBSERVED_MEAN",
        }

    rng = np.random.default_rng(seed)
    returns = df["forward_return"].to_numpy()
    random_means = []

    for _ in range(n):
        idx = rng.choice(np.arange(len(df)), size=selected_count, replace=False)
        random_means.append(float(np.mean(returns[idx])))

    arr = np.array(random_means)
    random_percentile = float(np.mean(arr <= observed_mean))

    if random_percentile >= 0.95:
        classification = "STRONG_VS_RANDOM"
    elif random_percentile >= 0.75:
        classification = "OK_VS_RANDOM"
    else:
        classification = "WEAK_VS_RANDOM"

    return {
        "runs": int(n),
        "selected_count": selected_count,
        "observed_mean": float(observed_mean),
        "random_mean_avg": float(arr.mean()),
        "random_p05": float(np.percentile(arr, 5)),
        "random_p50": float(np.percentile(arr, 50)),
        "random_p95": float(np.percentile(arr, 95)),
        "random_percentile": random_percentile,
        "classification": classification,
    }


def classify_true_walk_forward(
    candidate_count: int,
    selected_count: int,
    rule_audit: dict[str, Any],
    fold_df: pd.DataFrame,
    random_baseline: dict[str, Any],
    thresholds: TrueWalkForwardThresholds | None = None,
) -> str:
    thresholds = thresholds or TrueWalkForwardThresholds()

    if candidate_count < thresholds.min_total_candidates:
        return TrueWalkForwardClass.ARTIFACT_FAIL.value

    if selected_count < thresholds.min_total_selected:
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_INCONCLUSIVE.value

    if not rule_audit.get("pass"):
        return TrueWalkForwardClass.RULE_AUDIT_FAIL.value

    if fold_df.empty:
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_INCONCLUSIVE.value

    if (fold_df["selected_rows"] < thresholds.min_test_selected_per_fold).any():
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_INCONCLUSIVE.value

    selected_means = fold_df["selected_mean"].dropna()
    selected_hits = fold_df["selected_hit"].dropna()
    spreads = fold_df["selected_vs_rejected_spread"].dropna()

    if selected_means.empty or selected_hits.empty or spreads.empty:
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_FAIL.value

    positive_fold_rate = float((selected_means > 0).mean())
    avg_selected_mean = float(selected_means.mean())
    avg_selected_hit = float(selected_hits.mean())
    avg_spread = float(spreads.mean())

    random_percentile = random_baseline.get("random_percentile")

    if avg_selected_mean < thresholds.min_avg_test_mean:
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_FAIL.value

    if avg_selected_hit < thresholds.min_avg_test_hit:
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_FAIL.value

    if positive_fold_rate < thresholds.min_positive_test_folds_rate:
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_FAIL.value

    if avg_spread < thresholds.min_selected_vs_rejected_spread:
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_FAIL.value

    if random_percentile is None or random_percentile < thresholds.min_random_percentile:
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_FAIL.value

    if positive_fold_rate >= 1.0 and random_percentile >= 0.95:
        return TrueWalkForwardClass.TRUE_WALK_FORWARD_PASS.value

    return TrueWalkForwardClass.TRUE_WALK_FORWARD_WEAK_PASS.value


def load_candidate_ledger(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    return normalize_candidate_ledger(pd.read_csv(path))
