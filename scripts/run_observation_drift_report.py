from __future__ import annotations

from pathlib import Path

from src.research.meta.observation_drift import (
    BacktestBenchmark,
    classify_observation_drift,
    compare_to_benchmark,
    load_observation_ledger,
    load_outcome_ledger,
    next_action_from_classification,
    summarize_observation_state,
    summarize_resolved_outcomes,
    write_comparison_csv,
    write_markdown,
)


ROOT = Path(__file__).resolve().parents[1]

OBS_DIR = ROOT / "data" / "paper_observation"
REPORT_DIR = ROOT / "reports" / "strategy_factory"

OBS_LEDGER = OBS_DIR / "relative_strength_continuation_observation_ledger.csv"
OUTCOME_LEDGER = OBS_DIR / "relative_strength_continuation_outcome_ledger.csv"

DRIFT_REPORT = REPORT_DIR / "observation_drift_report.md"
COMPARISON_CSV = REPORT_DIR / "forward_vs_backtest_comparison.csv"
ACTIVE_STATUS = REPORT_DIR / "active_observation_status.md"
NEXT_ACTION_QUEUE = REPORT_DIR / "next_action_queue.md"


def main() -> None:
    benchmark = BacktestBenchmark()

    observation_df = load_observation_ledger(OBS_LEDGER)
    outcome_df = load_outcome_ledger(OUTCOME_LEDGER)

    observation_state = summarize_observation_state(observation_df, outcome_df)
    outcome_summary = summarize_resolved_outcomes(outcome_df)

    classification = classify_observation_drift(
        observation_state=observation_state,
        outcome_summary=outcome_summary,
    )

    comparison = compare_to_benchmark(outcome_summary, benchmark)
    next_action = next_action_from_classification(classification)

    write_comparison_csv(COMPARISON_CSV, comparison)

    report_rows = [
        f"classification: {classification}",
        f"next_action: {next_action}",
        f"observation_ledger: {OBS_LEDGER}",
        f"outcome_ledger: {OUTCOME_LEDGER}",
        "",
        "## Observation State",
        "",
    ]

    for k, v in observation_state.items():
        report_rows.append(f"{k}: {v}")

    report_rows.extend(["", "## Outcome Summary", ""])

    for k, v in outcome_summary.items():
        report_rows.append(f"{k}: {v}")

    report_rows.extend(["", "## Benchmark Comparison", ""])

    for k, v in comparison.items():
        report_rows.append(f"{k}: {v}")

    report_rows.extend(
        [
            "",
            "## Hard Blocks",
            "",
            "Production: BLOCKED",
            "Live: BLOCKED",
            "Broker execution: DISABLED",
            "Shadow orders: DISABLED",
        ]
    )

    write_markdown(DRIFT_REPORT, "Observation Drift Report", report_rows)

    active_rows = [
        "lineage: relative_strength_continuation",
        f"classification: {classification}",
        f"next_action: {next_action}",
        f"observations_total: {observation_state['observations_total']}",
        f"pending: {observation_state['pending']}",
        f"resolved: {observation_state['resolved']}",
        f"latest_signal_ts: {observation_state['latest_signal_ts']}",
        f"sent_to_broker_any: {observation_state['sent_to_broker_any']}",
        "",
        "Production: BLOCKED",
        "Live: BLOCKED",
        "Broker execution: DISABLED",
        "Shadow orders: DISABLED",
    ]

    write_markdown(ACTIVE_STATUS, "Active Observation Status", active_rows)

    next_rows = [
        "relative_strength_continuation:",
        f"- classification: {classification}",
        f"- next_allowed_action: {next_action}",
        f"- pending: {observation_state['pending']}",
        f"- resolved: {observation_state['resolved']}",
        "",
        "Archived families:",
        "- no rescue",
        "- no retuning",
        "",
        "Production: BLOCKED",
        "Live: BLOCKED",
        "Broker execution: DISABLED",
        "Shadow orders: DISABLED",
    ]

    write_markdown(NEXT_ACTION_QUEUE, "Next Action Queue", next_rows)

    if classification == "OBSERVATION_DRIFT_HARD_FAIL_BROKER_FLAG":
        raise RuntimeError("Broker flag detected in observation ledgers")

    print("=== PHASE 30A COMPLETE ===")
    print("Observation drift report: PASS")
    print(f"Lineage: {benchmark.lineage}")
    print(f"Observations total: {observation_state['observations_total']}")
    print(f"Pending: {observation_state['pending']}")
    print(f"Resolved: {observation_state['resolved']}")
    print(f"Latest signal ts: {observation_state['latest_signal_ts']}")
    print(f"Mean return: {outcome_summary['mean_return']}")
    print(f"Hit rate: {outcome_summary['hit_rate']}")
    print(f"Phase28A expected mean: {benchmark.historical_mean}")
    print(f"Phase28A expected hit: {benchmark.historical_hit_rate}")
    print(f"Classification: {classification}")
    print(f"Next action: {next_action}")
    print("Production: BLOCKED")
    print("Live: BLOCKED")
    print("Broker execution: DISABLED")
    print("Shadow orders: DISABLED")


if __name__ == "__main__":
    main()
