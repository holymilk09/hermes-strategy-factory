#!/usr/bin/env python3
"""Export Strategy Factory outputs to database-ready format.

Reads CSV ledgers and latest edge audit JSON. Produces JSONL or SQL INSERT
file. Default: DRY-RUN (no live database writes). CSV ledgers remain the
source of truth.

Usage:
    PYTHONPATH=/opt/data python3 scripts/export_strategy_factory_outputs.py
    PYTHONPATH=/opt/data python3 scripts/export_strategy_factory_outputs.py --format sql
    PYTHONPATH=/opt/data python3 scripts/export_strategy_factory_outputs.py --live-db  # FUTURE
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_short(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:8]


def _safe_float(val: Any) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _safe_bool(val: Any) -> bool | None:
    if val is None or val == "":
        return None
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no"):
        return False
    return None


def _run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{ts}_{_sha256_short(ts)}"


# ─────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────


class ExportValidationError(Exception):
    """Fail-closed: export aborts on any validation failure."""


def validate_ledgers(
    obs_rows: list[dict[str, str]],
    out_rows: list[dict[str, str]],
    ghost_rows: list[dict[str, str]],
) -> list[str]:
    """Run all integrity checks. Returns list of error messages (empty = pass)."""
    errors: list[str] = []

    # 1. Observation count
    obs_count = len(obs_rows)
    if obs_count != EXPECTED_OBSERVATION_COUNT:
        errors.append(
            f"Observation count {obs_count} != expected {EXPECTED_OBSERVATION_COUNT}"
        )

    # 2. Outcome rows match observations
    out_count = len(out_rows)
    if out_count != obs_count:
        errors.append(
            f"Outcome rows ({out_count}) != observation rows ({obs_count})"
        )

    # 3. Resolved count
    resolved = [r for r in out_rows if r.get("outcome_status", "").strip() == "RESOLVED"]
    pending = [r for r in out_rows if r.get("outcome_status", "").strip() != "RESOLVED"]
    if len(resolved) != EXPECTED_RESOLVED_COUNT:
        errors.append(
            f"Resolved count {len(resolved)} != expected {EXPECTED_RESOLVED_COUNT}"
        )
    if len(pending) != EXPECTED_PENDING_COUNT:
        errors.append(
            f"Pending count {len(pending)} != expected {EXPECTED_PENDING_COUNT}"
        )

    # 4. No duplicate observation IDs
    obs_ids = [r["observation_id"] for r in obs_rows]
    if len(obs_ids) != len(set(obs_ids)):
        import collections
        dupes = [oid for oid, count in collections.Counter(obs_ids).items() if count > 1]
        errors.append(f"Duplicate observation IDs: {dupes}")

    # 5. Observation IDs match between ledgers
    obs_id_set = set(obs_ids)
    out_id_set = {r["observation_id"] for r in out_rows}
    if obs_id_set != out_id_set:
        only_obs = obs_id_set - out_id_set
        only_out = out_id_set - obs_id_set
        if only_obs:
            errors.append(f"In observation but not outcome: {only_obs}")
        if only_out:
            errors.append(f"In outcome but not observation: {only_out}")

    # 6. No broker fields populated
    for row in obs_rows:
        if row.get("sent_to_broker", "").strip().lower() == "true":
            errors.append(
                f"sent_to_broker=True on {row.get('observation_id', '?')}"
            )
            break
    for row in obs_rows:
        bid = row.get("broker_order_id", "").strip()
        if bid:
            errors.append(
                f"broker_order_id populated: {bid} on {row.get('observation_id', '?')}"
            )
            break

    # 7. Ghost ledger has minimum expected rows
    ghost_count = len(ghost_rows)
    if ghost_count < EXPECTED_GHOST_MIN_COUNT:
        errors.append(
            f"Ghost rows {ghost_count} < expected minimum {EXPECTED_GHOST_MIN_COUNT}"
        )

    return errors


# ─────────────────────────────────────────────────────────
# Build export records from CSVs + edge audit JSON
# ─────────────────────────────────────────────────────────


def build_setup_cards(
    obs_rows: list[dict[str, str]],
) -> list[SetupCard]:
    """Convert observation ledger rows to SetupCard records."""
    cards: list[SetupCard] = []
    for row in obs_rows:
        obs_id = row["observation_id"].strip()
        symbol = row["symbol"].strip()
        signal_date_str = row.get("signal_timestamp", "").strip()
        signal_close = _safe_float(row.get("signal_close")) or 0.0
        lineage = row.get("lineage", "").strip()
        strategy = row.get("strategy", "").strip() or "relative_strength_continuation"
        status = row.get("outcome_status", "PENDING").strip()
        maturity_window = int(row.get("outcome_window", "10") or 10)
        ret_5d = _safe_float(row.get("ret_5d"))
        ret_20d = _safe_float(row.get("ret_20d"))
        ret_60d = _safe_float(row.get("ret_60d"))
        ret_20d_rank = _safe_float(row.get("ret_20d_rank"))
        ret_60d_rank = _safe_float(row.get("ret_60d_rank"))
        close_above_ma50 = _safe_bool(row.get("close_above_ma50"))

        # Derive setup_label from plain-English convention
        setup_label = "Research Observation"

        card = SetupCard(
            observation_id=obs_id,
            symbol=symbol,
            signal_date=signal_date_str,
            signal_close=signal_close,
            setup_label=setup_label,
            lineage=lineage,
            strategy=strategy,
            status=status,
            maturity_bars=0,  # computed at read time if needed
            maturity_window=maturity_window,
            ret_5d=ret_5d,
            ret_20d=ret_20d,
            ret_60d=ret_60d,
            ret_20d_rank=ret_20d_rank,
            ret_60d_rank=ret_60d_rank,
            close_above_ma50=close_above_ma50,
        )
        cards.append(card)
    return cards


def build_maturity_results(
    out_rows: list[dict[str, str]],
    drift_map: dict[str, dict[str, Any]],
    econ_map: dict[str, dict[str, Any]],
) -> list[MaturityResult]:
    """Combine outcome ledger + edge audit for MaturityResult records."""
    results: list[MaturityResult] = []
    for row in out_rows:
        obs_id = row["observation_id"].strip()
        symbol = row["symbol"].strip()
        signal_date_str = row.get("signal_timestamp", "").strip()
        outcome_date_str = row.get("outcome_timestamp", "").strip() or None
        signal_close = _safe_float(row.get("signal_close")) or 0.0
        outcome_close = _safe_float(row.get("outcome_close"))
        raw_return = _safe_float(row.get("outcome_return"))
        outcome_status = row.get("outcome_status", "PENDING").strip()

        # Drift attribution data
        drift = drift_map.get(obs_id, {})
        spy_ret = _safe_float(drift.get("SPY_forward_return"))
        qqq_ret = _safe_float(drift.get("QQQ_forward_return"))
        bmr = _safe_float(drift.get("benchmark_relative_return"))
        drift_label = drift.get("drift_attribution_label")

        # Economic sanity data
        econ = econ_map.get(obs_id, {})
        cost_adj = _safe_float(econ.get("cost_adjusted_return"))
        delay_adj = _safe_float(econ.get("delay_adjusted_return"))
        econ_status = econ.get("economic_sanity_status")
        concurrent_warn = bool(econ.get("concurrent_exposure_warning"))

        result = MaturityResult(
            observation_id=obs_id,
            symbol=symbol,
            signal_date=signal_date_str,
            outcome_date=outcome_date_str,
            signal_close=signal_close,
            outcome_close=outcome_close,
            raw_return=raw_return,
            spy_return=spy_ret,
            qqq_return=qqq_ret,
            benchmark_relative_return=bmr,
            cost_adjusted_return=cost_adj,
            delay_adjusted_return=delay_adj,
            drift_label=drift_label,
            sample_size_warning=True,  # n=7 < 30
            concurrent_exposure_warning=concurrent_warn,
            economic_sanity_status=econ_status,
            outcome_status=outcome_status,
        )
        results.append(result)
    return results


def build_edge_audit_results(
    drift_map: dict[str, dict[str, Any]],
    econ_map: dict[str, dict[str, Any]],
    audit_run_id: str,
) -> list[EdgeAuditResult]:
    """Build EdgeAuditResult records from drift + economic sanity detail."""
    results: list[EdgeAuditResult] = []
    all_ids = set(drift_map.keys()) | set(econ_map.keys())

    for obs_id in sorted(all_ids):
        drift = drift_map.get(obs_id, {})
        econ = econ_map.get(obs_id, {})

        symbol = drift.get("symbol", econ.get("symbol", ""))
        drift_label = drift.get("drift_attribution_label")
        econ_status = econ.get("economic_sanity_status")
        stock_ret = _safe_float(drift.get("stock_forward_return"))
        spy_ret = _safe_float(drift.get("SPY_forward_return"))
        qqq_ret = _safe_float(drift.get("QQQ_forward_return"))
        cost_adj = _safe_float(econ.get("cost_adjusted_return"))
        delay_adj = _safe_float(econ.get("delay_adjusted_return"))
        comp_warn = bool(econ.get("compounding_artifact_warning"))
        conc_warn = bool(econ.get("concurrent_exposure_warning"))

        # Derive cost/delay status from economic sanity
        cost_status = "cost_fragile" if (cost_adj is not None and cost_adj < 0) else \
                     "cost_resilient" if cost_adj is not None else "insufficient_data"
        delay_status = "delay_sensitive" if (delay_adj is not None and abs(delay_adj) > 0.05) else \
                       "delay_resilient" if delay_adj is not None else "insufficient_data"

        result = EdgeAuditResult(
            observation_id=obs_id,
            symbol=symbol,
            drift_label=drift_label,
            economic_sanity_status=econ_status,
            cost_status=cost_status,
            delay_status=delay_status,
            filter_lift_status="ghost_baseline_available",
            stock_forward_return=stock_ret,
            spy_forward_return=spy_ret,
            qqq_forward_return=qqq_ret,
            cost_adjusted_return=cost_adj,
            delay_adjusted_return=delay_adj,
            compounding_artifact_warning=comp_warn,
            concurrent_exposure_warning=conc_warn,
            audit_run_id=audit_run_id,
        )
        results.append(result)
    return results


def build_ghost_rejections(
    ghost_rows: list[dict[str, str]],
    audit_run_id: str,
) -> list[GhostRejection]:
    """Convert ghost ledger rows to GhostRejection records."""
    rejections: list[GhostRejection] = []
    for row in ghost_rows:
        ghost_id = row.get("ghost_id", "").strip()
        if not ghost_id:
            continue
        symbol = row.get("symbol", "").strip().upper()
        signal_date = row.get("signal_date", "").strip()
        rejection_reason = row.get("rejection_reason", "").strip()
        failed_gate = row.get("failed_gate", "").strip()
        strategy_id = row.get("strategy_id", "relative_strength_continuation").strip()
        setup_type = row.get("setup_type", "swing").strip()
        score_str = row.get("score_if_available", "").strip()
        price = _safe_float(row.get("price_at_signal")) or 0.0
        outcome_5d = row.get("outcome_5d", "").strip()
        outcome_10d = row.get("outcome_10d", "").strip()
        outcome_20d = row.get("outcome_20d", "").strip()
        max_fav = row.get("max_favorable_move", "").strip()
        max_adv = row.get("max_adverse_move", "").strip()
        setup_broke = row.get("setup_broke", "").strip()
        data_status = row.get("data_status", "PENDING").strip()

        rejection = GhostRejection(
            ghost_id=ghost_id,
            symbol=symbol,
            rejection_date=signal_date,
            rejection_reason=rejection_reason,
            failed_gate=failed_gate,
            lineage=strategy_id,  # strategy_id serves as lineage identifier
            strategy_id=strategy_id,
            setup_type=setup_type,
            score_if_available=score_str,
            price_at_signal=price,
            outcome_5d=outcome_5d,
            outcome_10d=outcome_10d,
            outcome_20d=outcome_20d,
            max_favorable_move=max_fav,
            max_adverse_move=max_adv,
            setup_broke=setup_broke,
            data_status=data_status,
            audit_run_id=audit_run_id,
        )
        rejections.append(rejection)
    return rejections


# ─────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise ExportValidationError(f"Ledger missing: {path}")
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def load_edge_audit(root: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Load latest edge audit. Returns (drift_map, econ_map, audit_date)."""
    audit_dir = root / "reports" / "edge_audit"
    if not audit_dir.exists():
        raise ExportValidationError("No edge audit reports found")

    # Find latest audit
    json_files = sorted(audit_dir.glob("*_edge_audit.json"), reverse=True)
    if not json_files:
        raise ExportValidationError("No edge audit JSON found")
    latest = json_files[0]

    with latest.open() as f:
        audit = json.load(f)

    audit_date = audit.get("report_date", "")

    # Build drift map: observation_id → drift detail
    drift_map: dict[str, dict[str, Any]] = {}
    drift_data = audit.get("drift_attribution", {}).get("label_breakdown", [])
    for entry in drift_data:
        oid = entry.get("observation_id")
        if oid:
            drift_map[oid] = entry

    # Build econ map: observation_id → economic sanity detail
    econ_map: dict[str, dict[str, Any]] = {}
    econ_data = audit.get("economic_sanity", {}).get("detailed_metrics", [])
    for entry in econ_data:
        oid = entry.get("observation_id")
        if oid:
            econ_map[oid] = entry

    return drift_map, econ_map, audit_date


# ─────────────────────────────────────────────────────────
# Output formatters
# ─────────────────────────────────────────────────────────


def format_jsonl(
    cards: list[SetupCard],
    results: list[MaturityResult],
    audits: list[EdgeAuditResult],
    ghosts: list[GhostRejection],
    run_rec: SystemRun,
) -> str:
    """Produce JSONL with one line per record, prefixed by table name."""
    lines: list[str] = []
    for c in cards:
        lines.append(json.dumps({"table": "setup_cards", "data": c.to_dict()}))
    for r in results:
        lines.append(json.dumps({"table": "maturity_results", "data": r.to_dict()}))
    for a in audits:
        lines.append(json.dumps({"table": "edge_audit_results", "data": a.to_dict()}))
    for g in ghosts:
        lines.append(json.dumps({"table": "ghost_rejections", "data": g.to_dict()}))
    lines.append(json.dumps({"table": "system_runs", "data": run_rec.to_dict()}))
    return "\n".join(lines) + "\n"


def format_sql_inserts(
    cards: list[SetupCard],
    results: list[MaturityResult],
    audits: list[EdgeAuditResult],
    ghosts: list[GhostRejection],
    run_rec: SystemRun,
) -> str:
    """Produce PostgreSQL INSERT statements with ON CONFLICT DO NOTHING."""
    out: list[str] = []
    out.append("-- Strategy Factory Export — generated " + _now_iso())
    out.append("BEGIN;\n")

    # setup_cards
    for c in cards:
        d = c.to_dict()
        out.append(
            "INSERT INTO setup_cards (observation_id, symbol, signal_date, signal_close, "
            "setup_label, lineage, strategy, status, maturity_bars, maturity_window, "
            "ret_5d, ret_20d, ret_60d, ret_20d_rank, ret_60d_rank, close_above_ma50) "
            "VALUES ("
            f"{_sql_str(d['observation_id'])}, {_sql_str(d['symbol'])}, "
            f"{_sql_str(d['signal_date'])}::timestamptz, {d['signal_close']}, "
            f"{_sql_str(d['setup_label'])}, {_sql_str(d['lineage'])}, "
            f"{_sql_str(d['strategy'])}, {_sql_str(d['status'])}, "
            f"{d['maturity_bars']}, {d['maturity_window']}, "
            f"{_sql_num(d['ret_5d'])}, {_sql_num(d['ret_20d'])}, {_sql_num(d['ret_60d'])}, "
            f"{_sql_num(d['ret_20d_rank'])}, {_sql_num(d['ret_60d_rank'])}, "
            f"{_sql_bool(d['close_above_ma50'])}"
            ") ON CONFLICT (observation_id) DO NOTHING;"
        )

    out.append("")

    # maturity_results
    for r in results:
        d = r.to_dict()
        out.append(
            "INSERT INTO maturity_results (observation_id, symbol, signal_date, outcome_date, "
            "signal_close, outcome_close, raw_return, spy_return, qqq_return, "
            "benchmark_relative_return, cost_adjusted_return, delay_adjusted_return, "
            "drift_label, sample_size_warning, concurrent_exposure_warning, "
            "economic_sanity_status, outcome_status) "
            "VALUES ("
            f"{_sql_str(d['observation_id'])}, {_sql_str(d['symbol'])}, "
            f"{_sql_str(d['signal_date'])}::timestamptz, {_sql_str(d['outcome_date'])}::timestamptz, "
            f"{d['signal_close']}, {_sql_num(d['outcome_close'])}, "
            f"{_sql_num(d['raw_return'])}, {_sql_num(d['spy_return'])}, {_sql_num(d['qqq_return'])}, "
            f"{_sql_num(d['benchmark_relative_return'])}, {_sql_num(d['cost_adjusted_return'])}, "
            f"{_sql_num(d['delay_adjusted_return'])}, "
            f"{_sql_str(d['drift_label'])}, {_sql_bool(d['sample_size_warning'])}, "
            f"{_sql_bool(d['concurrent_exposure_warning'])}, "
            f"{_sql_str(d['economic_sanity_status'])}, {_sql_str(d['outcome_status'])}"
            ") ON CONFLICT (observation_id) DO NOTHING;"
        )

    out.append("")

    # edge_audit_results
    for a in audits:
        d = a.to_dict()
        out.append(
            "INSERT INTO edge_audit_results (observation_id, symbol, drift_label, "
            "economic_sanity_status, cost_status, delay_status, filter_lift_status, "
            "stock_forward_return, spy_forward_return, qqq_forward_return, "
            "cost_adjusted_return, delay_adjusted_return, "
            "compounding_artifact_warning, concurrent_exposure_warning, audit_run_id) "
            "VALUES ("
            f"{_sql_str(d['observation_id'])}, {_sql_str(d['symbol'])}, "
            f"{_sql_str(d['drift_label'])}, {_sql_str(d['economic_sanity_status'])}, "
            f"{_sql_str(d['cost_status'])}, {_sql_str(d['delay_status'])}, "
            f"{_sql_str(d['filter_lift_status'])}, "
            f"{_sql_num(d['stock_forward_return'])}, {_sql_num(d['spy_forward_return'])}, "
            f"{_sql_num(d['qqq_forward_return'])}, {_sql_num(d['cost_adjusted_return'])}, "
            f"{_sql_num(d['delay_adjusted_return'])}, "
            f"{_sql_bool(d['compounding_artifact_warning'])}, "
            f"{_sql_bool(d['concurrent_exposure_warning'])}, "
            f"{_sql_str(d['audit_run_id'])}"
            ") ON CONFLICT (observation_id, audit_run_id) DO NOTHING;"
        )

    out.append("")

    # ghost_rejections
    for g in ghosts:
        d = g.to_dict()
        out.append(
            "INSERT INTO ghost_rejections (ghost_id, symbol, rejection_date, "
            "rejection_reason, failed_gate, lineage, strategy_id, setup_type, "
            "score_if_available, price_at_signal, outcome_5d, outcome_10d, outcome_20d, "
            "max_favorable_move, max_adverse_move, setup_broke, data_status, audit_run_id) "
            "VALUES ("
            f"{_sql_str(d['ghost_id'])}, {_sql_str(d['symbol'])}, "
            f"{_sql_str(d['rejection_date'])}::timestamptz, "
            f"{_sql_str(d['rejection_reason'])}, {_sql_str(d['failed_gate'])}, "
            f"{_sql_str(d['lineage'])}, {_sql_str(d['strategy_id'])}, "
            f"{_sql_str(d['setup_type'])}, {_sql_str(d['score_if_available'])}, "
            f"{d['price_at_signal']}, "
            f"{_sql_str(d['outcome_5d'])}, {_sql_str(d['outcome_10d'])}, "
            f"{_sql_str(d['outcome_20d'])}, "
            f"{_sql_str(d['max_favorable_move'])}, {_sql_str(d['max_adverse_move'])}, "
            f"{_sql_str(d['setup_broke'])}, {_sql_str(d['data_status'])}, "
            f"{_sql_str(d['audit_run_id'])}"
            ") ON CONFLICT (ghost_id) DO NOTHING;"
        )

    out.append("")

    # system_runs
    d = run_rec.to_dict()
    errors_json = json.dumps(d["validation_errors"])
    out.append(
        "INSERT INTO system_runs (run_id, run_type, status, ledgers_source, "
        "observation_count, resolved_count, pending_count, ghost_count, "
        "edge_audit_date, export_rows_written, validation_passed, validation_errors, "
        "ledger_hash_observation, ledger_hash_outcome, ledger_hash_ghost, "
        "started_at, completed_at) "
        "VALUES ("
        f"{_sql_str(d['run_id'])}, {_sql_str(d['run_type'])}, {_sql_str(d['status'])}, "
        f"{_sql_str(d['ledgers_source'])}, {d['observation_count']}, {d['resolved_count']}, "
        f"{d['pending_count']}, {d['ghost_count']}, {_sql_str(d['edge_audit_date'])}, "
        f"{d['export_rows_written']}, {_sql_bool(d['validation_passed'])}, "
        f"'{errors_json}'::jsonb, "
        f"{_sql_str(d['ledger_hash_observation'])}, {_sql_str(d['ledger_hash_outcome'])}, "
        f"{_sql_str(d['ledger_hash_ghost'])}, "
        f"{_sql_str(d['started_at'])}::timestamptz, {_sql_str(d['completed_at'])}::timestamptz"
        ") ON CONFLICT (run_id) DO NOTHING;"
    )

    out.append("\nCOMMIT;")
    return "\n".join(out) + "\n"


def _sql_str(val: Any) -> str:
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def _sql_num(val: Any) -> str:
    if val is None:
        return "NULL"
    return str(val)


def _sql_bool(val: Any) -> str:
    if val is None:
        return "NULL"
    return "TRUE" if val else "FALSE"


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export Strategy Factory outputs to database-ready format."
    )
    parser.add_argument(
        "--format", choices=["jsonl", "sql"], default="jsonl",
        help="Output format (default: jsonl)"
    )
    parser.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--live-db", action="store_true", default=False,
        help="Write to live database (NOT YET IMPLEMENTED — requires Supabase credentials)"
    )
    parser.add_argument(
        "--root", type=Path, default=ROOT,
        help="Project root directory"
    )
    args = parser.parse_args()

    root: Path = args.root
    run_id = _run_id()
    errors: list[str] = []

    # --- Load ledgers ---
    obs_path = root / "data" / "paper_observation" / "relative_strength_continuation_observation_ledger.csv"
    out_path = root / "data" / "paper_observation" / "relative_strength_continuation_outcome_ledger.csv"
    ghost_path = root / "data" / "trust_calibration" / "ghost_ledger.csv"

    try:
        obs_rows = load_csv(obs_path)
        out_rows = load_csv(out_path)
        ghost_rows = load_csv(ghost_path)
    except ExportValidationError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 1

    # --- Validate ---
    validation_errors = validate_ledgers(obs_rows, out_rows, ghost_rows)
    if validation_errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for err in validation_errors:
            print(f"  - {err}", file=sys.stderr)
        # Fail closed — do not produce export
        run_rec = SystemRun(
            run_id=run_id,
            run_type="export",
            status="failed",
            observation_count=len(obs_rows),
            resolved_count=sum(1 for r in out_rows if r.get("outcome_status") == "RESOLVED"),
            pending_count=sum(1 for r in out_rows if r.get("outcome_status") != "RESOLVED"),
            ghost_count=len(ghost_rows),
            validation_passed=False,
            validation_errors=validation_errors,
        )
        # Still write the run record for auditing
        if args.format == "sql":
            print(format_sql_inserts([], [], [], [], run_rec))
        else:
            print(json.dumps({"table": "system_runs", "data": run_rec.to_dict()}))
        return 1

    # --- Compute hashes ---
    def _hash_file(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    ledger_hash_obs = _hash_file(obs_path)
    ledger_hash_out = _hash_file(out_path)
    ledger_hash_ghost = _hash_file(ghost_path)

    # --- Load edge audit ---
    try:
        drift_map, econ_map, audit_date = load_edge_audit(root)
    except ExportValidationError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 1

    # Build export records
    cards = build_setup_cards(obs_rows)
    results = build_maturity_results(out_rows, drift_map, econ_map)
    audits = build_edge_audit_results(drift_map, econ_map, run_id)
    ghosts = build_ghost_rejections(ghost_rows, run_id)

    # Compute maturity_bars from outcome date and rebuild cards
    from datetime import datetime as dt
    rebuilt_cards: list[SetupCard] = []
    for card in cards:
        maturity_bars = 0
        for result in results:
            if result.observation_id == card.observation_id and result.outcome_date:
                try:
                    sig_dt = dt.fromisoformat(card.signal_date.replace("Z", "+00:00"))
                    out_dt = dt.fromisoformat(str(result.outcome_date).replace("Z", "+00:00"))
                    maturity_bars = max((out_dt - sig_dt).days, 0)
                except Exception:
                    pass
                break
        rebuilt_cards.append(SetupCard(
            observation_id=card.observation_id,
            symbol=card.symbol,
            signal_date=card.signal_date,
            signal_close=card.signal_close,
            setup_label=card.setup_label,
            lineage=card.lineage,
            strategy=card.strategy,
            status=card.status,
            maturity_bars=maturity_bars,
            maturity_window=card.maturity_window,
            ret_5d=card.ret_5d,
            ret_20d=card.ret_20d,
            ret_60d=card.ret_60d,
            ret_20d_rank=card.ret_20d_rank,
            ret_60d_rank=card.ret_60d_rank,
            close_above_ma50=card.close_above_ma50,
        ))
    cards = rebuilt_cards

    total_rows = len(cards) + len(results) + len(audits) + len(ghosts)

    run_rec = SystemRun(
        run_id=run_id,
        run_type="export",
        status="completed",
        observation_count=len(obs_rows),
        resolved_count=sum(1 for r in out_rows if r.get("outcome_status") == "RESOLVED"),
        pending_count=sum(1 for r in out_rows if r.get("outcome_status") != "RESOLVED"),
        ghost_count=len(ghost_rows),
        edge_audit_date=audit_date,
        export_rows_written=total_rows,
        validation_passed=True,
        validation_errors=[],
        ledger_hash_observation=ledger_hash_obs,
        ledger_hash_outcome=ledger_hash_out,
        ledger_hash_ghost=ledger_hash_ghost,
        completed_at=_now_iso(),
    )

    # --- Format output ---
    if args.live_db:
        print("ERROR: --live-db not yet implemented. Requires Supabase credentials.", file=sys.stderr)
        return 1

    if args.format == "sql":
        output_text = format_sql_inserts(cards, results, audits, ghosts, run_rec)
    else:
        output_text = format_jsonl(cards, results, audits, ghosts, run_rec)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_text, encoding="utf-8")
        print(f"Written: {args.output} ({len(output_text)} bytes)")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())