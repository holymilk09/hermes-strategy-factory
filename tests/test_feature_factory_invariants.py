"""Phase 30K — Feature Factory Invariant Tests
Tests check integrity of observation ledgers, hypothesis registry, and backup state.
No strategy behavior is changed — reads only.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # /opt/data
EXPECTED_SYMBOLS = {"AMD", "ARM", "CRWD", "DDOG", "MRVL", "SEDG"}

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


def test_observation_ledger_exactly_6_rows():
    rows = _load_ledger(OBS_LEDGER)
    assert len(rows) == 6, f"Expected 6 observations, got {len(rows)}"


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