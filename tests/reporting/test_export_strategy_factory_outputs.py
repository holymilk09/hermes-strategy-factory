"""Tests for export_strategy_factory_outputs — validation and export logic.

Source-only tests use synthetic fixtures. Data-backed tests use requires_data marker.
"""

from __future__ import annotations

import csv
import io
import json
import tempfile
from pathlib import Path

import pytest

# Mark all data-backed tests
pytestmark = pytest.mark.requires_data

# Import after path setup
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.export_strategy_factory_outputs import (
    ExportValidationError,
    _safe_bool,
    _safe_float,
    build_ghost_rejections,
    build_maturity_results,
    build_setup_cards,
    format_jsonl,
    validate_ledgers,
)


# ─────────────────────────────────────────────────────────
# Synthetic fixtures
# ─────────────────────────────────────────────────────────


def _make_obs_row(
    obs_id: str = "abc123",
    symbol: str = "TEST",
    signal_ts: str = "2026-06-01T04:00:00+00:00",
    signal_close: str = "100.0",
    lineage: str = "test_lineage",
    strategy: str = "relative_strength_continuation",
    outcome_status: str = "PENDING",
    sent_to_broker: str = "False",
    broker_order_id: str = "",
) -> dict[str, str]:
    return {
        "observation_id": obs_id,
        "signal_timestamp": signal_ts,
        "symbol": symbol,
        "strategy": strategy,
        "lineage": lineage,
        "signal_close": signal_close,
        "ret_5d": "0.05",
        "ret_20d": "0.15",
        "ret_60d": "0.30",
        "ret_20d_rank": "0.90",
        "ret_60d_rank": "0.75",
        "close_above_ma50": "True",
        "outcome_window": "10",
        "outcome_status": outcome_status,
        "outcome_return": "",
        "outcome_timestamp": "",
        "created_at": "2026-06-01T00:00:00Z",
        "sent_to_broker": sent_to_broker,
        "broker_order_id": broker_order_id,
    }


def _make_out_row(
    obs_id: str = "abc123",
    symbol: str = "TEST",
    signal_ts: str = "2026-06-01T04:00:00+00:00",
    signal_close: str = "100.0",
    outcome_status: str = "RESOLVED",
    outcome_close: str = "110.0",
    outcome_return: str = "0.10",
    outcome_ts: str = "2026-06-15T04:00:00+00:00",
) -> dict[str, str]:
    return {
        "observation_id": obs_id,
        "signal_timestamp": signal_ts,
        "symbol": symbol,
        "strategy": "relative_strength_continuation",
        "lineage": "test_lineage",
        "signal_close": signal_close,
        "ret_5d": "0.05",
        "ret_20d": "0.15",
        "ret_60d": "0.30",
        "ret_20d_rank": "0.90",
        "ret_60d_rank": "0.75",
        "close_above_ma50": "True",
        "outcome_window": "10",
        "outcome_status": outcome_status,
        "outcome_return": outcome_return,
        "outcome_timestamp": outcome_ts,
        "created_at": "2026-06-01T00:00:00Z",
        "sent_to_broker": "False",
        "broker_order_id": "",
        "outcome_close": outcome_close,
    }


def _make_ghost_row(
    ghost_id: str = "ghost001",
    symbol: str = "TEST",
    signal_date: str = "2026-06-01T04:00:00+00:00",
    rejection_reason: str = "20d_momentum_too_weak",
    failed_gate: str = "ret_20d_rank",
    strategy_id: str = "test_lineage",
) -> dict[str, str]:
    return {
        "ghost_id": ghost_id,
        "source_observation_id": "",
        "symbol": symbol,
        "strategy_id": strategy_id,
        "setup_type": "swing",
        "signal_date": signal_date,
        "rejection_reason": rejection_reason,
        "failed_gate": failed_gate,
        "score_if_available": "0.75",
        "price_at_signal": "100.0",
        "market_weather": "",
        "published_status": "GHOST_ONLY",
        "reason_not_published": "",
        "outcome_5d": "",
        "outcome_10d": "",
        "outcome_20d": "",
        "outcome_30d": "",
        "max_favorable_move": "",
        "max_adverse_move": "",
        "setup_broke": "",
        "data_status": "PENDING",
        "created_at": "2026-06-01T00:00:00Z",
    }


# ─────────────────────────────────────────────────────────
# Source-only tests
# ─────────────────────────────────────────────────────────


class TestSafeConverters:
    def test_safe_float_valid(self):
        assert _safe_float("100.5") == 100.5
        assert _safe_float("0") == 0.0
        assert _safe_float("-1.5") == -1.5

    def test_safe_float_none(self):
        assert _safe_float(None) is None
        assert _safe_float("") is None

    def test_safe_float_invalid(self):
        assert _safe_float("not_a_number") is None

    def test_safe_bool_true(self):
        assert _safe_bool("True") is True
        assert _safe_bool("true") is True
        assert _safe_bool("1") is True
        assert _safe_bool(True) is True

    def test_safe_bool_false(self):
        assert _safe_bool("False") is False
        assert _safe_bool("false") is False
        assert _safe_bool("0") is False
        assert _safe_bool(False) is False

    def test_safe_bool_none(self):
        assert _safe_bool(None) is None
        assert _safe_bool("") is None


class TestValidateLedgers:
    def test_valid_state_passes(self):
        """7 resolved, 0 pending, no dupes, no broker flags."""
        obs = [_make_obs_row(f"id{i:03d}", f"SYM{i}", outcome_status="PENDING") for i in range(7)]
        out = [_make_out_row(f"id{i:03d}", f"SYM{i}", outcome_status="RESOLVED") for i in range(7)]
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(81)]
        errors = validate_ledgers(obs, out, ghost)
        assert errors == []

    def test_wrong_observation_count_fails(self):
        obs = [_make_obs_row(f"id{i:03d}", f"SYM{i}") for i in range(8)]
        out = [_make_out_row(f"id{i:03d}", f"SYM{i}") for i in range(8)]
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(81)]
        errors = validate_ledgers(obs, out, ghost)
        assert any("count" in e.lower() for e in errors)

    def test_mismatched_outcome_rows_fails(self):
        obs = [_make_obs_row(f"id{i:03d}", f"SYM{i}") for i in range(7)]
        out = [_make_out_row(f"id{i:03d}", f"SYM{i}") for i in range(6)]  # missing one
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(81)]
        errors = validate_ledgers(obs, out, ghost)
        assert any("outcome rows" in e.lower() for e in errors)

    def test_duplicate_observation_ids_fails(self):
        obs = [_make_obs_row("same_id", f"SYM{i}") for i in range(7)]
        out = [_make_out_row("same_id", f"SYM{i}") for i in range(7)]
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(81)]
        errors = validate_ledgers(obs, out, ghost)
        assert any("duplicate" in e.lower() for e in errors)

    def test_sent_to_broker_true_fails(self):
        obs = [_make_obs_row(f"id{i:03d}", f"SYM{i}", sent_to_broker="True") for i in range(7)]
        out = [_make_out_row(f"id{i:03d}", f"SYM{i}") for i in range(7)]
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(81)]
        errors = validate_ledgers(obs, out, ghost)
        assert any("sent_to_broker" in e.lower() for e in errors)

    def test_broker_order_id_populated_fails(self):
        obs = [_make_obs_row(f"id{i:03d}", f"SYM{i}", broker_order_id="ord_12345") for i in range(7)]
        out = [_make_out_row(f"id{i:03d}", f"SYM{i}") for i in range(7)]
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(81)]
        errors = validate_ledgers(obs, out, ghost)
        assert any("broker_order_id" in e.lower() for e in errors)

    def test_observation_outcome_id_mismatch_fails(self):
        obs = [_make_obs_row(f"id{i:03d}", f"SYM{i}") for i in range(7)]
        out = [_make_out_row(f"different_id{i:03d}", f"SYM{i}") for i in range(7)]
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(81)]
        errors = validate_ledgers(obs, out, ghost)
        assert any("observation but not outcome" in e.lower() or "outcome but not observation" in e.lower() for e in errors)

    def test_ghost_rows_below_minimum_fails(self):
        obs = [_make_obs_row(f"id{i:03d}", f"SYM{i}") for i in range(7)]
        out = [_make_out_row(f"id{i:03d}", f"SYM{i}") for i in range(7)]
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(5)]  # only 5
        errors = validate_ledgers(obs, out, ghost)
        assert any("ghost" in e.lower() for e in errors)

    def test_unresolved_rows_cause_pending_failure(self):
        obs = [_make_obs_row(f"id{i:03d}", f"SYM{i}") for i in range(7)]
        out = [_make_out_row(f"id{i:03d}", f"SYM{i}", outcome_status="PENDING") for i in range(7)]
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(81)]
        errors = validate_ledgers(obs, out, ghost)
        assert any("pending" in e.lower() for e in errors)


class TestBuildSetupCards:
    def test_7_observations_produce_7_cards(self):
        obs = [_make_obs_row(f"id{i:03d}", f"SYM{i}") for i in range(7)]
        cards = build_setup_cards(obs)
        assert len(cards) == 7

    def test_card_has_correct_fields(self):
        obs = [_make_obs_row("abc123", "TEST")]
        cards = build_setup_cards(obs)
        card = cards[0]
        assert card.observation_id == "abc123"
        assert card.symbol == "TEST"
        assert card.signal_close == 100.0
        assert card.lineage == "test_lineage"
        assert card.status == "PENDING"

    def test_empty_input_produces_empty_output(self):
        cards = build_setup_cards([])
        assert cards == []


class TestBuildGhostRejections:
    def test_81_ghost_rows_produce_81_records(self):
        ghost = [_make_ghost_row(f"ghost{i:03d}") for i in range(81)]
        rejections = build_ghost_rejections(ghost, "audit_run_001")
        assert len(rejections) == 81

    def test_empty_ghost_id_skipped(self):
        ghost = [_make_ghost_row("")]  # empty ghost_id
        rejections = build_ghost_rejections(ghost, "audit_run_001")
        assert len(rejections) == 0

    def test_rejection_has_correct_fields(self):
        ghost = [_make_ghost_row("ghost001", "TEST", rejection_reason="20d_momentum_too_weak")]
        rejections = build_ghost_rejections(ghost, "audit_run_001")
        r = rejections[0]
        assert r.ghost_id == "ghost001"
        assert r.symbol == "TEST"
        assert r.rejection_reason == "20d_momentum_too_weak"
        assert r.lineage == "test_lineage"


class TestBuildMaturityResults:
    def test_7_outcomes_produce_7_results(self):
        out = [_make_out_row(f"id{i:03d}", f"SYM{i}") for i in range(7)]
        # Empty drift/econ maps — data comes from outcome ledger
        results = build_maturity_results(out, {}, {})
        assert len(results) == 7

    def test_result_has_drift_data_when_available(self):
        out = [_make_out_row("abc123", "TEST")]
        drift_map = {
            "abc123": {
                "observation_id": "abc123",
                "symbol": "TEST",
                "SPY_forward_return": 0.02,
                "QQQ_forward_return": 0.03,
                "benchmark_relative_return": 0.07,
                "drift_attribution_label": "Independent Strength",
            }
        }
        econ_map = {
            "abc123": {
                "observation_id": "abc123",
                "cost_adjusted_return": 0.09,
                "delay_adjusted_return": 0.095,
                "economic_sanity_status": "pass",
                "concurrent_exposure_warning": True,
            }
        }
        results = build_maturity_results(out, drift_map, econ_map)
        r = results[0]
        assert r.spy_return == 0.02
        assert r.qqq_return == 0.03
        assert r.drift_label == "Independent Strength"
        assert r.cost_adjusted_return == 0.09
        assert r.concurrent_exposure_warning is True


class TestFormatJsonl:
    def test_produces_valid_json_per_line(self):
        from src.reporting.output_store_schema import (
            GhostRejection,
            MaturityResult,
            SetupCard,
            SystemRun,
        )
        cards = [
            SetupCard(
                observation_id="abc123",
                symbol="TEST",
                signal_date="2026-06-01T00:00:00Z",
                signal_close=100.0,
                setup_label="Research Observation",
                lineage="test_lineage",
            )
        ]
        results = [
            MaturityResult(
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
        ]
        ghosts = [
            GhostRejection(
                ghost_id="ghost001",
                symbol="TEST",
                rejection_date="2026-06-01T00:00:00Z",
                rejection_reason="20d_momentum_too_weak",
                failed_gate="ret_20d_rank",
                lineage="test_lineage",
            )
        ]
        run = SystemRun(run_id="test_run", run_type="export", status="completed")
        output = format_jsonl(cards, results, [], ghosts, run)
        lines = [l for l in output.strip().split("\n") if l.strip()]
        assert len(lines) == 4  # card + result + ghost + system_run
        for line in lines:
            parsed = json.loads(line)
            assert "table" in parsed
            assert "data" in parsed

    def test_no_sent_to_broker_in_jsonl(self):
        from src.reporting.output_store_schema import SetupCard, MaturityResult, SystemRun
        cards = [
            SetupCard(
                observation_id="abc123",
                symbol="TEST",
                signal_date="2026-06-01T00:00:00Z",
                signal_close=100.0,
                setup_label="Research Observation",
                lineage="test_lineage",
            )
        ]
        results: list = []
        ghosts: list = []
        run = SystemRun(run_id="test_run", run_type="export", status="completed")
        output = format_jsonl(cards, results, [], ghosts, run)
        assert "sent_to_broker" not in output.lower()
        assert "broker_order_id" not in output.lower()


# ─────────────────────────────────────────────────────────
# Data-backed tests (requires_data)
# ─────────────────────────────────────────────────────────


class TestExportWithProductionLedgers:
    """Validate export against real production ledgers. Marked requires_data."""

    def test_7_observation_export_produces_7_maturity_rows(self):
        """End-to-end: export runs and produces 7 maturity rows."""
        import subprocess
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [
                root / ".venv" / "bin" / "python3",
                str(root / "scripts" / "export_strategy_factory_outputs.py"),
                "--format", "jsonl",
                "--root", str(root),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": str(root)},
        )
        assert result.returncode == 0, f"Export failed: {result.stderr[:500]}"
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        # Should have: 7 cards + 7 results + 7 audits + N ghosts + 1 system_run
        maturity_lines = [l for l in lines if '"table": "maturity_results"' in l]
        assert len(maturity_lines) == 7

    def test_export_has_no_duplicate_observation_ids(self):
        import subprocess
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [
                root / ".venv" / "bin" / "python3",
                str(root / "scripts" / "export_strategy_factory_outputs.py"),
                "--format", "jsonl",
                "--root", str(root),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": str(root)},
        )
        assert result.returncode == 0
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        maturity_lines = [l for l in lines if '"table": "maturity_results"' in l]
        obs_ids = [json.loads(l)["data"]["observation_id"] for l in maturity_lines]
        assert len(obs_ids) == len(set(obs_ids)), f"Duplicates: {len(obs_ids) - len(set(obs_ids))}"

    def test_export_does_not_mutate_ledgers(self):
        """Running export leaves ledger hashes unchanged."""
        import hashlib
        import subprocess
        root = Path(__file__).resolve().parents[2]
        obs_path = root / "data" / "paper_observation" / "relative_strength_continuation_observation_ledger.csv"
        out_path = root / "data" / "paper_observation" / "relative_strength_continuation_outcome_ledger.csv"
        ghost_path = root / "data" / "trust_calibration" / "ghost_ledger.csv"

        h1 = hashlib.sha256(obs_path.read_bytes()).hexdigest()
        h2 = hashlib.sha256(out_path.read_bytes()).hexdigest()
        h3 = hashlib.sha256(ghost_path.read_bytes()).hexdigest()

        subprocess.run(
            [
                root / ".venv" / "bin" / "python3",
                str(root / "scripts" / "export_strategy_factory_outputs.py"),
                "--format", "jsonl",
                "--root", str(root),
            ],
            capture_output=True,
            timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": str(root)},
        )

        assert hashlib.sha256(obs_path.read_bytes()).hexdigest() == h1
        assert hashlib.sha256(out_path.read_bytes()).hexdigest() == h2
        assert hashlib.sha256(ghost_path.read_bytes()).hexdigest() == h3

    def test_ghost_export_handles_87_plus_rows(self):
        import subprocess
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [
                root / ".venv" / "bin" / "python3",
                str(root / "scripts" / "export_strategy_factory_outputs.py"),
                "--format", "jsonl",
                "--root", str(root),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": str(root)},
        )
        assert result.returncode == 0
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        ghost_lines = [l for l in lines if '"table": "ghost_rejections"' in l]
        assert len(ghost_lines) >= 80

    def test_sql_export_produces_valid_dml(self):
        import subprocess
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [
                root / ".venv" / "bin" / "python3",
                str(root / "scripts" / "export_strategy_factory_outputs.py"),
                "--format", "sql",
                "--root", str(root),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": str(root)},
        )
        assert result.returncode == 0
        output = result.stdout
        assert "BEGIN;" in output
        assert "COMMIT;" in output
        assert "INSERT INTO setup_cards" in output
        assert "INSERT INTO maturity_results" in output
        assert "INSERT INTO edge_audit_results" in output
        assert "INSERT INTO ghost_rejections" in output
        assert "INSERT INTO system_runs" in output
        assert "ON CONFLICT" in output