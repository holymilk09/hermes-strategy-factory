"""Phase 30K — Feature Factory Invariant Tests
Tests check integrity of observation ledgers, hypothesis registry, and backup state.
No strategy behavior is changed — reads only.

All tests in this file require production data (ledger CSVs, backups).
They are marked ``requires_data`` so a fresh clone can skip them:
  pytest -m "not requires_data"
"""
import csv
from pathlib import Path
import pytest

pytestmark = pytest.mark.requires_data  # all tests need production ledger CSVs + backups

ROOT = Path(__file__).resolve().parents[1]  # /opt/data
EXPECTED_SYMBOLS = {
    "AMD", "ARM", "CRWD", "DDOG", "MRVL", "SEDG",
    "ARQQ", "ASML", "LLY", "MU", "SNOW", "UNH",
}

OBS_LEDGER = ROOT / "data/paper_observation/relative_strength_continuation_observation_ledger.csv"
OUTCOME_LEDGER = ROOT / "data/paper_observation/relative_strength_continuation_outcome_ledger.csv"
HYPOTHESIS_REGISTRY = ROOT / "reports/strategy_factory/hypothesis_registry.csv"
BACKUP_DIR = ROOT / "backups"


def _load_ledger(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader)


# --- Observation Ledger Tests ---

def test_observation_ledger_exists():
    assert OBS_LEDGER.exists(), f"Observation ledger not found: {OBS_LEDGER}"


# ─── Approved observation cohort manifest ────────────────────
# Phase 7D: 13 observations (7 resolved original + 6 pending Phase 7C cohort).
# Must stay in sync with scripts/run_feature_factory_healthcheck.py.
APPROVED_OBSERVATION_IDS = [
    "6e506d15369deef3ea4d82ec",  # AMD, cohort 1
    "d17b6c30f3bd58a0746592a5",  # ARM, cohort 1
    "1eaba1549790ef85879bd98a",  # CRWD, cohort 1
    "17fd3fa4ae84027e82b8b2fd",  # DDOG, cohort 1
    "6c2f1eb80f83da084c393fb0",  # MRVL, cohort 1
    "e9e478ad4f2034c2ad27d6e4",  # SEDG, cohort 1
    "f6fda996fae00a3e35ed61c6",  # MRVL, cohort 2 (approved Phase 6K)
    # Phase 7C cohort (pending, signal_date=2026-07-01)
    "f54f34012202faba8a690c34",  # ARQQ
    "ab6b139e2f2ecce96af94cd8",  # ASML
    "bd95a00ebac7170b49677d97",  # LLY
    "37c9afc96ac77985f3bb5a54",  # MU
    "d90ef692ac93f2cb5d44f46d",  # SNOW
    "878bd2388a62ad1db98fcef2",  # UNH
]


def test_observation_ledger_exactly_matching_manifest():
    """Verify observation ledger contains exactly the approved cohort IDs."""
    rows = _load_ledger(OBS_LEDGER)
    actual_ids = set(r["observation_id"].strip() for r in rows)
    expected_ids = set(APPROVED_OBSERVATION_IDS)
    assert actual_ids == expected_ids, (
        f"Observation IDs mismatch: extra={actual_ids - expected_ids}, "
        f"missing={expected_ids - actual_ids}, "
        f"expected total={len(expected_ids)}, actual total={len(actual_ids)}"
    )


def test_observation_ledger_symbols_match():
    rows = _load_ledger(OBS_LEDGER)
    symbols = set(r["symbol"].strip() for r in rows)
    assert symbols == EXPECTED_SYMBOLS, f"Symbols mismatch: {symbols} != {EXPECTED_SYMBOLS}"


def test_all_sent_to_broker_false():
    rows = _load_ledger(OBS_LEDGER)
    true_col = "sent_to_broker"
    true_tokens = {"true", "1", "yes", "y", "on"}
    violations = []
    for r in rows:
        val = r.get(true_col, "").strip().lower()
        if val in true_tokens:
            violations.append((r.get("observation_id", "?"), val))
    assert len(violations) == 0, f"sent_to_broker=true found: {violations}"


def test_broker_order_id_empty():
    rows = _load_ledger(OBS_LEDGER)
    if "broker_order_id" not in rows[0]:
        return  # column absent = pass
    populated = []
    for r in rows:
        oid = r.get("broker_order_id", "").strip()
        if oid and oid.lower() not in ("", "nan", "none", "null"):
            populated.append((r.get("observation_id", "?"), oid))
    assert len(populated) == 0, f"broker_order_id populated: {populated}"


def test_no_duplicate_observation_ids():
    rows = _load_ledger(OBS_LEDGER)
    ids = [r["observation_id"].strip() for r in rows if r.get("observation_id", "").strip()]
    assert len(ids) == len(set(ids)), f"Duplicate observation_ids found: {len(ids)} ids, {len(set(ids))} unique"


def test_all_outcome_status_pending():
    rows = _load_ledger(OBS_LEDGER)
    for r in rows:
        status = r.get("outcome_status", "").strip().upper()
        assert status == "PENDING", f"Observation {r.get('observation_id', '?')} status={status}, expected PENDING"


# --- Outcome Ledger Tests ---

def test_outcome_ledger_exists():
    assert OUTCOME_LEDGER.exists(), f"Outcome ledger not found: {OUTCOME_LEDGER}"


def test_outcome_ledger_row_count_matches():
    obs_rows = _load_ledger(OBS_LEDGER)
    out_rows = _load_ledger(OUTCOME_LEDGER)
    assert len(obs_rows) == len(out_rows), (
        f"Row count mismatch: observation={len(obs_rows)} outcome={len(out_rows)}"
    )


def test_outcome_ledger_symbols_match():
    rows = _load_ledger(OUTCOME_LEDGER)
    symbols = set(r["symbol"].strip() for r in rows)
    assert symbols == EXPECTED_SYMBOLS, f"Outcome symbols mismatch: {symbols} != {EXPECTED_SYMBOLS}"


def test_outcome_ledger_sent_to_broker_false():
    rows = _load_ledger(OUTCOME_LEDGER)
    true_tokens = {"true", "1", "yes", "y", "on"}
    violations = []
    for r in rows:
        val = r.get("sent_to_broker", "").strip().lower()
        if val in true_tokens:
            violations.append((r.get("observation_id", "?"), val))
    assert len(violations) == 0, f"sent_to_broker=true in outcome ledger: {violations}"


# --- Hypothesis Registry Tests ---

def test_hypothesis_registry_exists():
    assert HYPOTHESIS_REGISTRY.exists(), f"Hypothesis registry not found: {HYPOTHESIS_REGISTRY}"


def test_hypothesis_registry_contains_active_lineage():
    rows = _load_ledger(HYPOTHESIS_REGISTRY)
    lineages = [r["lineage"].strip() for r in rows]
    assert "relative_strength_continuation" in lineages, (
        f"relative_strength_continuation not in hypothesis registry: {lineages}"
    )


def test_hypothesis_registry_all_expected_columns():
    rows = _load_ledger(HYPOTHESIS_REGISTRY)
    expected_cols = {"lineage", "phase", "family", "classification", "grade", "status", "decision"}
    actual_cols = set(rows[0].keys())
    missing = expected_cols - actual_cols
    assert not missing, f"Missing columns in hypothesis registry: {missing}"


# --- Backup Tests ---

def test_backup_exists():
    backups = sorted(BACKUP_DIR.glob("feature_factory_state_*.tar.gz"), reverse=True)
    assert len(backups) >= 1, f"No backups found in {BACKUP_DIR}"


def test_backup_size_above_1mb():
    backups = sorted(BACKUP_DIR.glob("feature_factory_state_*.tar.gz"), reverse=True)
    assert len(backups) >= 1, "No backup to check size"
    size = backups[0].stat().st_size
    assert size > 1_000_000, f"Latest backup too small: {size:,} bytes (expected >1MB)"