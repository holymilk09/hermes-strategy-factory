# Phase 12.5 Pre-FMP Checkpoint

## Status
CREATED: 20260518_123708
GATE: PENDING

## Why This Checkpoint Exists
Freeze validated research state before any FMP event-data work.
Prevent accidental loss of trend-extension rejection, residual_z candidate status,
event-blocked classification, and alpha graveyard entries.

## Current Research State
- trend_extension_reversal: REJECTED_FILTER / ARCHIVED
- residual_reversion: CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED
- FMP: JUSTIFIED_FOR_SANDBOX_ONLY — not integrated
- production migration: BLOCKED
- live trading: BLOCKED

## What Is Preserved
- configs: 6 files
- reports: 18 phase summaries
- alpha graveyard: trend_extension_reversal_filter.md
- residual decision state: residual_reversion_state.json
- cache manifest: 76-symbol ETF-inclusive feature cache
- backtest integration state: BLOCKED

## Current Valid Decisions
1. Trend-extension reversal is REJECTED. Do not rescue.
2. Residual_z <= -2.0 is NOT standalone alpha.
3. Residual_z + GOOD/ACCEPTABLE fit passes strategy-conditioned random pruning.
4. Event context remains INCOMPLETE.
5. FMP is allowed only as sandbox event-risk blocker.
6. Production and live trading remain BLOCKED.

## Forbidden Actions
- Do not retune trend-extension thresholds
- Do not claim residual_z as standalone alpha
- Do not promote residual_z to production
- Do not use FMP as alpha source or trade trigger
- Do not unlock production migration

## Next Allowed Step
FMP sandbox evaluation only (Phase 13)

## Restore Notes
To restore: copy checkpoint files back to original paths.
Cache remains at cache/phase12_etf_inclusive_features/ — reuse from there.
