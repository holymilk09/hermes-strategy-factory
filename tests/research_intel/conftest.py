from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.research_intel.data import Series  # noqa: E402


def business_days(start: date, n: int) -> list[date]:
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def series_from_returns(symbol: str, dates: list[date], rets, start_price: float = 100.0) -> Series:
    """dates has len(rets)+1 entries; first close is start_price."""
    closes = [start_price]
    for r in rets:
        closes.append(closes[-1] * (1.0 + float(r)))
    return Series(symbol, tuple(dates), tuple(closes), "synthetic")


@pytest.fixture
def calendar():
    return business_days(date(2026, 1, 5), 260)


@pytest.fixture
def rng():
    return np.random.default_rng(20261008)
