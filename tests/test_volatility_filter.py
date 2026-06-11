"""Tests for volatility filters."""
import pandas as pd
from src.research.filters.volatility_filter import VolatilityFilterName, build_volatility_filter


def test_block_high_vol():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    regimes = pd.Series(["LOW_VOL", "NORMAL_VOL", "HIGH_VOL", "PANIC_VOL", "NO_DATA"], index=idx)
    result = build_volatility_filter(regimes, VolatilityFilterName.BLOCK_HIGH_VOL)
    assert result.eligible.tolist() == [True, True, False, False, False]
    assert result.scale.tolist() == [1.0, 1.0, 1.0, 1.0, 1.0]


def test_block_panic_vol():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    regimes = pd.Series(["LOW_VOL", "NORMAL_VOL", "HIGH_VOL", "PANIC_VOL", "NO_DATA"], index=idx)
    result = build_volatility_filter(regimes, VolatilityFilterName.BLOCK_PANIC_VOL)
    assert result.eligible.tolist() == [True, True, True, False, False]


def test_only_normal_vol():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    regimes = pd.Series(["LOW_VOL", "NORMAL_VOL", "HIGH_VOL", "PANIC_VOL", "NO_DATA"], index=idx)
    result = build_volatility_filter(regimes, VolatilityFilterName.ONLY_NORMAL_VOL)
    assert result.eligible.tolist() == [False, True, False, False, False]


def test_adaptive_position_scale():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    regimes = pd.Series(["VOL_CRUSH", "NORMAL_VOL", "HIGH_VOL", "PANIC_VOL", "NO_DATA"], index=idx)
    result = build_volatility_filter(regimes, VolatilityFilterName.ADAPTIVE_POSITION_SCALE)
    assert result.eligible.tolist() == [True, True, True, True, False]
    assert result.scale.tolist() == [0.75, 1.0, 0.5, 0.25, 1.0]
