"""Corporate-action audit tests. Fixtures mirror the real cases found in Phase 1b."""
from __future__ import annotations

from datetime import date

from src.research_intel.data import INSUFFICIENT_DATA, OK, CacheStore, Series, aligned_returns
from src.research_intel.data_quality import CLEAN_SPLIT, DISTRIBUTION, INVALID, adjustment_audit
from tests.research_intel.conftest import series_from_returns


def _pair(calendar, ratio_fn, n=60):
    days = calendar[:n]
    adj = series_from_returns("X", days, [0.001] * (n - 1))
    raw = Series("X", adj.dates, tuple(c * ratio_fn(i) for i, c in enumerate(adj.closes)), "raw")
    return adj, raw, days


def test_clean_split_is_ok(calendar):           # NVDA 10:1, 2024-06-10
    adj, raw, _ = _pair(calendar, lambda i: 10.0 if i < 30 else 1.0)
    a = adjustment_audit(adj, raw)
    assert a.status == "OK" and a.steps[0].kind == CLEAN_SPLIT and a.steps[0].factor == 10.0


def test_reverse_split_is_ok(calendar):
    adj, raw, _ = _pair(calendar, lambda i: 0.1 if i < 30 else 1.0)
    assert adjustment_audit(adj, raw).steps[0].kind == CLEAN_SPLIT


def test_spin_off_is_ok(calendar):              # GE Vernova, factor 1.240352
    adj, raw, _ = _pair(calendar, lambda i: 1.240352 if i < 30 else 1.0)
    a = adjustment_audit(adj, raw)
    assert a.status == "OK" and a.steps[0].kind == DISTRIBUTION


def test_irregular_upward_adjustment_is_quarantined(calendar):   # HON, factor 0.953987
    def r(i):
        return 1.012548 if i < 20 else (0.953987 if i < 40 else 1.0)
    adj, raw, days = _pair(calendar, r)
    a = adjustment_audit(adj, raw)
    assert [s.kind for s in a.steps] == [DISTRIBUTION, INVALID]
    assert a.status == "QUARANTINED"
    q = {date.fromisoformat(d) for d in a.quarantine}
    assert days[20] in q and days[40] in q and days[43] in q   # prev step .. invalid step + 3
    assert days[19] not in q and days[44] not in q


def test_quarantined_dates_block_windows(tmp_path, calendar):
    days = calendar[:61]
    st = CacheStore(tmp_path)
    st.write(series_from_returns("SPY", days, [0.001] * 60))
    st.write(series_from_returns("X", days, [0.002] * 60))
    assert aligned_returns(st, ["X"], days[-1], 20).status == OK
    st.write_quarantine({"X": {"dates": [days[-5].isoformat()], "reason": "test"}})
    w = aligned_returns(st, ["X"], days[-1], 20)
    assert w.status == INSUFFICIENT_DATA and w.missing["X"] == (days[-5],)
    assert len(st.raw_series("X").dates) == 61       # audit view still sees everything
    st.write(series_from_returns("X", days, [0.002] * 60))  # rewrite with same data is allowed
