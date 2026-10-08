from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from src.research_intel.data import INSUFFICIENT_DATA, MemoryProvider
from src.research_intel.events import EventCalendar
from src.research_intel.moves import ALERT, NORMAL, move_alerts, move_context
from tests.research_intel.conftest import series_from_returns

N = 120


def _prov(calendar, rng, last_qqq, last_aaa, beta_=2.0, noise=0.004, listed=None):
    days = calendar[: N + 1]
    m = rng.normal(0.0005, 0.01, N)
    m[-1] = last_qqq
    a = beta_ * m + rng.normal(0, noise, N)
    a[-1] = last_aaa
    spy = rng.normal(0.0003, 0.002, N)  # deliberately a poor fit for AAA
    aaa_days, aaa_rets = days, a
    if listed:
        aaa_days, aaa_rets = days[-listed:], a[-(listed - 1):]
    return MemoryProvider([series_from_returns("QQQ", days, m), series_from_returns("SPY", days, spy),
                           series_from_returns("AAA", aaa_days, aaa_rets)]), days


def test_market_explained_big_move_is_not_an_alert(calendar, rng):
    p, days = _prov(calendar, rng, last_qqq=-0.03, last_aaa=-0.06)   # -6% on a -3% day, beta 2
    mc = move_context(p, "AAA", days[-1])
    assert mc.benchmark == "QQQ"                                    # better fit chosen
    assert mc.beta == pytest.approx(2.0, abs=0.15)
    assert mc.move_pp == pytest.approx(-6.0)
    assert mc.status == NORMAL, mc.reason


def test_unexplained_move_alerts(calendar, rng):
    p, days = _prov(calendar, rng, last_qqq=0.0, last_aaa=0.04)       # +4% on a flat day
    mc = move_context(p, "AAA", days[-1])
    assert mc.status == ALERT
    assert mc.residual_z > 2.5
    assert move_alerts(p, ["AAA", "QQQ"], days[-1])[0].symbol == "AAA"


def test_baseline_excludes_the_judged_day(calendar, rng):
    p1, days = _prov(calendar, np.random.default_rng(7), 0.0, 0.0)
    p2, _ = _prov(calendar, np.random.default_rng(7), 0.0, 0.50)      # absurd last-day move
    a, b = move_context(p1, "AAA", days[-1]), move_context(p2, "AAA", days[-1])
    assert a.beta == pytest.approx(b.beta, abs=1e-12)                  # yardstick unchanged
    assert a.baseline_n == 60


def test_short_history_move(calendar, rng):
    p, days = _prov(calendar, rng, 0.0, 0.001, listed=50)
    mc = move_context(p, "AAA", days[-1])
    assert mc.sample == "SHORT_HISTORY" and mc.baseline_n == 48
    p2, _ = _prov(calendar, rng, 0.0, 0.001, listed=20)
    assert move_context(p2, "AAA", days[-1]).status == INSUFFICIENT_DATA


CAL = {"data": {"results": [
    {"symbol": "TSM", "eps": {"actual": None}, "report": {"date": "2026-10-15", "timing": "am", "verified": True}},
    {"symbol": "ON", "eps": {"actual": None}, "report": {"date": "2026-11-02", "timing": "am", "verified": False}},
    {"symbol": "SVNDY", "eps": {"actual": "0.175"}, "report": {"date": "2026-10-08", "timing": "am", "verified": True}},
    {"symbol": "LATE", "eps": {"actual": None}, "report": {"date": "2026-12-30", "timing": "pm", "verified": True}},
]}}


def test_events_upcoming_and_labels():
    cal = EventCalendar.from_robinhood(CAL, date(2026, 10, 8))
    up = cal.upcoming(["TSM", "ON", "SVNDY", "LATE"], date(2026, 10, 8), days=31)
    assert [e.symbol for e in up] == ["TSM", "ON"]          # reported + out-of-window dropped
    assert up[0].label() == "Thu Oct 15 (before the open)"
    assert "tentative" in up[1].label()
    assert cal.upcoming(["TSM"], date(2026, 10, 16)) == []   # already past
