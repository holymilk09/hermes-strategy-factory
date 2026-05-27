# Phase 6I — Strategy Factory Organization, Integration, and Roadmap Hardening

Date: 2026-05-27
Branch: trust-calibration-working
Commit: b8280d7

## Current Repo Status

Branch: trust-calibration-working
Commit: b8280d7 — "Wire ghost recording into observation scripts"
Ahead/behind: 0/0 (synced with origin/trust-calibration-working)
Dirty tracked files: 4 (checkpoints/.last_prune, config/backtest_integration_plan.yaml, reports/strategy_factory/feature_factory_healthcheck.{json,md})
Untracked top-level: SOUL.md, backtest_engine.py, config.yaml, debug_signals.py, 6+ strategy files, 6+ ml files, hermes-agent/ (subrepo), reports/ (generated), scripts/ (new), tests/ (new), docs/ (new), data/ (new)
Tests: 70/70 reporting tests pass
Healthcheck: HEALTHCHECK_PASS_CONTINUE_WAITING
Production/live/broker/shadow: ALL BLOCKED

## Purpose

This phase documents the canonical architecture of the Hermes Strategy Factory to prevent duplication, reduce operational risk, and prepare the repo for retail-facing Edge Sheet product launch. No files are moved, deleted, or renamed. No strategy logic, thresholds, scoring, features, or maturity rules are changed.

## Key Artifacts Created

- `docs/strategy_factory/REPO_ORGANIZATION_MAP.md` — canonical owner map, overlap risk, do-not-duplicate rules
- `docs/strategy_factory/OPERATOR_RUNBOOK.md` — daily after-market maturity update runbook
- `docs/strategy_factory/PRODUCT_ROADMAP.md` — staged roadmap from maturity to ML calibration
- `docs/strategy_factory/OUTPUT_CONTRACTS.md` — canonical Setup Card fields and retail label spec
- `docs/strategy_factory/SAFETY_GUARDRAILS.md` — model, data, product, and engineering guardrails
- This file — integration plan and risk tracker

## Open Risks (from Missing Risks Checklist)

See SAFETY_GUARDRAILS.md for full risk audit. Key open items:

- Small sample false confidence — covered by HEALTHCHECK_PASS_CONTINUE_WAITING
- Over-filtering — covered by ghost ledger
- Survivorship bias — PARTIAL, needs explicit detection
- Corporate actions — ABSENT, needs dividend/split adjustment logic
- Popular ticker bias — PARTIAL, needs documentation in Edge Sheet
- Timeframe confusion — PARTIAL, needs per-horizon tracking if adding more timeframes
- Marketing performance claims — covered by compliance language
- AI hallucination risk — COVERED (no AI assistant in MVP)

## Next Phase

Continue daily maturity only. No feature work.
Commercial packaging and ML-0 dataset are gated behind completed outcomes.

No strategy behavior changed.
No thresholds changed.
No scoring changed.
No maturity behavior changed.
No broker/live/shadow behavior changed.
No files moved, deleted, renamed, or cleaned.