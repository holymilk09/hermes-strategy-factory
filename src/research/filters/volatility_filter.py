"""Deterministic volatility filters — baseline, block high/panic, only normal, adaptive scale."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import pandas as pd

from src.research.regimes.volatility_regime import VolatilityRegime


class VolatilityFilterName(str, Enum):
    BASELINE = "BASELINE"
    BLOCK_HIGH_VOL = "BLOCK_HIGH_VOL"
    BLOCK_PANIC_VOL = "BLOCK_PANIC_VOL"
    ONLY_NORMAL_VOL = "ONLY_NORMAL_VOL"
    ONLY_HIGH_VOL = "ONLY_HIGH_VOL"
    ADAPTIVE_POSITION_SCALE = "ADAPTIVE_POSITION_SCALE"


@dataclass(frozen=True)
class FilterResult:
    name: str
    eligible: pd.Series
    scale: pd.Series


def build_volatility_filter(regimes: pd.Series, filter_name: VolatilityFilterName) -> FilterResult:
    """Deterministic volatility filter. eligible = trade permission mask. scale = position multiplier."""
    if regimes.empty:
        raise ValueError("regimes cannot be empty")
    r = regimes.astype(str)
    eligible = pd.Series(True, index=r.index)
    scale = pd.Series(1.0, index=r.index)

    if filter_name == VolatilityFilterName.BASELINE:
        pass
    elif filter_name == VolatilityFilterName.BLOCK_HIGH_VOL:
        eligible = ~r.isin([VolatilityRegime.HIGH_VOL.value, VolatilityRegime.PANIC_VOL.value, VolatilityRegime.NO_DATA.value])
    elif filter_name == VolatilityFilterName.BLOCK_PANIC_VOL:
        eligible = ~r.isin([VolatilityRegime.PANIC_VOL.value, VolatilityRegime.NO_DATA.value])
    elif filter_name == VolatilityFilterName.ONLY_NORMAL_VOL:
        eligible = r.eq(VolatilityRegime.NORMAL_VOL.value)
    elif filter_name == VolatilityFilterName.ONLY_HIGH_VOL:
        eligible = r.eq(VolatilityRegime.HIGH_VOL.value)
    elif filter_name == VolatilityFilterName.ADAPTIVE_POSITION_SCALE:
        eligible = ~r.eq(VolatilityRegime.NO_DATA.value)
        scale.loc[r.eq(VolatilityRegime.HIGH_VOL.value)] = 0.50
        scale.loc[r.eq(VolatilityRegime.PANIC_VOL.value)] = 0.25
        scale.loc[r.eq(VolatilityRegime.VOL_CRUSH.value)] = 0.75
    else:
        raise ValueError(f"Unknown filter: {filter_name}")

    return FilterResult(name=filter_name.value, eligible=eligible.astype(bool), scale=scale.astype(float))
