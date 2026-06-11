#!/usr/bin/env bash
set -euo pipefail

cd /opt/data
mkdir -p backups

TS=$(date +%Y%m%d_%H%M%S)
OUT="backups/feature_factory_state_${TS}.tar.gz"

# Curated state-only artifact backup
# Excludes venvs, large caches, secrets, and unrelated logs.
tar -czf "$OUT" \
  --exclude='*.key' \
  --exclude='*.pem' \
  --exclude='*.env' \
  --exclude='*.token' \
  data/paper_observation \
  data/research/candidate_artifacts \
  reports/strategy_factory \
  filter_graveyard \
  scripts/run_daily_observation_ops.sh \
  scripts/run_relative_strength_observation_cycle.py \
  scripts/update_relative_strength_observation_outcomes.py \
  scripts/run_observation_drift_report.py \
  scripts/show_relative_strength_maturity_watchdog.py

SIZE=$(du -h "$OUT" | awk '{print $1}')
echo "BACKUP_DONE path=/opt/data/$OUT size=$SIZE"
