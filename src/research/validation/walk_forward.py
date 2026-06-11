from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class WalkForwardValidationLevel(str, Enum):
    TRUE_WALK_FORWARD = "TRUE_WALK_FORWARD"
    LEDGER_ONLY_OOS_AUDIT = "LEDGER_ONLY_OOS_AUDIT"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class WalkForwardClass(str, Enum):
    WALK_FORWARD_PASS = "WALK_FORWARD_PASS"
    WALK_FORWARD_WEAK_PASS = "WALK_FORWARD_WEAK_PASS"
    WALK_FORWARD_FAIL = "WALK_FORWARD_FAIL"
    WALK_FORWARD_INCONCLUSIVE = "WALK_FORWARD_INCONCLUSIVE"
    ARTIFACTS_INSUFFICIENT = "ARTIFACTS_INSUFFICIENT"


@dataclass(frozen=True)
class WalkForwardThresholds:
    min_total_trades: int = 100
    min_test_trades_per_fold: int = 20
    min_positive_test_folds_rate: float = 0.60
    min_oos_mean_return: float = 0.005
    min_oos_hit_rate: float = 0.52
    min_train_test_consistency_ratio: float = 0.35


@dataclass(frozen=True)
class FoldSpec:
    fold: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp


def normalize_trade_ledger(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    time_col = None
    for c in ["entry_time", "timestamp", "date", "datetime"]:
        if c in df.columns:
            time_col = c
            break

    if time_col is None:
        raise ValueError("Missing time column")

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


def artifact_audit(root: Path) -> dict[str, Any]:
    candidates = {
        "trade_ledger": [
            root / "reports" / "strategy_factory" / "residual_reversion_trade_ledger.csv",
            root / "reports" / "strategy_factory" / "residual_strategy_trade_ledger.csv",
            root / "reports" / "strategy_factory" / "phase14_residual_trade_ledger.csv",
        ],
        "candidate_feature_ledger": [
            root / "reports" / "strategy_factory" / "residual_candidate_feature_ledger.csv",
            root / "reports" / "strategy_factory" / "residual_candidates_with_features.csv",
            root / "data" / "research" / "residual_candidate_feature_ledger.csv",
        ],
        "selection_config": [
            root / "config" / "residual_strategy.yaml",
            root / "config" / "strategy_factory.yaml",
            root / "reports" / "strategy_factory" / "residual_selection_config.json",
        ],
    }

    found: dict[str, list[str]] = {}
    missing: dict[str, list[str]] = {}

    for key, paths in candidates.items():
        existing = [str(p) for p in paths if p.exists()]
        absent = [str(p) for p in paths if not p.exists()]
        found[key] = existing
        missing[key] = absent

    has_trade_ledger = len(found["trade_ledger"]) > 0
    has_candidate_features = len(found["candidate_feature_ledger"]) > 0
    has_selection_config = len(found["selection_config"]) > 0

    if has_candidate_features and has_selection_config:
        level = WalkForwardValidationLevel.TRUE_WALK_FORWARD.value
    elif has_trade_ledger:
        level = WalkForwardValidationLevel.LEDGER_ONLY_OOS_AUDIT.value
    else:
        level = WalkForwardValidationLevel.INSUFFICIENT_DATA.value

    return {
        "validation_level": level,
        "found": found,
        "missing": missing,
        "has_trade_ledger": has_trade_ledger,
        "has_candidate_features": has_candidate_features,
        "has_selection_config": has_selection_config,
    }


def build_chronological_folds(
    trades: pd.DataFrame,
    n_folds: int = 4,
    min_test_trades: int = 20,
) -> list[FoldSpec]:
    if n_folds < 2:
        raise ValueError("n_folds must be >= 2")

    d = trades.sort_values("timestamp").reset_index(drop=True)

    if len(d) < min_test_trades * n_folds:
        raise ValueError(
            f"Not enough trades for {n_folds} folds with min_test_trades={min_test_trades}"
        )

    indices = np.array_split(d.index.to_numpy(), n_folds + 1)
    folds: list[FoldSpec] = []

    for i in range(1, len(indices)):
        train_idx = np.concatenate(indices[:i])
        train = d.loc[train_idx]
        test = d.loc[indices[i]]

        if len(test) < min_test_trades:
            continue

        folds.append(
            FoldSpec(
                fold=i,
                train_start=train["timestamp"].min(),
                train_end=train["timestamp"].max(),
                test_start=test["timestamp"].min(),
                test_end=test["timestamp"].max(),
            )
        )

    return folds


def evaluate_fold(
    trades: pd.DataFrame,
    fold: FoldSpec,
) -> dict[str, Any]:
    train = trades[
        (trades["timestamp"] >= fold.train_start)
        & (trades["timestamp"] <= fold.train_end)
    ].copy()

    test = trades[
        (trades["timestamp"] >= fold.test_start)
        & (trades["timestamp"] <= fold.test_end)
    ].copy()

    train_summary = summarize_returns(train)
    test_summary = summarize_returns(test)

    train_mean = train_summary["mean"]
    test_mean = test_summary["mean"]

    if train_mean is None or train_mean == 0 or test_mean is None:
        consistency_ratio = None
    else:
        consistency_ratio = float(test_mean / train_mean)

    return {
        "fold": fold.fold,
        "train_start": fold.train_start,
        "train_end": fold.train_end,
        "test_start": fold.test_start,
        "test_end": fold.test_end,
        "train": train_summary,
        "test": test_summary,
        "consistency_ratio": consistency_ratio,
    }


def run_ledger_only_walk_forward(
    trades: pd.DataFrame,
    n_folds: int = 4,
    min_test_trades: int = 20,
) -> list[dict[str, Any]]:
    folds = build_chronological_folds(
        trades=trades,
        n_folds=n_folds,
        min_test_trades=min_test_trades,
    )

    return [evaluate_fold(trades, fold) for fold in folds]


def classify_walk_forward(
    baseline: dict[str, Any],
    fold_results: list[dict[str, Any]],
    validation_level: str,
    thresholds: WalkForwardThresholds | None = None,
) -> str:
    thresholds = thresholds or WalkForwardThresholds()

    if validation_level == WalkForwardValidationLevel.INSUFFICIENT_DATA.value:
        return WalkForwardClass.ARTIFACTS_INSUFFICIENT.value

    if baseline["trades"] < thresholds.min_total_trades:
        return WalkForwardClass.WALK_FORWARD_INCONCLUSIVE.value

    if not fold_results:
        return WalkForwardClass.WALK_FORWARD_INCONCLUSIVE.value

    test_means = []
    test_hits = []
    test_trades = []
    consistency = []

    for r in fold_results:
        test = r["test"]
        test_trades.append(test["trades"])
        test_means.append(test["mean"])
        test_hits.append(test["hit_rate"])
        consistency.append(r["consistency_ratio"])

    if any(t < thresholds.min_test_trades_per_fold for t in test_trades):
        return WalkForwardClass.WALK_FORWARD_INCONCLUSIVE.value

    clean_means = [x for x in test_means if x is not None]
    clean_hits = [x for x in test_hits if x is not None]
    clean_consistency = [x for x in consistency if x is not None]

    if not clean_means or not clean_hits:
        return WalkForwardClass.WALK_FORWARD_FAIL.value

    positive_test_rate = float(np.mean(np.array(clean_means) > 0))
    avg_oos_mean = float(np.mean(clean_means))
    avg_oos_hit = float(np.mean(clean_hits))

    consistency_pass_rate = 0.0
    if clean_consistency:
        consistency_pass_rate = float(
            np.mean(np.array(clean_consistency) >= thresholds.min_train_test_consistency_ratio)
        )

    if avg_oos_mean < thresholds.min_oos_mean_return:
        return WalkForwardClass.WALK_FORWARD_FAIL.value

    if avg_oos_hit < thresholds.min_oos_hit_rate:
        return WalkForwardClass.WALK_FORWARD_FAIL.value

    if positive_test_rate < thresholds.min_positive_test_folds_rate:
        return WalkForwardClass.WALK_FORWARD_FAIL.value

    if validation_level == WalkForwardValidationLevel.LEDGER_ONLY_OOS_AUDIT.value:
        if positive_test_rate >= 1.0 and consistency_pass_rate >= 0.75:
            return WalkForwardClass.WALK_FORWARD_WEAK_PASS.value
        return WalkForwardClass.WALK_FORWARD_INCONCLUSIVE.value

    if validation_level == WalkForwardValidationLevel.TRUE_WALK_FORWARD.value:
        if positive_test_rate >= 1.0 and consistency_pass_rate >= 0.75:
            return WalkForwardClass.WALK_FORWARD_PASS.value
        return WalkForwardClass.WALK_FORWARD_WEAK_PASS.value

    return WalkForwardClass.WALK_FORWARD_INCONCLUSIVE.value


def fold_results_to_frame(fold_results: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []

    for r in fold_results:
        rows.append(
            {
                "fold": r["fold"],
                "train_start": r["train_start"],
                "train_end": r["train_end"],
                "test_start": r["test_start"],
                "test_end": r["test_end"],
                "train_trades": r["train"]["trades"],
                "train_mean": r["train"]["mean"],
                "train_hit": r["train"]["hit_rate"],
                "test_trades": r["test"]["trades"],
                "test_mean": r["test"]["mean"],
                "test_hit": r["test"]["hit_rate"],
                "consistency_ratio": r["consistency_ratio"],
            }
        )

    return pd.DataFrame(rows)
