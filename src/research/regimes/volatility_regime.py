"""Volatility regime labeler — PIT-safe trailing percentile based on ATR."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Iterable

import numpy as np
import pandas as pd


class VolatilityRegime(str, Enum):
    VOL_CRUSH = "VOL_CRUSH"
    LOW_VOL = "LOW_VOL"
    NORMAL_VOL = "NORMAL_VOL"
    HIGH_VOL = "HIGH_VOL"
    PANIC_VOL = "PANIC_VOL"
    NO_DATA = "NO_DATA"


@dataclass(frozen=True)
class VolatilityRegimeConfig:
    lookback: int = 252
    atr_window: int = 14
    min_periods: int = 126

    vol_crush_pct: float = 0.10
    low_vol_pct: float = 0.30
    high_vol_pct: float = 0.70
    panic_vol_pct: float = 0.90

    def validate(self) -> None:
        if self.lookback <= 20:
            raise ValueError("lookback must be > 20")
        if self.atr_window <= 1:
            raise ValueError("atr_window must be > 1")
        if self.min_periods <= 20:
            raise ValueError("min_periods must be > 20")
        if self.min_periods > self.lookback:
            raise ValueError("min_periods cannot exceed lookback")
        levels = [self.vol_crush_pct, self.low_vol_pct, self.high_vol_pct, self.panic_vol_pct]
        if not all(0.0 < x < 1.0 for x in levels):
            raise ValueError("percentile thresholds must be between 0 and 1")
        if not (self.vol_crush_pct < self.low_vol_pct < self.high_vol_pct < self.panic_vol_pct):
            raise ValueError("percentile thresholds must be strictly increasing")

    @property
    def config_hash(self) -> str:
        raw = repr(self).encode("utf-8")
        return sha256(raw).hexdigest()[:16]


REQUIRED_OHLC = ("open", "high", "low", "close")


def validate_ohlc(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_OHLC if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLC columns: {missing}")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("Input DataFrame must use DatetimeIndex")
    if not df.index.is_monotonic_increasing:
        raise ValueError("Input index must be monotonic increasing")
    if df.index.has_duplicates:
        raise ValueError("Input index has duplicate timestamps")


def true_range(df: pd.DataFrame) -> pd.Series:
    validate_ohlc(df)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.rename("true_range")


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    tr = true_range(df)
    return tr.rolling(window=window, min_periods=window).mean().rename("atr")


def trailing_percentile_rank(series: pd.Series, lookback: int, min_periods: int) -> pd.Series:
    """PIT-safe trailing percentile rank. Current value included in trailing window."""
    def pct_rank(window_values: np.ndarray) -> float:
        clean = window_values[~np.isnan(window_values)]
        if clean.size < min_periods:
            return np.nan
        current = clean[-1]
        return float(np.mean(clean <= current))
    return series.rolling(window=lookback, min_periods=min_periods).apply(pct_rank, raw=True).rename("vol_percentile")


def assign_regime_from_percentile(pct: float, config: VolatilityRegimeConfig) -> VolatilityRegime:
    if pd.isna(pct):
        return VolatilityRegime.NO_DATA
    if pct <= config.vol_crush_pct:
        return VolatilityRegime.VOL_CRUSH
    if pct <= config.low_vol_pct:
        return VolatilityRegime.LOW_VOL
    if pct < config.high_vol_pct:
        return VolatilityRegime.NORMAL_VOL
    if pct < config.panic_vol_pct:
        return VolatilityRegime.HIGH_VOL
    return VolatilityRegime.PANIC_VOL


def compute_volatility_regimes(ohlc: pd.DataFrame, config: VolatilityRegimeConfig | None = None) -> pd.DataFrame:
    """Returns PIT-safe volatility regime labels."""
    config = config or VolatilityRegimeConfig()
    config.validate()
    validate_ohlc(ohlc)
    out = pd.DataFrame(index=ohlc.index.copy())
    out["atr"] = atr(ohlc, window=config.atr_window)
    out["vol_percentile"] = trailing_percentile_rank(out["atr"], lookback=config.lookback, min_periods=config.min_periods)
    out["volatility_regime"] = [assign_regime_from_percentile(x, config).value for x in out["vol_percentile"].to_numpy()]
    out["regime_config_hash"] = config.config_hash
    return out


def regime_definition_hash(config: VolatilityRegimeConfig, source: str = "ATR_TRAILING_PERCENTILE") -> str:
    payload = f"{source}|{repr(config)}".encode("utf-8")
    return sha256(payload).hexdigest()[:16]
