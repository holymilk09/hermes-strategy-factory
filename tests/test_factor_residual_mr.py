"""Tests for Phase 24A — Factor-Neutral Residual Mean Reversion."""

from pathlib import Path

import numpy as np
import pandas as pd

from src.research.factors.factor_residual_mr import (
    FactorResidualConfig,
    build_trade_ledger,
    compute_forward_return,
    compute_rsi_2,
    rolling_factor_residual_features,
    summarize_ledger,
    write_csv_atomic,
)


def test_compute_rsi_2():
    close = pd.Series([10, 9, 8, 9, 10, 11], dtype=float)
    rsi = compute_rsi_2(close)
    assert len(rsi) == len(close)
    assert rsi.notna().all()


def test_compute_forward_return():
    close = pd.Series([100, 105, 110, 120], dtype=float)
    fwd = compute_forward_return(close, 2)
    assert round(float(fwd.iloc[0]), 4) == 0.1


def test_rolling_factor_residual_features():
    rng = np.random.default_rng(seed=42)
    y = pd.Series(rng.normal(0, 0.01, 120))
    x = pd.DataFrame(
        {
            "SPY": rng.normal(0, 0.01, 120),
            "XLK": rng.normal(0, 0.01, 120),
        }
    )

    z, r2 = rolling_factor_residual_features(y, x, lookback=40, min_obs=30)

    assert len(z) == 120
    assert len(r2) == 120


def test_build_trade_ledger():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=3, tz="UTC"),
            "symbol": ["A", "B", "C"],
            "strategy": ["factor_residual_mr"] * 3,
            "selected": [True, False, True],
            "forward_return": [0.01, -0.01, 0.02],
            "factor_residual_z": [-2.5, -1.0, -3.0],
            "factor_model_r2": [0.3, 0.3, 0.5],
            "residual_z": [-2.5, -1.0, -3.0],
            "residual_r2": [0.3, 0.3, 0.5],
            "rsi_2": [20, 50, 10],
            "candidate_id": ["a", "b", "c"],
            "lineage": ["x", "x", "x"],
            "feature_config_hash": ["h", "h", "h"],
        }
    )

    trades = build_trade_ledger(df)

    assert len(trades) == 2
    assert "realized_return" in trades.columns


def test_summarize_ledger():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=3, tz="UTC"),
            "selected": [True, False, True],
            "forward_return": [0.01, -0.01, 0.02],
        }
    )

    s = summarize_ledger(df)

    assert s["candidate_rows"] == 3
    assert s["selected_rows"] == 2
    assert s["rejected_rows"] == 1


def test_write_csv_atomic(tmp_path: Path):
    path = tmp_path / "x.csv"
    df = pd.DataFrame({"a": [1]})

    write_csv_atomic(df, path)

    assert path.exists()
