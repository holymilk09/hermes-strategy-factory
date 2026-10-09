"""Property and fuzz tests: invariants any correct engine must satisfy, on many random worlds."""
from __future__ import annotations

import json

import numpy as np
import pytest

from src.research_intel.brief import build_brief, render_brief_md
from src.research_intel.data import INSUFFICIENT_DATA, OK, MemoryProvider, Series, aligned_returns
from src.research_intel.interest import Profile
from src.research_intel.moves import move_context
from src.research_intel.relationships import ClusterMap, beta, pair_health
from src.research_intel.weekly import weekly_map
from tests.research_intel.conftest import series_from_returns

N = 160
SEEDS = range(25)


def world(calendar, seed, gaps=0):
    r = np.random.default_rng(seed)
    days = calendar[: N + 1]
    m = r.normal(0.0004, r.uniform(0.005, 0.02), N)
    out = [series_from_returns("SPY", days, m), series_from_returns("QQQ", days, 1.2 * m)]
    for k, name in enumerate(("AAA", "BBB", "CCC")):
        b = r.uniform(-1, 3)
        s = series_from_returns(name, days, b * m + r.normal(0, r.uniform(0.001, 0.03), N),
                                start_price=r.uniform(1, 2000))
        if gaps:
            drop = set(r.choice(np.arange(1, N), size=gaps, replace=False))
            s = Series(name, tuple(d for i, d in enumerate(s.dates) if i not in drop),
                       tuple(c for i, c in enumerate(s.closes) if i not in drop), "t")
        out.append(s)
    return MemoryProvider(out), days


@pytest.mark.parametrize("seed", SEEDS)
def test_beta_invariant_to_price_scale(calendar, seed):
    p, days = world(calendar, seed)
    a = p.series("AAA")
    scaled = MemoryProvider([p.series(s) for s in ("SPY", "QQQ")] +
                            [Series("AAA", a.dates, tuple(c * 37.5 for c in a.closes), "t")])
    b1, b2 = beta(p, "AAA", days[-1], "SPY", 60), beta(scaled, "AAA", days[-1], "SPY", 60)
    assert b1.beta == pytest.approx(b2.beta, rel=1e-10, abs=1e-12)


@pytest.mark.parametrize("seed", SEEDS)
def test_pair_correlation_is_symmetric(calendar, seed):
    p, days = world(calendar, seed)
    ab, ba = pair_health(p, "AAA", "BBB", days[-1]), pair_health(p, "BBB", "AAA", days[-1])
    assert ab.corr_long == pytest.approx(ba.corr_long, abs=1e-12)
    assert ab.corr_short == pytest.approx(ba.corr_short, abs=1e-12)


@pytest.mark.parametrize("seed", SEEDS)
def test_gapped_data_never_crashes_and_ok_means_complete(calendar, seed):
    p, days = world(calendar, seed, gaps=3)
    for sym in ("AAA", "BBB", "CCC"):
        for d in days[-10:]:
            w = aligned_returns(p, [sym], d, 60)
            if w.status == OK:
                have = set(p.series(sym).dates)
                assert all(s in have for s in w.sessions)
            m = move_context(p, sym, d)
            assert m.status in ("NORMAL", "ALERT", INSUFFICIENT_DATA)
            if m.status != INSUFFICIENT_DATA:
                assert np.isfinite(m.residual_z) and m.baseline_n >= 40


@pytest.mark.parametrize("seed", SEEDS)
def test_residual_identity(calendar, seed):
    p, days = world(calendar, seed)
    m = move_context(p, "AAA", days[-1])
    if m.status != INSUFFICIENT_DATA:
        assert m.move_pp == pytest.approx(m.implied_pp + m.residual_pp, abs=1e-9)
        assert m.implied_pp == pytest.approx(m.beta * m.benchmark_move_pp, abs=1e-9)


@pytest.mark.parametrize("seed", SEEDS)
def test_random_profiles_never_crash_and_stay_research_only(calendar, seed):
    r = np.random.default_rng(1000 + seed)
    p, days = world(calendar, seed, gaps=int(r.integers(0, 4)))
    syms = ["AAA", "BBB", "CCC", "ZZZ", "SPY"]
    prof = Profile.from_dict({
        "holdings": [{"symbol": s, "shares": float(r.integers(0, 500))}
                     for s in r.choice(syms, size=int(r.integers(0, 4)), replace=False)],
        "tickers": [{"symbol": s, "weight": float(r.uniform()), "last_mentioned": str(days[-int(r.integers(1, 60))])}
                    for s in r.choice(syms, size=int(r.integers(0, 3)), replace=False)],
        "pins": list(r.choice(syms, size=int(r.integers(0, 3)), replace=False)),
    })
    cm = ClusterMap({"x": {"stocks": ["AAA", "BBB", "CCC", "ZZZ"]}})
    as_of = days[-int(r.integers(1, 30))]
    b = build_brief(p, prof, as_of, clusters=cm)
    md = render_brief_md(b)
    json.dumps(b)
    json.dumps(weekly_map(p, prof, as_of, clusters=cm))
    assert b["sent_to_broker"] is False
    body = md.replace(b["disclaimer"], "").lower()
    assert "buy " not in body and "sell " not in body
    assert "nan" not in body.replace("nancial", "")
