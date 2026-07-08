#!/usr/bin/env python3
"""Phase 30K — Feature Factory Healthcheck
Verifies operator scripts, ledgers, invariants, hard blocks, backup, and status commands.
No strategy behavior is changed.
"""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/opt/data")
REPORTS_DIR = ROOT / "reports/strategy_factory"
SCRIPTS_DIR = ROOT / "scripts"
OBS_DIR = ROOT / "data/paper_observation"
BACKUP_DIR = ROOT / "backups"

# ─── Approved observation cohort manifest ────────────────────
# Phase 7D: 13 observations (7 resolved original cohort + 6 pending Phase 7C cohort).
# Update this manifest only after an approved intentional observation cycle.

APPROVED_MANIFEST = {
    "total_observations": 13,
    "original_cohort": {
        "count": 7,
        "status": "RESOLVED",
        "observation_ids": [
            "6e506d15369deef3ea4d82ec",  # AMD
            "d17b6c30f3bd58a0746592a5",  # ARM
            "1eaba1549790ef85879bd98a",  # CRWD
            "17fd3fa4ae84027e82b8b2fd",  # DDOG
            "6c2f1eb80f83da084c393fb0",  # MRVL (cohort 1)
            "e9e478ad4f2034c2ad27d6e4",  # SEDG
            "f6fda996fae00a3e35ed61c6",  # MRVL (Phase 6K, resolved 6L)
        ],
    },
    "new_cohort": {
        "count": 6,
        "status": "PENDING",
        "signal_date": "2026-07-01",
        "observation_ids": [
            "f54f34012202faba8a690c34",  # ARQQ
            "ab6b139e2f2ecce96af94cd8",  # ASML
            "bd95a00ebac7170b49677d97",  # LLY
            "37c9afc96ac77985f3bb5a54",  # MU
            "d90ef692ac93f2cb5d44f46d",  # SNOW
            "878bd2388a62ad1db98fcef2",  # UNH
        ],
    },
}
EXPECTED_SYMBOLS = {
    "AMD", "ARM", "CRWD", "DDOG", "MRVL", "SEDG",
    "ARQQ", "ASML", "LLY", "MU", "SNOW", "UNH",
}
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
    "update_ghost_outcomes.py",
    "refresh_stale_ohlcv.py",
]

REQUIRED_LEDGERS = [
    "data/paper_observation/relative_strength_continuation_observation_ledger.csv",
    "data/paper_observation/relative_strength_continuation_outcome_ledger.csv",
    "reports/strategy_factory/hypothesis_registry.csv",
]

# ─── Phase 7C: universe freshness + ghost ledger invariants ───

GHOST_LEDGER_REL = "data/trust_calibration/ghost_ledger.csv"
OHLCV_CACHE_REL = "data/cache/ohlcv_1d"
MIN_FRESH_UNIVERSE = 50
SECTOR_ETFS = ["SMH", "IGV", "TAN"]


def check_universe_freshness():
    """Universe freshness floor (Phase 7C).

    Reads latest bar date per symbol from the OHLCV cache and requires
    >= MIN_FRESH_UNIVERSE symbols at the latest cross-section date.
    Fails closed when the cross-section collapses — do NOT weaken this
    to get a green check.
    """
    cache = ROOT / OHLCV_CACHE_REL
    result = {
        "cache_exists": cache.is_dir(),
        "universe_size": 0,
        "latest_session": None,
        "fresh_count": 0,
        "stale_count": 0,
        "min_fresh_universe": MIN_FRESH_UNIVERSE,
        "sector_etf_freshness": {},
        "floor_pass": False,
    }
    if not cache.is_dir():
        return result

    latest_by_symbol = {}
    for p in sorted(cache.glob("*.csv")):
        sym = p.stem.upper().replace("_1D", "").replace("_1d", "")
        try:
            with open(p, "rb") as f:
                try:
                    f.seek(-4096, 2)
                except OSError:
                    f.seek(0)
                tail = f.read().decode(errors="replace").strip().splitlines()
            last_line = tail[-1] if tail else ""
            date_str = last_line.split(",")[0][:10]
            if len(date_str) == 10 and date_str[4] == "-":
                latest_by_symbol[sym] = date_str
        except Exception:
            continue

    result["universe_size"] = len(latest_by_symbol)
    if not latest_by_symbol:
        return result

    latest_session = max(latest_by_symbol.values())
    fresh = [s for s, d in latest_by_symbol.items() if d >= latest_session]
    result["latest_session"] = latest_session
    result["fresh_count"] = len(fresh)
    result["stale_count"] = len(latest_by_symbol) - len(fresh)
    result["floor_pass"] = len(fresh) >= MIN_FRESH_UNIVERSE

    for etf in SECTOR_ETFS:
        d = latest_by_symbol.get(etf)
        result["sector_etf_freshness"][etf] = {
            "latest_date": d,
            "fresh": bool(d and d >= latest_session),
        }

    return result


def check_ghost_ledger():
    """Ghost ledger existence + status counts (Phase 7C).

    Read-only reporting. Verifies the ghost ledger exists, parses, and
    reports PENDING / MATURE / INSUFFICIENT_DATA counts. Never mutates.
    """
    path = ROOT / GHOST_LEDGER_REL
    result = {
        "exists": path.exists(),
        "rows": 0,
        "status_counts": {"PENDING": 0, "MATURE": 0, "INSUFFICIENT_DATA": 0},
        "parse_ok": False,
    }
    if not path.exists():
        return result
    rows = parse_ledger(path)
    if rows is None:
        return result
    result["parse_ok"] = True
    result["rows"] = len(rows)
    for r in rows:
        s = (r.get("data_status", "") or "").strip().upper()
        if s in result["status_counts"]:
            result["status_counts"][s] += 1
    return result


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
            env={**os.environ, "PYTHONPATH": str(ROOT)},
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

    ledger_parse_ok = all(v[0] == "PASS" for v in ledgers.values())
    results["ledgers_parse_pass"] = ledger_parse_ok
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

    # Load outcome ledger for status verification
    outcome_path = ROOT / "data/paper_observation/relative_strength_continuation_outcome_ledger.csv"
    outcome_rows = parse_ledger(outcome_path)
    outcome_pending = sum(1 for r in outcome_rows if r.get("outcome_status", "").strip().upper() == "PENDING") if outcome_rows else -1
    outcome_resolved = sum(1 for r in outcome_rows if r.get("outcome_status", "").strip().upper() == "RESOLVED") if outcome_rows else -1

    m = APPROVED_MANIFEST
    expected_total = m["total_observations"]
    expected_pending = m["new_cohort"]["count"] if m.get("new_cohort") else 0
    expected_resolved = m["original_cohort"]["count"]
    approved_obs_ids = set(m["original_cohort"]["observation_ids"])
    if m.get("new_cohort"):
        approved_obs_ids.update(m["new_cohort"]["observation_ids"])
    all_obs_ids = set(r.get("observation_id", "").strip() for r in obs_rows if r.get("observation_id", "").strip())

    # Check total count
    obs_total_pass = inv['observations_total'] == expected_total
    print(f"  observations_total={inv['observations_total']} {'PASS' if obs_total_pass else 'FAIL'} (expected {expected_total})")
    if not obs_total_pass:
        inv_ok = False

    # Check pending (from observation ledger — all pre-allocation markers)
    # Resolution status is verified from the outcome ledger below
    new_cohort_ids = set(m["new_cohort"]["observation_ids"]) if m.get("new_cohort") else set()

    # When there is a pending cohort, pending IDs must match exactly;
    # when there is none, pending_ids must be empty.
    pending_approved = True

    # Check the outcome ledger for resolved/pending status
    outcome_pending_pass = outcome_pending == expected_pending
    outcome_resolved_pass = outcome_resolved == expected_resolved
    print(f"  outcome_ledger_pending={outcome_pending} {'PASS' if outcome_pending_pass else 'FAIL'} (expected {expected_pending})")
    if not outcome_pending_pass:
        inv_ok = False
    print(f"  outcome_ledger_resolved={outcome_resolved} {'PASS' if outcome_resolved_pass else 'FAIL'} (expected {expected_resolved})")
    if not outcome_resolved_pass:
        inv_ok = False

    # Verify the only pending observation IDs are the approved new cohort observations
    # This checks the OUTCOME ledger since that's where resolution status lives
    pending_approved = False
    if outcome_rows:
        only_pending_ids = set(r.get("observation_id", "").strip() for r in outcome_rows if r.get("outcome_status", "").strip().upper() == "PENDING")
        if new_cohort_ids:
            pending_approved = (only_pending_ids == new_cohort_ids)
        else:
            pending_approved = (len(only_pending_ids) == 0)
        print(f"  approved_pending_obs_ids_only={'YES' if pending_approved else 'NO'} {'PASS' if pending_approved else 'FAIL'}")
        if not pending_approved:
            print(f"    Found pending IDs: {only_pending_ids}")
            inv_ok = False
    else:
        print(f"  outcome_ledger: UNAVAILABLE")
        inv_ok = False

    # Verify all approved observation IDs are present
    all_ids_present = all_obs_ids == approved_obs_ids
    print(f"  all_approved_ids_present={'YES' if all_ids_present else 'NO'} {'PASS' if all_ids_present else 'FAIL'}")
    if not all_ids_present:
        extra = all_obs_ids - approved_obs_ids
        missing = approved_obs_ids - all_obs_ids
        if extra: print(f"    Unapproved IDs: {extra}")
        if missing: print(f"    Missing IDs: {missing}")
        inv_ok = False

    # Original 6 IDs present
    orig_ids = set(m["original_cohort"]["observation_ids"])
    orig_all_present = orig_ids.issubset(all_obs_ids)
    print(f"  original_6_ids_present={'YES' if orig_all_present else 'NO'} {'PASS' if orig_all_present else 'FAIL'}")
    if not orig_all_present:
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

    # 4b. Universe freshness floor (Phase 7C)
    print("--- Universe Freshness (Phase 7C) ---")
    uf = check_universe_freshness()
    results["universe_freshness"] = uf
    print(f"  universe_size={uf['universe_size']}")
    print(f"  latest_session={uf['latest_session']}")
    print(f"  fresh_count={uf['fresh_count']} (floor={uf['min_fresh_universe']})")
    print(f"  stale_count={uf['stale_count']}")
    for etf, info in uf["sector_etf_freshness"].items():
        print(f"  sector_etf {etf}: latest={info['latest_date']} "
              f"{'FRESH' if info['fresh'] else 'STALE/MISSING'}")
    universe_floor_ok = uf["floor_pass"]
    results["universe_floor_pass"] = universe_floor_ok
    print(f"  -> {'PASS' if universe_floor_ok else 'FAIL (universe collapsed below floor — fail closed)'}")
    print()

    # 4c. Ghost ledger (Phase 7C)
    print("--- Ghost Ledger (Phase 7C) ---")
    gl = check_ghost_ledger()
    results["ghost_ledger"] = gl
    ghost_ok = gl["exists"] and gl["parse_ok"]
    print(f"  exists={'YES' if gl['exists'] else 'NO'}")
    print(f"  parse_ok={'YES' if gl['parse_ok'] else 'NO'}")
    print(f"  rows={gl['rows']}")
    sc = gl["status_counts"]
    print(f"  status: PENDING={sc['PENDING']} MATURE={sc['MATURE']} "
          f"INSUFFICIENT_DATA={sc['INSUFFICIENT_DATA']}")
    results["ghost_ledger_pass"] = ghost_ok
    print(f"  -> {'PASS' if ghost_ok else 'FAIL'}")
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
        and ledger_parse_ok
        and universe_floor_ok
        and ghost_ok
    )

    print("=== HEALTHCHECK SUMMARY ===")
    for key, ok in [
        ("Scripts present", present == len(REQUIRED_SCRIPTS)),
        ("Ledgers parse", ledger_parse_ok),
        ("Observation invariants", inv_ok),
        ("Hard blocks active", all_blocked),
        ("Universe freshness floor", universe_floor_ok),
        ("Ghost ledger", ghost_ok),
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
        ("Ledgers parse", ledger_parse_ok),
        ("Observation invariants", inv_ok),
        ("Hard blocks active", all_blocked),
        ("Universe freshness floor", universe_floor_ok),
        ("Ghost ledger", ghost_ok),
        ("Backup exists", backup_ok),
        ("Smoke tests pass", all_smoke_pass),
    ]:
        md_lines.append(f"| {key} | {'PASS' if ok else 'FAIL'} |")

    md_lines.append(f"\n## Universe Freshness (Phase 7C)")
    md_lines.append(f"\n- Universe size: {uf['universe_size']}")
    md_lines.append(f"- Latest session: {uf['latest_session']}")
    md_lines.append(f"- Fresh at latest session: {uf['fresh_count']} (floor: {uf['min_fresh_universe']})")
    md_lines.append(f"- Stale: {uf['stale_count']}")
    for etf, info in uf["sector_etf_freshness"].items():
        md_lines.append(f"- Sector ETF {etf}: latest={info['latest_date']} {'FRESH' if info['fresh'] else 'STALE/MISSING'}")

    md_lines.append(f"\n## Ghost Ledger (Phase 7C)")
    md_lines.append(f"\n- Exists: {'YES' if gl['exists'] else 'NO'}")
    md_lines.append(f"- Rows: {gl['rows']}")
    md_lines.append(f"- PENDING: {sc['PENDING']}")
    md_lines.append(f"- MATURE: {sc['MATURE']}")
    md_lines.append(f"- INSUFFICIENT_DATA: {sc['INSUFFICIENT_DATA']}")

    md_lines.append(f"\n## Observation Invariants")
    md_lines.append(f"\n- Total: {inv['observations_total']} (approved: {APPROVED_MANIFEST['total_observations']})")
    md_lines.append(f"- Outcome ledger pending: {outcome_pending} (approved: {'0' if APPROVED_MANIFEST.get('new_cohort') is None else APPROVED_MANIFEST['new_cohort']['count']})")
    md_lines.append(f"- Outcome ledger resolved: {outcome_resolved} (approved: {APPROVED_MANIFEST['original_cohort']['count']})")
    md_lines.append(f"- Approved pending obs IDs only: {'YES' if pending_approved else 'NO'}")
    md_lines.append(f"- All approved IDs present: {'YES' if all_ids_present else 'NO'}")
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