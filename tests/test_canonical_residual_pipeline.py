from pathlib import Path

import numpy as np
import pandas as pd

from src.research.canonical.canonical_residual_pipeline import (
    CanonicalResidualRule,
    apply_canonical_residual_rule,
    assign_strategy,
    build_canonical_candidate_ledger,
    build_selected_trade_ledger,
    load_canonical_symbol_npz,
    summarize_candidate_ledger,
)


def make_npz(path: Path, symbol_rows: int = 10) -> None:
    ts = pd.date_range("2026-05-01", periods=symbol_rows, freq="D", tz="UTC")

    np.savez_compressed(
        path,
        timestamp=ts.astype("int64").to_numpy(),
        residual_z=np.array([-2.5, -1.0] * (symbol_rows // 2)),
        residual_r2=np.array([0.30, 0.30] * (symbol_rows // 2)),
        rsi_2=np.array([20, 50] * (symbol_rows // 2)),
        regime_score=np.array([0.5, 1.5] * (symbol_rows // 2)),
        forward_return_5d=np.array([0.02, -0.01] * (symbol_rows // 2)),
        forward_return_10d=np.array([0.03, -0.02] * (symbol_rows // 2)),
        forward_return_20d=np.array([0.04, -0.03] * (symbol_rows // 2)),
    )


def test_load_canonical_symbol_npz(tmp_path: Path):
    path = tmp_path / "AAPL.npz"
    make_npz(path)

    df = load_canonical_symbol_npz(path)

    assert len(df) == 10
    assert set(["timestamp", "symbol", "residual_z", "residual_r2"]).issubset(df.columns)
    assert df["symbol"].iloc[0] == "AAPL"


def test_apply_canonical_rule():
    df = pd.DataFrame(
        {
            "residual_z": [-2.5, -1.5, -3.0],
            "residual_r2": [0.3, 0.3, 0.1],
        }
    )

    selected = apply_canonical_residual_rule(df, CanonicalResidualRule())

    assert selected.tolist() == [True, False, False]


def test_assign_strategy():
    df = pd.DataFrame(
        {
            "rsi_2": [20, 40],
            "regime_score": [0.5, 0.5],
        }
    )

    strategy = assign_strategy(df)

    assert strategy.tolist() == ["mean_reversion", "structural_mr"]


def test_build_canonical_candidate_ledger(tmp_path: Path):
    make_npz(tmp_path / "AAPL.npz")
    make_npz(tmp_path / "MSFT.npz")

    ledger = build_canonical_candidate_ledger(tmp_path)

    assert len(ledger) == 20
    assert int(ledger["selected"].sum()) == 10
    assert "candidate_id" in ledger.columns
    assert "lineage" in ledger.columns


def test_build_selected_trade_ledger(tmp_path: Path):
    make_npz(tmp_path / "AAPL.npz")

    ledger = build_canonical_candidate_ledger(tmp_path)
    trades = build_selected_trade_ledger(ledger)

    assert len(trades) == int(ledger["selected"].sum())
    assert "realized_return" in trades.columns


def test_summarize_candidate_ledger(tmp_path: Path):
    make_npz(tmp_path / "AAPL.npz")

    ledger = build_canonical_candidate_ledger(tmp_path)
    summary = summarize_candidate_ledger(ledger)

    assert summary["candidate_rows"] == 10
    assert summary["selected_rows"] == 5
    assert summary["rejected_rows"] == 5
