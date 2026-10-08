"""Relationship engine tests on synthetic data with KNOWN answers.

Each fixture is constructed so the correct output is known in advance (an exact beta,
a planted divergence, a planted correlation breakdown). If the engine is wrong, these
fail; they do not just check that code runs.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from src.research_intel.data import INSUFFICIENT_DATA, OK, MemoryProvider, Series
from src.research_intel.relationships import (
    DECOUPLING,
    DIVERGENCE,
    HEALTHY,
    NOT_LINKED,
    ClusterMap,
    Thresholds,
    beta,
    cluster_cohesion,
    decouplings,
    lead_lag,
    pair_health,
    relationship_map,
)
from tests.research_intel.conftest import series_from_returns

N = 200  # returns per series


def _mkt(rng, n=N):
    return rng.normal(0.0005, 0.01, n)


def _prov(calendar, **rets):
    days = calendar[: N + 1]
    return MemoryProvider([series_from_returns(k, days, v) for k, v in rets.items()]), days


# ------------------------------------------------------------------ beta

def test_beta_exact_when_noise_free(calendar, rng):
    m = _mkt(rng)
    p, days = _prov(calendar, SPY=m, AAA=1.5 * m)
    r = beta(p, "AAA", days[-1], "SPY", 60)
    assert r.status == OK and r.n == 60
    assert r.beta == pytest.approx(1.5, abs=1e-9)
    assert r.r2 == pytest.approx(1.0, abs=1e-9)


def test_beta_recovered_under_noise(calendar, rng):
    m = _mkt(rng)
    p, days = _prov(calendar, SPY=m, AAA=1.2 * m + rng.normal(0, 0.004, N))
    r = beta(p, "AAA", days[-1], "SPY", 120)
    assert r.status == OK
    assert abs(r.beta - 1.2) < 3 * r.stderr
    assert 0.0 < r.stderr < 0.1


def test_beta_is_point_in_time(calendar, rng):
    m = _mkt(rng)
    # relationship flips to beta 3.0 in the final 40 sessions
    a = np.concatenate([0.8 * m[:-40], 3.0 * m[-40:]])
    p, days = _prov(calendar, SPY=m, AAA=a)
    early = days[-41]
    r = beta(p, "AAA", early, "SPY", 60)
    assert r.beta == pytest.approx(0.8, abs=1e-9)
    assert r.as_of == early.isoformat()


def test_beta_blocks_on_gap(calendar, rng):
    m = _mkt(rng)
    days = calendar[: N + 1]
    spy = series_from_returns("SPY", days, m)
    a = series_from_returns("AAA", days, 1.1 * m)
    gap_day = days[-10]
    gapped = Series("AAA", tuple(d for d in a.dates if d != gap_day),
                    tuple(c for d, c in zip(a.dates, a.closes) if d != gap_day), "t")
    r = beta(MemoryProvider([spy, gapped]), "AAA", days[-1], "SPY", 60)
    assert r.status == INSUFFICIENT_DATA
    assert r.beta is None


# ------------------------------------------------------------------ clusters

def test_cluster_from_repo_sector_map():
    cm = ClusterMap.from_yaml()
    mu = cm.info("MU")
    assert mu.primary == "semiconductors"
    assert "technology" in mu.clusters
    assert mu.etf == "XLK"
    assert "NVDA" in mu.peers and "MU" not in mu.peers
    assert cm.info("ZZZZ").primary is None


def test_cluster_extra_override():
    cm = ClusterMap.from_yaml(extra={"memory": {"etf": "SMH", "stocks": ["MU", "SKHY"]}})
    info = cm.info("SKHY")
    assert info.primary == "memory" and info.peers == ("MU",)
    assert cm.info("MU").primary == "memory"  # most specific wins


# ------------------------------------------------------------------ pair health

def test_pair_healthy(calendar, rng):
    m = _mkt(rng)
    p, days = _prov(calendar, SPY=m, AAA=m + rng.normal(0, 0.003, N), BBB=m + rng.normal(0, 0.003, N))
    h = pair_health(p, "AAA", "BBB", days[-1])
    assert h.status == HEALTHY, h.reason
    assert h.corr_long > 0.8


def test_pair_not_linked(calendar, rng):
    p, days = _prov(calendar, SPY=_mkt(rng), AAA=rng.normal(0, 0.01, N), BBB=rng.normal(0, 0.01, N))
    assert pair_health(p, "AAA", "BBB", days[-1]).status == NOT_LINKED


def test_divergence_planted(calendar, rng):
    m = _mkt(rng)
    b = m + rng.normal(0, 0.003, N)
    a = m + rng.normal(0, 0.003, N)
    b[-5:] = 0.02   # leader rips +2%/day for 5 days
    a[-5:] = 0.0    # follower does nothing
    p, days = _prov(calendar, SPY=m, AAA=a, BBB=b)
    h = pair_health(p, "AAA", "BBB", days[-1])
    assert h.status == DIVERGENCE, h.reason
    assert h.residual_z < -2.5
    assert "lagged" in h.direction
    assert h.recent_return_b_pp == pytest.approx((1.02 ** 5 - 1) * 100, rel=1e-9)
    assert h.recent_return_a_pp == pytest.approx(0.0, abs=1e-12)


def test_decoupling_planted(calendar, rng):
    m = _mkt(rng)
    b = m + rng.normal(0, 0.002, N)
    a = m + rng.normal(0, 0.002, N)
    # last 20 sessions: same volatility, independent paths, no drift
    a[-20:] = rng.normal(0, 0.01, 20)
    b[-20:] = rng.normal(0, 0.01, 20)
    p, days = _prov(calendar, SPY=m, AAA=a, BBB=b)
    h = pair_health(p, "AAA", "BBB", days[-1])
    assert h.status in (DECOUPLING, DIVERGENCE), h.reason
    assert h.corr_short < h.corr_long - 0.3
    assert h.corr_change_z <= -2.0


def test_pair_health_insufficient(calendar, rng):
    days = calendar[:101]  # only 100 returns; pair_health needs 120 + 5
    p = MemoryProvider([series_from_returns("SPY", days, _mkt(rng, 100)),
                        series_from_returns("AAA", days, _mkt(rng, 100))])
    assert pair_health(p, "AAA", "SPY", days[-1]).status == INSUFFICIENT_DATA


def test_on_semiconductor_ticker_survives_yaml():
    cm = ClusterMap.from_yaml()
    assert cm.info("ON").primary == "semiconductors"


# ------------------------------------------------------------------ lead/lag

def test_lead_lag_detects_one_day_lag(calendar, rng):
    lead = _mkt(rng)
    follow = np.concatenate([[0.0], lead[:-1]]) + rng.normal(0, 0.001, N)
    p, days = _prov(calendar, SPY=lead, LEAD=lead, FOLL=follow)
    r = lead_lag(p, "LEAD", "FOLL", days[-1], 120, 3)
    assert r.status == OK
    assert r.lag_corr[1] > 0.95
    assert abs(r.lag_corr[0]) < 0.3


# ------------------------------------------------------------------ cohesion / scans

def test_cluster_cohesion_flags_weak_member(calendar, rng):
    m = _mkt(rng)
    cm = ClusterMap({"chips": {"etf": "SMH", "stocks": ["AAA", "BBB", "CCC", "NODATA"]}})
    p, days = _prov(calendar, SPY=m,
                    AAA=m + rng.normal(0, 0.003, N), BBB=m + rng.normal(0, 0.003, N),
                    CCC=rng.normal(0, 0.01, N))
    c = cluster_cohesion(p, cm, "chips", days[-1])
    assert c.status == OK
    assert c.weak_members == ("CCC",)
    assert c.unavailable == ("NODATA",)


def test_decouplings_scan_and_map_are_serializable(calendar, rng):
    m = _mkt(rng)
    b = m + rng.normal(0, 0.003, N)
    a = m + rng.normal(0, 0.003, N)
    c = m + rng.normal(0, 0.003, N)
    b[-5:] = 0.02
    a[-5:] = 0.0
    c[-5:] = 0.02
    cm = ClusterMap({"chips": {"etf": "SMH", "stocks": ["AAA", "BBB", "CCC"]}})
    p, days = _prov(calendar, SPY=m, QQQ=m, AAA=a, BBB=b, CCC=c)
    ev = decouplings(p, cm, ["AAA", "BBB", "CCC"], days[-1])
    flagged = {(e.a, e.b) for e in ev}
    assert ("AAA", "BBB") in flagged and ("AAA", "CCC") in flagged
    assert ("BBB", "CCC") not in flagged and ("CCC", "BBB") not in flagged
    rm = relationship_map(p, cm, ["AAA", "BBB"], days[-1])
    s = json.dumps(rm)
    assert rm["sent_to_broker"] is False
    assert len(rm["symbols"]["AAA"]["betas"]) == 4
    assert "not investment advice" in s.lower()
    # deterministic
    assert json.dumps(relationship_map(p, cm, ["BBB", "AAA"], days[-1])) == s


def test_thresholds_are_reported():
    t = Thresholds()
    assert t.long_window == 120 and t.short_window == 20


# ------------------------------------------------------------------ short history

def _listing(calendar, rng, listed_bars):
    m = _mkt(rng)
    days = calendar[: N + 1]
    spy = series_from_returns("SPY", days, m)
    full = series_from_returns("OLD", days, m + rng.normal(0, 0.003, N))
    new_days = days[-listed_bars:]
    new = series_from_returns("NEW", new_days, (m + rng.normal(0, 0.003, N))[-(listed_bars - 1):])
    return MemoryProvider([spy, full, new]), days


def test_short_history_shrinks_window_and_labels_it(calendar, rng):
    p, days = _listing(calendar, rng, 70)
    assert pair_health(p, "NEW", "OLD", days[-1], allow_short=False).status == INSUFFICIENT_DATA
    h = pair_health(p, "NEW", "OLD", days[-1])
    assert h.sample == "SHORT_HISTORY"
    assert h.n_long == 69 - 5
    assert h.status == HEALTHY
    assert any("SMALL SAMPLE" in e for e in h.evidence)


def test_short_history_floor_blocks_tiny_samples(calendar, rng):
    p, days = _listing(calendar, rng, 30)
    h = pair_health(p, "NEW", "OLD", days[-1])
    assert h.status == INSUFFICIENT_DATA
    assert "longest gap-free window" in h.reason


def test_full_history_pair_is_labelled_full(calendar, rng):
    m = _mkt(rng)
    p, days = _prov(calendar, SPY=m, AAA=m + rng.normal(0, 0.003, N), BBB=m + rng.normal(0, 0.003, N))
    assert pair_health(p, "AAA", "BBB", days[-1]).sample == "FULL"


def test_recent_gap_bounds_short_window(calendar, rng):
    m = _mkt(rng)
    days = calendar[: N + 1]
    a = series_from_returns("AAA", days, m + rng.normal(0, 0.003, N))
    gap = days[-60]
    gapped = Series("AAA", tuple(d for d in a.dates if d != gap),
                    tuple(c for d, c in zip(a.dates, a.closes) if d != gap), "t")
    p = MemoryProvider([series_from_returns("SPY", days, m), gapped,
                        series_from_returns("BBB", days, m + rng.normal(0, 0.003, N))])
    h = pair_health(p, "AAA", "BBB", days[-1])
    assert h.sample == "SHORT_HISTORY"
    assert h.n_long == 58 - 5  # 59 closes after the gap -> 58 returns; the gap is never bridged
