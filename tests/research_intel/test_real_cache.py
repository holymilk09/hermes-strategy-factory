"""Real-data checks against the local Robinhood cache (gitignored).

Skipped when the cache is absent (e.g. clean clone / CI). These pin facts that must
hold for ANY correct engine on real data, not specific market values.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from src.research_intel.data import INSUFFICIENT_DATA, OK, CacheStore
from src.research_intel.relationships import ClusterMap, beta, cluster_cohesion, pair_health

CACHE = Path(__file__).resolve().parents[2] / "cache" / "research_intel" / "ohlcv"
AS_OF = date(2026, 10, 7)

pytestmark = pytest.mark.skipif(not (CACHE / "SPY_1D.csv").exists(),
                                reason="local Robinhood cache not present")


@pytest.fixture(scope="module")
def p():
    return CacheStore(CACHE)


def test_index_self_beta_is_one(p):
    r = beta(p, "SPY", AS_OF, "SPY", 120)
    assert r.status == OK and r.beta == pytest.approx(1.0, abs=1e-12)


def test_semis_more_market_sensitive_than_healthcare(p):
    semis = [beta(p, s, AS_OF, "QQQ", 120).beta for s in ("MU", "AMD", "MRVL", "SMH")]
    health = [beta(p, s, AS_OF, "QQQ", 120).beta for s in ("LLY", "UNH")]
    assert min(semis) > max(health)


def test_short_history_listing_is_blocked_not_padded(p):
    # SKHY: Robinhood returned 73 interpolated gap-fill bars before 2026-07-10; all dropped.
    s = p.series("SKHY")
    assert s.dates[0] >= date(2026, 7, 10)
    assert beta(p, "SKHY", AS_OF, "SPY", 120).status == INSUFFICIENT_DATA
    assert beta(p, "SKHY", AS_OF, "SPY", 60).status == OK
    assert pair_health(p, "MU", "SKHY", AS_OF, allow_short=False).status == INSUFFICIENT_DATA
    h = pair_health(p, "MU", "SKHY", AS_OF)
    assert h.sample == "SHORT_HISTORY" and h.status != INSUFFICIENT_DATA
    assert h.n_long == 62 - 5  # 63 bars -> 62 returns, minus the 5-day divergence window
    assert any("SMALL SAMPLE" in e for e in h.evidence)


def test_configured_cluster_reports_missing_member(p):
    c = cluster_cohesion(p, ClusterMap.from_yaml(), "semiconductors", AS_OF)
    assert c.status == OK
    assert "ARM" in c.unavailable  # not cached -> listed, not silently dropped
