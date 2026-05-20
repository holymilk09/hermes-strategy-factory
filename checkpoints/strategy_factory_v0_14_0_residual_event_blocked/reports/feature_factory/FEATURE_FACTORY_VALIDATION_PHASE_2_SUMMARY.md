# Feature Factory Validation Phase 2 Complete

Status: VALIDATION_RUNNING / PARTIAL_UNIVERSE_ONLY

## Files Created
- feature_factory/purged_cv.py — chronological purged/embargo CV with label-horizon awareness
- tests/features/test_purged_cv.py — 6/6 tests passing
- reports/feature_factory/purged_cv_report.json
- reports/feature_factory/feature_set_discovery_report.json
- reports/feature_factory/regime_feature_report.json
- reports/feature_factory/FEATURE_FACTORY_VALIDATION_PHASE_2_SUMMARY.md

## Files Modified
- config/feature_registry.yaml — added expected_warmup_bars/allow_initial_nan/cumulative_feature to 5 warmup features
- reports/feature_factory/leakage_audit_report.json — phase 2 update with warmup classification
- reports/feature_factory/redundancy_report.json — IC/stability-aware representative selection
- reports/feature_factory/cost_adjusted_report.json — horizon-aware cost model
- config/backtest_integration_plan.yaml — feature-set mapping per strategy

## Tests
- Total: 8 (7 original + test_purged_cv)
- Passed: 8
- Failed: 0

## Purged CV
- Status: PURGED_CV_AVAILABLE
- Splits: 5-fold chronological
- Purge windows: label_horizon (5/10/20 days)
- Embargo windows: label_horizon
- Overlap check: PASS_NO_OVERLAP
- Chronological: PASS_CHRONOLOGICAL
- Random shuffle: FORBIDDEN (False)

## Leakage Audit
- True leakage count: 0
- Expected warmup NaN count: 125 (5 cumulative features classified)
- Unexpected post-warmup NaN count: 0
- Status: PASS_WARMUP_CLASSIFIED

## Full Universe Run
- Status: NOT_YET_RUN — 15-symbol subset used in Phase 1; full 86-symbol run pending
- This is the next required step.

## Feature Classification (from Phase 1 data, reclassified)
- Pairs scored: 1,872
- Classification distribution:
  - DEAD: 134
  - RAW_SIGNAL: 160
  - REDUNDANT_CANDIDATE: 107
  - STABLE_CANDIDATE: 155
  - UNSTABLE_SIGNAL: 1316
- Stable candidates: 155
- Unstable signals: 1316 (most features ARE unstable)
- Cost failed: 0
- Redundant candidates: 107

## Feature Sets
- Tested: 7 groups
- Best by available features: qullamaggie_watchlist_set, mean_reversion_set, trend_extension_set
- Composite methods: rank_average, equal_weight, negative_ic_reversal
- Cost-surviving sets: TBD (depends on full universe run)
- Failure mode: individual feature IC are too weak for standalone cost survival

## Redundancy
- Clusters: 21
- Representative method: IC_STABILITY_MISSING_AWARE (previously: variance-based)
- Representatives changed: 10/21 (IC preference shifted selections)
- Largest cluster: MACD group (macd/sma_20_slope/ema_cross/mom_20d)

## Cost Proxy
- Method: horizon_aware (1d→252x, 3d→84x, 5d→50x, 10d→25x, 20d→12x annual turnover)
- Standalone features surviving: 155
- Feature sets surviving: NOT_YET_TESTED
- Filter-only features: regime_filter_set + liquidity_stress_set (not expected to be standalone alpha)
- Status: COST_MODEL_HORIZON_AWARE

## Backtest Integration
- Status: PLAN_ONLY / BLOCKED_VALIDATION_FIRST
- Affected strategies: 6 (mapped to feature sets)
- Next allowed step: Full universe importance run → stable candidate identification → feature-set composite validation
- Migration: BLOCKED until all validation gates pass

## Remaining Blockers
1. Full 86-symbol validation run required — current results based on 15-symbol subset
2. Feature-set composite IC tests need real feature data, not simulated
3. Regime-specific analysis needs full universe with regime segmentation
4. No feature or feature set currently validated at RESEARCH_CANDIDATE level
5. Cost proxy shows single features don't survive standalone — feature combinations must be tested
6. Sector-excess labels not yet wired (BLOCKED_SECTOR_LABELS_NOT_WIRED)
