# Phase 11.5 — Residual Diagnostic Packet

Timestamp: 20260518_111653

## 1. Current Classification

EVENT_CONTEXT_BLOCKED_FILTER
Standalone alpha: NO
Filter candidate: YES (mean_reversion, structural_mr)
Production migration: BLOCKED
Live trading: BLOCKED

## 2. Residual Feature Health

76 stocks, 58,398 valid residual_z observations
NaN rate: 1.0 (expected warmup)
Sector ETFs: 
Mean R²: 0.0000
Median R²: 0.0000
Low R² (< 0.10): 76 symbols
Half-life median: 0.0 days
Status: RESIDUAL_FEATURES_WARN_LOW_R2

## 3. Standalone Event Study

| Variant | Horizon | Events | Mean | Hit | Cost Adj | Rand p95 | Status |
|---|---|---|---|---|---|---|---|
| Z_NEG_1_5 | 5d | 1596 | 0.73% | 0.547 | 0.63% | 3.1514 | FAILS_RANDOM_BASELINE |
| Z_NEG_1_5 | 10d | 1588 | 1.11% | 0.537 | 1.01% | 3.1514 | FAILS_RANDOM_BASELINE |
| Z_NEG_1_5 | 20d | 1558 | 0.33% | 0.509 | 0.23% | 3.1514 | FAILS_RANDOM_BASELINE |
| Z_NEG_2_0 | 5d | 348 | 1.69% | 0.583 | 1.59% | 6.0399 | BORDERLINE |
| Z_NEG_2_0 | 10d | 345 | 2.34% | 0.606 | 2.24% | 6.0399 | BORDERLINE |
| Z_NEG_2_0 | 20d | 338 | 2.49% | 0.571 | 2.39% | 6.0399 | BORDERLINE |
| Z_NEG_2_5 | 5d | 51 | 2.89% | 0.726 | 2.79% | 6.9696 | BORDERLINE |
| Z_NEG_2_5 | 10d | 51 | 4.98% | 0.784 | 4.88% | 6.9696 | BORDERLINE |
| Z_NEG_2_5 | 20d | 51 | 5.24% | 0.804 | 5.13% | 6.9696 | BORDERLINE |

Verdict: No residual threshold decisively beats random pruning.
Z_NEG_2_0 is BORDERLINE. Z_NEG_2_5 is SAMPLE_BLOCKED (51 events).

## 4. Strategy-Conditioned

| Strategy | Variant | Events | Mean | Hit | Imp vs Base | Status |
|---|---|---|---|---|---|---|
| mean_reversion | Z_NEG_1_5 | 829 | 0.62% | 0.517 | -1.25% | RESIDUAL_FILTER_FAILS_SETUP |
| mean_reversion | Z_NEG_2_0 | 196 | 2.58% | 0.587 | +0.72% | RESIDUAL_FILTER_IMPROVES_SETUP |
| structural_mr | Z_NEG_1_5 | 250 | -0.54% | 0.508 | -1.68% | RESIDUAL_FILTER_FAILS_SETUP |
| structural_mr | Z_NEG_2_0 | 71 | 3.19% | 0.606 | +2.05% | RESIDUAL_FILTER_IMPROVES_SETUP |

Verdict: Z_NEG_2_0 improves MR (+0.72%) and SMR (+2.05%) but samples are small (71-196).

## 5. Event Proxy Diagnostic

| Flag | Events | Overlap % | Improved? |
|---|---|---|---|
| large_gap_down | 72 | ?% | NO |
| large_gap_up | 0 | ?% | NO |
| abnormal_volume_spike | 268 | ?% | NO |
| extreme_single_day_return | 402 | ?% | NO |
| extreme_range_expansion | 0 | ?% | NO |

Verdict: PRICE_VOLUME_PROXY_INSUFFICIENT — need FMP for real event detection.

## 6. Missing: Portfolio Random-Pruning

Status: TIMED_OUT
Root cause: Feature generation (180s/300s) + bar-level event flags
Fix: Cache features, 250 permutations first pass
Plan: phase11_5_optimized_random_pruning_plan.md

## 7. FMP / Event Data Need

Spec: reports/data_sources/fmp_need_spec_for_residual_filter.md
Required: earnings dates, surprises, guidance, analyst changes, sector, market cap
Decision: ADD_FMP_NEXT — evaluate and integration-plan in Phase 12

## 8. Current Blockers

1. Portfolio random-pruning timed out — needs optimized rerun
2. EVENT_CONTEXT_INCOMPLETE — price proxies insufficient, needs FMP
3. Strategy-conditioned samples small (71-196 events)
4. Production migration: BLOCKED
5. Live trading: BLOCKED

## 9. Next Allowed Step

1. Optimized residual portfolio random-pruning (Phase 11.5 rerun)
2. FMP event data evaluation plan (Phase 12)
3. Do NOT: tune thresholds, integrate FMP prematurely, claim alpha

No profitability claims. No live-readiness claims.
