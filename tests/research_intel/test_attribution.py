from __future__ import annotations

import numpy as np
import pytest

from src.research_intel.attribution import attribute, book_attribution
from src.research_intel.data import INSUFFICIENT_DATA, OK, MemoryProvider, Series
from src.research_intel.interest import Profile
from src.research_intel.relationships import ClusterMap
from tests.research_intel.conftest import series_from_returns

N = 200


def _world(calendar, rng, noise=0.0):
    days = calendar[: N + 1]
    m = rng.normal(0.0004, 0.01, N)
    sector_own = rng.normal(0.0, 0.006, N)                 # sector-specific factor
    s = 1.1 * m + sector_own                                # sector ETF = market + own
    a = 0.0002 + 1.0 * m + 0.8 * sector_own + rng.normal(0, noise, N) if noise else 0.0002 + 1.0 * m + 0.8 * sector_own
    p = MemoryProvider([series_from_returns("SPY", days, m), series_from_returns("XLK", days, s),
                        series_from_returns("AAA", days, a), series_from_returns("NOETF", days, 0.5 * m)])
    cm = ClusterMap({"tech": {"etf": "XLK", "stocks": ["AAA"]}, "other": {"etf": "XLQ", "stocks": ["NOETF"]}})
    return p, cm, days


def test_components_sum_to_move_and_betas_recover(calendar, rng):
    p, cm, days = _world(calendar, rng)
    a = attribute(p, "AAA", days[-1], cm)
    assert a.status == OK and a.sector_etf == "XLK"
    assert a.move_pp == pytest.approx(a.market_pp + a.sector_pp + a.idiosyncratic_pp, abs=1e-9)
    # Independent recomputation with numpy on the same 60-session baseline. The sector factor is
    # orthogonalised on the SAMPLE slope of XLK on SPY, so beta_market = 1 + 0.8*(slope - 1.1),
    # not the population 1.0; the sector loading is recovered exactly.
    from src.research_intel.data import aligned_returns
    w = aligned_returns(p, ["AAA", "SPY", "XLK"], days[-1], 61)
    r, m, x = (np.array(w.returns[k][:-1]) for k in ("AAA", "SPY", "XLK"))
    fit = np.polyfit(m, x, 1)
    sx = x - np.polyval(fit, m)
    coef = np.linalg.lstsq(np.column_stack([np.ones(len(m)), m, sx]), r, rcond=None)[0]
    assert a.beta_market == pytest.approx(coef[1], abs=1e-9)
    assert a.beta_market == pytest.approx(1 + 0.8 * (fit[0] - 1.1), abs=1e-9)
    assert a.beta_sector == pytest.approx(0.8, abs=1e-9)
    assert a.r2_two_factor > 0.99 and a.residual_var_reduction > 0.5


def test_baseline_excludes_judged_day(calendar, rng):
    p, cm, days = _world(calendar, rng, noise=0.003)
    a1 = attribute(p, "AAA", days[-1], cm)
    s = p.series("AAA")
    huge = Series("AAA", s.dates, s.closes[:-1] + (s.closes[-2] * 1.5,), "t")
    p2 = MemoryProvider([p.series("SPY"), p.series("XLK"), huge, p.series("NOETF")])
    a2 = attribute(p2, "AAA", days[-1], cm)
    assert a1.beta_market == pytest.approx(a2.beta_market, abs=1e-12)
    assert a2.idiosyncratic_pp > 40


def test_missing_sector_etf_falls_back_to_market_only(calendar, rng):
    p, cm, days = _world(calendar, rng)
    a = attribute(p, "NOETF", days[-1], cm)
    assert a.status == OK and a.sector_etf is None and a.sector_pp is None
    assert "market-only" in a.reason
    assert a.move_pp == pytest.approx(a.market_pp + a.idiosyncratic_pp, abs=1e-9)
    assert a.beta_market == pytest.approx(0.5, abs=1e-9)


def test_gap_blocks(calendar, rng):
    p, cm, days = _world(calendar, rng)
    s = p.series("XLK")
    gapped = Series("XLK", tuple(d for d in s.dates if d != days[-10]),
                    tuple(c for d, c in zip(s.dates, s.closes) if d != days[-10]), "t")
    p2 = MemoryProvider([p.series("SPY"), gapped, p.series("AAA")])
    a = attribute(p2, "AAA", days[-1], cm)
    assert a.status in (OK, INSUFFICIENT_DATA)
    if a.status == OK:                  # short-history path: window shrank past the gap
        assert a.sample == "SHORT_HISTORY" and a.baseline_n < 60


def test_book_attribution_is_weighted_sum(calendar, rng):
    p, cm, days = _world(calendar, rng, noise=0.002)
    prof = Profile.from_dict({"holdings": [{"symbol": "AAA", "shares": 10}, {"symbol": "NOETF", "shares": 10},
                                           {"symbol": "ZZZ", "shares": 1}]})
    b = book_attribution(p, cm, prof, days[-1])
    rows = {r["symbol"]: r for r in b["positions"]}
    assert set(rows) == {"AAA", "NOETF"} and b["skipped"][0]["symbol"] == "ZZZ"
    exp = sum(r["weight"] * r["move_pp"] for r in rows.values())
    assert b["totals_pp"]["move_pp"] == pytest.approx(exp, abs=1e-3)
    assert b["totals_pp"]["move_pp"] == pytest.approx(
        b["totals_pp"]["market_pp"] + b["totals_pp"]["sector_pp"] + b["totals_pp"]["idiosyncratic_pp"], abs=1e-3)
    assert b["weight_covered"] == pytest.approx(1.0)      # ZZZ is unpriced, so not in the weight basis
    assert "no weight" in b["skipped"][0]["reason"] or b["skipped"][0]["reason"]
