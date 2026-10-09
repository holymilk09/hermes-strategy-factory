"""Regression tests for the independent review of 2026-10-09 (each reproduces a confirmed finding)."""
from __future__ import annotations

import csv
from datetime import date, timedelta

import numpy as np

from src.research_intel.brief import build_brief, render_brief_md, render_record_line
from src.research_intel.data import CacheStore, MemoryProvider, Series
from src.research_intel.events import EarningsEvent, EventCalendar
from src.research_intel.interest import Profile
from src.research_intel.moves import move_context
from src.research_intel.relationships import ClusterMap
from src.research_intel.research_record import HYPOTHESIS_V1, summarize
from src.research_intel.weekly import weekly_map
from tests.research_intel.conftest import series_from_returns

N = 150


def _prov(calendar, rng, extra=()):
    days = calendar[: N + 1]
    m = rng.normal(0.0005, 0.01, N)
    s = [series_from_returns("SPY", days, m), series_from_returns("QQQ", days, m),
         series_from_returns("AAA", days, 1.5 * m + rng.normal(0, 0.004, N)),
         series_from_returns("BBB", days, 1.5 * m + rng.normal(0, 0.004, N))]
    return MemoryProvider(list(s) + list(extra)), days


def test_headline_does_not_claim_nothing_unusual_when_nothing_was_judged(calendar, rng):
    p, days = _prov(calendar, rng)
    prof = Profile.from_dict({"pins": ["AAA"]})
    saturday = next(d for d in (days[-1] + timedelta(days=i) for i in range(1, 8)) if d.weekday() == 5)
    h = build_brief(p, prof, saturday)["headline"][0]
    assert not h.startswith("No flags across") and "could be judged" in h
    assert "empty" in build_brief(p, Profile(), days[-1])["headline"][0]


def test_upcoming_has_no_reverse_lookahead():
    ev = EarningsEvent("MU", date(2026, 9, 30), "pm", True, True)        # reported by fetch time
    cal = EventCalendar([ev], date(2026, 10, 8), [(date(2026, 9, 1), date(2026, 10, 8))])
    assert [e.symbol for e in cal.upcoming(["MU"], date(2026, 9, 25))] == ["MU"]   # replay sees it
    live = EventCalendar([ev], date(2026, 10, 1), [(date(2026, 9, 1), date(2026, 10, 8))])
    assert live.upcoming(["MU"], date(2026, 10, 1)) == []                # live: already past


def test_weekly_has_no_link_unlink_changes(calendar, rng):
    p, days = _prov(calendar, rng)
    cm = ClusterMap({"x": {"stocks": ["AAA", "BBB"]}})
    prof = Profile.from_dict({"pins": ["AAA"]})
    w1 = weekly_map(p, prof, days[-6], clusters=cm)
    for k in w1["pairs"]:
        w1["pairs"][k]["status"] = "NOT_LINKED"
    w2 = weekly_map(p, prof, days[-1], w1, clusters=cm)
    assert not any("not_linked ->" in c for c in w2["changes"])


def test_record_line_with_no_resolved_rows(tmp_path):
    f = tmp_path / "h.csv"
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["signal_date", "outcome_status", "outcome_return_pp"])
        w.writeheader()
        w.writerows([{"signal_date": "2026-10-09", "outcome_status": "PENDING", "outcome_return_pp": ""}] * 2)
    line = render_record_line(summarize(f, HYPOTHESIS_V1).to_dict())
    assert "No results yet" in line


def test_zero_variance_baseline_is_not_called_normal(calendar, rng):
    days = calendar[: N + 1]
    flat = Series("ZZZ", tuple(days), tuple([10.0] * N + [14.0]), "t")
    p, _ = _prov(calendar, rng, extra=[flat])
    m = move_context(p, "ZZZ", days[-1])
    assert m.status == "INSUFFICIENT_DATA" and "zero-variance" in m.reason


def test_corrupt_symbol_file_does_not_kill_brief(tmp_path, calendar, rng):
    p, days = _prov(calendar, rng)
    st = CacheStore(tmp_path)
    for s in p.symbols():
        st.write(p.series(s))
    with open(st.path("AAA"), "a") as fh:
        fh.write(f"{days[-1].isoformat()},999.0,t\n")                 # conflicting duplicate
    b = build_brief(st, Profile.from_dict({"pins": ["AAA", "BBB"]}), days[-1])
    items = {i["symbol"]: i for i in b["items"]}
    assert items["AAA"]["move"]["status"] == "INSUFFICIENT_DATA"
    assert items["BBB"]["move"]["status"] != "INSUFFICIENT_DATA"
    render_brief_md(b)
