# Handoff reconciliation — ChatGPT claims vs working-branch code

**Date:** 2026-09-29
**Branch inspected:** `origin/trust-calibration-working` @ `1f1a238eb8c17f2340699ed6d6a30017fe3eeb13`
**Method:** `git show` / `git grep` on the exact handoff commit. No code executed,
no VPS accessed. Verdicts use the handoff's own evidence labels.

## Verdict table

| # | Handoff claim | Verdict | Evidence |
|---|---|---|---|
| 1 | residual_z = normalized cumulative-20 residual; windows 60/20 | ✅ CODE VERIFIED | `feature_factory/residual.py:13` `compute_residual_features`; `regression_window=60`, `zscore_window=20` defaults; `(cum_res − mean_res·k)/(std_res·√k)` |
| 2 | 7 residual features incl. half-life; nonneg slope → inf | ✅ CODE VERIFIED | `residual.py`: `residual_z/beta/alpha`, `cumulative_residual`, `residual_half_life`, `residual_r2`, `residual_return`; `_estimate_half_life` returns `np.inf` when `b >= 0` |
| 3 | NumPy default std (ddof=0) | ✅ CODE VERIFIED | `np.std(residuals)` — no ddof argument |
| 4 | Benchmark fallback: sector ETF → SPY (market-only) → BLOCKED | ✅ CODE VERIFIED | `feature_factory/__init__.py:84-124`; comment "Fallback: sector ETF → SPY (market-only) → BLOCKED"; `benchmark_type="market_only"` vs `"sector"` travels with the call; blocked reason `BLOCKED_RESIDUAL_NAN_RATE` |
| 5 | Phase 27A params 60/45/−2.0/0.15/5; different normalization | ✅ CODE VERIFIED | `src/research/sector_residual/sector_residual_mr.py:95-99`; `residual_z = residual / resid_std` where `resid_std` is rolling(60, min_periods=45) SD of the *current-bar* residual — genuinely different statistic from the cumulative-20 formula |
| 6 | Continuation signal: ret_5d>0, close>ma50, ranks ≥0.85/0.70 | ✅ CODE VERIFIED | `src/research/momentum/relative_strength_continuation.py:16-17,172-179`; ranks are `groupby("timestamp").rank(pct=True)`; `forward_window=10` |
| 7 | ETF exclusion set missing IGV/TAN; cache-glob discovery | ✅ CODE VERIFIED | `relative_strength_continuation.py:85-103`: excluded set lacks IGV/TAN; universe built by `glob("*.csv")` on cache dirs — a cached IGV/TAN file would enter the rank universe |
| 8 | Eight escalating gates as listed | ✅ CODE VERIFIED | `docs/STRATEGY_FACTORY_STATE.md:9-17` — verbatim match |
| 9 | Outcome resolver rebuilds from observation ledger; no preservation of prior resolved rows | ✅ CODE VERIFIED | `src/paper/relative_strength_observation.py:308`: reads `observation_path`, never reads existing `output_path`; recomputes every non-RESOLVED row from current cache |
| 10 | Outcome = Nth *available* bar, not Nth session | ✅ CODE VERIFIED | Same file: `prices.iloc[outcome_window − 1]` after `prices[timestamp > signal_timestamp]` — a missing bar shifts the economic window (§10.3) |
| 11 | Timestamp comparison `bar > signal` without availability semantics | ✅ CODE VERIFIED | Same file: `prices["timestamp"] > row["signal_timestamp"]` (§10.4) |
| 12 | Ghost five-bar terminal state | ✅ CODE VERIFIED | `src/reporting/ghost_ledger.py:159`: skips MATURE/INSUFFICIENT_DATA; marks MATURE at ≥5 bars; fills 10/20/30-bar fields only if those horizons exist *in the same run* — a 5-bar MATURE row never gets longer horizons |
| 13 | Ghost write is direct mode `"w"`, non-atomic | ✅ CODE VERIFIED | `ghost_ledger.py:280` `ghost_path.open("w", newline="")` |
| 14 | `resolve_ghost_outcomes()` defaults `dry_run=False` | ✅ CODE VERIFIED | `ghost_ledger.py:159` signature |
| 15 | Return-unit magnitude heuristic ("0.5"→50%, "1.5"→1.5%) | ✅ CODE VERIFIED | `src/reporting/filter_quality_audit.py:93` `_normalize_return`; its own docstring admits "a fractional return of exactly ±1.0 (±100%) is ambiguous" |
| 16 | Delay-adjusted = flat 5bp deduction, not a resimulated delayed entry | ✅ CODE VERIFIED | `src/reporting/economic_sanity.py:18-19,257-260`: `TRANSACTION_COST_BPS=10`, `DELAY_SLIPPAGE_BPS=5`; `cost_adjusted = forward_ret − 0.15`, `delay_adjusted = forward_ret − 0.05` in percent units (`compute_forward_return` ×100.0) |
| 17 | Leakage audit: `timestamp_valid=True` hardcoded; `decision_dates` unused | ✅ CODE VERIFIED | `feature_factory/leakage_audit.py:33,43` — `checks["timestamp_valid"] = True  # Verified in ingestion module` |
| 18 | Redundancy: 0.90 abs-correlation; highest-variance representative | ✅ CODE VERIFIED | `feature_factory/redundancy_analyzer.py:18,109-116` (`np.var`, comment "most informative") |
| 19 | `stability_by_regime = "NOT_IMPLEMENTED"` | ✅ CODE VERIFIED | `feature_factory/feature_importance_runner.py:176` |
| 20 | Registry holds 7 lineages incl. canonical_spy_residual, sector/factor residual, capitulation ×3, RS continuation | ✅ CODE VERIFIED | `src/research/meta/hypothesis_registry.py:9-59` |
| 21 | `LIFT_SIGNIFICANCE_THRESHOLD = 0.5` is percentage points, not a significance test | ✅ CODE VERIFIED | `filter_quality_audit.py:28` — comment literally says `# percentage points` |
| 22 | "Independent Strength" label with sector-freshness gating | ✅ CODE VERIFIED | `src/reporting/drift_attribution.py:18`; `scripts/run_edge_audit.py:103,191,276-277` |
| 23 | Manifest 13/7/6 | ✅ CODE VERIFIED (contract level) | `src/reporting/output_store_schema.py:288-291`: `EXPECTED_OBSERVATION_COUNT=13`, `EXPECTED_RESOLVED_COUNT=7`, `EXPECTED_PENDING_COUNT=6` (actual ledger rows live on the VPS, not in git — consistent with Fable's no-ledgers-in-git rule) |
| 24 | Docs claim "16 Python modules" in feature_factory/ | ⚠️ NOT VERIFIED | Exactly 15 `.py` files in `feature_factory/` on this branch. The handoff's flag stands: do not repeat "16" as verified |

## Extra findings (not in the handoff, observed during verification)

- **E1.** `residual.py` requires ≥60 bars of ETF data (`if etf_df is None or len(etf_df) < 60`) regardless of a smaller configured `regression_window`. A config change to the window would not take effect below 60.
- **E2.** When residual std is 0, `residual_z` is written as `0.0`, not NaN — a degenerate constant-residual case reads as "no dislocation."
- **E3.** Phase 27A uses pandas rolling `.std()` (ddof=1, sample SD) while the original engine uses NumPy `np.std` (ddof=0, population SD). Same-named "z-scores" across lineages differ in *three* ways: normalization target (cumulative-20 vs current-bar), window semantics, and SD convention.
- **E4.** Refinement to handoff §10.9: the *outcome* resolver (`resolve_observation_outcomes`) writes atomically via tmp-file + replace; only the *ghost* resolver writes non-atomically. The preservation gap (§10.2) is about recomputation, not atomicity.
- **E5.** `checkpoint_result` (used by the ghost resolver) and `_parse_pct` conventions: ghost `max_favorable_move` is stored as a percent *string* (`"12.34%"`) while `outcome_5d`-style fields come from `checkpoint_result` — the mixed-unit surface that `_normalize_return` papers over is real and still present in the write path.

## Remains OPERATOR REPORTED / HISTORICAL (not code-verifiable from this branch)

- Phase 12.5 conditioning-order correction (research-report claim; the `checkpoints/phase12_5_pre_fmp_checkpoint/` dir and graveyard file exist, corroborating the *process* but not the numbers)
- The 7 resolved observation values incl. second-MRVL +16.85% (VPS ledgers)
- July cohort signal prices (operator-reported)
- 497/409 test counts and passing healthcheck (historical run results)
- May 28 accidental observation cycle (operator-reported)
- FMP cached-earnings overlay experiment outcome (needs its Phase 14 artifact)

## Bottom line

Every code-checkable claim in the handoff verified. No contradictions found
between the handoff and the working branch. The handoff's self-labeling was
honest: what it marked CODE VERIFIED held up; what it marked OPERATOR
REPORTED / HISTORICAL is genuinely not in the repo. The document is a
trustworthy design record and a safe backtrack anchor.
