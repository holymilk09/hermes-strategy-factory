from pathlib import Path

import pandas as pd

from src.research.validation.walk_forward import (
    WalkForwardValidationLevel,
    artifact_audit,
    build_chronological_folds,
    classify_walk_forward,
    fold_results_to_frame,
    normalize_trade_ledger,
    run_ledger_only_walk_forward,
    summarize_returns,
)


def test_normalize_trade_ledger():
    raw = pd.DataFrame(
        {
            "symbol": ["A", "B"],
            "entry_time": ["2024-01-01", "2024-01-02"],
            "return": [0.01, -0.02],
        }
    )

    out = normalize_trade_ledger(raw)

    assert "timestamp" in out.columns
    assert "realized_return" in out.columns
    assert "strategy" in out.columns
    assert "side" in out.columns
    assert len(out) == 2


def test_build_chronological_folds():
    raw = pd.DataFrame(
        {
            "symbol": ["A"] * 100,
            "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
            "realized_return": [0.01] * 100,
            "strategy": ["x"] * 100,
            "side": ["long"] * 100,
        }
    )

    folds = build_chronological_folds(raw, n_folds=4, min_test_trades=10)

    assert len(folds) == 4
    assert folds[0].train_end < folds[0].test_start


def test_run_ledger_only_walk_forward():
    raw = pd.DataFrame(
        {
            "symbol": ["A"] * 100,
            "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
            "realized_return": [0.01] * 100,
            "strategy": ["x"] * 100,
            "side": ["long"] * 100,
        }
    )

    results = run_ledger_only_walk_forward(raw, n_folds=4, min_test_trades=10)

    assert len(results) == 4
    assert all(abs(r["test"]["mean"] - 0.01) < 1e-10 for r in results)


def test_fold_results_to_frame():
    raw = pd.DataFrame(
        {
            "symbol": ["A"] * 100,
            "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
            "realized_return": [0.01] * 100,
            "strategy": ["x"] * 100,
            "side": ["long"] * 100,
        }
    )

    results = run_ledger_only_walk_forward(raw, n_folds=4, min_test_trades=10)
    frame = fold_results_to_frame(results)

    assert len(frame) == 4
    assert "test_mean" in frame.columns


def test_classify_walk_forward_weak_pass_for_ledger_only():
    baseline = {"trades": 200, "mean": 0.01, "hit_rate": 0.56}
    fold_results = []

    for i in range(4):
        fold_results.append(
            {
                "test": {"trades": 50, "mean": 0.01, "hit_rate": 0.56},
                "consistency_ratio": 0.80,
            }
        )

    result = classify_walk_forward(
        baseline=baseline,
        fold_results=fold_results,
        validation_level=WalkForwardValidationLevel.LEDGER_ONLY_OOS_AUDIT.value,
    )

    assert result == "WALK_FORWARD_WEAK_PASS"


def test_classify_walk_forward_true_pass():
    baseline = {"trades": 200, "mean": 0.01, "hit_rate": 0.56}
    fold_results = []

    for i in range(4):
        fold_results.append(
            {
                "test": {"trades": 50, "mean": 0.01, "hit_rate": 0.56},
                "consistency_ratio": 0.80,
            }
        )

    result = classify_walk_forward(
        baseline=baseline,
        fold_results=fold_results,
        validation_level=WalkForwardValidationLevel.TRUE_WALK_FORWARD.value,
    )

    assert result == "WALK_FORWARD_PASS"


def test_classify_walk_forward_fail_negative_oos():
    baseline = {"trades": 200, "mean": 0.01, "hit_rate": 0.56}
    fold_results = []

    for i in range(4):
        fold_results.append(
            {
                "test": {"trades": 50, "mean": -0.01, "hit_rate": 0.40},
                "consistency_ratio": -1.0,
            }
        )

    result = classify_walk_forward(
        baseline=baseline,
        fold_results=fold_results,
        validation_level=WalkForwardValidationLevel.TRUE_WALK_FORWARD.value,
    )

    assert result == "WALK_FORWARD_FAIL"


def test_artifact_audit_insufficient_tmp(tmp_path: Path):
    result = artifact_audit(tmp_path)

    assert result["validation_level"] == "INSUFFICIENT_DATA"
