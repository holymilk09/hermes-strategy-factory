"""Shared loaders for the validation phases (gitignored data, committed code)."""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import date, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.research_intel.data import CacheStore  # noqa: E402
from src.research_intel.events import EarningsEvent, EventCalendar  # noqa: E402

CACHE = ROOT / "cache/research_intel/ohlcv_v2"
HIST = ROOT / "cache/research_intel/events/hist"
OUT = ROOT / "cache/research_intel/validation"
OOS_START = date(2025, 7, 1)
SETTLED = date(2026, 10, 7)
UNIVERSE_STOCKS = ["MU", "NVDA", "AMD", "AVGO", "TSM", "ASML", "MRVL", "QCOM", "ON", "ARM", "SKHY",
                   "AAPL", "MSFT", "GOOGL", "META", "AMZN", "JPM", "GS", "MS", "BAC",
                   "LLY", "UNH", "JNJ", "ABBV", "MRK", "CAT", "GE", "HON"]
FETCHED = date(2026, 10, 8)


def store() -> CacheStore:
    return CacheStore(CACHE)


def calendar() -> EventCalendar:
    """All saved windows + manually transcribed inline windows, with exact coverage."""
    wmap = json.loads((HIST / "window_map.json").read_text())
    cal = EventCalendar.empty()
    for start, fid in wmap.items():
        s = date.fromisoformat(start)
        c = EventCalendar.load(HIST / f"cal_{fid}" if str(fid).endswith(".json") else HIST / f"cal_{fid}.json", FETCHED, s, s + timedelta(days=30))
        cal = cal.merged(c)
    manual = json.loads((HIST / "inline_windows_manual.json").read_text())["windows"]
    for start, evs in manual.items():
        s = date.fromisoformat(start)
        ev = [EarningsEvent(sym, date.fromisoformat(d), t, True, date.fromisoformat(d) <= SETTLED)
              for sym, d, t in evs]
        cal = cal.merged(EventCalendar(ev, FETCHED, [(s, s + timedelta(days=30))]))
    return cal
