from __future__ import annotations

from pathlib import Path

from src.paper.forward_observation import (
    ForwardObservationConfig,
    append_observations_atomic,
    build_current_signal_universe,
    build_observation_rows,
    latest_fresh_signals,
)

from src.reporting.ghost_ledger import record_observation_rejections

ROOT = Path(__file__).resolve().parents[1]
SPY_PATH = ROOT / "data" / "cache" / "SPY_1D.csv"

OBS_DIR = ROOT / "data" / "paper_observation"
REPORT_DIR = ROOT / "reports" / "strategy_factory"

OBS_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OBS_LEDGER = OBS_DIR / "regime_conditioned_capitulation_v2_observation_ledger.csv"
RUN_REPORT = REPORT_DIR / "forward_observation_run_report.md"
STATUS_REPORT = REPORT_DIR / "forward_observation_status.md"


def main() -> None:
    config = ForwardObservationConfig()

    universe = build_current_signal_universe(
        root=ROOT,
        spy_path=SPY_PATH,
        config=config,
    )

    selected, freshness = latest_fresh_signals(
        universe=universe,
        config=config,
    )

    observations = build_observation_rows(selected, config)

    # Ghost recording: non-selected symbols at latest timestamp (observational only)
    CAPITULATION_GATES = [
        ("ret_3d_z", lambda v: v <= -1.5, "ret_3d_z_threshold", "pullback_not_deep_enough"),
        ("volume_z_20", lambda v: v >= 1.0, "volume_z_20_threshold", "volume_not_elevated"),
        ("close_location", lambda v: v >= 0.50, "close_location_threshold", "close_too_low_in_range"),
        ("spy_drawdown_60d", lambda v: v <= -0.0146, "spy_drawdown_60d_threshold", "spy_not_in_drawdown"),
    ]
    ghost_count = record_observation_rejections(
        universe_df=universe,
        root=ROOT,
        strategy_id=config.strategy,
        setup_type="swing",
        gates=CAPITULATION_GATES,
    )

    append_result = append_observations_atomic(
        observations=observations,
        output_path=OBS_LEDGER,
    )

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
    report.append("# Forward Observation Run Report")
    report.append("")
    report.append(f"classification: {classification}")
    report.append(f"observation_ledger: {OBS_LEDGER}")
    report.append("")
    report.append("## Freshness")
    report.append("")
    for k, v in freshness.items():
        report.append(f"{k}: {v}")
    report.append("")
    report.append("## Observation")
    report.append("")
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
    status.append("# Forward Observation Status")
    status.append("")
    status.append(f"classification: {classification}")
    status.append(f"latest_signal_ts: {freshness['latest_signal_ts']}")
    status.append(f"signal_age_days: {freshness['signal_age_days']}")
    status.append(f"latest_selected_rows: {freshness['latest_selected_rows']}")
    status.append(f"signals_written: {append_result['rows_written']}")
    status.append("")
    status.append("Production: BLOCKED")
    status.append("Live: BLOCKED")
    status.append("Broker execution: DISABLED")

    STATUS_REPORT.write_text("\n".join(status), encoding="utf-8")

    print("=== PHASE 26A FORWARD OBSERVATION RUN COMPLETE ===")
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
