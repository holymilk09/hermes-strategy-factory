"""Output store schema — read-only PostgreSQL export layer.

CSV ledgers remain the source of truth. This module defines the
target schema that the exporter writes to. No live DB writes
unless explicitly configured (default: dry-run).

Phase 7B — Strategy Factory Production Readiness
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ─────────────────────────────────────────────────────────
# Table schemas as dataclass definitions
# ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SystemRun:
    run_id: str
    run_type: str
    status: str = "started"
    ledgers_source: str = "csv"
    observation_count: int | None = None
    resolved_count: int | None = None
    pending_count: int | None = None
    ghost_count: int | None = None
    edge_audit_date: str | None = None
    export_rows_written: int = 0
    validation_passed: bool | None = None
    validation_errors: list[str] = field(default_factory=list)
    ledger_hash_observation: str | None = None
    ledger_hash_outcome: str | None = None
    ledger_hash_ghost: str | None = None
    started_at: str = ""
    completed_at: str | None = None

    def __post_init__(self):
        if not self.started_at:
            object.__setattr__(self, "started_at", datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        d = {
            "run_id": self.run_id,
            "run_type": self.run_type,
            "status": self.status,
            "ledgers_source": self.ledgers_source,
            "observation_count": self.observation_count,
            "resolved_count": self.resolved_count,
            "pending_count": self.pending_count,
            "ghost_count": self.ghost_count,
            "edge_audit_date": self.edge_audit_date,
            "export_rows_written": self.export_rows_written,
            "validation_passed": self.validation_passed,
            "validation_errors": self.validation_errors,
            "ledger_hash_observation": self.ledger_hash_observation,
            "ledger_hash_outcome": self.ledger_hash_outcome,
            "ledger_hash_ghost": self.ledger_hash_ghost,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }
        d["validation_errors"] = list(self.validation_errors)
        return d


@dataclass(frozen=True)
class SetupCard:
    observation_id: str
    symbol: str
    signal_date: str
    signal_close: float
    setup_label: str
    lineage: str
    strategy: str = "relative_strength_continuation"
    status: str = "RESOLVED"
    maturity_bars: int = 0
    maturity_window: int = 10
    ret_5d: float | None = None
    ret_20d: float | None = None
    ret_60d: float | None = None
    ret_20d_rank: float | None = None
    ret_60d_rank: float | None = None
    close_above_ma50: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "symbol": self.symbol,
            "signal_date": self.signal_date,
            "signal_close": self.signal_close,
            "setup_label": self.setup_label,
            "lineage": self.lineage,
            "strategy": self.strategy,
            "status": self.status,
            "maturity_bars": self.maturity_bars,
            "maturity_window": self.maturity_window,
            "ret_5d": self.ret_5d,
            "ret_20d": self.ret_20d,
            "ret_60d": self.ret_60d,
            "ret_20d_rank": self.ret_20d_rank,
            "ret_60d_rank": self.ret_60d_rank,
            "close_above_ma50": self.close_above_ma50,
        }


@dataclass(frozen=True)
class MaturityResult:
    observation_id: str
    symbol: str
    signal_date: str
    outcome_date: str | None
    signal_close: float
    outcome_close: float | None
    raw_return: float | None
    spy_return: float | None
    qqq_return: float | None
    benchmark_relative_return: float | None
    cost_adjusted_return: float | None
    delay_adjusted_return: float | None
    drift_label: str | None
    sample_size_warning: bool = True
    concurrent_exposure_warning: bool = False
    economic_sanity_status: str | None = None
    outcome_status: str = "RESOLVED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "symbol": self.symbol,
            "signal_date": self.signal_date,
            "outcome_date": self.outcome_date,
            "signal_close": self.signal_close,
            "outcome_close": self.outcome_close,
            "raw_return": self.raw_return,
            "spy_return": self.spy_return,
            "qqq_return": self.qqq_return,
            "benchmark_relative_return": self.benchmark_relative_return,
            "cost_adjusted_return": self.cost_adjusted_return,
            "delay_adjusted_return": self.delay_adjusted_return,
            "drift_label": self.drift_label,
            "sample_size_warning": self.sample_size_warning,
            "concurrent_exposure_warning": self.concurrent_exposure_warning,
            "economic_sanity_status": self.economic_sanity_status,
            "outcome_status": self.outcome_status,
        }


@dataclass(frozen=True)
class EdgeAuditResult:
    observation_id: str
    symbol: str
    drift_label: str | None
    economic_sanity_status: str | None
    cost_status: str | None
    delay_status: str | None
    filter_lift_status: str | None
    stock_forward_return: float | None = None
    spy_forward_return: float | None = None
    qqq_forward_return: float | None = None
    cost_adjusted_return: float | None = None
    delay_adjusted_return: float | None = None
    compounding_artifact_warning: bool = False
    concurrent_exposure_warning: bool = False
    audit_run_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "symbol": self.symbol,
            "drift_label": self.drift_label,
            "economic_sanity_status": self.economic_sanity_status,
            "cost_status": self.cost_status,
            "delay_status": self.delay_status,
            "filter_lift_status": self.filter_lift_status,
            "stock_forward_return": self.stock_forward_return,
            "spy_forward_return": self.spy_forward_return,
            "qqq_forward_return": self.qqq_forward_return,
            "cost_adjusted_return": self.cost_adjusted_return,
            "delay_adjusted_return": self.delay_adjusted_return,
            "compounding_artifact_warning": self.compounding_artifact_warning,
            "concurrent_exposure_warning": self.concurrent_exposure_warning,
            "audit_run_id": self.audit_run_id,
        }


@dataclass(frozen=True)
class GhostRejection:
    ghost_id: str
    symbol: str
    rejection_date: str
    rejection_reason: str
    failed_gate: str
    lineage: str
    strategy_id: str = "relative_strength_continuation"
    setup_type: str = "swing"
    score_if_available: str = ""
    price_at_signal: float = 0.0
    outcome_5d: str = ""
    outcome_10d: str = ""
    outcome_20d: str = ""
    max_favorable_move: str = ""
    max_adverse_move: str = ""
    setup_broke: str = ""
    data_status: str = "PENDING"
    audit_run_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ghost_id": self.ghost_id,
            "symbol": self.symbol,
            "rejection_date": self.rejection_date,
            "rejection_reason": self.rejection_reason,
            "failed_gate": self.failed_gate,
            "lineage": self.lineage,
            "strategy_id": self.strategy_id,
            "setup_type": self.setup_type,
            "score_if_available": self.score_if_available,
            "price_at_signal": self.price_at_signal,
            "outcome_5d": self.outcome_5d,
            "outcome_10d": self.outcome_10d,
            "outcome_20d": self.outcome_20d,
            "max_favorable_move": self.max_favorable_move,
            "max_adverse_move": self.max_adverse_move,
            "setup_broke": self.setup_broke,
            "data_status": self.data_status,
            "audit_run_id": self.audit_run_id,
        }


@dataclass(frozen=True)
class ApprovedPublication:
    publication_date: str
    audit_run_id: str
    status: str = "generated"
    grade: str | None = None
    market_weather: str | None = None
    observations_count: int = 0
    resolved_count: int = 0
    pending_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "publication_date": self.publication_date,
            "audit_run_id": self.audit_run_id,
            "status": self.status,
            "grade": self.grade,
            "market_weather": self.market_weather,
            "observations_count": self.observations_count,
            "resolved_count": self.resolved_count,
            "pending_count": self.pending_count,
        }


# ─────────────────────────────────────────────────────────
# Required columns per table (for validation)
# ─────────────────────────────────────────────────────────

REQUIRED_COLUMNS: dict[str, set[str]] = {
    "setup_cards": {
        "observation_id", "symbol", "signal_date", "signal_close",
        "setup_label", "lineage", "strategy", "status",
        "maturity_bars", "maturity_window",
    },
    "maturity_results": {
        "observation_id", "symbol", "signal_date", "outcome_date",
        "signal_close", "outcome_close", "raw_return",
        "spy_return", "qqq_return", "benchmark_relative_return",
        "cost_adjusted_return", "delay_adjusted_return",
        "drift_label", "sample_size_warning", "concurrent_exposure_warning",
    },
    "edge_audit_results": {
        "observation_id", "symbol", "drift_label",
        "economic_sanity_status", "cost_status",
        "delay_status", "filter_lift_status",
    },
    "ghost_rejections": {
        "symbol", "rejection_date", "rejection_reason", "lineage", "audit_run_id",
    },
}

# Forbidden fields — must NOT be populated in any exported row
FORBIDDEN_FIELDS = {"sent_to_broker", "broker_order_id"}

# Expected approved counts (Phase 6L / Phase 6M baseline)
EXPECTED_OBSERVATION_COUNT = 13
EXPECTED_RESOLVED_COUNT = 7
EXPECTED_PENDING_COUNT = 6
EXPECTED_GHOST_MIN_COUNT = 80  # floor — ghost ledger grows over time