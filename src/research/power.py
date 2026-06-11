"""Statistical power classification for filter tests."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PowerClass(str, Enum):
    NO_POWER = "NO_POWER"
    LOW_POWER = "LOW_POWER"
    ENOUGH_POWER = "ENOUGH_POWER"


@dataclass(frozen=True)
class PowerThresholds:
    min_total_trades: int = 100
    min_blocked_trades: int = 30
    min_surviving_trades: int = 30
    min_regime_trades: int = 25


@dataclass(frozen=True)
class PowerResult:
    classification: PowerClass
    reason: str


def classify_filter_power(total_trades: int, blocked_trades: int, surviving_trades: int, thresholds: PowerThresholds | None = None) -> PowerResult:
    thresholds = thresholds or PowerThresholds()
    if total_trades < thresholds.min_total_trades:
        return PowerResult(PowerClass.NO_POWER, f"total_trades={total_trades} < {thresholds.min_total_trades}")
    if blocked_trades < thresholds.min_blocked_trades:
        return PowerResult(PowerClass.NO_POWER, f"blocked_trades={blocked_trades} < {thresholds.min_blocked_trades}")
    if surviving_trades < thresholds.min_surviving_trades:
        return PowerResult(PowerClass.NO_POWER, f"surviving_trades={surviving_trades} < {thresholds.min_surviving_trades}")
    if blocked_trades < thresholds.min_blocked_trades * 2 or surviving_trades < thresholds.min_surviving_trades * 2:
        return PowerResult(PowerClass.LOW_POWER, "enough to inspect, weak for broad inference")
    return PowerResult(PowerClass.ENOUGH_POWER, "sufficient blocked and surviving samples")
