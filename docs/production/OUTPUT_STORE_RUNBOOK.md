# Output Store Runbook — Strategy Factory Phase 7B

> **Version:** 1.0  
> **Date:** 2026-07-01  
> **Status:** READY FOR VALIDATION  
> **Source of truth:** CSV ledgers (unchanged)  
> **Output store:** PostgreSQL / Supabase (read-only export target)

---

## 1. Quick Start

```bash
cd /opt/data

# Dry-run JSONL export (default — writes to stdout, never touches DB)
PYTHONPATH=/opt/data /opt/data/.venv/bin/python3 \
    scripts/export_strategy_factory_outputs.py

# JSONL export to file
PYTHONPATH=/opt/data /opt/data/.venv/bin/python3 \
    scripts/export_strategy_factory_outputs.py \
    --format jsonl -o /tmp/export.jsonl

# SQL export (for manual DB ingestion)
PYTHONPATH=/opt/data /opt/data/.venv/bin/python3 \
    scripts/export_strategy_factory_outputs.py \
    --format sql -o /tmp/export.sql
```

---

## 2. Architecture

```
CSV Ledgers (source of truth)
│
│  observation_ledger.csv  ─────┐
│  outcome_ledger.csv      ─────┤
│  ghost_ledger.csv         ────┤
│                                │
│  edge_audit.json          ────┤
│                                ▼
│                    export_strategy_factory_outputs.py
│                    │
│                    ├── validate_ledgers() — fail-closed checks
│                    ├── build_setup_cards()
│                    ├── build_maturity_results()
│                    ├── build_edge_audit_results()
│                    ├── build_ghost_rejections()
│                    │
│                    └── format_jsonl() or format_sql_inserts()
│                              │
│                              ▼
│                    JSONL or SQL output (stdout or file)
│                              │
│                    ┌─────────▼─────────┐
│                    │  Supabase / PG    │  ← NOT YET IMPLEMENTED
│                    │  (--live-db flag) │     requires credentials
│                    └───────────────────┘
```

---

## 3. Tables Exported

| Table | Rows (current) | Source |
|---|---|---|
| `setup_cards` | 7 | Observation ledger |
| `maturity_results` | 7 | Outcome ledger + edge audit JSON |
| `edge_audit_results` | 7 | Edge audit JSON (drift + economic sanity) |
| `ghost_rejections` | 87 | Ghost ledger |
| `system_runs` | 1 per export | Generated at runtime |
| `approved_publications` | — | Not yet auto-generated (manual approval phase) |
| `user_ticker_selections` | — | Placeholder — no auth implementation |

---

## 4. Validation Checks (Fail-Closed)

The exporter aborts with exit code 1 if any check fails:

| # | Check | Failure Mode |
|---|---|---|
| V1 | Observation count = 7 | Wrong count → no export |
| V2 | Outcome rows match observation rows | Mismatch → no export |
| V3 | Resolved count = 7, Pending count = 0 | Unexpected state → no export |
| V4 | No duplicate observation IDs | Duplicates → no export |
| V5 | Observation IDs match between ledgers | ID mismatch → no export |
| V6 | No `sent_to_broker=True` | Broker flag → no export |
| V7 | No `broker_order_id` populated | Broker ID → no export |
| V8 | Ghost ledger ≥ 80 rows | Too few ghost rows → no export |
| V9 | Ledger files exist | Missing file → no export |
| V10 | Edge audit JSON exists | Missing audit → no export |

---

## 5. Output Formats

### 5.1 JSONL (default)

One JSON object per line. Each line has `table` and `data` keys.

```json
{"table": "setup_cards", "data": {"observation_id": "abc...", "symbol": "MRVL", ...}}
{"table": "maturity_results", "data": {"observation_id": "abc...", "raw_return": 0.1685, ...}}
{"table": "edge_audit_results", "data": {"observation_id": "abc...", "drift_label": "Independent Strength", ...}}
{"table": "ghost_rejections", "data": {"ghost_id": "def...", "rejection_reason": "20d_momentum_too_weak", ...}}
{"table": "system_runs", "data": {"run_id": "20260701_120000_abc12345", "status": "completed", ...}}
```

### 5.2 SQL

Valid PostgreSQL with `BEGIN/COMMIT`, `INSERT ... ON CONFLICT DO NOTHING`. Safe to pipe to `psql` or paste into Supabase SQL Editor.

```sql
-- Strategy Factory Export — generated 2026-07-01T...
BEGIN;

INSERT INTO setup_cards (...) VALUES (...) ON CONFLICT (observation_id) DO NOTHING;
INSERT INTO maturity_results (...) VALUES (...) ON CONFLICT (observation_id) DO NOTHING;
-- ... etc

COMMIT;
```

---

## 6. Integration Points

### 6.1 Hermes Cron

Add to the daily post-market cron job (runs after observation cycle + edge audit):

```python
# In cron prompt or script:
cd /opt/data && PYTHONPATH=/opt/data /opt/data/.venv/bin/python3 \
    scripts/export_strategy_factory_outputs.py \
    --format sql -o /tmp/strategy_factory_export.sql
```

### 6.2 Supabase (future)

When `--live-db` is implemented:

```bash
export SUPABASE_URL="https://[project].supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="eyJ..."

PYTHONPATH=/opt/data /opt/data/.venv/bin/python3 \
    scripts/export_strategy_factory_outputs.py \
    --live-db
```

### 6.3 Healthcheck Integration

Add export check to healthcheck:

```bash
# Verify export succeeds
PYTHONPATH=/opt/data /opt/data/.venv/bin/python3 \
    scripts/export_strategy_factory_outputs.py --format jsonl > /dev/null
echo "Export: $?"  # must be 0
```

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Ledger missing` | CSV file not found | Check file paths, run `check_market_data_freshness.py` |
| `Observation count N != expected 7` | New observations generated | Run Phase 6K protocol to approve new cohort, update `EXPECTED_OBSERVATION_COUNT` |
| `Duplicate observation IDs` | Ledger corruption | Restore from backup, investigate root cause |
| `sent_to_broker=True` | Critical safety violation | **DO NOT export.** Restore ledgers from backup. Investigate how broker flags were set. |
| `Ghost rows N < expected minimum 80` | Ghost ledger truncated | Check ghost ledger file, investigate |
| `No edge audit JSON found` | Edge audit not run today | Run `scripts/run_edge_audit.py` first |
| Export output is empty | Dry-run only — no stdout written | Check for validation errors on stderr |

---

## 8. Security

| Rule | Enforcement |
|---|---|
| No broker fields in export | `validate_ledgers()` rejects `sent_to_broker=True` or `broker_order_id` populated |
| No live DB writes without explicit flag | `--live-db` flag not implemented; default is dry-run |
| Source ledgers never mutated | Exporter reads only — no write operations on CSV paths |
| No credentials in export output | Passwords/tokens never appear in JSONL/SQL output |
| Idempotent inserts | All `INSERT ... ON CONFLICT DO NOTHING` — safe to run multiple times |

---

## 9. Schema Drift Management

When the approved observation count changes (new cohort approved):

1. Update `EXPECTED_OBSERVATION_COUNT` in `src/reporting/output_store_schema.py`
2. Update `EXPECTED_RESOLVED_COUNT` if newly generated observations are pending
3. Update `test_expected_observation_count` in `tests/reporting/test_output_store_schema.py`
4. Run `pytest tests/reporting/test_output_store_schema.py` to confirm
5. Re-run `pytest tests/reporting/test_export_strategy_factory_outputs.py` with real data
6. Commit schema + test changes as a contract update (similar to healthcheck manifest rebaseline)

---

## 10. Current Baseline

| Metric | Value |
|---|---|
| Export format | JSONL (default), SQL |
| Live DB writes | Disabled (--live-db not implemented) |
| Source of truth | CSV ledgers (unchanged) |
| Expected observation count | 7 |
| Expected resolved count | 7 |
| Expected pending count | 0 |
| Ghost rows minimum | 80 |
| Fail-closed | Yes — any validation error aborts export |
| Idempotent | Yes — ON CONFLICT DO NOTHING |