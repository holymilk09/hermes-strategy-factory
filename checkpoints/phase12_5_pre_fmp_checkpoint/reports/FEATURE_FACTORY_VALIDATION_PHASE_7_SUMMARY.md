# Feature Factory Validation Phase 7 Complete

Status: PORTFOLIO_VALIDATION_COMPLETE / CONTROLLED_RESEARCH_CANDIDATES_IDENTIFIED / PRODUCTION_MIGRATION_BLOCKED

## Files Created
- reports/feature_factory/phase6_classification_correction.json — 3 classifications corrected
- reports/feature_factory/phase7_portfolio_simulation_report.json — 3 strategies x 5 variants
- reports/feature_factory/phase7_opportunity_cost_report.json — 10 variant analyses
- reports/feature_factory/phase7_random_pruning_baseline_report.json — 500 permutations/variant
- reports/feature_factory/phase7_distribution_diagnostics_report.json — 13 distribution profiles
- reports/feature_factory/phase7_mae_mfe_stop_report.json — 9 MAE/MFE profiles
- reports/feature_factory/phase7_factor_residual_wiring_report.json — wiring audit
- reports/feature_factory/phase7_promotion_rules.json — final classifications
- reports/feature_factory/FEATURE_FACTORY_VALIDATION_PHASE_7_SUMMARY.md

## Files Modified
- config/backtest_integration_plan.yaml — phase7 results added

## Phase 6 Classification Corrections
- mean_reversion AVOID_D1_D3: HIT_RATE_ONLY -> WEAK_RETURN_IMPROVEMENT (hit rate unchanged)
- structural_mr AVOID_D1_D3: RESEARCH_CANDIDATE -> WEAK_RETURN_IMPROVEMENT
- qullamaggie AVOID_D1_D3: HIT_RATE_ONLY -> WEAK_RETURN_IMPROVEMENT

## Portfolio Simulations
Portfolio-level (8 positions max, sequential bar scanning, simultaneous entries managed):
- mean_reversion D8_D10: beats BASE, beats random pruning (p95 baseline)
- mean_reversion D9_D10: beats BASE, beats random pruning
- structural_mr D8_D10: beats BASE, beats random pruning (strongest)
- structural_mr D9_D10: beats BASE, beats random pruning
- AVOID_D1_D3: FAILS for MR and SMR (worsens portfolio return)
- qullamaggie compressed variants: ALL SAMPLE BLOCKED

Note: Absolute returns inflated by simplified portfolio sim. Direction only.

## Opportunity Cost
- D8_D10: increases trade count for MR, maintains for SMR — no missed opportunity
- AVOID_D1_D3: reduces trades 7-21% AND worsens return — negative opportunity value
- D10_ONLY: reduces trades 40%, return improvement weakens — too restrictive
- Best: D8_D10 for both MR and SMR

## Random-Pruning Baselines (500 permutations)
- mean_reversion D8_D10: BEATS_RANDOM_PRUNING (actual >> p95=2.7%)
- mean_reversion D9_D10: BEATS_RANDOM_PRUNING (actual >> p95=2.9%)
- mean_reversion D10_ONLY: BEATS_RANDOM_PRUNING (borderline: 4.1% vs 3.4%)
- structural_mr D8_D10: BEATS_RANDOM_PRUNING
- structural_mr D9_D10: BEATS_RANDOM_PRUNING
- structural_mr D10_ONLY: BEATS_RANDOM_PRUNING
- AVOID_D1_D3: FAILS for MR/SMR, BEATS for QULL

## Distribution Diagnostics
- Returns are positive across filtered D8-D10 variants
- Some tail dependence but median returns are also positive
- D8_D10 filter does NOT worsen distribution shape vs BASE

## MAE/MFE
- Event-study path analysis computed
- D8_D10 filter does not worsen adverse excursion vs BASE
- Status: EVENT_STUDY_ONLY — full stop simulation not included

## Factor Residual Wiring
- residual_z_20: MISMATCH
- Correct feature: residual_z
- Status: RESOLVED_STRATEGY_SHOULD_USE_RESIDUAL_Z
- Fix: one-line rename in strategy code

## Final Classifications
- CONTROLLED_RESEARCH_BACKTEST_CANDIDATE:
  mean_reversion D8_D10, mean_reversion D9_D10,
  structural_mr D8_D10, structural_mr D9_D10
- WEAK_FILTER:
  mean_reversion D10_ONLY, structural_mr D10_ONLY
- REJECTED_FILTER:
  mean_reversion AVOID_D1_D3, structural_mr AVOID_D1_D3
- HIT_RATE_ONLY_FILTER: qullamaggie AVOID_D1_D3
- SAMPLE_BLOCKED_FILTER: qullamaggie D8_D10, D9_D10, D10_ONLY

## Backtest Integration
- production migration: BLOCKED
- controlled research backtest unlocked: TRUE (D8_D10 variants only)
- live trading: BLOCKED
- reason: Portfolio sim shows directional improvement. Requires full backtrader
  simulation with real cost model, proper stop/exit/sizing, and drawdown tracking.

## Remaining Blockers
1. Portfolio sim simplified — needs full backtrader integration
2. Qullamaggie compressed variants sample-blocked (55, 4, 0 trades)
3. Factor residual MR untested (wiring fix trivial but not applied)
4. MAE/MFE without stop/exit simulation
5. Regime segmentation limited to 20-symbol subset
6. Absolute portfolio returns unreliable (direction only valid)
7. Production migration remains BLOCKED

No emoji. No hype. No profitability claims. No live-readiness claims.
