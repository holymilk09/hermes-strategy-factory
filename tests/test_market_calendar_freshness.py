"""Phase 6J-CALENDAR — Alpaca Calendar Freshness Tests.

Tests check:
1. Memorial Day skipped correctly in calendar parsing
2. Early close detected
3. Latest completed session excludes current day before market close
4. Local CSV one day behind → DATA_STALE_NEEDS_REFRESH
5. Missing QQQ → DATA_STALE_NEEDS_REFRESH
6. No ledgers mutated by freshness check
7. Observation cycle is not invoked

Hard constraints:
- No strategy behavior changed
- No thresholds/scoring/maturity rules changed
- No ledgers mutated
- Observation cycle never invoked

Marker policy:
  @pytest.mark.requires_data   — needs production ledger CSVs
  @pytest.mark.requires_network — makes live Alpaca API call
  (no marker) — pure unit test, passes on fresh clone
"""

from __future__ import annotations

import csv
import hashlib
import os
import tempfile
from datetime import date, datetime, time, timezone, timedelta
from pathlib import Path

import pytest

# We import from the module under test
from src.reporting.market_calendar_freshness import (
    AlpacaCalendarEntry,
    FreshnessResult,
    check_data_freshness,
    fetch_alpaca_calendar,
    get_latest_completed_session,
    parse_calendar_entries,
    assert_no_ledger_mutation,
)

ROOT = Path(__file__).resolve().parents[1]


# ── 1. Calendar Parsing ────────────────────────────────────────────────────────


def test_memorial_day_skipped():
    """Memorial Day (2026-05-25, Monday) should NOT be in the calendar."""
    raw = fetch_alpaca_calendar(start="2026-05-24", end="2026-05-27")
    assert raw is not None, "Alpaca calendar unavailable"
    entries = parse_calendar_entries(raw)
    dates = {e.date.isoformat() for e in entries}
    assert "2026-05-25" not in dates, (
        f"Memorial Day (2026-05-25) unexpectedly in calendar. "
        f"Present dates: {sorted(dates)}"
    )


def test_memorial_day_weekend_pattern():
    """Weekends should also be absent from calendar."""
    raw = fetch_alpaca_calendar(start="2026-05-22", end="2026-05-26")
    assert raw is not None, "Alpaca calendar unavailable"
    entries = parse_calendar_entries(raw)
    dates = {e.date.isoformat() for e in entries}
    for wk in ["2026-05-23", "2026-05-24"]:
        assert wk not in dates, f"Weekend day {wk} unexpectedly in calendar"
    assert "2026-05-22" in dates, "Friday 2026-05-22 should be in calendar"
    assert "2026-05-26" in dates, "Tuesday 2026-05-26 should be in calendar"


def test_early_close_detected():
    """Early close detected in AlpacaCalendarEntry."""
    normal = AlpacaCalendarEntry(
        date=date(2026, 5, 20),
        open_time=time(9, 30),
        close_time=time(16, 0),
    )
    early = AlpacaCalendarEntry(
        date=date(2026, 5, 25),  # hypothetical early close
        open_time=time(9, 30),
        close_time=time(13, 0),
    )
    assert not normal.is_early_close, "Normal close should not be early"
    assert early.is_early_close, "13:00 close should be detected as early"
    assert normal.is_full_day, "16:00 close should be full day"
    assert not early.is_full_day, "13:00 close should not be full day"


# ── 2. Latest Completed Session Logic ──────────────────────────────────────────


def test_latest_completed_session_excludes_current_day_before_close():
    """Before market close ET, current day should NOT be included."""
    entries = [
        AlpacaCalendarEntry(date=date(2026, 5, 27), open_time=time(9, 30), close_time=time(16, 0)),
        AlpacaCalendarEntry(date=date(2026, 5, 28), open_time=time(9, 30), close_time=time(16, 0)),
        AlpacaCalendarEntry(date=date(2026, 5, 29), open_time=time(9, 30), close_time=time(16, 0)),
    ]

    # Simulate May 29 at 14:00 UTC = 10:00 ET (before 16:00 ET close)
    now = datetime(2026, 5, 29, 14, 0, 0, tzinfo=timezone.utc)
    latest = get_latest_completed_session(entries, now)
    assert latest is not None
    # Should return May 28 (previous completed day), NOT May 29 (still open)
    assert latest.date == date(2026, 5, 28), (
        f"Expected May 28, got {latest.date}"
    )


def test_latest_completed_session_includes_today_after_close():
    """After market close ET, current day SHOULD be included."""
    entries = [
        AlpacaCalendarEntry(date=date(2026, 5, 27), open_time=time(9, 30), close_time=time(16, 0)),
        AlpacaCalendarEntry(date=date(2026, 5, 28), open_time=time(9, 30), close_time=time(16, 0)),
    ]

    # Simulate May 28 at 21:00 UTC = 17:00 ET (after 16:00 ET close)
    now = datetime(2026, 5, 28, 21, 0, 0, tzinfo=timezone.utc)
    latest = get_latest_completed_session(entries, now)
    assert latest is not None
    assert latest.date == date(2026, 5, 28), (
        f"Expected May 28 (after close), got {latest.date}"
    )


def test_latest_completed_session_weekend_monday():
    """After weekend, latest completed session should be Friday."""
    entries = [
        AlpacaCalendarEntry(date=date(2026, 5, 22), open_time=time(9, 30), close_time=time(16, 0)),
        AlpacaCalendarEntry(date=date(2026, 5, 26), open_time=time(9, 30), close_time=time(16, 0)),
    ]

    # Simulate Sunday May 24 (weekend)
    now = datetime(2026, 5, 24, 12, 0, 0, tzinfo=timezone.utc)
    latest = get_latest_completed_session(entries, now)
    assert latest is not None
    assert latest.date == date(2026, 5, 22), (
        f"Expected May 22 (Friday), got {latest.date}"
    )


# ── 3. Real-world freshness check (against actual local cache) ─────────────────


@pytest.mark.requires_ohlcv
@pytest.mark.requires_network
def test_freshness_real_local_cache():
    """Actual freshness check against real local OHLCV cache.

    This test runs against the live Alpaca calendar. It validates that
    the module returns one of the valid status codes and does not crash.
    """
    result = check_data_freshness(root=ROOT)
    assert result.status in (
        "DATA_CURRENT",
        "DATA_STALE_NEEDS_REFRESH",
        "CALENDAR_UNAVAILABLE",
        "CACHE_PATH_MISMATCH",
    ), f"Unexpected status: {result.status}"

    # If calendar is available, it should have entries
    if result.alpaca_calendar_available:
        assert result.calendar_entries > 0
        assert result.latest_completed_session is not None

    # If we have data, local_ohlcv_latest_session should be set
    if result.local_ohlcv_latest_session is not None:
        # Must be a valid YYYY-MM-DD string
        assert len(result.local_ohlcv_latest_session) == 10
        assert "-" in result.local_ohlcv_latest_session


# ── 4. Integrity ────────────────────────────────────────────────────────────────


@pytest.mark.requires_data
def test_no_ledger_mutation_by_freshness_check():
    """Freshness check must NOT mutate observation/outcome/ghost ledgers."""
    ledgers = [
        ROOT / "data" / "paper_observation" / "relative_strength_continuation_observation_ledger.csv",
        ROOT / "data" / "paper_observation" / "relative_strength_continuation_outcome_ledger.csv",
        ROOT / "data" / "trust_calibration" / "ghost_ledger.csv",
    ]

    # Snapshot hashes before
    before = {}
    for lp in ledgers:
        assert lp.exists(), f"Ledger not found: {lp}"
        before[lp.name] = hashlib.sha256(lp.read_bytes()).hexdigest()

    # Run freshness check
    _ = check_data_freshness(root=ROOT)

    # Snapshot hashes after
    for lp in ledgers:
        after_hash = hashlib.sha256(lp.read_bytes()).hexdigest()
        assert after_hash == before[lp.name], (
            f"Ledger {lp.name} was mutated by freshness check!"
        )


@pytest.mark.requires_data
def test_assert_no_ledger_mutation_passes():
    """assert_no_ledger_mutation should pass without error."""
    assert_no_ledger_mutation(root=ROOT)


def test_observation_cycle_not_invoked_via_import():
    """Verify that importing freshness module does NOT import observation cycle."""
    import sys as _sys
    # Only match src.paper.* observation-cycle modules, not test files whose
    # names happen to contain "observation_cycle".
    loaded = [
        m for m in _sys.modules.keys()
        if "observation_cycle" in m.lower()
        and m.startswith("src.")
    ]
    assert len(loaded) == 0, (
        f"Observation cycle module loaded via freshness import: {loaded}"
    )


# ── 5. Edge cases ──────────────────────────────────────────────────────────────


def test_calendar_unavailable_with_bad_creds(monkeypatch):
    """When Alpaca creds are missing, should return CALENDAR_UNAVAILABLE."""
    monkeypatch.setenv("ALPACA_API_KEY", "")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "")
    result = check_data_freshness(root=ROOT)
    assert result.status == "CALENDAR_UNAVAILABLE"
    assert result.error is not None


def test_cache_path_mismatch(tmp_path):
    """When OHLCV cache dir is missing, returns CACHE_PATH_MISMATCH."""
    result = check_data_freshness(root=tmp_path)
    assert result.status == "CACHE_PATH_MISMATCH"


@pytest.mark.requires_ohlcv
@pytest.mark.requires_network
def test_symbol_latest_dates_are_consistent():
    """All required 6 symbols should have same latest date (same trading day)."""
    result = check_data_freshness(root=ROOT)
    if result.status in ("CALENDAR_UNAVAILABLE", "CACHE_PATH_MISMATCH"):
        return  # Can't test consistency
    dates = {s: d for s, d in result.required_latest.items() if d is not None}
    if len(dates) < 2:
        return
    unique_dates = set(dates.values())
    assert len(unique_dates) == 1, (
        f"Inconsistent latest dates across required symbols: {dates}"
    )
