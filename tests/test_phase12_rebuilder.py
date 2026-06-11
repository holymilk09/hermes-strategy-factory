from pathlib import Path
import numpy as np
import pandas as pd

from src.features.phase12_parity import (
    aggregate_parity_results,
    classify_parity,
    compare_npz_features,
)
from src.features.phase12_rebuilder import (
    Phase12FeatureConfig,
    build_symbol_features,
    compute_rsi,
    rolling_beta_residual,
    save_symbol_npz,
)


def test_compute_rsi():
    close = pd.Series([10, 9, 8, 9, 10, 11], dtype=float)
    rsi = compute_rsi(close, window=2)
    assert len(rsi) == len(close)
    assert rsi.notna().all()


def test_rolling_beta_residual():
    y = pd.Series([0.01, 0.02, -0.01, 0.03, 0.01, -0.02, 0.01] * 20)
    x = pd.Series([0.005, 0.01, -0.005, 0.02, 0.0, -0.01, 0.005] * 20)
    z, r2 = rolling_beta_residual(y, x, lookback=20)
    assert len(z) == len(y)
    assert len(r2) == len(y)


def test_build_symbol_features():
    idx = pd.date_range("2024-01-01", periods=200, freq="D", tz="UTC")
    sym = pd.DataFrame({"timestamp": idx, "open": np.linspace(100, 120, len(idx)), "high": np.linspace(101, 121, len(idx)), "low": np.linspace(99, 119, len(idx)), "close": np.linspace(100, 120, len(idx))})
    mkt = pd.DataFrame({"timestamp": idx, "open": np.linspace(400, 430, len(idx)), "high": np.linspace(401, 431, len(idx)), "low": np.linspace(399, 429, len(idx)), "close": np.linspace(400, 430, len(idx))})
    features = build_symbol_features(sym, mkt, Phase12FeatureConfig(start_date="2024-01-01", residual_lookback=20))
    assert "residual_z" in features.columns
    assert "residual_r2" in features.columns
    assert "rsi_2" in features.columns
    assert "regime_score" in features.columns


def test_save_and_compare_npz(tmp_path: Path):
    old_path = tmp_path / "old.npz"
    new_path = tmp_path / "new.npz"
    arr = np.linspace(0, 1, 100)
    np.savez(old_path, residual_z=arr, residual_r2=arr, rsi_2=arr, regime_score=arr, forward_return_5d=arr, forward_return_10d=arr, forward_return_20d=arr)
    np.savez(new_path, residual_z=arr, residual_r2=arr, rsi_2=arr, regime_score=arr, forward_return_5d=arr, forward_return_10d=arr, forward_return_20d=arr)
    comp = compare_npz_features(old_path, new_path)
    assert classify_parity(comp) == "PARITY_DIRECTIONAL_PASS"


def test_aggregate_parity_results():
    base = {"rows": [{"key": "residual_z", "status": "OK", "corr": 0.9}, {"key": "residual_r2", "status": "OK", "corr": 0.8}, {"key": "rsi_2", "status": "OK", "corr": 0.95}]}
    rows = [base, base, base, base]
    result = aggregate_parity_results(rows)
    assert result["final"] == "PARITY_PASS"
