#!/usr/bin/env python3
"""Run Trust Calibration + Ghost Ledger audit cycle.

Produces:
  - reports/trust_calibration/TRUST_STATE_SUMMARY_<date>.md
  - reports/trust_calibration/FILTER_IMPACT_AUDIT_<date>.md
  - reports/trust_calibration/GHOST_LEDGER_SUMMARY_<date>.md

Hard constraints:
  - Never modifies strategy behavior, thresholds, or filters.
  - Never promotes, retires, quarantines, or alters a strategy.
  - Reports only. Human approval required for any action.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/opt/data")


def _load_active_outcomes() -> list[dict[str, str]]:
    """Load outcomes from all known observation systems."""
    from src.research.meta.observation_status import OBSERVATION_SYSTEMS

    all_outcomes: list[dict[str, str]] = []
    for system in OBSERVATION_SYSTEMS:
        path = ROOT / system["outcome_ledger"]
        if path.exists():
            import csv

            with path.open() as f:
                for row in csv.DictReader(f):
                    row["_source_system"] = system["name"]
                    all_outcomes.append(row)
    return all_outcomes


def _load_hypothesis_registry() -> list[dict[str, str]]:
    """Load hypothesis registry for strategy metadata."""
    registry_path = ROOT / "reports" / "strategy_factory" / "hypothesis_registry.csv"
    if not registry_path.exists():
        return []
    import csv

    with registry_path.open() as f:
        return list(csv.DictReader(f))


def _load_strategy_manifest() -> list[dict[str, str]]:
    """Load strategy manifest if available."""
    manifest_path = (
        ROOT / "reports" / "strategy_factory" / "paper_shadow_strategy_manifest.json"
    )
    if not manifest_path.exists():
        return []
    import json

    with manifest_path.open() as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get("strategies", data.get("entries", []))


def main() -> int:
    print("=== Trust Calibration + Ghost Ledger Audit ===")
    print(f"Root: {ROOT}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")

    from src.reporting.ghost_ledger import (
        ghost_summary,
        resolve_ghost_outcomes,
    )
    from src.reporting.trust_calibration import (
        audit_all_filters,
        recommend_trust_state,
    )
    from src.reporting.trust_calibration_reports import (
        generate_filter_impact_audit,
        generate_ghost_ledger_summary,
        generate_trust_state_summary,
    )

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Step 1: Resolve pending ghost outcomes
    print("\n--- Step 1: Resolve Ghost Outcomes ---")
    resolved = resolve_ghost_outcomes(root=ROOT)
    print(f"  Ghost records resolved: {resolved}")

    # Step 2: Load data
    print("\n--- Step 2: Load Active Outcomes ---")
    all_outcomes = _load_active_outcomes()
    print(f"  Active outcomes loaded: {len(all_outcomes)}")

    ghosts = ghost_summary()
    print(f"  Ghost records: {ghosts.get('total_ghost_records', 0)}")

    # Step 3: Trust state per strategy
    print("\n--- Step 3: Trust State Summary ---")
    from src.reporting.ghost_ledger import load_ghost_ledger

    ghost_records = load_ghost_ledger()
    strategies = ["relative_strength_continuation", "regime_conditioned_capitulation_v2"]
    trust_reports = 0
    for strategy_id in strategies:
        outcomes = [r for r in all_outcomes if r.get("_source_system", "") == strategy_id]
        completed = [r for r in outcomes if r.get("outcome_status", "").upper() not in ("PENDING", "")]
        if not completed:
            print(f"  {strategy_id}: No completed outcomes, skipping trust state.")
            continue
        rec = recommend_trust_state(strategy_id, completed, ghost_records=ghost_records, root=ROOT)
        path = generate_trust_state_summary(rec, ROOT)
        print(f"  {strategy_id}: {rec.trust_state} ({rec.completed_sample_count} samples) -> {path}")
        trust_reports += 1
    if trust_reports == 0:
        print("  (No trust state reports generated: no completed outcomes for any strategy)")

    # Step 4: Filter impact audit
    print("\n--- Step 4: Filter Impact Audit ---")
    if ghost_records and all_outcomes:
        impacts = audit_all_filters(ghost_records, all_outcomes)
        if impacts:
            path = generate_filter_impact_audit(impacts, ROOT)
            print(f"  Filter impact audit -> {path}")
            for imp in impacts:
                print(f"    {imp.filter_name}: {imp.filter_helped} ({imp.blocked_count} blocked)")
        else:
            print("  No filters with sufficient data for analysis.")
    else:
        print("  No ghost records or active outcomes available.")

    # Step 5: Ghost ledger summary
    print("\n--- Step 5: Ghost Ledger Summary ---")
    path = generate_ghost_ledger_summary(ghosts, ROOT)
    print(f"  Ghost ledger summary -> {path}")

    print("\n=== Audit Complete ===")
    print("No strategy behavior changed.")
    print("No thresholds changed.")
    print("No broker/live/shadow behavior changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())