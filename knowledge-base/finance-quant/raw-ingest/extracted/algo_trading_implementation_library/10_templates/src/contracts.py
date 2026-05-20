from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class Signal:
    run_id: str
    strategy_id: str
    symbol: str
    timestamp: datetime
    direction: Literal["long", "short", "flat"]
    score: float
    confidence: float
    horizon: str
    reason_codes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Target:
    run_id: str
    strategy_id: str
    symbol: str
    timestamp: datetime
    target_quantity: float
    target_weight: float | None
    reason: str


@dataclass(frozen=True)
class OrderInstruction:
    client_order_id: str
    symbol: str
    side: Literal["buy", "sell"]
    quantity: float
    order_type: Literal["market", "limit", "stop", "stop_limit", "trailing_stop"]
    time_in_force: str
    limit_price: float | None = None
    risk_approval_id: str | None = None
