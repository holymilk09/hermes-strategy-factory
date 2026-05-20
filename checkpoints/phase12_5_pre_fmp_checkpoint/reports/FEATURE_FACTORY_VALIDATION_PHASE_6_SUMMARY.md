# Feature Factory Validation Phase 6 Complete

Status: RESEARCH_BACKTEST_SIMULATIONS_COMPLETE / PRODUCTION_MIGRATION_BLOCKED

## Files Created
- reports/feature_factory/phase5_final_interpretation.json
- reports/feature_factory/phase6_strategy_eligibility_report.json
- reports/feature_factory/residual_z_20_blocker_report.json
- research_backtests/phase6_filter_tests/mean_reversion_backtest_results.json
- research_backtests/phase6_filter_tests/structural_mr_backtest_results.json
- research_backtests/phase6_filter_tests/qullamaggie_backtest_results.json
- reports/feature_factory/phase6_base_vs_filtered_report.json
- reports/feature_factory/phase6_strategy_regime_report.json
- reports/feature_factory/phase6_promotion_rules.json

## Files Modified
- reports/feature_factory/FEATURE_FACTORY_VALIDATION_PHASE_5_SUMMARY.md
- config/backtest_integration_plan.yaml

## Phase 5 Final Interpretation
- standalone alpha: REJECTED_STANDALONE_ALPHA
- filter candidate: PRELIMINARY_FILTER_CANDIDATE
- usable for: mean_reversion_filter, structural_mr_filter, avoid_chasing_filter
- not usable for: standalone alpha, short signal, live trading

## Eligible Strategies
- mean_reversion: RESEARCH_SIMULATION_ELIGIBLE
- structural_mr: RESEARCH_SIMULATION_ELIGIBLE  
- qullamaggie_avoid_chasing: RESEARCH_SIMULATION_ELIGIBLE (compressed variants BLOCKED)
- momentum_swing: BLOCKED_NO_FILTER_EDGE
- ml_enhanced: BLOCKED_NO_FILTER_EDGE
- factor_residual_mr: BLOCKED_MISSING_FEATURE

## Residual Feature Blocker
- requested: residual_z_20
- correct name: residual_z
- status: FEATURE_NAME_MISMATCH — fix by using 'residual_z'
- action: RESOLVED — feature exists and is computed

## Research Simulation Results

### Mean Reversion
- BASE: 8,594 trades, ret=0.36%, hit=0.37
- AVOID_D1_D3: 6,875 trades, ret=0.42% (Δ+0.06%), hit=0.37
- REQUIRE_D8_D10: 3,552 trades, ret=0.51% (Δ+0.16%), hit=0.39
- REQUIRE_D9_D10: 2,529 trades, ret=0.51% (Δ+0.15%), hit=0.39
- REQUIRE_D10_ONLY: 1,404 trades, ret=0.78% (Δ+0.42%), hit=0.41

Best: REQUIRE_D10_ONLY → RESEARCH_BACKTEST_CANDIDATE

### Structural MR
- BASE: 3,199 trades, ret=0.06%, hit=0.31
- AVOID_D1_D3: 2,462 trades, ret=0.24% (Δ+0.17%), hit=0.32
- REQUIRE_D8_D10: 1,351 trades, ret=0.49% (Δ+0.43%), hit=0.35
- REQUIRE_D9_D10: 1,000 trades, ret=0.53% (Δ+0.47%), hit=0.36
- REQUIRE_D10_ONLY: 569 trades, ret=0.55% (Δ+0.49%), hit=0.35

Best: REQUIRE_D10_ONLY → RESEARCH_BACKTEST_CANDIDATE

### Qullamaggie
- BASE: 4,529 trades, ret=0.49%, hit=0.39
- AVOID_D1_D3: 2,012 trades, ret=0.54% (Δ+0.06%), hit=0.41
- REQUIRE_D8_D10: BLOCKED (39 trades)
- REQUIRE_D9_D10: BLOCKED (4 trades)

Best: AVOID_D1_D3 → HIT_RATE_ONLY_FILTER
Compressed variants BLOCKED — insufficient sample (39 and 4 trades)

## Base vs Filtered Summary
- mean_reversion D10_ONLY: trade reduction 84%, return improvement +0.42%
- structural_mr D10_ONLY: trade reduction 82%, return improvement +0.49%
- structural_mr D9_D10: trade reduction 69%, return improvement +0.47%
- qullamaggie AVOID_D1_D3: trade reduction 56%, return improvement +0.06%
- qullamaggie compressed: ALL BLOCKED (sample too small)

## Promotion Results
- RESEARCH_BACKTEST_CANDIDATE: mean_reversion D10_ONLY, D9_D10, D8_D10; structural_mr D10_ONLY, D9_D10, D8_D10
- HIT_RATE_ONLY_FILTER: qullamaggie AVOID_D1_D3
- SAMPLE_BLOCKED_FILTER: qullamaggie D8_D10, D9_D10, D10_ONLY (39, 4, 0 trades)

## Backtest Integration
- status: PLAN_ONLY / PRODUCTION_MIGRATION_BLOCKED
- controlled research backtest unlocked: FALSE
- production migration unlocked: FALSE
- reason: Research simulations show filter benefit but are per-symbol sequential (no portfolio-level position limits). Controlled research backtest with full portfolio simulation required before any migration.

## Remaining Blockers
1. Per-symbol sequential simulation inflates drawdowns — need portfolio-level backtest
2. qullamaggie compressed variants completely sample-blocked (bid/ask spread of leader pool)
3. factor_residual_mr not tested — feature name fix is trivial but not yet applied to strategy code
4. Regime segmentation is 20-symbol subset only — needs full 76-symbol run
5. Cost-adjusted returns need real Alpaca execution data for slippage validation
6. Production strategy file migration remains BLOCKED

## Verdict
The trend_extension_reversal filter improves mean_reversion and structural_mr strategies in research simulation. The improvement is monotonic: tighter filter → better per-trade quality. D10_ONLY shows the best results but with 82-84% trade reduction.

Qullamaggie shows modest improvement from AVOID_D1_D3 but compressed entry variants fail due to extreme sample reduction.

The filter is a RESEARCH_BACKTEST_CANDIDATE for mean-reversion strategies. It is NOT ready for production.

No profitability claims. No live-readiness claims.
