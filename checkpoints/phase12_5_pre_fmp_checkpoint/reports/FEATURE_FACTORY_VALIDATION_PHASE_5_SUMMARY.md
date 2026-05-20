# Feature Factory Validation Phase 5 Complete

Status: PRELIMINARY_AVOID_CHASING_FILTER

## Files Created
- reports/feature_factory/trend_extension_reversal_interpretation.md — signal interpretation
- reports/feature_factory/trend_extension_reversal_full_universe_confirmation.json — 76-symbol confirmation
- reports/feature_factory/trend_extension_threshold_test.json — 7 thresholds, all failed
- reports/feature_factory/strategy_conditioned_feature_test.json — 6 strategies × 5 variants
- reports/feature_factory/qullamaggie_conditioned_test.json — 3 conditions (1 blocked)
- reports/feature_factory/mean_reversion_conditioned_test.json — 2 conditions
- reports/feature_factory/filter_cost_impact_report.json — 5 strategies
- reports/feature_factory/phase5_classification.json — final classification
- reports/feature_factory/FEATURE_FACTORY_VALIDATION_PHASE_5_SUMMARY.md

## Files Modified
- config/backtest_integration_plan.yaml — trend_extension_reversal_set integration plan added

## Critical Finding: 30-Symbol vs 76-Symbol Discrepancy

30-symbol audit (Phase 4.5): D10-D1 spread +1.86%, clear D10 outperformance
76-symbol full universe (Phase 5): D10-D1 spread -0.19%, effectively zero

The signal DOES NOT GENERALIZE to the full universe as a standalone ranking factor.
The 30-symbol result was sample-specific.

## What DOES Survive

Hit rate monotonically improves from D1 (47.3%) to D10 (54.2%) on full universe.
Strategy-conditioned filter shows improvement:
- mean_reversion + D8-D10: +0.58% improvement (MR_FILTER_CONFIRMED)
- structural_mr + D8-D10: +0.71% improvement  
- qullamaggie + Avoid D1-D3: +0.50% improvement (but compressed sample BLOCKED at 51 events)
- momentum_swing + D10 only: +0.06% (negligible)
- ml_enhanced: no improvement

## Full Universe Confirmation
- symbols: 76
- IC raw (forward_return_20d): 0.0656
- IC excess SPY: 0.0388
- D10-D1 spread: -0.0019 (FAILED)
- Hit rate D1: 0.473 | Hit rate D10: 0.542
- status: WEAKENED_ON_FULL_UNIVERSE

## Threshold Test
- ALL FAILED — no threshold edge on full universe
- 30-symbol spread (+1.86%) vanishes on 76 symbols
- status: NO_THRESHOLD_EDGE

## Strategy-Conditioned Results
- Qullamaggie: leader_compressed BLOCKED (51 events only) — insufficient sample
- mean reversion: MR_FILTER_CONFIRMED (+0.58% improvement with D8-D10)
- momentum swing: no meaningful improvement
- factor residual MR: BLOCKED (residual_z_20 feature not in store)
- structural MR: improvement observed (+0.71%)
- ML enhanced: no improvement

## Cost/Filter Impact
- mean_reversion trade reduction: 21% with quality improvement +0.41%
- structural_mr trade reduction: 18% with quality improvement +0.71%
- status: FILTER_IMPROVES_COST_ADJUSTED_QUALITY for MR strategies only

## Signal Interpretation
- classification: PRELIMINARY_AVOID_CHASING_FILTER
- type: EXTREME_THRESHOLD_SIGNAL (only D1/D10 matter, and only on hit rate, not return)
- standalone alpha: NO — FAILED decile spread on full universe
- filter use: AVOID_CHASING + HIT_RATE_IMPROVER (MR strategies only)

## Backtest Integration
- status: PLAN_ONLY / BLOCKED_VALIDATION_FIRST
- migration unlocked: FALSE
- reason: Signal fails standalone validation on full universe. Survives only as conditional hit-rate filter in MR strategies. Not sufficient for strategy migration.

## Remaining Blockers
1. D10-D1 spread FAILS on full 76-stock universe — signal does not generalize
2. Qullamaggie leader+compressed sample BLOCKED (51 events) — cannot conclude
3. Factor residual MR BLOCKED — residual_z_20 feature not found in feature store
4. Hit-rate improvement exists but return improvement is modest
5. Strategy-conditioning requires per-strategy backtest simulation for conclusive evidence

## Verdict

The trend_extension_reversal signal is NOT a standalone alpha candidate.
It is a PRELIMINARY_AVOID_CHASING_FILTER — useful for:
- Improving hit rate in mean reversion and structural MR strategies
- Avoiding poor-timing entries in D1-D3
- It does NOT predict higher returns — only slightly better win rates

No emoji. No hype. No profitability claims. No live-readiness claims.

## Phase 6 Prep — Final Interpretation Stored
- standalone alpha: REJECTED_STANDALONE_ALPHA
- filter candidate: PRELIMINARY_FILTER_CANDIDATE
- next required step: strategy-level research backtest simulation
- residual_z_20 blocker: RESOLVED — feature is 'residual_z'
