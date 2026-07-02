"""Tests for output_store_schema — dataclass definitions and validation rules.

Source-only tests: no production ledgers, no OHLCV data, no live DB.
"""

from __future__ import annotations

import pytest

from src.reporting.output_store_schema import (
    EXPECTED_GHOST_MIN_COUNT,
    EXPECTED_OBSERVATION_COUNT,
    EXPECTED_PENDING_COUNT,
    EXPECTED_RESOLVED_COUNT,
    FORBIDDEN_FIELDS,
    REQUIRED_COLUMNS,
    ApprovedPublication,
    EdgeAuditResult,
    GhostRejection,
    MaturityResult,
    SetupCard,
    SystemRun,
)


class TestSchemaRequiredColumns:
    """Verify REQUIRED_COLUMNS dict is complete for each table."""

    def test_setup_cards_has_required_columns(self):
        required = REQUIRED_COLUMNS["setup_cards"]
        assert "observation_id" in required
        assert "symbol" in required
        assert "signal_date" in required
        assert "signal_close" in required
        assert "setup_label" in required
        assert "lineage" in required
        assert "status" in required
        assert "maturity_bars" in required
        assert "maturity_window" in required

    def test_maturity_results_has_required_columns(self):
        required = REQUIRED_COLUMNS["maturity_results"]
        assert "observation_id" in required
        assert "symbol" in required
        assert "signal_date" in required
        assert "outcome_date" in required
        assert "signal_close" in required
        assert "outcome_close" in required
        assert "raw_return" in required
        assert "spy_return" in required
        assert "qqq_return" in required
        assert "benchmark_relative_return" in required
        assert "cost_adjusted_return" in required
        assert "delay_adjusted_return" in required
        assert "drift_label" in required
        assert "sample_size_warning" in required
        assert "concurrent_exposure_warning" in required

    def test_edge_audit_results_has_required_columns(self):
        required = REQUIRED_COLUMNS["edge_audit_results"]
        assert "observation_id" in required
        assert "symbol" in required
        assert "drift_label" in required
        assert "economic_sanity_status" in required
        assert "cost_status" in required
        assert "delay_status" in required
        assert "filter_lift_status" in required

    def test_ghost_rejections_has_required_columns(self):
        required = REQUIRED_COLUMNS["ghost_rejections"]
        assert "symbol" in required
        assert "rejection_date" in required
        assert "rejection_reason" in required
        assert "lineage" in required
        assert "audit_run_id" in required


class TestForbiddenFields:
    """Verify FORBIDDEN_FIELDS includes broker/live fields."""

    def test_forbidden_includes_sent_to_broker(self):
        assert "sent_to_broker" in FORBIDDEN_FIELDS

    def test_forbidden_includes_broker_order_id(self):
        assert "broker_order_id" in FORBIDDEN_FIELDS


class TestExpectedCounts:
    """Verify baseline approved counts match Phase 6L/6M state."""

    def test_expected_observation_count(self):
        assert EXPECTED_OBSERVATION_COUNT == 7

    def test_expected_resolved_count(self):
        assert EXPECTED_RESOLVED_COUNT == 7

    def test_expected_pending_count(self):
        assert EXPECTED_PENDING_COUNT == 0

    def test_expected_ghost_min_count(self):
        assert EXPECTED_GHOST_MIN_COUNT >= 80


class TestSetupCard:
    def test_create_minimal(self):
        card = SetupCard(
            observation_id="abc123",
            symbol="TEST",
            signal_date="2026-06-01T00:00:00Z",
            signal_close=100.0,
            setup_label="Research Observation",
            lineage="test_lineage",
        )
        assert card.observation_id == "abc123"
        assert card.symbol == "TEST"
        assert card.status == "RESOLVED"
        assert card.maturity_window == 10
        assert card.strategy == "relative_strength_continuation"

    def test_to_dict_includes_all_fields(self):
        card = SetupCard(
            observation_id="abc123",
            symbol="TEST",
            signal_date="2026-06-01T00:00:00Z",
            signal_close=100.0,
            setup_label="Research Observation",
            lineage="test_lineage",
        )
        d = card.to_dict()
        assert d["observation_id"] == "abc123"
        assert d["symbol"] == "TEST"
        assert d["signal_close"] == 100.0
        assert "ret_5d" in d
        assert "ret_20d" in d
        assert "close_above_ma50" in d

    def test_defaults_do_not_leak_sent_to_broker(self):
        """SetupCard must never include broker fields."""
        card = SetupCard(
            observation_id="abc123",
            symbol="TEST",
            signal_date="2026-06-01T00:00:00Z",
            signal_close=100.0,
            setup_label="Research Observation",
            lineage="test_lineage",
        )
        d = card.to_dict()
        assert "sent_to_broker" not in d
        assert "broker_order_id" not in d


class TestMaturityResult:
    def test_create_minimal(self):
        result = MaturityResult(
            observation_id="abc123",
            symbol="TEST",
            signal_date="2026-06-01T00:00:00Z",
            outcome_date="2026-06-15T00:00:00Z",
            signal_close=100.0,
            outcome_close=110.0,
            raw_return=0.10,
            spy_return=0.02,
            qqq_return=0.03,
            benchmark_relative_return=0.07,
            cost_adjusted_return=0.09,
            delay_adjusted_return=0.095,
            drift_label="Independent Strength",
        )
        assert result.observation_id == "abc123"
        assert result.sample_size_warning is True
        assert result.concurrent_exposure_warning is False
        assert result.outcome_status == "RESOLVED"

    def test_to_dict_includes_all_required(self):
        result = MaturityResult(
            observation_id="abc123",
            symbol="TEST",
            signal_date="2026-06-01T00:00:00Z",
            outcome_date=None,
            signal_close=100.0,
            outcome_close=None,
            raw_return=None,
            spy_return=None,
            qqq_return=None,
            benchmark_relative_return=None,
            cost_adjusted_return=None,
            delay_adjusted_return=None,
            drift_label=None,
        )
        d = result.to_dict()
        required = REQUIRED_COLUMNS["maturity_results"]
        for field in required:
            assert field in d, f"Missing required field: {field}"


class TestEdgeAuditResult:
    def test_create_minimal(self):
        audit = EdgeAuditResult(
            observation_id="abc123",
            symbol="TEST",
            drift_label="Independent Strength",
            economic_sanity_status="pass",
            cost_status="cost_resilient",
            delay_status="delay_resilient",
            filter_lift_status="ghost_baseline_available",
        )
        assert audit.observation_id == "abc123"
        assert audit.compounding_artifact_warning is False

    def test_to_dict_includes_required(self):
        audit = EdgeAuditResult(
            observation_id="abc123",
            symbol="TEST",
            drift_label="Independent Strength",
            economic_sanity_status="pass",
            cost_status="cost_resilient",
            delay_status="delay_resilient",
            filter_lift_status="ghost_baseline_available",
        )
        d = audit.to_dict()
        required = REQUIRED_COLUMNS["edge_audit_results"]
        for field in required:
            assert field in d, f"Missing required field: {field}"


class TestGhostRejection:
    def test_create_minimal(self):
        ghost = GhostRejection(
            ghost_id="abc123def456",
            symbol="TEST",
            rejection_date="2026-06-01T00:00:00Z",
            rejection_reason="20d_momentum_too_weak",
            failed_gate="ret_20d_rank",
            lineage="test_lineage",
        )
        assert ghost.ghost_id == "abc123def456"
        assert ghost.symbol == "TEST"
        assert ghost.strategy_id == "relative_strength_continuation"
        assert ghost.setup_type == "swing"

    def test_to_dict_includes_required(self):
        ghost = GhostRejection(
            ghost_id="abc123",
            symbol="TEST",
            rejection_date="2026-06-01T00:00:00Z",
            rejection_reason="20d_momentum_too_weak",
            failed_gate="ret_20d_rank",
            lineage="test_lineage",
        )
        d = ghost.to_dict()
        required = REQUIRED_COLUMNS["ghost_rejections"]
        for field in required:
            assert field in d, f"Missing required field: {field}"


class TestSystemRun:
    def test_auto_generates_started_at(self):
        run = SystemRun(run_id="test_run", run_type="export")
        assert run.started_at != ""

    def test_validation_errors_default_empty(self):
        run = SystemRun(run_id="test_run", run_type="export")
        assert run.validation_errors == []

    def test_to_dict_serializable(self):
        run = SystemRun(
            run_id="test_run",
            run_type="export",
            status="completed",
            observation_count=7,
            validation_passed=True,
            validation_errors=[],
        )
        d = run.to_dict()
        assert d["run_id"] == "test_run"
        assert d["status"] == "completed"
        assert d["validation_passed"] is True


class TestImmutableDataclass:
    """Verify dataclasses are frozen (immutable)."""

    def test_setup_card_is_frozen(self):
        card = SetupCard(
            observation_id="abc123",
            symbol="TEST",
            signal_date="2026-06-01T00:00:00Z",
            signal_close=100.0,
            setup_label="Research Observation",
            lineage="test_lineage",
        )
        with pytest.raises(Exception):
            card.symbol = "CHANGED"  # type: ignore[misc]

    def test_maturity_result_is_frozen(self):
        result = MaturityResult(
            observation_id="abc123",
            symbol="TEST",
            signal_date="2026-06-01T00:00:00Z",
            outcome_date=None,
            signal_close=100.0,
            outcome_close=None,
            raw_return=None,
            spy_return=None,
            qqq_return=None,
            benchmark_relative_return=None,
            cost_adjusted_return=None,
            delay_adjusted_return=None,
            drift_label=None,
        )
        with pytest.raises(Exception):
            result.symbol = "CHANGED"  # type: ignore[misc]