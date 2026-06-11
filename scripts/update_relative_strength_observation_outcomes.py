from __future__ import annotations

from pathlib import Path

from src.paper.relative_strength_observation import (
    resolve_observation_outcomes,
    summarize_outcomes,
)


ROOT = Path(__file__).resolve().parents[1]
OBS_DIR = ROOT / "data" / "paper_observation"
REPORT_DIR = ROOT / "reports" / "strategy_factory"

OBS_LEDGER = OBS_DIR / "relative_strength_continuation_observation_ledger.csv"
OUTCOME_LEDGER = OBS_DIR / "relative_strength_continuation_outcome_ledger.csv"
OUTCOME_REPORT = REPORT_DIR / "relative_strength_forward_observation_outcome_report.md"


def main() -> None:
    result = resolve_observation_outcomes(OBS_LEDGER, ROOT, OUTCOME_LEDGER)
    summary = summarize_outcomes(OUTCOME_LEDGER)

    report = []
    report.append("# Relative Strength Forward Observation Outcome Report")
    report.append("")
    report.append(f"observation_ledger: {OBS_LEDGER}")
    report.append(f"outcome_ledger: {OUTCOME_LEDGER}")
    report.append("")
    report.append("## Update Result")
    for k, v in result.items():
        report.append(f"{k}: {v}")
    report.append("")
    report.append("## Outcome Summary")
    for k, v in summary.items():
        report.append(f"{k}: {v}")
    report.append("")
    report.append("Production: BLOCKED")
    report.append("Live: BLOCKED")
    report.append("Broker execution: DISABLED")
    report.append("Shadow orders: DISABLED")

    OUTCOME_REPORT.write_text("\n".join(report), encoding="utf-8")

    print("=== PHASE 28B OUTCOME UPDATE COMPLETE ===")
    print(f"Observation ledger: {OBS_LEDGER}")
    print(f"Outcome ledger: {OUTCOME_LEDGER}")
    print(f"Resolved: {result['resolved']}")
    print(f"Pending: {result['pending']}")
    print(f"Total: {result['total']}")
    print(f"Outcome mean: {summary['mean']}")
    print(f"Outcome hit rate: {summary['hit_rate']}")
    print("Production: BLOCKED")
    print("Live: BLOCKED")
    print("Broker execution: DISABLED")
    print("Shadow orders: DISABLED")


if __name__ == "__main__":
    main()
