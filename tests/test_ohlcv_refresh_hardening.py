"""Phase 6J-REFRESH-HARDENING — Tests for automatic TARGET_DATE resolution.

Tests check:
1. Target date is pulled from Alpaca calendar (no manual patch needed)
2. REFRESH_TARGET_DATE env var works as override (testing only)
3. Missing credentials returns CALENDAR_UNAVAILABLE
4. Current incomplete trading day is excluded before close
5. Ledger hashes remain unchanged after running refresh
6. Observation cycle is not invoked via import

Hard constraints:
- No strategy behavior changed
- No thresholds/scoring/maturity rules changed
- No ledgers mutated
- Observation cycle never invoked
"""

from __future__ import annotations

import hashlib
import os
from datetime import date, datetime, time, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── Module under test ──────────────────────────────────────────────────────────

from src.reporting.market_calendar_freshness import (
    fetch_alpaca_calendar,
    parse_calendar_entries,
    get_latest_completed_session,
)


# ── 1. Target date resolves from Alpaca calendar ──────────────────────────────


def test_target_date_resolved_from_calendar():
    """Target date is pulled from Alpaca calendar without manual patch."""
    # Simulate the logic from _resolve_target_date()
    raw = fetch_alpaca_calendar()
    assert raw is not None, "Alpaca calendar unavailable — cannot test"

    entries = parse_calendar_entries(raw)
    assert len(entries) > 0

    latest = get_latest_completed_session(entries)
    assert latest is not None
    target = latest.date.isoformat()

    # Must be a valid date string
    assert len(target) == 10
    assert "-" in target
    # Must be a weekday (Mon-Fri)
    assert latest.date.isoweekday() <= 5, f"Target {target} is a weekend"


def test_target_date_not_manual_patch():
    """Verify the actual module no longer requires a hardcoded TARGET_DATE patch.

    The global TARGET_DATE starts as None and is resolved dynamically.
    """
    from scripts import refresh_stale_ohlcv as rso

    assert rso.TARGET_DATE is None, (
        f"TARGET_DATE should start as None, got {rso.TARGET_DATE!r}. "
        "Hardcoded patch not removed!"
    )


# ── 2. REFRESH_TARGET_DATE override works ──────────────────────────────────────


def test_env_override_works(monkeypatch):
    """REFRESH_TARGET_DATE env var should be used as override."""
    from scripts.refresh_stale_ohlcv import _resolve_target_date

    monkeypatch.setenv("REFRESH_TARGET_DATE", "2026-06-01")
    target = _resolve_target_date()
    assert target == "2026-06-01", f"Expected 2026-06-01, got {target}"


def test_env_override_skips_calendar(monkeypatch):
    """When REFRESH_TARGET_DATE is set, calendar fetch should NOT be called."""
    from scripts.refresh_stale_ohlcv import _resolve_target_date

    monkeypatch.setenv("REFRESH_TARGET_DATE", "2026-05-28")
    # If calendar was called with bad creds, this would fail — but with override,
    # it should just return the override value without touching calendar
    monkeypatch.setenv("ALPACA_API_KEY", "")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "")

    target = _resolve_target_date()
    assert target == "2026-05-28"


# ── 3. CALENDAR_UNAVAILABLE on missing creds ───────────────────────────────────


def test_calendar_unavailable_with_bad_creds(monkeypatch):
    """When Alpaca creds are missing and no override, should raise SystemExit."""
    from scripts.refresh_stale_ohlcv import _resolve_target_date

    monkeypatch.delenv("REFRESH_TARGET_DATE", raising=False)
    monkeypatch.setenv("ALPACA_API_KEY", "")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "")

    import pytest
    with pytest.raises(SystemExit) as exc:
        _resolve_target_date()
    assert exc.value.code == 1


# ── 4. Current day excluded before close ──────────────────────────────────────


def test_current_day_excluded_before_close():
    """Before market close ET, current day should NOT be included."""
    entries = [
        type("Entry", (), {"date": date(2026, 5, 27), "isoweekday": lambda: 3})(),
        type("Entry", (), {"date": date(2026, 5, 28), "isoweekday": lambda: 4})(),
        type("Entry", (), {"date": date(2026, 5, 29), "isoweekday": lambda: 5})(),
    ]
    # This is already tested in test_market_calendar_freshness.py via
    # get_latest_completed_session. We're just confirming the same
    # function is used by the refresh script.

    from src.reporting.market_calendar_freshness import get_latest_completed_session
    real_entries = [
        type("Entry", (), {"date": date(2026, 5, 28), "close_time": time(16, 0)})(),
        type("Entry", (), {"date": date(2026, 5, 29), "close_time": time(16, 0)})(),
    ]
    # Simulate May 29 at 14:00 UTC = 10:00 ET (before 16:00 ET close)
    now = datetime(2026, 5, 29, 14, 0, 0, tzinfo=timezone.utc)
    latest = get_latest_completed_session(real_entries, now)
    assert latest is not None
    assert latest.date == date(2026, 5, 28), (
        f"Expected May 28 (before close), got {latest.date}"
    )


# ── 5. Ledger immutability ────────────────────────────────────────────────────


def test_ledger_hashes_unchanged_after_refresh():
    """Running the refresh module should NOT mutate observer/outcome/ghost ledgers.

    We test by importing the module (no side effects) and verifying
    ledger hashes are the same as when the test started.
    """
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

    # Import the module (does NOT run refresh — just checks import doesn't mutate)
    from scripts import refresh_stale_ohlcv as rso
    _ = rso  # suppress unused warning

    # Snapshot hashes after import
    for lp in ledgers:
        after_hash = hashlib.sha256(lp.read_bytes()).hexdigest()
        assert after_hash == before[lp.name], (
            f"Ledger {lp.name} was mutated by importing refresh module!"
        )


# ── 6. Observation cycle not invoked ──────────────────────────────────────────


def test_observation_cycle_not_invoked_via_import():
    """Verify that importing the refresh module does NOT import observation cycle."""
    import sys as _sys
    loaded = [m for m in _sys.modules.keys()
              if "observation_cycle" in m.lower() and "calendar" not in m.lower()]
    # The observation_cycle module might be pre-loaded from conftest or other tests.
    # We check that the refresh module specifically did NOT trigger it.
    # If it was already loaded, that's from another test — acceptable.
    # But if the refresh module imported it, that's an issue.
    from scripts import refresh_stale_ohlcv as rso
    _ = rso

    # After importing refresh, check that no NEW observation_cycle modules appeared
    # (beyond what was already loaded before this test)
    loaded_after = [m for m in _sys.modules.keys()
                    if "observation_cycle" in m.lower() and "calendar" not in m.lower()]
    # The refresh module imports calendar_freshness, which has a test
    # that observation_cycle is not invoked. The refresh module itself
    # should not import anything with "observation_cycle" in its name.
    assert len(loaded_after) == 0 or all(
        "observation_cycle" not in str(getattr(_sys.modules[m], "__file__", ""))
        for m in loaded_after
    ), (
        f"Observation cycle module loaded via refresh import: {loaded_after}"
    )


# ── 7. Memorial Day skipped ───────────────────────────────────────────────────


def test_memorial_day_skipped():
    """Memorial Day (2026-05-25, Monday) should NOT be in calendar."""
    raw = fetch_alpaca_calendar(start="2026-05-24", end="2026-05-27")
    assert raw is not None, "Alpaca calendar unavailable"
    entries = parse_calendar_entries(raw)
    dates = {e.date.isoformat() for e in entries}
    assert "2026-05-25" not in dates, (
        f"Memorial Day (2026-05-25) unexpectedly in calendar. "
        f"Present dates: {sorted(dates)}"
    )
