from __future__ import annotations

from pathlib import Path

from src.paper.observation_cycle import (
    append_cycle_log,
    classify_cycle,
    read_observation_status,
    run_command,
)


ROOT = Path(__file__).resolve().parents[1]

OBS_DIR = ROOT / "data" / "paper_observation"
REPORT_DIR = ROOT / "reports" / "strategy_factory"

OBS_LEDGER = OBS_DIR / "regime_conditioned_capitulation_v2_observation_ledger.csv"
OUTCOME_LEDGER = OBS_DIR / "regime_conditioned_capitulation_v2_outcome_ledger.csv"
CYCLE_LOG = OBS_DIR / "forward_observation_cycle_log.csv"

CYCLE_REPORT = REPORT_DIR / "forward_observation_cycle_report.md"
STATUS_SNAPSHOT = REPORT_DIR / "forward_observation_status_snapshot.md"


def main() -> None:
    observation_result = run_command(
        name="observation_run",
        command=["/opt/data/.venv/bin/python", "scripts/run_regime_conditioned_forward_observation_once.py"],
        cwd=ROOT,
    )

    outcome_result = run_command(
        name="outcome_update",
        command=["/opt/data/.venv/bin/python", "scripts/update_forward_observation_outcomes.py"],
        cwd=ROOT,
    )

    status = read_observation_status(
        observation_ledger=OBS_LEDGER,
        outcome_ledger=OUTCOME_LEDGER,
    )

    classification = classify_cycle(
        observation_result=observation_result,
        outcome_result=outcome_result,
        status_snapshot=status,
    )

    if classification == "OBSERVATION_CYCLE_HARD_FAIL_BROKER_FLAG":
        raise RuntimeError("Broker flag detected in observation system")

    log_result = append_cycle_log(
        log_path=CYCLE_LOG,
        cycle_status=classification,
        observation_result=observation_result,
        outcome_result=outcome_result,
        status_snapshot=status,
    )

    report = []
    report.append("# Forward Observation Cycle Report")
    report.append("")
    report.append(f"classification: {classification}")
    report.append(f"cycle_log: {CYCLE_LOG}")
    report.append("")
    report.append("## Observation Command")
    report.append(f"returncode: {observation_result.returncode}")
    report.append("stdout_tail:")
    report.append("```")
    report.append(observation_result.stdout_tail)
    report.append("```")
    report.append("stderr_tail:")
    report.append("```")
    report.append(observation_result.stderr_tail)
    report.append("```")
    report.append("")
    report.append("## Outcome Command")
    report.append(f"returncode: {outcome_result.returncode}")
    report.append("stdout_tail:")
    report.append("```")
    report.append(outcome_result.stdout_tail)
    report.append("```")
    report.append("stderr_tail:")
    report.append("```")
    report.append(outcome_result.stderr_tail)
    report.append("```")
    report.append("")
    report.append("## Status Snapshot")
    for k, v in status.items():
        report.append(f"{k}: {v}")
    report.append("")
    report.append("Production: BLOCKED")
    report.append("Live: BLOCKED")
    report.append("Broker execution: DISABLED")
    report.append("Shadow orders: DISABLED")

    CYCLE_REPORT.write_text("\n".join(report), encoding="utf-8")

    snapshot = []
    snapshot.append("# Forward Observation Status Snapshot")
    snapshot.append("")
    snapshot.append(f"classification: {classification}")
    for k, v in status.items():
        snapshot.append(f"{k}: {v}")
    snapshot.append("")
    snapshot.append("Production: BLOCKED")
    snapshot.append("Live: BLOCKED")
    snapshot.append("Broker execution: DISABLED")
    snapshot.append("Shadow orders: DISABLED")

    STATUS_SNAPSHOT.write_text("\n".join(snapshot), encoding="utf-8")

    print("=== PHASE 26B OBSERVATION CYCLE COMPLETE ===")
    print(f"Classification: {classification}")
    print(f"Cycle log: {log_result['output_path']}")
    print(f"Cycle events total: {log_result['total_events']}")
    print(f"Observation returncode: {observation_result.returncode}")
    print(f"Outcome returncode: {outcome_result.returncode}")
    print(f"Observations total: {status['observations_total']}")
    print(f"Observations pending: {status['observations_pending']}")
    print(f"Outcomes total: {status['outcomes_total']}")
    print(f"Outcomes resolved: {status['outcomes_resolved']}")
    print(f"Outcomes pending: {status['outcomes_pending']}")
    print(f"Outcome mean: {status['outcome_mean']}")
    print(f"Outcome hit rate: {status['outcome_hit_rate']}")
    print(f"Latest signal ts: {status['latest_signal_ts']}")
    print("sent_to_broker_any: false")
    print("Production: BLOCKED")
    print("Live: BLOCKED")
    print("Broker execution: DISABLED")
    print("Shadow orders: DISABLED")


if __name__ == "__main__":
    main()
