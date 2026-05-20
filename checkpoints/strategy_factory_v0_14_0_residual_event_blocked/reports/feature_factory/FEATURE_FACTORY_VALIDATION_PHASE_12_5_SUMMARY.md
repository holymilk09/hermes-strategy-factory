# Feature Factory Validation Phase 12.5 Complete — Repaired Random Pruning

Status: CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED

## Bug Audit
- BUG CONFIRMED: Phase 12 random pruning used ALL residual events without strategy signals
- Fix: Apply strategy signal filter (RSI(2)<30, Hurst+regime) BEFORE residual_z filter
- Candidate pools now correct: BASE strategy signals + Z_NEG_2_0 + R² filter

## Strategy-Conditioned Random Pruning (250 perms, corrected pools)

mean_reversion/ALL:       n=196, actual=2.58%, p95=10.49% → BORDERLINE
mean_reversion/GOOD:      n=188, actual=2.65%, p95=2.21%  → BEATS_STRATEGY_RANDOM
structural_mr/ALL:        n=71,  actual=3.19%, p95=10.62% → BORDERLINE
structural_mr/GOOD:       n=67,  actual=3.26%, p95=1.41%  → BEATS_STRATEGY_RANDOM

Key: GOOD/ACCEPTABLE fit filter transforms BORDERLINE into BEATS.
Residual_z is only meaningful when the benchmark relationship is strong enough.

## Portfolio Random Pruning
mean_reversion/GOOD:      pf=1.93, p95_pf=1.66 → BEATS_PORTFOLIO_RANDOM
structural_mr/GOOD:       pf=2.19, p95_pf=1.26 → BEATS_PORTFOLIO_RANDOM

## Decision
- final: CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED
- FMP: ADD_FMP_NEXT_FOR_EVENT_BLOCKER
- production: BLOCKED
- live: BLOCKED

## The Two-Gate Story

Good/acceptable residual fit (R² >= 0.20) is the critical enabler.
Without it: BORDERLINE at best.
With it: BEATS random pruning at both candidate and portfolio level.

The filter only works on symbols where the sector ETF regression
actually explains the stock's returns. This is a valid edge —
not all residual_z signals are created equal.

No profitability claims. No live-readiness claims.
