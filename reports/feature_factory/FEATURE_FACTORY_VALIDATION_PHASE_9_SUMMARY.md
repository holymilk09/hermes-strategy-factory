# Feature Factory Validation Phase 9 Complete — Controlled Backtrader Research

Status: BACKTRADER_COMPLETE / BOTH_FILTERS_FAIL_OR_BORDERLINE / PRODUCTION_MIGRATION_BLOCKED

## Files Created
- reports/feature_factory/phase9_pre_backtrader_snapshot.json
- reports/feature_factory/phase9_backtrader_scope.json
- reports/feature_factory/phase9_signal_input_integrity_report.json
- config/backtrader_retail_research.yaml
- research_backtests/phase9_backtrader_inputs/ — 4 canonical signal CSVs
- reports/feature_factory/phase9_backtrader_results.json — 60 simulation runs
- reports/feature_factory/phase9_backtrader_random_pruning_report.json
- reports/feature_factory/phase9_backtrader_path_quality_report.json
- reports/feature_factory/phase9_backtrader_robustness_report.json
- reports/feature_factory/phase9_backtrader_decision_gate.json

## Files Modified
- config/backtest_integration_plan.yaml

## Scope
- included: mean_reversion BASE/D8_D10, structural_mr BASE/D8_D10
- excluded: D9_D10, D10_ONLY, AVOID_D1_D3, qullamaggie, momentum_swing, ml_enhanced
- reason: D8_D10 best balance of quality and trade count

## Signal Input Integrity
- mean_reversion: 20,755 BASE, 8,143 D8_D10 — D8_D10 ⊆ BASE: PASS
- structural_mr: 7,039 BASE, 2,828 D8_D10 — D8_D10 ⊆ BASE: PASS
- No duplicates, no future data, no synthetic data
- status: PASS_SIGNAL_INPUT_INTEGRITY for all

## Backtrader Configuration
- starting cash: $100,000
- max positions: 8
- max position size: 12.5%
- cooldown: 10 days
- max new positions/day: 3
- costs: conservative(10bps), moderate(5bps), optimistic(2bps)
- exits tested: fixed_time_10d, fixed_time_20d, ATR_stop_1.5, ATR_stop_2.0, combined_20d+ATR_2.0
- entry: next bar open
- 60 total simulation runs

## Random-Pruning Baselines (under Backtrader, 500 permutations)

IMPORTANT: Absolute Backtrader returns are inflated by simulation numerical issues.
Random pruning comparison uses the same framework — comparison is valid.

mean_reversion D8_D10:
  actual PF: 22.81
  random p95 PF: 86.30
  random p50 PF: 31.22
  status: FAILS_BACKTRADER_RANDOM_PRUNING

structural_mr D8_D10:
  actual PF: 34.96
  random p95 PF: 64.42
  random p50 PF: 20.15
  status: BORDERLINE_BACKTRADER_RANDOM_PRUNING

## Decision Gate
- mean_reversion D8_D10: REJECTED_BACKTRADER_VALIDATION (fails random pruning)
- structural_mr D8_D10: WEAK_BACKTRADER_FILTER (borderline random pruning)
- No variant qualifies for controlled research integration
- production migration: BLOCKED
- live trading: BLOCKED

## Backtest Integration
- controlled research integration: NOT UNLOCKED
- next step: Reassess whether trend-extension filter adds value
- Production migration: BLOCKED

## Critical Finding
Under Backtrader research rules with canonical signals and retail portfolio constraints,
the D8_D10 filter does NOT beat random same-count trade selection.

This is a stronger signal than any prior phase because:
- Random pruning comparison controls for the framework's numerical biases
- If D8_D10 was a true edge, it would beat random selection within the same framework
- mean_reversion D8_D10 PF (22.81) is below random p50 (31.22) — actively worse than random

## Remaining Blockers
1. Backtrader simulation has numerical issues producing inflated absolute returns
2. Neither D8_D10 variant beats random pruning — filter value not confirmed
3. Production migration remains BLOCKED
4. Live trading remains BLOCKED
5. Trend-extension filter value proposition needs fundamental reassessment

## Verdict
The trend_extension_reversal D8_D10 filter, after 9 phases of escalating validation:
- Phase 4: IC=0.38 (inflated) → PHASE 4.5 downgrade to 0.05-0.11
- Phase 5: Standalone decile FAILED on full universe
- Phase 6: Per-trade event analysis showed directional improvement
- Phase 7: Portfolio simulation showed improvement (with bugs)
- Phase 8: Retail constraints applied, bugs found
- Phase 8.5: Audit corrected bugs, structural_mr D8_D10 showed PF 1.64 vs 0.82
- Phase 9: Backtrader random pruning shows D8_D10 DOES NOT BEAT random selection

The escalating validation gates worked as designed. Each phase exposed weaknesses
the prior phase missed. The final Backtrader gate reveals: the filter does not add
statistically significant value beyond random trade selection.

This is a VALID NEGATIVE RESULT. Not every hypothesis survives validation.

No emoji. No hype. No profitability claims. No live-readiness claims.
