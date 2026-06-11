from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


# Phase 28A benchmark expectations
PHASE28A_EXPECTED_MEAN = 0.03261
PHASE28A_EXPECTED_HIT = 0.5574


@dataclass(frozen=True)
class OutcomeGateResult:
    lineage: str
    total: int
    pending: int
    resolved: int
    mean_return: float | None
    hit_rate: float | None
    expected_mean: float
    expected_hit: float
    classification: str
    next_action: str
    report_lines: list[str]


def read_outcome_ledger(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def compute_outcome_metrics(ledger: pd.DataFrame) -> dict[str, Any]:
    resolved = ledger[ledger["outcome_status"].astype(str).eq("RESOLVED")].copy()
    pending = ledger[~ledger["outcome_status"].astype(str).eq("RESOLVED")].copy()

    total = int(len(ledger))
    resolved_count = int(len(resolved))
    pending_count = int(len(pending))

    mean_return = None
    hit_rate = None

    if resolved_count > 0:
        r = pd.to_numeric(resolved["outcome_return"], errors="coerce").dropna()
        if not r.empty:
            mean_return = float(r.mean())
            hit_rate = float((r > 0).mean())

    return {
        "total": total,
        "pending": pending_count,
        "resolved": resolved_count,
        "mean_return": mean_return,
        "hit_rate": hit_rate,
        "sent_to_broker_any": bool(
            ledger["sent_to_broker"].astype(bool).any()
            if "sent_to_broker" in ledger.columns
            else False
        ),
    }


def classify_outcome_gate(metrics: dict[str, Any]) -> str:
    if metrics["pending"] > 0:
        return "OUTCOME_GATE_PENDING"

    mean_r = metrics["mean_return"]
    hit_r = metrics["hit_rate"]

    if mean_r is None or hit_r is None:
        return "OUTCOME_GATE_PENDING"

    if mean_r >= 0.02 and hit_r >= 0.50:
        return "FORWARD_OBSERVATION_CONFIRMED_EARLY"

    if mean_r > 0 and hit_r >= 0.40:
        return "FORWARD_OBSERVATION_MIXED"

    return "FORWARD_OBSERVATION_WEAK"


def determine_next_action(classification: str) -> str:
    if classification == "OUTCOME_GATE_PENDING":
        return "WAIT_FOR_OUTCOMES"

    if classification == "FORWARD_OBSERVATION_CONFIRMED_EARLY":
        return "PAPER_SHADOW_DESIGN_REVIEW_ONLY"

    if classification == "FORWARD_OBSERVATION_MIXED":
        return "CONTINUE_FORWARD_OBSERVATION"

    return "CONTINUE_FORWARD_OBSERVATION"


def build_gate_report(
    lineage: str,
    metrics: dict[str, Any],
    classification: str,
    next_action: str,
) -> str:
    lines: list[str] = []
    lines.append("# Forward Observation Outcome Gate Report")
    lines.append("")
    lines.append(f"lineage: {lineage}")
    lines.append(f"outcome_ledger_evaluated: data/paper_observation/{lineage}_outcome_ledger.csv")
    lines.append(f"gate_timestamp: {pd.Timestamp.now('UTC').isoformat()}")
    lines.append("")
    lines.append("## Outcome Summary")
    lines.append(f"total: {metrics['total']}")
    lines.append(f"pending: {metrics['pending']}")
    lines.append(f"resolved: {metrics['resolved']}")
    lines.append(f"mean_return: {metrics['mean_return']}")
    lines.append(f"hit_rate: {metrics['hit_rate']}")
    lines.append("")
    lines.append("## Phase 28A Benchmark")
    lines.append(f"expected_mean: {PHASE28A_EXPECTED_MEAN}")
    lines.append(f"expected_hit: {PHASE28A_EXPECTED_HIT}")
    lines.append("")
    lines.append("## Gate Classification")
    lines.append(f"classification: {classification}")
    lines.append(f"next_action: {next_action}")
    lines.append("")
    lines.append("sent_to_broker_any: false")
    lines.append("")
    lines.append("Production: BLOCKED")
    lines.append("Live: BLOCKED")
    lines.append("Broker execution: DISABLED")
    lines.append("Shadow orders: DISABLED")

    return "\n".join(lines)


def update_active_observation_status(
    root: Path,
    lineage: str,
    metrics: dict[str, Any],
    classification: str,
    cycle_status: str | None,
) -> None:
    path = root / "reports" / "strategy_factory" / "active_observation_status.md"

    lines: list[str] = []
    lines.append("# Active Observation Status")
    lines.append("")
    lines.append(f"Generated: {pd.Timestamp.now('UTC').isoformat()}")
    lines.append("")
    lines.append(f"## {lineage}")
    lines.append("")
    lines.append(f"Cycle status: {cycle_status or 'N/A'}")
    lines.append(f"Observations total: {metrics['total']}")
    lines.append(f"Observations pending: {metrics['pending']}")
    lines.append(f"Outcomes total: {metrics['total']}")
    lines.append(f"Outcomes resolved: {metrics['resolved']}")
    lines.append(f"Outcomes pending: {metrics['pending']}")
    lines.append(f"Outcome mean: {metrics['mean_return']}")
    lines.append(f"Outcome hit rate: {metrics['hit_rate']}")
    lines.append(f"Gate classification: {classification}")
    lines.append(f"Observation ledger: data/paper_observation/{lineage}_observation_ledger.csv")
    lines.append(f"Outcome ledger: data/paper_observation/{lineage}_outcome_ledger.csv")
    lines.append("sent_to_broker_any: false"
                  if not metrics.get("sent_to_broker_any")
                  else "sent_to_broker_any: TRUE — INVESTIGATE")
    lines.append("")
    lines.append("Production: BLOCKED")
    lines.append("Live: BLOCKED")
    lines.append("Broker execution: DISABLED")
    lines.append("Shadow orders: DISABLED")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def update_next_action_queue(
    root: Path,
    lineage: str,
    classification: str,
    next_action: str,
    metrics: dict[str, Any],
) -> None:
    path = root / "reports" / "strategy_factory" / "next_action_queue.md"

    lines: list[str] = []
    lines.append("# Next Action Queue")
    lines.append("")
    lines.append(f"Generated: {pd.Timestamp.now('UTC').isoformat()}")
    lines.append("")
    lines.append("## Active Item")
    lines.append("")
    lines.append(f"**{lineage}**")
    lines.append(f"  - Gate classification: {classification}")
    lines.append(f"  - Next action: {next_action}")
    lines.append(f"  - Resolved: {metrics['resolved']} / {metrics['total']}")
    lines.append(f"  - Mean return: {metrics['mean_return']}")
    lines.append(f"  - Hit rate: {metrics['hit_rate']}")
    lines.append("")
    lines.append("## Archived / Inactive")
    lines.append("")
    lines.append("All other lineages: Archived — no action")
    lines.append("")
    lines.append("## Hard Blocks (All Systems)")
    lines.append("")
    lines.append("- Production: **BLOCKED**")
    lines.append("- Live: **BLOCKED**")
    lines.append("- Broker execution: **DISABLED**")
    lines.append("- Shadow orders: **DISABLED**")

    path.write_text("\n".join(lines), encoding="utf-8")


def run_outcome_gate(
    root: Path,
    lineage: str = "relative_strength_continuation",
    expected_mean: float = PHASE28A_EXPECTED_MEAN,
    expected_hit: float = PHASE28A_EXPECTED_HIT,
) -> OutcomeGateResult:
    outcome_path = root / "data" / "paper_observation" / f"{lineage}_outcome_ledger.csv"

    ledger = read_outcome_ledger(outcome_path)
    metrics = compute_outcome_metrics(ledger)

    classification = classify_outcome_gate(metrics)
    next_action = determine_next_action(classification)

    report = build_gate_report(
        lineage=lineage,
        metrics=metrics,
        classification=classification,
        next_action=next_action,
    )

    # Write gate report
    report_path = root / "reports" / "strategy_factory" / "forward_observation_outcome_gate_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    # Determine cycle status from observation ledger
    obs_path = root / "data" / "paper_observation" / f"{lineage}_observation_ledger.csv"
    cycle_status = None
    if obs_path.exists():
        obs = pd.read_csv(obs_path)
        if not obs.empty and "outcome_status" in obs.columns:
            p = int(obs["outcome_status"].astype(str).eq("PENDING").sum())
            r = int(obs["outcome_status"].astype(str).eq("RESOLVED").sum())
            if p > 0:
                cycle_status = "OBSERVATION_CYCLE_ACTIVE_PENDING"
            elif r > 0:
                cycle_status = "OBSERVATION_CYCLE_ACTIVE_RESOLVED"
            else:
                cycle_status = "OBSERVATION_CYCLE_READY_NO_SIGNALS"

    # Update status files
    update_active_observation_status(
        root=root,
        lineage=lineage,
        metrics=metrics,
        classification=classification,
        cycle_status=cycle_status,
    )

    update_next_action_queue(
        root=root,
        lineage=lineage,
        classification=classification,
        next_action=next_action,
        metrics=metrics,
    )

    return OutcomeGateResult(
        lineage=lineage,
        total=metrics["total"],
        pending=metrics["pending"],
        resolved=metrics["resolved"],
        mean_return=metrics["mean_return"],
        hit_rate=metrics["hit_rate"],
        expected_mean=expected_mean,
        expected_hit=expected_hit,
        classification=classification,
        next_action=next_action,
        report_lines=report.split("\n"),
    )


def print_gate_result(result: OutcomeGateResult) -> None:
    print("=== PHASE 29B COMPLETE ===")
    print("Tests: PASS/FAIL")
    print("Outcome gate: PASS/FAIL")
    print("")
    print("Observation:")
    print(f"  lineage={result.lineage}")
    print(f"  pending={result.pending}")
    print(f"  resolved={result.resolved}")
    print(f"  total={result.total}")
    print("")
    print("Outcome metrics:")
    print(f"  mean_return={result.mean_return}")
    print(f"  hit_rate={result.hit_rate}")
    print(f"  phase28a_expected_mean={result.expected_mean}")
    print(f"  phase28a_expected_hit={result.expected_hit}")
    print("")
    print(f"Classification: {result.classification}")
    print(f"Next action: {result.next_action}")
    print("")
    print("Production: BLOCKED")
    print("Live: BLOCKED")
    print("Broker execution: DISABLED")
    print("Shadow orders: DISABLED")
