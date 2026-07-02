#!/usr/bin/env python3
"""PHASE 7C-DATA-REPAIR — Controlled ghost outcome resolution.

Resolves PENDING ghost ledger records to MATURE / INSUFFICIENT_DATA using
local OHLCV bars. This is the ONLY approved path for updating ghost
outcome fields.

Safety contract:
  - DEFAULT MODE IS DRY-RUN. Nothing is written unless --write is passed.
  - Updates ONLY ghost ledger outcome/status fields
    (data/trust_calibration/ghost_ledger.csv).
  - NEVER mutates the observation ledger.
  - NEVER mutates the outcome ledger.
  - NEVER creates new observations or new ghost rows.
  - Ghost row COUNT before must equal ghost row count after.
  - Observation/outcome ledger hashes are verified unchanged after a
    write run; any difference aborts with LEDGER_INTEGRITY_FAIL.

This script is intentionally NOT wired into
run_relative_strength_observation_cycle.py — ghost resolution is an
explicit operator command so the approved observation cycle cannot
accidentally mutate the ghost ledger. Recommended operating order:

  1. scripts/refresh_stale_ohlcv.py           (full-universe data refresh)
  2. scripts/run_relative_strength_observation_cycle.py  (only if intentionally invoked)
  3. scripts/update_relative_strength_observation_outcomes.py
  4. scripts/update_ghost_outcomes.py --write  (this script)
  5. scripts/run_edge_audit.py
  6. scripts/run_feature_factory_healthcheck.py

Usage:
  python scripts/update_ghost_outcomes.py            # dry-run (default)
  python scripts/update_ghost_outcomes.py --write    # explicit write mode
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

GHOST_LEDGER = ROOT / "data" / "trust_calibration" / "ghost_ledger.csv"
OBSERVATION_LEDGER = (
    ROOT / "data" / "paper_observation"
    / "relative_strength_continuation_observation_ledger.csv"
)
OUTCOME_LEDGER = (
    ROOT / "data" / "paper_observation"
    / "relative_strength_continuation_outcome_ledger.csv"
)


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _status_counts(records: list[dict[str, str]]) -> Counter:
    return Counter((r.get("data_status", "") or "").upper() for r in records)


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve ghost ledger outcomes.")
    parser.add_argument(
        "--write", action="store_true",
        help="Explicitly enable write mode. Default is dry-run (no writes).",
    )
    args = parser.parse_args()
    dry_run = not args.write

    from src.reporting.ghost_ledger import load_ghost_ledger, resolve_ghost_outcomes

    print("=" * 60)
    print("PHASE 7C — Ghost Outcome Resolution")
    print(f"Mode: {'DRY-RUN (no writes)' if dry_run else 'WRITE (explicit)'}")
    print("=" * 60)
    print()

    if not GHOST_LEDGER.exists():
        print(f"GHOST_LEDGER_MISSING: {GHOST_LEDGER}")
        return 1

    # Snapshot protected-ledger hashes and ghost state BEFORE
    obs_hash_before = _sha256(OBSERVATION_LEDGER)
    out_hash_before = _sha256(OUTCOME_LEDGER)

    before = load_ghost_ledger(GHOST_LEDGER)
    before_counts = _status_counts(before)
    print(f"Ghost rows before: {len(before)}")
    print(f"Status before: PENDING={before_counts.get('PENDING', 0)} "
          f"MATURE={before_counts.get('MATURE', 0)} "
          f"INSUFFICIENT_DATA={before_counts.get('INSUFFICIENT_DATA', 0)}")
    print()

    updated = resolve_ghost_outcomes(
        root=ROOT, ghost_path=GHOST_LEDGER, dry_run=dry_run
    )

    after = load_ghost_ledger(GHOST_LEDGER)
    after_counts = _status_counts(after)

    print(f"Records {'that would be updated' if dry_run else 'updated'}: {updated}")
    print(f"Ghost rows after: {len(after)}")
    print(f"Status after: PENDING={after_counts.get('PENDING', 0)} "
          f"MATURE={after_counts.get('MATURE', 0)} "
          f"INSUFFICIENT_DATA={after_counts.get('INSUFFICIENT_DATA', 0)}")
    print()

    # Invariant: row count must never change
    if len(after) != len(before):
        print(f"LEDGER_INTEGRITY_FAIL: ghost row count changed "
              f"{len(before)} -> {len(after)}")
        return 2

    # Invariant: observation/outcome ledgers untouched
    obs_hash_after = _sha256(OBSERVATION_LEDGER)
    out_hash_after = _sha256(OUTCOME_LEDGER)
    if obs_hash_after != obs_hash_before:
        print("LEDGER_INTEGRITY_FAIL: observation ledger hash changed")
        return 2
    if out_hash_after != out_hash_before:
        print("LEDGER_INTEGRITY_FAIL: outcome ledger hash changed")
        return 2

    print("Observation ledger: UNCHANGED (hash verified)")
    print("Outcome ledger: UNCHANGED (hash verified)")
    print("New observations generated: NO")
    print("Ghost rows added/removed: NO")
    print()
    print("Production: BLOCKED")
    print("Live: BLOCKED")
    print("Broker execution: DISABLED")
    print("Shadow orders: DISABLED")

    if dry_run:
        print()
        print("DRY-RUN complete — nothing was written. "
              "Re-run with --write to apply.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
