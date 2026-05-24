#!/usr/bin/env python3
"""Phase 30I — Backup Restore Verification
Creates temp restore folder, extracts latest backup, verifies key files,
validates ledgers parse correctly, compares snapshot against current live state,
then cleans up temp folder.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import csv
from pathlib import Path

BASE = Path("/opt/data")
BACKUP_DIR = BASE / "backups"
SNAPSHOT_PATH = BASE / "reports/strategy_factory/feature_factory_state_snapshot.json"

CRITICAL_FILES = [
    "data/paper_observation/relative_strength_continuation_observation_ledger.csv",
    "data/paper_observation/relative_strength_continuation_outcome_ledger.csv",
    "reports/strategy_factory/feature_factory_state_snapshot.json",
    "reports/strategy_factory/active_observation_status.md",
    "reports/strategy_factory/next_action_queue.md",
    "reports/strategy_factory/hypothesis_registry.csv",
    "reports/strategy_factory/relative_strength_maturity_watchdog.json",
]


def get_latest_backup():
    backups = sorted(BACKUP_DIR.glob("feature_factory_state_*.tar.gz"), reverse=True)
    if not backups:
        print("FAIL: No backup archives found in backups/")
        sys.exit(1)
    return backups[0]


def extract_backup(archive_path, dest_dir):
    print(f"Extracting {archive_path.name} to {dest_dir} ...")
    result = subprocess.run(
        ["tar", "xzf", str(archive_path), "-C", str(dest_dir)],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"FAIL: tar extract returned {result.returncode}")
        print(result.stderr)
        return False
    print(f"  extracted OK")
    return True


def verify_files_exist(extract_dir):
    print("\n--- File Existence Check ---")
    missing = []
    found = []
    for rel in CRITICAL_FILES:
        path = extract_dir / rel
        if path.exists():
            found.append(rel)
        else:
            missing.append(rel)
    for f in found:
        size = os.path.getsize(extract_dir / f)
        print(f"  OK  {f} ({size:,} bytes)")
    for f in missing:
        print(f"  MISS {f}")
    if missing:
        print(f"FAIL: {len(missing)} critical files missing")
        return False
    print(f"PASS: All {len(CRITICAL_FILES)} critical files present")
    return True


def verify_ledgers_parse(extract_dir):
    print("\n--- Ledger Parse Check ---")
    ledger_files = [
        extract_dir / "data/paper_observation/relative_strength_continuation_observation_ledger.csv",
        extract_dir / "data/paper_observation/relative_strength_continuation_outcome_ledger.csv",
        extract_dir / "reports/strategy_factory/hypothesis_registry.csv",
    ]
    all_ok = True
    for path in ledger_files:
        if not path.exists():
            continue
        try:
            with open(path) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            print(f"  OK  {path.name}: {len(rows)} rows, columns={list(rows[0].keys()) if rows else 'empty'}")
        except Exception as e:
            print(f"  FAIL {path.name}: {e}")
            all_ok = False
    if all_ok:
        print("PASS: All ledgers parse correctly")
    else:
        print("FAIL: Some ledgers failed to parse")
    return all_ok


def verify_snapshot_matches_live(extract_dir):
    print("\n--- Snapshot Consistency Check ---")
    backup_snap_path = extract_dir / "reports/strategy_factory/feature_factory_state_snapshot.json"
    if not backup_snap_path.exists():
        print(f"SKIP: No snapshot in backup")
        return True

    if not SNAPSHOT_PATH.exists():
        print(f"SKIP: No live snapshot to compare against")
        return True

    try:
        with open(backup_snap_path) as f:
            backup_snap = json.load(f)
        with open(SNAPSHOT_PATH) as f:
            live_snap = json.load(f)
    except Exception as e:
        print(f"  FAIL: Could not parse snapshots: {e}")
        return False

    # Compare key fields
    compare_fields = [
        "active_lineage", "pending", "resolved", "maturity_classification",
        "mature_count", "next_allowed_action", "broker_leakage",
        "production_hard_block", "live_hard_block", "shadow_disabled",
        "broker_execution_disabled",
    ]
    mismatches = []
    for field in compare_fields:
        bv = backup_snap.get(field)
        lv = live_snap.get(field)
        if bv != lv:
            mismatches.append(f"  MISMATCH {field}: backup={bv!r} live={lv!r}")

    # Compare symbol sets
    b_symbols = sorted(backup_snap.get("symbols", []))
    l_symbols = sorted(live_snap.get("symbols", []))
    if b_symbols != l_symbols:
        mismatches.append(f"  MISMATCH symbols: backup={b_symbols} live={l_symbols}")

    # Compare bars remaining
    b_bars = backup_snap.get("bars_remaining_per_symbol", {})
    l_bars = live_snap.get("bars_remaining_per_symbol", {})
    if b_bars != l_bars:
        mismatches.append(f"  MISMATCH bars_remaining: backup={b_bars} live={l_bars}")

    if mismatches:
        for m in mismatches:
            print(m)
        print("FAIL: Snapshot mismatch between backup and live state")
        return False
    else:
        print("PASS: Backup snapshot matches live state")
        return True


def main():
    print("=== PHASE 30I — BACKUP RESTORE VERIFICATION ===")
    print()

    latest = get_latest_backup()
    print(f"Backup: {latest.name}")
    print(f"Size:   {os.path.getsize(latest) / (1024*1024):.0f}M")
    print()

    # Create temp directory
    with tempfile.TemporaryDirectory(prefix="ff_restore_test_") as tmpdir:
        extract_dir = Path(tmpdir)
        print(f"Temp:   {extract_dir}")
        print()

        # Step 1: Extract
        ok = extract_backup(latest, extract_dir)
        if not ok:
            sys.exit(1)
        print()

        # Step 2: Verify files
        ok = verify_files_exist(extract_dir)
        if not ok:
            sys.exit(1)
        print()

        # Step 3: Verify ledgers parse
        ok = verify_ledgers_parse(extract_dir)
        if not ok:
            sys.exit(1)
        print()

        # Step 4: Verify snapshot consistency
        ok = verify_snapshot_matches_live(extract_dir)
        if not ok:
            sys.exit(1)
        print()

    # Temp directory auto-deleted
    print("--- Cleanup ---")
    print("OK: Temp directory removed")
    print()
    print("=== RESTORE VERIFICATION PASSED ===")


if __name__ == "__main__":
    main()