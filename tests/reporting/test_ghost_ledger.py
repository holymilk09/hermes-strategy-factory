"""Tests for Ghost Ledger — append-only audit of rejected/filtered-out setups."""

from __future__ import annotations

import csv
from pathlib import Path

from src.reporting.ghost_ledger import (
    GHOST_FIELDS,
    GhostRecord,
    append_ghost_records,
    build_ghost_record,
    ghost_summary,
    load_ghost_ledger,
    resolve_ghost_outcomes,
)


def _make_record(ghost_id: str = "g1", rejection_reason: str = "too_stretched") -> GhostRecord:
    return build_ghost_record(
        ghost_id=ghost_id,
        source_observation_id="obs1",
        symbol="NVDA",
        strategy_id="momentum_breakout",
        setup_type="swing",
        signal_date="2026-05-20T04:00:00+00:00",
        rejection_reason=rejection_reason,
        failed_gate="volatility_filter",
        score_if_available="70",
        price_at_signal=100.0,
        market_weather="helping",
    )


# ─── Tests ───


def test_ghost_ledger_append(tmp_path: Path) -> None:
    """Ghost record appends to CSV."""
    ledger = tmp_path / "ghost_ledger.csv"
    r = _make_record()
    count = append_ghost_records([r], path=ledger)
    assert count == 1
    assert ledger.exists()
    rows = load_ghost_ledger(ledger)
    assert len(rows) == 1
    assert rows[0]["ghost_id"] == "g1"


def test_ghost_ledger_idempotent(tmp_path: Path) -> None:
    """Same ghost_id does not create duplicate entries."""
    ledger = tmp_path / "ghost_ledger.csv"
    r = _make_record("dedup")
    append_ghost_records([r], path=ledger)
    append_ghost_records([r], path=ledger)  # same record again
    rows = load_ghost_ledger(ledger)
    assert len(rows) == 1  # no duplicate


def test_ghost_record_has_required_fields() -> None:
    """Ghost record contains all required schema fields."""
    r = _make_record()
    d = {f.name: str(getattr(r, f.name)) for f in type(r).__dataclass_fields__.values()}  # type: ignore[arg-type]
    for field in GHOST_FIELDS:
        assert field in d, f"Missing field: {field}"


def test_ghost_record_published_status() -> None:
    """Published status is always GHOST_ONLY."""
    r = _make_record()
    assert r.published_status == "GHOST_ONLY"


def test_ghost_record_has_rejection_reason() -> None:
    """Rejection reason is preserved."""
    r = _make_record(rejection_reason="trend_filter")
    assert r.rejection_reason == "trend_filter"
    assert "trend_filter" in r.reason_not_published


def test_ghost_record_defaults() -> None:
    """Default fields are empty strings, not None."""
    r = _make_record()
    assert r.outcome_5d == ""
    assert r.outcome_10d == ""
    assert r.outcome_20d == ""
    assert r.outcome_30d == ""
    assert r.data_status == "PENDING"
    assert r.setup_broke == ""


def test_ghost_summary_empty(tmp_path: Path) -> None:
    """Empty ghost ledger returns zero-count summary."""
    s = ghost_summary(tmp_path / "empty.csv")
    assert s["total_ghost_records"] == 0


def test_ghost_summary_with_records(tmp_path: Path) -> None:
    """Ghost summary counts records correctly."""
    ledger = tmp_path / "ghost_ledger.csv"
    append_ghost_records([_make_record("g1"), _make_record("g2", rejection_reason="low_score")], path=ledger)
    s = ghost_summary(ledger)
    assert s["total_ghost_records"] == 2
    assert s["rejection_reasons"].get("too_stretched", 0) == 1
    assert s["rejection_reasons"].get("low_score", 0) == 1


def test_ghost_outcomes_no_fabrication(tmp_path: Path) -> None:
    """Without OHLCV data, outcomes remain PENDING/INSUFFICIENT_DATA, never fabricated."""
    ledger = tmp_path / "ghost_ledger.csv"
    r = build_ghost_record(
        ghost_id="no_ohlcv",
        source_observation_id="obs99",
        symbol="NONEXISTENT_SYMBOL",
        strategy_id="momentum",
        setup_type="swing",
        signal_date="2026-05-20T04:00:00+00:00",
        rejection_reason="no_data",
        failed_gate="test",
        price_at_signal=100.0,
    )
    append_ghost_records([r], path=ledger)
    resolve_ghost_outcomes(root=Path("/opt/data"), ghost_path=ledger)
    rows = load_ghost_ledger(ledger)
    assert rows[0]["data_status"] in ("INSUFFICIENT_DATA", "PENDING")
    # Ensure no fake numbers were generated
    assert rows[0].get("outcome_5d", "") == ""
    assert rows[0].get("outcome_10d", "") == ""


def test_ghost_ledger_csv_structure(tmp_path: Path) -> None:
    """CSV header matches GHOST_FIELDS exactly in order."""
    ledger = tmp_path / "ghost_ledger.csv"
    append_ghost_records([_make_record("csv_test")], path=ledger)
    with ledger.open() as f:
        reader = csv.reader(f)
        header = next(reader)
    assert header == GHOST_FIELDS


def test_multiple_ghost_records_appended(tmp_path: Path) -> None:
    """Multiple records append correctly."""
    ledger = tmp_path / "ghost_ledger.csv"
    records = [_make_record(f"g{i}") for i in range(5)]
    count = append_ghost_records(records, path=ledger)
    assert count == 5
    rows = load_ghost_ledger(ledger)
    assert len(rows) == 5