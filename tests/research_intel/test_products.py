"""Product-level tests: daily brief, weekly map, CLI. Synthetic data with planted events."""
from __future__ import annotations

import json
from datetime import date

import numpy as np

from src.research_intel import cli
from src.research_intel.brief import build_brief, render_brief_md
from src.research_intel.data import CacheStore, MemoryProvider
from src.research_intel.events import NOT_COVERED, EarningsEvent, EventCalendar
from src.research_intel.interest import Profile
from src.research_intel.relationships import ClusterMap
from src.research_intel.weekly import render_weekly_md, weekly_map
from tests.research_intel.conftest import series_from_returns

N = 180
FORBIDDEN = ("buy ", "sell ", "strong buy", "guaranteed", "you should", "price target")


def _world(calendar, rng, last=None):
    days = calendar[: N + 1]
    m = rng.normal(0.0005, 0.01, N)
    m[-1] = 0.0                       # flat market on the judged day
    a = 2.0 * m + rng.normal(0, 0.004, N)
    b = 2.0 * m + rng.normal(0, 0.004, N)
    a[-1] = b[-1] = 0.0               # names flat too -> nothing unusual
    h = rng.normal(0, 0.01, N)
    if last:
        a[-1] = last
    s = {"SPY": m, "QQQ": m, "AAA": a, "BBB": b, "HHH": h}
    prov = MemoryProvider([series_from_returns(k, days, v) for k, v in s.items()])
    cm = ClusterMap({"chips": {"etf": "SMH", "stocks": ["AAA", "BBB"]},
                     "health": {"etf": "XLV", "stocks": ["HHH", "NODATA"]},
                     "fin": {"etf": "XLF", "stocks": ["FFF", "GGG"]}})
    return prov, cm, days


PROFILE = Profile.from_dict({"holdings": [{"symbol": "AAA", "shares": 10}, {"symbol": "HHH", "shares": 5}],
                             "pins": ["FFF"]})


def test_quiet_day_says_nothing_unusual(calendar, rng):
    p, cm, days = _world(calendar, rng)
    b = build_brief(p, PROFILE, days[-1], clusters=cm)
    assert b["headline"][0].startswith("No flags across the watchlist")
    assert b["sent_to_broker"] is False and b["book"]["portfolio_beta"] is not None
    md = render_brief_md(b)
    assert "Not investment advice" in md
    body = md.replace(b["disclaimer"], "").lower()      # the disclaimer itself says "buy or sell"
    assert not any(f in body for f in FORBIDDEN)


def test_unexplained_move_with_covered_calendar(calendar, rng):
    p, cm, days = _world(calendar, rng, last=0.08)
    cal = EventCalendar([], days[-1], [(days[-30], days[-1])])
    b = build_brief(p, PROFILE, days[-1], cal, clusters=cm)
    assert b["headline"][0].startswith("AAA: abnormal move, no scheduled earnings")
    aaa = next(i for i in b["items"] if i["symbol"] == "AAA")
    assert "No scheduled earnings for AAA fall on this session" in aaa["notes"][0]


def test_earnings_reaction_is_named(calendar, rng):
    p, cm, days = _world(calendar, rng, last=0.08)
    ev = EarningsEvent("AAA", days[-2], "pm", True, True)
    cal = EventCalendar([ev], days[-1], [(days[-30], days[-1])])
    b = build_brief(p, PROFILE, days[-1], cal, clusters=cm)
    assert b["headline"][0].startswith("AAA: earnings reaction")


def test_uncovered_calendar_never_rules_out_earnings(calendar, rng):
    p, cm, days = _world(calendar, rng, last=0.08)
    b = build_brief(p, PROFILE, days[-1], clusters=cm)          # no calendar at all
    assert "earnings not checked" in b["headline"][0]
    assert EventCalendar.empty().reaction_to("AAA", days[-1], days[-2]) is NOT_COVERED


def test_removed_features_stay_removed(calendar, rng):
    """Gates 3b (peer lists) and 3d (peer-earnings read-through) failed OOS validation.
    These claims must not reappear in the brief or weekly map."""
    p, cm, days = _world(calendar, rng)
    future = date.fromordinal(days[-1].toordinal() + 3)
    cal = EventCalendar([EarningsEvent("BBB", future, "am", True, False)], days[-1], [(days[-1], future)])
    b = build_brief(p, PROFILE, days[-1], cal, clusters=cm)
    md = render_brief_md(b)
    assert "Moves most with" not in md and "Linked peer" not in md
    assert all("linked_peers" not in i and "peer_events" not in i for i in b["items"])
    assert "Linked:" not in render_weekly_md(weekly_map(p, PROFILE, days[-1], clusters=cm))


def test_earnings_follow_through_label(calendar, rng):
    p, cm, days = _world(calendar, rng, last=0.08)
    ev = EarningsEvent("AAA", days[-3], "pm", True, True)     # reaction was days[-2]
    cal = EventCalendar([ev], days[-1], [(days[-30], days[-1])])
    b = build_brief(p, PROFILE, days[-1], cal, clusters=cm)
    assert b["headline"][0].startswith("AAA: earnings follow-through")


def test_low_fit_caveat(calendar, rng):
    p, cm, days = _world(calendar, rng)
    hhh = next(i for i in build_brief(p, PROFILE, days[-1], clusters=cm)["items"] if i["symbol"] == "HHH")
    assert any("weak yardstick" in g for g in hhh["notes"])   # HHH is pure noise vs the market


def test_weekly_map_and_changes(calendar, rng):
    p, cm, days = _world(calendar, rng)
    w1 = weekly_map(p, PROFILE, days[-6], clusters=cm)
    assert w1["changes"] is None
    w1["names"]["AAA"]["betas"]["QQQ_60"] = 0.5               # pretend beta was very different
    w1["names"]["ZZZ"] = {"cluster": None, "betas": {}}
    w2 = weekly_map(p, PROFILE, days[-1], w1, clusters=cm)
    ch = " ".join(w2["changes"])
    assert "AAA beta to QQQ (60d) moved 0.50" in ch
    assert "ZZZ dropped off" in ch
    md = render_weekly_md(w2)
    assert "## What changed" in md and "not investment advice" in md.lower()
    json.dumps(w2)


def test_cli_end_to_end(tmp_path, calendar, rng):
    p, cm, days = _world(calendar, rng)
    store = CacheStore(tmp_path / "cache")
    for s in p.symbols():
        store.write(p.series(s))
    prof = tmp_path / "profile.json"
    prof.write_text(json.dumps({"holdings": [{"symbol": "AAA", "shares": 1}]}))
    cal = tmp_path / "cal.json"
    cal.write_text(json.dumps({"data": {"results": []}}))
    out = tmp_path / "out"
    span = f"{cal}:{days[-20].isoformat()}:{days[-1].isoformat()}"
    assert cli.main(["brief", "--cache", str(store.root), "--profile", str(prof),
                     "--events", span, "--out", str(out)]) == 0
    b = json.loads((out / f"brief_{days[-1].isoformat()}.json").read_text())
    assert b["as_of"] == days[-1].isoformat()
    assert {r["status"] for r in b["record"]} == {"NOT_LOADED"}
    assert cli.main(["weekly", "--cache", str(store.root), "--profile", str(prof), "--out", str(out)]) == 0
    assert cli.main(["alerts", "--cache", str(store.root), "--profile", str(prof)]) == 0
    assert cli.main(["record", "--cache", str(store.root)]) == 0
