from __future__ import annotations

import csv
from datetime import date

import pytest

from src.research_intel.research_record import (
    FROZEN_LINEAGE, HYPOTHESIS_V1, INCONCLUSIVE, KILL, LOADED, NOT_LOADED, PENDING_SAMPLE, SUCCESS,
    UNIT_SUSPECT, EXPIRED, hypothesis_status, summarize,
)


def _write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


def test_not_loaded_is_explicit():
    s = summarize(None, FROZEN_LINEAGE)
    assert s.status == NOT_LOADED and s.n_resolved == 0 and s.mean_pp is None


def test_frozen_fraction_units_converted_once(tmp_path):
    rows = [{"observation_id": str(i), "signal_date": d, "outcome_status": st, "outcome_return": r}
            for i, (d, st, r) in enumerate([
                ("2026-05-20", "RESOLVED", "0.10"), ("2026-05-20", "RESOLVED", "-0.02"),
                ("2026-07-01", "RESOLVED", "0.04"), ("2026-07-01", "PENDING", "")])]
    p = _write(tmp_path / "frozen.csv", rows)
    before = p.read_bytes()
    s = summarize(p, FROZEN_LINEAGE)
    assert p.read_bytes() == before                    # read-only
    assert s.status == LOADED
    assert (s.n_rows, s.n_resolved, s.n_pending) == (4, 3, 1)
    assert s.mean_pp == pytest.approx(4.0)             # (10 - 2 + 4) / 3 in pp
    assert s.median_pp == pytest.approx(4.0)
    assert s.hit_rate == pytest.approx(2 / 3, abs=1e-4)
    assert s.mean_cost_adj_pp == pytest.approx(3.85)
    assert [(c.signal_date, c.n) for c in s.cohorts] == [("2026-05-20", 2), ("2026-07-01", 1)]


def test_unit_mismatch_is_flagged_not_guessed(tmp_path):
    rows = [{"signal_date": "2026-05-20", "outcome_status": "RESOLVED", "outcome_return": "69.4"}]
    s = summarize(_write(tmp_path / "f.csv", rows), FROZEN_LINEAGE)
    assert s.status == UNIT_SUSPECT
    rows = [{"signal_date": "2026-05-20", "outcome_status": "RESOLVED", "outcome_return_pp": "0.05"}] * 6
    s = summarize(_write(tmp_path / "h.csv", rows), HYPOTHESIS_V1)
    assert s.status == UNIT_SUSPECT


def test_missing_columns(tmp_path):
    s = summarize(_write(tmp_path / "x.csv", [{"a": "1"}]), FROZEN_LINEAGE)
    assert s.status == UNIT_SUSPECT and "not found" in s.notes[0]


def _hyp_rows(n_dates, per_date, ret, excess):
    rows = []
    for d in range(n_dates):
        for i in range(per_date):
            rows.append({"signal_date": f"2026-11-{d + 1:02d}", "symbol": f"S{i}", "outcome_status": "RESOLVED",
                         "outcome_return_pp": str(ret(i)), "excess_vs_spy_pp": str(excess(i))})
    return rows


def test_hypothesis_pending_until_target(tmp_path):
    sel = _write(tmp_path / "sel.csv", _hyp_rows(2, 20, lambda i: 1.0, lambda i: 1.0))
    h = hypothesis_status(sel, None, date(2026, 11, 30))
    assert h.verdict == PENDING_SAMPLE                 # 40 obs but only 2 dates
    assert h.scan_setups_gated
    assert hypothesis_status(None, None, date(2026, 10, 8)).verdict == PENDING_SAMPLE
    assert hypothesis_status(None, None, date(2027, 5, 1)).verdict == EXPIRED


def test_hypothesis_success_kill_inconclusive(tmp_path):
    sel = _write(tmp_path / "s.csv", _hyp_rows(3, 10, lambda i: 2.0 if i < 6 else -1.0, lambda i: 0.5))
    rej = _write(tmp_path / "r.csv", _hyp_rows(3, 10, lambda i: -0.5, lambda i: -0.5))
    h = hypothesis_status(sel, rej, date(2026, 12, 1))
    assert h.verdict == SUCCESS and not h.scan_setups_gated
    assert h.hit_rate == pytest.approx(0.6)
    bad = _write(tmp_path / "b.csv", _hyp_rows(3, 10, lambda i: -3.0, lambda i: -3.0))
    assert hypothesis_status(bad, rej, date(2026, 12, 1)).verdict == KILL
    meh = _write(tmp_path / "m.csv", _hyp_rows(3, 10, lambda i: 1.0 if i < 5 else -1.0, lambda i: 0.1))
    h = hypothesis_status(meh, rej, date(2026, 12, 1))
    assert h.verdict == INCONCLUSIVE                   # hit 50%: no success, no kill
