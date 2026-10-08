from __future__ import annotations

from datetime import date

import pytest

from src.research_intel.data import MemoryProvider
from src.research_intel.interest import Profile, mention_score, ranked_watchlist, Mention
from src.research_intel.portfolio import book_context
from src.research_intel.relationships import ClusterMap
from tests.research_intel.conftest import series_from_returns

AS_OF = date(2026, 10, 7)


def _profile(**kw):
    base = {
        "holdings": [{"symbol": "SKHY", "shares": 10}],
        "tickers": [{"symbol": "MU", "weight": 1.0, "last_mentioned": "2026-09-23"},
                    {"symbol": "NVDA", "weight": 0.5, "last_mentioned": "2026-10-07"}],
        "sectors": [{"sector": "semiconductors", "weight": 0.8}],
        "pins": ["LLY"],
    }
    base.update(kw)
    return Profile.from_dict(base)


def test_mention_half_life_is_exact():
    m = Mention("MU", 1.0, date(2026, 9, 23))
    assert mention_score(m, AS_OF, 14) == pytest.approx(0.5)
    assert mention_score(m, date(2026, 9, 1), 14) == 0.0  # future mention doesn't exist yet


def test_ranking_and_reasons():
    cm = ClusterMap.from_yaml()
    wl = ranked_watchlist(_profile(), AS_OF, cm)
    by = {i.symbol: i for i in wl}
    assert [i.symbol for i in wl][0] == "SKHY"           # holding outranks everything
    assert by["SKHY"].held and by["SKHY"].reasons == ("HOLDING",)
    assert by["LLY"].reasons == ("PINNED",)
    assert by["MU"].score == pytest.approx(0.5 + 0.8 * 0.25)
    assert "SECTOR_INTEREST semiconductors" in by["MU"].why_shown
    assert by["NVDA"].score == pytest.approx(0.5 + 0.2)
    assert "AMD" not in by                                # sector interest never adds names


def test_old_mentions_fall_off():
    p = _profile(tickers=[{"symbol": "MU", "weight": 1.0, "last_mentioned": "2026-06-01"}])
    assert "MU" not in {i.symbol for i in ranked_watchlist(p, AS_OF)}


def test_profile_validation():
    with pytest.raises(ValueError):
        Profile.from_dict({"tickers": [{"symbol": "MU", "weight": 3, "last_mentioned": "2026-10-01"}]})
    with pytest.raises(ValueError):
        Profile.from_dict({"holdings": [{"symbol": "MU", "shares": -1}]})


def _book_provider(calendar, rng):
    days = calendar[:101]
    m = rng.normal(0.0005, 0.01, 100)
    return MemoryProvider([
        series_from_returns("QQQ", days, m),
        series_from_returns("SPY", days, m),
        series_from_returns("AAA", days, 2.0 * m, start_price=50.0),
        series_from_returns("BBB", days, 0.5 * m, start_price=100.0),
    ]), days


def test_book_weights_and_portfolio_beta(calendar, rng):
    p, days = _book_provider(calendar, rng)
    cm = ClusterMap({"x": {"stocks": ["AAA"]}})
    prof = Profile.from_dict({"holdings": [{"symbol": "AAA", "shares": 10}, {"symbol": "BBB", "shares": 5}]})
    b = book_context(p, cm, prof, days[-1])
    pos = {x.symbol: x for x in b.positions}
    va, vb = 10 * pos["AAA"].price, 5 * pos["BBB"].price
    assert b.total_value == pytest.approx(va + vb)
    assert pos["AAA"].weight == pytest.approx(va / (va + vb))
    assert pos["AAA"].beta == pytest.approx(2.0, abs=1e-9)
    expected = pos["AAA"].weight * 2.0 + pos["BBB"].weight * 0.5
    assert b.portfolio_beta == pytest.approx(expected, abs=1e-9)
    assert b.beta_coverage == pytest.approx(1.0)
    assert b.cluster_weights["x"] == pytest.approx(pos["AAA"].weight)
    assert b.cluster_weights["unclustered"] == pytest.approx(pos["BBB"].weight)


def test_book_reports_unpriced_and_refuses_mixed(calendar, rng):
    p, days = _book_provider(calendar, rng)
    cm = ClusterMap({})
    prof = Profile.from_dict({"holdings": [{"symbol": "AAA", "shares": 1}, {"symbol": "ZZZ", "shares": 1}]})
    b = book_context(p, cm, prof, days[-1])
    assert b.unpriced == ("ZZZ",) and "ZZZ" in b.no_beta
    assert any("unpriced" in c for c in b.caveats)
    with pytest.raises(ValueError, match="mixed"):
        book_context(p, cm, Profile.from_dict({"holdings": [{"symbol": "AAA", "shares": 1},
                                                             {"symbol": "BBB", "weight": 0.5}]}), days[-1])


def test_book_stated_weights(calendar, rng):
    p, days = _book_provider(calendar, rng)
    prof = Profile.from_dict({"holdings": [{"symbol": "AAA", "weight": 0.3}, {"symbol": "BBB", "weight": 0.1}]})
    b = book_context(p, ClusterMap({}), prof, days[-1])
    assert b.basis == "stated_weights"
    assert {x.symbol: x.weight for x in b.positions}["AAA"] == pytest.approx(0.75)
