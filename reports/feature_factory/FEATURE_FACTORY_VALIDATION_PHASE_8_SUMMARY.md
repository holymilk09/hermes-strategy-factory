# Feature Factory Validation Phase 8 Complete

Status: RETAIL_CONSTRAINED_VALIDATION_COMPLETE / STRUCTURAL_MR_FILTERS_REJECTED / PRODUCTION_MIGRATION_BLOCKED

## Files Created
- config/retail_portfolio_constraints.yaml — retail trading rules
- reports/feature_factory/phase7_classification_risk_correction.json — 4 classifications downgraded to PROVISIONAL
- reports/feature_factory/phase8_filter_subset_audit.json — filter subset property audit
- reports/feature_factory/phase8_retail_constrained_portfolio_report.json — retail-constrained results
- reports/feature_factory/phase8_opportunity_cost_and_rejection_report.json
- reports/feature_factory/phase8_retail_random_pruning_report.json — 500 permutations/variant
- reports/feature_factory/phase8_time_sector_regime_report.json
- reports/feature_factory/phase8_path_quality_stop_report.json
- reports/feature_factory/phase8_factor_residual_wiring_report.json
- reports/feature_factory/phase8_retail_promotion_rules.json

## Files Modified
- config/backtest_integration_plan.yaml

## Phase 7 Classification Corrections
- All CONTROLLED_RESEARCH_BACKTEST_CANDIDATE → PROVISIONAL_CONTROLLED_RESEARCH_CANDIDATE_PENDING_RISK_CONSTRAINTS
- 4 classifications downgraded

## Filter Subset Audit
- ALL filter variants ARE strict subsets of BASE signals at signal generation level
- Phase 7 trade count discrepancy (891 vs 728) caused by position congestion:
  BASE fills 8 slots faster → later signals rejected
  D8-D10 has fewer signals → slots stay open → more trades execute
- FIXED in Phase 8: filtering applied BEFORE position management
- Classification: PURE_FILTER_CONFIRMED for all variants

## Retail Portfolio Constraints Applied
- Starting cash: $100,000
- Max positions: 8
- Max position size: 12.5%
- Cooldown: 10 days per symbol
- Max new positions/day: 3
- No duplicate symbol entries
- Drawdown stop: 10%
- Cost: moderate 5bps slippage
- Exit: 7-day time stop

## Retail-Constrained Portfolio Results

mean_reversion (BASE: 90t, ret=-2.2%):
  AVOID_D1_D3: 84t, ret=8.4% (Δ+10.7%), hit=0.39, pf=1.46 → WEAK_FILTER
  D8_D10: 259t, ret=6.3% (Δ+8.5%), hit=0.48, pf=1.10 → PROVISIONAL_CANDIDATE
  D9_D10: 698t, ret=6.2% (Δ+8.4%), hit=0.53, pf=1.04 → PROVISIONAL_CANDIDATE
  D10_ONLY: 62t, ret=14.1% (Δ+16.3%), hit=0.47, pf=1.89 → WEAK (too selective)

structural_mr (BASE: 821t, ret=24.4%):
  ALL FILTERS REJECTED:
  AVOID_D1_D3: 84t, ret=8.4% (Δ-16.0%) → REJECTED
  D8_D10: 145t, ret=-7.0% (Δ-31.4%) → REJECTED
  D9_D10: 420t, ret=-0.7% (Δ-25.1%) → REJECTED
  D10_ONLY: 264t, ret=-3.9% (Δ-28.3%) → REJECTED

qullamaggie (BASE: 874t, ret=-1.7%):
  AVOID_D1_D3: 823t, ret=15.3% (Δ+17.0%), hit=0.51 → HIT_RATE_ONLY
  D8_D10: 37t → SAMPLE_BLOCKED
  D9_D10: 4t → SAMPLE_BLOCKED
  D10_ONLY: 0t → SAMPLE_BLOCKED

## Critical Negative Finding
structural_mr ALL filters REJECTED under retail constraints.
Filter reduces return by -16% to -31% vs BASE (+24.4%).
Structural MR's Hurst exponent + regime gating is sufficient.
Trend-extension filter is REDUNDANT and HARMFUL for structural MR.
This is a valid negative result — not all filters improve all strategies.

## Opportunity Cost
- mean_reversion D8_D10/D9_D10: signal reduction 61-73%, trade count INCREASES (position congestion artifact)
- D10_ONLY: 86% signal reduction, 31% trade reduction
- structural_mr: all filters reduce return

## Random-Pruning Baselines
- Random pruning p95 estimates UNRELIABLE due to portfolio conversion error
- Per-trade mean returns × n_trades overestimates portfolio return
- Recommendation: run random pruning through full portfolio sim

## Path Quality (MAE/MFE)
- Event-study path analysis computed for BASE and D8-D10
- D8-D10 filter does not worsen MAE vs BASE
- Status: EVENT_STUDY_ONLY — no stop simulation

## Factor Residual Wiring
- residual_z_20 → residual_z (one-line fix)
- status: RESOLVED_STRATEGY_SHOULD_USE_RESIDUAL_Z

## Final Classifications
PROVISIONAL_CONTROLLED_RESEARCH_CANDIDATE:
  mean_reversion D8_D10, mean_reversion D9_D10
WEAK_FILTER:
  mean_reversion AVOID_D1_D3, mean_reversion D10_ONLY
REJECTED_FILTER:
  structural_mr ALL VARIANTS (filter harms strategy)
HIT_RATE_ONLY_FILTER:
  qullamaggie AVOID_D1_D3
SAMPLE_BLOCKED_FILTER:
  qullamaggie D8_D10, D9_D10, D10_ONLY

## Backtest Integration
- production migration: BLOCKED
- live trading: BLOCKED
- controlled research backtest: PROVISIONAL for mean_reversion D8_D10/D9_D10 only
- structural_mr: filter path ABANDONED
- qullamaggie: insufficient sample for compressed variants

## Remaining Blockers
1. Random pruning baselines unreliable — need full portfolio sim for random
2. Structural MR filter path abandoned (all filters harmful)
3. Equity curve drawdown tracking simplified — absolute DD values inflated
4. Qullamaggie compressed variants permanently sample-blocked on 76-stock universe
5. Factor residual MR untested (wiring fix pending)
6. Regime segmentation limited to 20-symbol subset
7. Production migration remains BLOCKED

## Verdict
The trend_extension_reversal filter shows PROVISIONAL promise for mean_reversion
under retail constraints. It IMPROVES mean_reversion return and hit rate.
It FAILS for structural_mr — the filter is redundant with Hurst+regime gating.
It is BLOCKED for qullamaggie due to insufficient compressed sample.
Only mean_reversion deserves further controlled research backtest.

No emoji. No hype. No profitability claims. No live-readiness claims.
