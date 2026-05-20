# Optimized Residual Random-Pruning Plan

## Method
1. Load pre-cached features + event flags from Phase 10/11 (no regeneration)
2. Build trade candidate matrices once
3. Run 250 permutations first
4. If actual PF > p95 or < p50: classify as PASS or FAIL with LOWER_CONFIDENCE
5. If borderline: run additional 250-750 permutations
6. Process mean_reversion first, structural_mr second

## Statuses
- PRELIMINARY_BEATS_RANDOM: actual > p95 with 250 perms
- PRELIMINARY_FAILS_RANDOM: actual < p50 with 250 perms
- PRELIMINARY_BORDERLINE: p50 < actual < p95
- FULL_RANDOM_PRUNING_REQUIRED: need 500-1000 perms

## Execution Order
1. mean_reversion + Z_NEG_2_0
2. structural_mr + Z_NEG_2_0 (only if MR passes)
