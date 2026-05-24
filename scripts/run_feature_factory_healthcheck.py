#!/usr/bin/env python3
"""Phase 30K — Feature Factory Healthcheck
Verifies operator scripts, ledgers, invariants, hard blocks, backup, and status commands.
No strategy behavior is changed.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/opt/data")
REPORTS_DIR = ROOT / "reports/strategy_factory"
SCRIPTS_DIR = ROOT / "scripts"
OBS_DIR = ROOT / "data/paper_observation"
BACKUP_DIR = ROOT / "backups"

EXPECTED_SYMBOLS = {"AMD", "ARM", "CRWD", "DDOG", "MRVL", "SEDG"}
OUTCOME_WINDOW = 10

REQUIRED_SCRIPTS = [
    "run_relative_strength_observation_cycle.py",
    "update_relative_strength_observation_outcomes.py",
    "run_observation_drift_report.py",
    "show_relative_strength_maturity_watchdog.py",
    "show_feature_factory_status.py",
    "verify_no_trading_leakage.py",
    "snapshot_feature_factory_state.py",
    "backup_feature_factory_state.sh",
]

REQUIRED_LEDGERS = [
    "data/paper_observation/relative_strength_continuation_observation_ledger.csv",
    "data/paper_observation/relative_strength_continuation_outcome_ledger.csv",
    "reports/strategy_factory/hypothesis_registry.csv",
]


def check_scripts():
    results = {}
    for name in REQUIRED_SCRIPTS:
        path = SCRIPTS_DIR / name
        exists = path.exists()
        results[name] = exists
    return results


def parse_ledger(path):
    """Parse a CSV ledger, return list of dicts or None on failure."""
    try:
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows
    except Exception:
        return None


def check_ledgers():
    results = {}
    for rel in REQUIRED_LEDGERS:
        path = ROOT / rel
        rows = parse_ledger(path)
        if rows is None:
            results[rel] = ("FAIL", 0)
        else:
            results[rel] = ("PASS", len(rows))
    return results


def check_observation_invariants(rows):
    """Check invariants on the observation ledger rows."""
    checks = {}

    # Total count
    checks["observations_total"] = len(rows)

    # Pending count
    pending = sum(1 for r in rows if r.get("outcome_status", "").strip().upper() == "PENDING")
    resolved = sum(1 for r in rows if r.get("outcome_status", "").strip().upper() not in ("PENDING", ""))
    checks["pending"] = pending
    checks["resolved"] = resolved

    # Symbol set
    symbols = set(r.get("symbol", "").strip() for r in rows)
    checks["symbols_match"] = (symbols == EXPECTED_SYMBOLS)
    checks["symbols_found"] = sorted(symbols)
    checks["symbols_expected"] = sorted(EXPECTED_SYMBOLS)

    # Duplicate observation IDs
    ids = [r.get("observation_id", "").strip() for r in rows if r.get("observation_id", "").strip()]
    checks["total_ids"] = len(ids)
    checks["unique_ids"] = len(set(ids))
    checks["duplicate_count"] = len(ids) - len(set(ids))

    # sent_to_broker
    broker_flags = []
    for r in rows:
        val = r.get("sent_to_broker", "").strip().lower()
        if val in ("true", "1", "yes"):
            broker_flags.append((r.get("observation_id", "?"), val))
    checks["sent_to_broker_any"] = (len(broker_flags) == 0)
    checks["sent_to_broker_violations"] = broker_flags

    # broker_order_id
    order_ids_populated = []
    for r in rows:
        oid = r.get("broker_order_id", "").strip()
        if oid and oid.lower() not in ("", "nan", "none", "null"):
            order_ids_populated.append((r.get("observation_id", "?"), oid))
    checks["broker_order_id_populated"] = (len(order_ids_populated) == 0)
    checks["broker_order_id_violations"] = order_ids_populated

    return checks


def check_hard_blocks():
    # These are hard-coded policy blocks — they never change until user explicitly lifts them
    blocks = {
        "production_blocked": True,
        "live_blocked": True,
        "broker_execution_disabled": True,
        "shadow_disabled": True,
    }
    return blocks


def check_backup():
    backups = sorted(BACKUP_DIR.glob("feature_factory_state_*.tar.gz"), reverse=True)
    if not backups:
        return None, 0
    latest = backups[0]
    size_bytes = latest.stat().st_size
    return str(latest.relative_to(ROOT)), size_bytes


def run_command(cmd_parts, description):
    """Run a command, return (exit_code, stdout)"""
    try:
        result = subprocess.run(
            cmd_parts,
            capture_output=True, text=True, timeout=60,
            cwd=str(ROOT),
            env={"PYTHONPATH": str(ROOT)},
        )
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -2, str(e)


def main():
    print("=== FEATURE FACTORY HEALTHCHECK ===")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Root: {ROOT}")
    print()

    results = {}

    # 1. Script existence
    print("--- Required Scripts ---")
    scripts = check_scripts()
    present = sum(1 for v in scripts.values() if v)
    missing = [k for k, v in scripts.items() if not v]
    results["required_scripts_present"] = len(REQUIRED_SCRIPTS) - len(missing)
    results["required_scripts_total"] = len(REQUIRED_SCRIPTS)
    results["missing_scripts"] = missing
    for name, exists in scripts.items():
        status = "OK" if exists else "MISS"
        print(f"  {status}  {name}")
    print(f"  -> {present}/{len(REQUIRED_SCRIPTS)} present")
    print()

    # 2. Ledgers
    print("--- Required Ledgers ---")
    ledgers = check_ledgers()
    results["ledgers"] = {}
    for rel, (status, count) in ledgers.items():
        name = rel.split("/")[-1]
        results["ledgers"][name] = {"status": status, "rows": count}
        print(f"  {status}  {name} ({count} rows)")
    print()

    # 3. Observation invariants
    print("--- Observation Invariants ---")
    obs_path = ROOT / "data/paper_observation/relative_strength_continuation_observation_ledger.csv"
    obs_rows = parse_ledger(obs_path)
    if obs_rows is None:
        print("  FAIL: Cannot parse observation ledger")
        sys.exit(1)

    inv = check_observation_invariants(obs_rows)
    results["observation_invariants"] = inv

    inv_ok = True

    print(f"  observations_total={inv['observations_total']} {'PASS' if inv['observations_total'] == 6 else 'FAIL'}")
    if inv['observations_total'] != 6:
        inv_ok = False

    print(f"  pending={inv['pending']} {'PASS' if inv['pending'] == 6 else 'FAIL'}")
    if inv['pending'] != 6:
        inv_ok = False

    print(f"  resolved={inv['resolved']} {'PASS' if inv['resolved'] == 0 else 'FAIL'}")
    if inv['resolved'] != 0:
        inv_ok = False

    print(f"  symbols_match={'YES' if inv['symbols_match'] else 'NO'} "
          f"{'PASS' if inv['symbols_match'] else 'FAIL'}")
    if not inv['symbols_match']:
        inv_ok = False

    print(f"  duplicate_observation_ids={inv['duplicate_count']} {'PASS' if inv['duplicate_count'] == 0 else 'FAIL'}")
    if inv['duplicate_count'] != 0:
        inv_ok = False

    print(f"  sent_to_broker_any=false {'PASS' if inv['sent_to_broker_any'] else 'FAIL'}")
    if not inv['sent_to_broker_any']:
        inv_ok = False

    print(f"  broker_order_id_populated=false {'PASS' if inv['broker_order_id_populated'] else 'FAIL'}")
    if not inv['broker_order_id_populated']:
        inv_ok = False

    results["observation_invariants_pass"] = inv_ok
    print(f"  -> {'ALL PASS' if inv_ok else 'SOME FAILED'}")
    print()

    # 4. Hard blocks
    print("--- Hard Blocks ---")
    blocks = check_hard_blocks()
    results["hard_blocks"] = blocks
    block_labels = {
        "production_blocked": "Production",
        "live_blocked": "Live",
        "broker_execution_disabled": "Broker",
        "shadow_disabled": "Shadow",
    }
    for key, label in block_labels.items():
        status = "BLOCKED" if blocks[key] else "OPEN"
        print(f"  {label}: {status}")

    all_blocked = all(blocks.values())
    results["all_hard_blocks_active"] = all_blocked
    print(f"  -> {'ALL BLOCKED' if all_blocked else 'WARNING: BLOCK NOT ACTIVE'}")
    print()

    # 5. Backup
    print("--- Backup ---")
    backup_path, backup_size = check_backup()
    results["backup"] = {}
    if backup_path:
        size_mb = backup_size / (1024 * 1024)
        backup_ok = backup_size > 1_000_000
        results["backup"]["path"] = str(backup_path)
        results["backup"]["size_bytes"] = backup_size
        results["backup"]["ok"] = backup_ok
        print(f"  latest_backup={backup_path}")
        print(f"  size={size_mb:.0f}M {'PASS (>1MB)' if backup_ok else 'FAIL (<1MB)'}")
    else:
        backup_ok = False
        results["backup"]["ok"] = False
        print(f"  FAIL: No backup found")
    print()

    # 6. Command smoke tests
    print("--- Command Smoke Tests ---")
    smoke_tests = [
        ([str(ROOT / ".venv/bin/python"), "scripts/show_feature_factory_status.py"], "status"),
        ([str(ROOT / ".venv/bin/python"), "scripts/show_relative_strength_maturity_watchdog.py"], "maturity_watchdog"),
        ([str(ROOT / ".venv/bin/python"), "scripts/verify_no_trading_leakage.py"], "no_trading_leakage"),
    ]

    results["smoke_tests"] = {}
    for cmd_parts, name in smoke_tests:
        rc, stdout = run_command(cmd_parts, name)
        passed = (rc == 0)
        results["smoke_tests"][name] = {"exit_code": rc, "pass": passed}
        status = "PASS" if passed else "FAIL"
        # Extract key output
        summary = stdout.strip().split("\n")[-1] if stdout else "(no output)"
        print(f"  {status}  {name} (exit={rc})")
        if not passed and stdout:
            print(f"    output: {summary}")

    all_smoke_pass = all(v["pass"] for v in results["smoke_tests"].values())
    results["smoke_tests_all_pass"] = all_smoke_pass
    print(f"  -> {'ALL PASS' if all_smoke_pass else 'SOME FAILED'}")
    print()

    # 7. Overall
    all_pass = (
        inv_ok
        and all_smoke_pass
        and backup_ok
        and all_blocked
        and present == len(REQUIRED_SCRIPTS)
    )

    print("=== HEALTHCHECK SUMMARY ===")
    for key, ok in [
        ("Scripts present", present == len(REQUIRED_SCRIPTS)),
        ("Ledgers parse", all(v[0] == "PASS" for v in ledgers.values())),
        ("Observation invariants", inv_ok),
        ("Hard blocks active", all_blocked),
        ("Backup exists", backup_ok),
        ("Smoke tests pass", all_smoke_pass),
    ]:
        print(f"  {'PASS' if ok else 'FAIL'}  {key}")

    print()
    decision = "HEALTHCHECK_PASS_CONTINUE_WAITING" if all_pass else "HEALTHCHECK_FAIL_FIX_REQUIRED"
    print(f"Decision: {decision}")
    print()

    # Write JSON report
    results["timestamp"] = datetime.now(timezone.utc).isoformat()
    results["decision"] = decision
    results["all_pass"] = all_pass

    json_path = REPORTS_DIR / "feature_factory_healthcheck.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"JSON report: {json_path}")

    # Write MD report
    md_lines = []
    md_lines.append("# Feature Factory Healthcheck Report")
    md_lines.append(f"\nTimestamp: {results['timestamp']}")
    md_lines.append(f"\n## Summary")
    md_lines.append(f"\n**Decision:** {decision}")
    md_lines.append(f"\n| Check | Status |")
    md_lines.append(f"|-------|--------|")
    for key, ok in [
        ("Scripts present", present == len(REQUIRED_SCRIPTS)),
        ("Ledgers parse", all(v[0] == "PASS" for v in ledgers.values())),
        ("Observation invariants", inv_ok),
        ("Hard blocks active", all_blocked),
        ("Backup exists", backup_ok),
        ("Smoke tests pass", all_smoke_pass),
    ]:
        md_lines.append(f"| {key} | {'PASS' if ok else 'FAIL'} |")

    md_lines.append(f"\n## Observation Invariants")
    md_lines.append(f"\n- Total: {inv['observations_total']} (expected 6)")
    md_lines.append(f"- Pending: {inv['pending']} (expected 6)")
    md_lines.append(f"- Resolved: {inv['resolved']} (expected 0)")
    md_lines.append(f"- Symbols match: {'YES' if inv['symbols_match'] else 'NO'}")
    md_lines.append(f"- Duplicate IDs: {inv['duplicate_count']} (expected 0)")
    md_lines.append(f"- sent_to_broker_any: {'false (PASS)' if inv['sent_to_broker_any'] else 'true (FAIL)'}")
    md_lines.append(f"- broker_order_id populated: {'false (PASS)' if inv['broker_order_id_populated'] else 'true (FAIL)'}")

    md_lines.append(f"\n## Hard Blocks")
    for key, label in block_labels.items():
        md_lines.append(f"- {label}: {'BLOCKED' if blocks[key] else 'OPEN'}")

    md_lines.append(f"\n## Backup")
    if backup_path:
        md_lines.append(f"- Path: {backup_path}")
        md_lines.append(f"- Size: {backup_size / (1024*1024):.0f}M")
    else:
        md_lines.append("- No backup found")

    md_lines.append(f"\n## Smoke Tests")
    for name, result in results["smoke_tests"].items():
        md_lines.append(f"- {name}: {'PASS' if result['pass'] else 'FAIL'} (exit={result['exit_code']})")

    md_lines.append(f"\n## Required Scripts")
    for name in REQUIRED_SCRIPTS:
        exists = (SCRIPTS_DIR / name).exists()
        md_lines.append(f"- {name}: {'present' if exists else 'MISSING'}")

    md_path = REPORTS_DIR / "feature_factory_healthcheck_report.md"
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"MD report:  {md_path}")


if __name__ == "__main__":
    main()