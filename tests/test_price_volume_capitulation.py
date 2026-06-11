"""Tests for Phase 24B — Price-Volume Capitulation Reversal."""

from pathlib import Path

import pandas as pd

from src.research.price_volume.capitulation_reversal import (
    CapitulationConfig,
    audit_selection_rule,
    build_trade_ledger,
    classify_capitulation_result,
    compute_close_location,
    evaluate_folds,
    random_selection_baseline,
    summarize_ledger,
    write_csv_atomic,
    zscore_trailing,
)


def test_compute_close_location():
    df = pd.DataFrame(
        {
            "high": [10, 10],
            "low": [0, 0],
            "close": [5, 9],
        }
    )

    loc = compute_close_location(df)

    assert loc.tolist() == [0.5, 0.9]


def test_zscore_trailing():
    s = pd.Series(range(100), dtype=float)
    z = zscore_trailing(s, 20)

    assert len(z) == 100
    assert z.notna().sum() > 0


def test_audit_selection_rule():
    config = CapitulationConfig()

    df = pd.DataFrame(
        {
            "ret_3d_z": [-2.5, -1.0],
            "volume_z_20": [2.0, 2.0],
            "close_location": [0.7, 0.7],
            "selected": [True, False],
        }
    )

    audit = audit_selection_rule(df, config)

    assert audit["pass"] is True
    assert audit["mismatch_count"] == 0


def test_summarize_and_trade_ledger():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=3, tz="UTC"),
            "symbol": ["A", "B", "C"],
            "strategy": ["price_volume_capitulation"] * 3,
            "selected": [True, False, True],
            "forward_return": [0.01, -0.01, 0.02],
            "ret_3d_z": [-2.5, -1.0, -3.0],
            "volume_z_20": [2.0, 2.0, 3.0],
            "close_location": [0.7, 0.7, 0.8],
            "candidate_id": ["a", "b", "c"],
            "lineage": ["x", "x", "x"],
            "feature_config_hash": ["h", "h", "h"],
        }
    )

    summary = summarize_ledger(df)
    trades = build_trade_ledger(df)

    assert summary["selected_rows"] == 2
    assert len(trades) == 2
    assert "realized_return" in trades.columns


def test_evaluate_folds_and_random_baseline():
    rows = []
    for i in range(120):
        rows.append(
            {
                "timestamp": pd.Timestamp("2026-01-01", tz="UTC") + pd.Timedelta(days=i),
                "symbol": f"S{i}",
                "selected": i % 5 == 0,
                "forward_return": 0.02 if i % 5 == 0 else 0.0,
            }
        )

    df = pd.DataFrame(rows)
    folds = evaluate_folds(df, n_folds=4)
    rand = random_selection_baseline(df, n=50, seed=1)

    assert len(folds) == 4
    assert rand["observed_mean"] > rand["random_mean_avg"]


def test_classify_capitulation_result_pass():
    df = pd.DataFrame({"selected": [True] * 120 + [False] * 1000})

    rule_audit = {"pass": True}

    fold_df = pd.DataFrame(
        {
            "selected_rows": [30, 30, 30, 30],
            "selected_mean": [0.01, 0.01, 0.01, 0.01],
            "selected_hit": [0.55, 0.55, 0.55, 0.55],
            "selected_vs_rejected_spread": [0.01, 0.01, 0.01, 0.01],
        }
    )

    random_baseline = {"random_percentile": 0.99}

    result = classify_capitulation_result(
        df,
        rule_audit,
        fold_df,
        random_baseline,
        CapitulationConfig(),
    )

    assert result == "TRUE_WALK_FORWARD_PASS"


def test_write_csv_atomic(tmp_path: Path):
    path = tmp_path / "x.csv"
    df = pd.DataFrame({"a": [1]})

    write_csv_atomic(df, path)

    assert path.exists()
