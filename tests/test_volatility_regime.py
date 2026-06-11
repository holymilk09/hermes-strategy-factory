"""Tests for volatility regime labeler."""
import pandas as pd
import pytest

from src.research.regimes.volatility_regime import (
    VolatilityRegime,
    VolatilityRegimeConfig,
    assign_regime_from_percentile,
    compute_volatility_regimes,
    trailing_percentile_rank,
)


def test_assign_regime_from_percentile():
    config = VolatilityRegimeConfig()
    assert assign_regime_from_percentile(0.05, config) == VolatilityRegime.VOL_CRUSH
    assert assign_regime_from_percentile(0.20, config) == VolatilityRegime.LOW_VOL
    assert assign_regime_from_percentile(0.50, config) == VolatilityRegime.NORMAL_VOL
    assert assign_regime_from_percentile(0.80, config) == VolatilityRegime.HIGH_VOL
    assert assign_regime_from_percentile(0.95, config) == VolatilityRegime.PANIC_VOL


def test_trailing_percentile_rank_no_bfill():
    s = pd.Series([1, 2, 3, 4, 5], index=pd.date_range("2024-01-01", periods=5, freq="D"))
    pct = trailing_percentile_rank(s, lookback=3, min_periods=3)
    assert pd.isna(pct.iloc[0])
    assert pd.isna(pct.iloc[1])
    assert pct.iloc[2] == 1.0
    assert pct.iloc[3] == 1.0
    assert pct.iloc[4] == 1.0


def test_compute_volatility_regimes_schema():
    idx = pd.date_range("2024-01-01", periods=300, freq="D")
    df = pd.DataFrame({"open": range(300), "high": [x + 2 for x in range(300)], "low": [x - 2 for x in range(300)], "close": [x + 1 for x in range(300)]}, index=idx)
    config = VolatilityRegimeConfig(lookback=50, atr_window=5, min_periods=25)
    out = compute_volatility_regimes(df, config)
    assert "atr" in out.columns
    assert "vol_percentile" in out.columns
    assert "volatility_regime" in out.columns
    assert "regime_config_hash" in out.columns
    assert len(out) == len(df)


def test_compute_volatility_regimes_rejects_unsorted_index():
    idx = pd.to_datetime(["2024-01-02", "2024-01-01"])
    df = pd.DataFrame({"open": [1, 2], "high": [2, 3], "low": [0, 1], "close": [1, 2]}, index=idx)
    with pytest.raises(ValueError):
        compute_volatility_regimes(df)
