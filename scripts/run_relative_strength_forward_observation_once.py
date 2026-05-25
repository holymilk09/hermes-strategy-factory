from __future__ import annotations

from pathlib import Path

from src.paper.relative_strength_observation import (
    RelativeStrengthObservationConfig,
    append_observations_atomic,
    build_current_relative_strength_universe,
    build_observation_rows,
    latest_fresh_signals,
)

from src.reporting.ghost_ledger import record_observation_rejections

ROOT = Path(__file__).resolve().parents[1]
OBS_DIR = ROOT / "data" / "paper_observation"
REPORT_DIR = ROOT / "reports" / "strategy_factory"

OBS_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OBS_LEDGER = OBS_DIR / "relative_strength_continuation_observation_ledger.csv"
RUN_REPORT = REPORT_DIR / "relative_strength_forward_observation_run_report.md"
STATUS_REPORT = REPORT_DIR / "relative_strength_forward_observation_status.md"


def main() -> None:
    config = RelativeStrengthObservationConfig()

    universe = build_current_relative_strength_universe(ROOT, config)
    selected, freshness = latest_fresh_signals(universe, config=config)
    observations = build_observation_rows(selected, config)

    # Ghost recording: non-selected symbols at latest timestamp (observational only)
    RELATIVE_STRENGTH_GATES = [
        ("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return"),
        ("close_above_ma50", lambda v: v > 0.5, "close_above_ma50", "below_50ma"),
        ("ret_20d_rank", lambda v: v >= 0.85, "ret_20d_rank", "20d_momentum_too_weak"),
        ("ret_60d_rank", lambda v: v >= 0.70, "ret_60d_rank", "60d_momentum_too_weak"),
    ]
    ghost_count = record_observation_rejections(
        universe_df=universe,
        root=ROOT,
        strategy_id=config.strategy,
        setup_type="swing",
        gates=RELATIVE_STRENGTH_GATES,
    )

    append_result = append_observations_atomic(observations, OBS_LEDGER)

    if append_result["sent_to_broker_any"]:
        raise RuntimeError("Observation ledger violation: sent_to_broker=True detected")

    classification = (
        "FORWARD_OBSERVATION_ACTIVE"
        if freshness["fresh"] and len(observations) > 0
        else "FORWARD_OBSERVATION_READY_NO_SIGNALS"
        if freshness["fresh"]
        else "FORWARD_OBSERVATION_STALE_SOURCE"
    )

    report = []
    report.append("# Relative Strength Forward Observation Run Report")
    report.append("")
    report.append(f"classification: {classification}")
    report.append(f"observation_ledger: {OBS_LEDGER}")
    report.append("")
    report.append("## Freshness")
    for k, v in freshness.items():
        report.append(f"{k}: {v}")
    report.append("")
    report.append("## Observation")
    report.append(f"signals_written: {append_result['rows_written']}")
    report.append(f"total_observations: {append_result['total_rows']}")
    report.append("sent_to_broker_any: false")
    report.append("")
    report.append("Production: BLOCKED")
    report.append("Live: BLOCKED")
    report.append("Broker execution: DISABLED")
    report.append("Shadow orders: DISABLED")

    RUN_REPORT.write_text("\n".join(report), encoding="utf-8")

    status = []
    status.append("# Relative Strength Forward Observation Status")
    status.append("")
    status.append(f"classification: {classification}")
    status.append(f"latest_signal_ts: {freshness['latest_signal_ts']}")
    status.append(f"signal_age_days: {freshness['signal_age_days']}")
    status.append(f"latest_selected_rows: {freshness['latest_selected_rows']}")
    status.append(f"signals_written: {append_result['rows_written']}")
    status.append(f"total_observations: {append_result['total_rows']}")
    status.append("")
    status.append("Production: BLOCKED")
    status.append("Live: BLOCKED")
    status.append("Broker execution: DISABLED")
    status.append("Shadow orders: DISABLED")

    STATUS_REPORT.write_text("\n".join(status), encoding="utf-8")

    print("=== PHASE 28B RELATIVE STRENGTH OBSERVATION RUN COMPLETE ===")
    print(f"Classification: {classification}")
    print(f"Observation ledger: {OBS_LEDGER}")
    print(f"Latest signal ts: {freshness['latest_signal_ts']}")
    print(f"Signal age days: {freshness['signal_age_days']}")
    print(f"Fresh: {freshness['fresh']}")
    print(f"Latest selected rows: {freshness['latest_selected_rows']}")
    print(f"Signals written: {append_result['rows_written']}")
    print(f"Total observations: {append_result['total_rows']}")
    print("sent_to_broker_any: false")
    print("Production: BLOCKED")
    print("Live: BLOCKED")
    print("Broker execution: DISABLED")
    print("Shadow orders: DISABLED")


if __name__ == "__main__":
    main()
