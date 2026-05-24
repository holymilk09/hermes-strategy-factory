# Feature Factory Healthcheck Report

Timestamp: 2026-05-24T05:13:14.217942+00:00

## Summary

**Decision:** HEALTHCHECK_PASS_CONTINUE_WAITING

| Check | Status |
|-------|--------|
| Scripts present | PASS |
| Ledgers parse | PASS |
| Observation invariants | PASS |
| Hard blocks active | PASS |
| Backup exists | PASS |
| Smoke tests pass | PASS |

## Observation Invariants

- Total: 6 (expected 6)
- Pending: 6 (expected 6)
- Resolved: 0 (expected 0)
- Symbols match: YES
- Duplicate IDs: 0 (expected 0)
- sent_to_broker_any: false (PASS)
- broker_order_id populated: false (PASS)

## Hard Blocks
- Production: BLOCKED
- Live: BLOCKED
- Broker: BLOCKED
- Shadow: BLOCKED

## Backup
- Path: backups/feature_factory_state_20260524_014249.tar.gz
- Size: 29M

## Smoke Tests
- status: PASS (exit=0)
- maturity_watchdog: PASS (exit=0)
- no_trading_leakage: PASS (exit=0)

## Required Scripts
- run_relative_strength_observation_cycle.py: present
- update_relative_strength_observation_outcomes.py: present
- run_observation_drift_report.py: present
- show_relative_strength_maturity_watchdog.py: present
- show_feature_factory_status.py: present
- verify_no_trading_leakage.py: present
- snapshot_feature_factory_state.py: present
- backup_feature_factory_state.sh: present
