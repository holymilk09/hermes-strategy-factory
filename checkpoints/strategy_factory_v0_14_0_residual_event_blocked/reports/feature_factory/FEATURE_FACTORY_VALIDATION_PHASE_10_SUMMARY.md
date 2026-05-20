# Feature Factory Validation Phase 10 Complete — Residual Reversion

Status: FILTER_ONLY_CANDIDATE / EVENT_CONTEXT_INCOMPLETE / PRODUCTION_MIGRATION_BLOCKED

## Files Created
- phase10_pre_residual_snapshot.json
- phase10_residual_integrity_audit.json
- phase10_residual_model_quality_report.json
- phase10_residual_signal_definitions.json
- phase10_residual_standalone_event_study.json
- phase10_residual_random_baseline_report.json
- phase10_residual_strategy_conditioned_report.json
- phase10_retail_portfolio_report.json
- phase10_event_risk_limitation_note.md
- phase10_residual_decision_gate.json
- FEATURE_FACTORY_VALIDATION_PHASE_10_SUMMARY.md

## Files Modified
- config/backtest_integration_plan.yaml

## Critical Discovery
Residual features require sector ETFs in the symbol list. Fix: include XLK, XLF, XLV,
XLI, XLY, XLP, XLE, XLB, XLRE in feature factory requests. 76/76 stocks now have valid
residual_z after fix.

## Residual Integrity
- All 7 residual features present and computed for all 76 symbols
- 58,398 valid residual_z observations across universe
- NaN rate: ~7% (expected warmup for 60-day rolling regression)
- residual_z alias: RESOLVED (canonical name)

## Standalone Event Study

Z_NEG_1_5 (z <= -1.5, R² >= 0.10):
  5d: n=1,596, mean=+0.73%, hit=54.7%, cost_adj=+0.63%
  10d: n=1,588, mean=+1.11%, hit=53.7%, cost_adj=+1.01%
  20d: n=1,558, mean=+0.33%, hit=50.9%, cost_adj=+0.23%

Z_NEG_2_0 (z <= -2.0, R² >= 0.10):
  5d: n=348, mean=+1.69%, hit=58.3%, cost_adj=+1.59%
  10d: n=345, mean=+2.34%, hit=60.6%, cost_adj=+2.24%
  20d: n=338, mean=+2.49%, hit=57.1%, cost_adj=+2.39%

Z_NEG_2_5 (z <= -2.5, R² >= 0.10):
  20d: n=51, mean=+5.24%, hit=80.4%, cost_adj=+5.14%

## Random Baselines (500 permutations)
- Z_NEG_1_5: FAILS (actual 0.33% vs p95 3.15%)
- Z_NEG_2_0: BORDERLINE (actual 2.49% vs p95 6.04%)
- Z_NEG_2_5: BORDERLINE (actual 5.24% vs p95 6.97%)

No residual threshold decisively beats random pruning.

## Strategy-Conditioned
- mean_reversion + Z_NEG_2_0: 196 events, +2.58% vs BASE +1.86% → IMPROVES (+0.72%)
- structural_mr + Z_NEG_2_0: 71 events, +3.19% vs BASE +1.14% → IMPROVES (+2.05%)
- Z_NEG_1_5: FAILS both strategies (too broad, dilutes edge)

## Event Risk Limitation
- EVENT_CONTEXT_INCOMPLETE: residual reversion cannot distinguish temporary
  dislocation from real repricing without earnings/fundamental/event data

## Decision Gate
- classification: FILTER_ONLY_CANDIDATE
- Z_NEG_2_0 shows promise as strategy conditioner (+0.72-2.05% over base)
- BUT: fails standalone random baseline, small sample (196-338 events),
  event context incomplete
- No promotion to controlled research integration
- production migration: BLOCKED
- live trading: BLOCKED

## Remaining Blockers
1. EVENT_CONTEXT_INCOMPLETE — no earnings/fundamental/event data
2. Fails standalone random baseline
3. Small sample (196-338 events at Z_NEG_2_0, 51 at Z_NEG_2_5)
4. Production migration remains BLOCKED

No emoji. No hype. No profitability claims. No live-readiness claims.
