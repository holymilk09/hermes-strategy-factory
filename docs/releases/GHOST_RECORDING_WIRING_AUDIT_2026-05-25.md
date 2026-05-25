# Phase 6G-A: Ghost Recording Wiring Audit

**Date:** 2026-05-25  
**Branch:** trust-calibration-working  
**Commit:** 8c9194b — Add trust calibration and ghost ledger reporting layer  
**Base:** c149578 — Release Strategy Factory Edge Sheet packaging layer  
**Phase 6 Status:** Committed, additive layer only, no existing files modified

---

## 1. Current Safety State

| Check | Status |
|---|---|
| Branch | `trust-calibration-working` |
| Latest commit | `8c9194b` — Add trust calibration and ghost ledger reporting layer |
| Dirty tracked files | 4 — `checkpoints/.last_prune`, `config/backtest_integration_plan.yaml`, `reports/strategy_factory/feature_factory_healthcheck.json`, `reports/strategy_factory/feature_factory_healthcheck_report.md` |
| Untracked files | ~160 files (research artifacts, scripts, reports, experiments — all pre-existing VPS noise) |
| Production block | BLOCKED |
| Live block | BLOCKED |
| Broker block | BLOCKED |
| Shadow block | BLOCKED |
| ghost ledger | Empty (0 records) — no filter/rejection paths currently wired |
| Phase 6 test result | 54 passed (32 new + 22 existing, no regressions) |
| Healthcheck | `HEALTHCHECK_PASS_CONTINUE_WAITING` |

---

## 2. Rejection Path Inventory

### Path A: Primary Observation Selection — Relative Strength Continuation

**File:** `src/paper/relative_strength_observation.py`  
**Function:** `latest_fresh_signals()` (line 166), called via `scripts/run_relative_strength_forward_observation_once.py` (line 30)

**Selection criteria (lines 151-156):**
- `ret_20d_rank >= 0.85`
- `ret_60d_rank >= 0.70`
- `close_above_ma50 == True`
- `ret_5d > 0`

**Rejection:** Rows not matching all 4 criteria are discarded silently via `latest[latest["selected"]]` (line 195). Non-selected rows are never written to any ledger.

| Metadata | Available? | Source |
|---|---|---|
| symbol | Yes | universe has `symbol` column |
| signal_timestamp | Yes | universe has `timestamp` column |
| price_at_signal | Yes | universe has `close` column |
| score | Partial | `ret_20d_rank`, `ret_60d_rank` values |
| market_weather / regime | Not present | Not available in this module |
| rejection reason | Computable | Can derive from which gates failed by checking each threshold |
| strategy_id | Yes | Config string |

**Safety to append ghost record:** **SAFE** — this is a pure data pipeline with no side effects beyond CSV output. Adding ghost record appends after rejection is non-invasive.

### Path B: Primary Observation Selection — Regime Conditioned Capitulation V2

**File:** `src/paper/forward_observation.py`  
**Function:** `build_current_signal_universe()` (line 146), then `latest_fresh_signals()` (line ~200) called via `scripts/run_forward_observation_once.py`

**Selection criteria (lines 184-189):**
- `ret_3d_z <= -1.5`
- `volume_z_20 >= 1.0`
- `close_location >= 0.50`
- `spy_drawdown_60d <= -0.0146`

**Rejection:** Same pattern — non-selected rows discarded silently via `latest[latest["selected"]]`.

| Metadata | Available? | Source |
|---|---|---|
| symbol | Yes | universe has `symbol` column |
| signal_timestamp | Yes | universe has `timestamp` column |
| price_at_signal | Yes | universe has `close` column |
| score | Partial | Feature values available |
| market_weather | Partial | `spy_drawdown_60d` available |
| rejection reason | Computable | Can derive from which gate failed |
| strategy_id | Yes | Config string |

**Safety to append ghost record:** **SAFE** — identical structure to Path A.

### Path C: Symbol-Level Build Failures

**Files:** `src/paper/relative_strength_observation.py` line 139-140, `src/paper/forward_observation.py` line 166-167

**Condition:** Individual symbol fails to build its feature frame (missing data, parse error, corrupt file).

**Current side effect:** Failure appended to `failures` list stored in `universe.attrs["failures"]`. No CSV output.

| Metadata | Available? |
|---|---|
| symbol | Yes |
| failure reason | Yes (exception message) |
| price_at_signal | No — frame couldn't be built |
| signal_timestamp | No — frame couldn't be built |
| score | No |
| market_weather | No |

**Safety to append ghost record:** **SAFE** — but record would be `INSUFFICIENT_DATA` only. Low value since no price or timestamp is available.

### Path D: Freshness/System-Level Gates

**File:** `src/paper/freshness_gates.py` (lines 77-84)  
**Function:** `evaluate_freshness()`

**Conditions:**
- `STALE_CANDIDATE_LEDGER` — candidate data too old
- `STALE_OR_MISSING_SELECTED_SIGNAL` — no fresh signals available

**Current side effect:** String classification returned, no CSV ledger entry.

**Safety to append ghost record:** **NOT RECOMMENDED** — these are system-level gates, not individual setup rejections. No per-symbol metadata available.

### Path E: Edge Sheet Reject Ledger

**File:** `scripts/generate_edge_sheet.py` (lines 154-168)  
**Function:** `make_reject_rows()`

**Condition:** Hypothesis registry row has `status == "archived"`.

**Current side effect:** Produces "reject_ledger" entries in the edge sheet. Hypothesis-level, not per-setup.

| Metadata | Available? |
|---|---|
| lineage | Yes |
| phase | Yes |
| family | Yes |
| grade | Yes |

**Safety to append ghost record:** **SAFE** — but these are whole-hypothesis rejections, not individual setup rejections. Should be a different ghost record type or treated as meta-rejections.

### Path F: Research Candidate Builders (Separate Pipeline)

All files under `scripts/build_*_candidates.py` and `src/research/*/*.py`

**Pattern:** Each research strategy has a candidate ledger with `selected` boolean. Rejected rows are computed as `df[~df["selected"]]`.

**Pipeline:** These are **research validation scripts**, not the active observation/edge-sheet pipeline. They live in `data/research/candidate_artifacts/`.

**Safety to append ghost record:** **SAFE BUT NOT PRIORITY** — the research pipeline has no customer-facing output. Ghost recording in the active observation pipeline (Paths A and B) is the priority.

### Path G: Filter Graveyard (Static Archives)

**Directory:** `filter_graveyard/`  
**Files:** 6 markdown files (earnings_event_blocker, factor_residual_mr, price_volume_capitulation_v1/v2, sector_residual_mr, volatility_regime_filter)

**Current side effect:** Static markdown files written by validation scripts when a filter hypothesis is rejected. No structured data.

**Safety to append ghost record:** **NOT APPLICABLE** — these are archival records of filter decisions, not rejection paths. Filter graveyard content could inform `rejection_reason` taxonomy but should not be wired for ghost recording.

### Path H: Event Tracker (Archived)

**Directory:** `event_tracker/`  
**Files:** `__init__.py`, `earnings_feature_generator.py`

**Status:** CLOSED (phase14_5 conclusion: earnings blocking did not improve the residual candidate set). Not active.

**Safety to append ghost record:** **NOT APPLICABLE** — archived, not active rejection path.

---

## 3. Existing Overlap

| Source | Status | Classification |
|---|---|---|
| `filter_graveyard/earnings_event_blocker_for_residual_reversion.md` | Static markdown, phase14_5 rejected | Obsolete |
| `filter_graveyard/factor_residual_mr.md` | Static markdown, rejected | Obsolete |
| `filter_graveyard/price_volume_capitulation.md` | Static markdown, rejected | Obsolete |
| `filter_graveyard/price_volume_capitulation_v2.md` | Static markdown, rejected | Obsolete |
| `filter_graveyard/sector_residual_mr.md` | Static markdown, rejected | Obsolete |
| `filter_graveyard/volatility_regime_filter.md` | Static markdown, rejected | Obsolete |
| `event_tracker/earnings_feature_generator.py` | Archived code, not active | Obsolete |
| `scripts/generate_edge_sheet.py:make_reject_rows()` | Active, hypothesis-level | Partial — captures archived hypotheses but not per-setup filter rejections |
| `data/research/candidate_artifacts/*.csv` | Active, research pipeline | Unrelated to observation pipeline |
| Research `df[~df["selected"]]` splits | Active in every strategy module | Unrelated — these are research-walk-forward splits, not live filtering |

**Verdict:** No existing code captures per-setup rejection for the active observation pipeline. The ghost ledger is needed as new functionality, not replacement of existing overlap.

---

## 4. Recommended Canonical Hook Point

### Primary Recommendation: Hook into Script Caller, Not Library Code

**File to modify:** `scripts/run_relative_strength_forward_observation_once.py` (and its mirror `scripts/run_forward_observation_once.py`)

**Rationale:** The script already has the full universe DataFrame before filtering:
```python
universe = build_current_relative_strength_universe(ROOT, config)  # has selected column
selected, freshness = latest_fresh_signals(universe, config=config)   # filters to selected
observations = build_observation_rows(selected, config)                 # only selected
```

Between steps 1 and 2, `universe` is available with the `selected` column. A ghost-recording adapter can iterate non-selected rows and append `GhostRecord` entries without touching any strategy logic.

**Why not inside the library functions?** Library functions (`build_current_relative_strength_universe`, `latest_fresh_signals`) are imported by multiple callers. Adding ghost recording inside them would affect all callers — including research pipelines — which is broader than needed. The script-level hook limits ghost recording to the active observation pipeline.

### Secondary Recommendation (if script-level hook is too complex):

**Add a new function in the observation module** `src/paper/relative_strength_observation.py`:
```python
def build_ghost_records_from_universe(
    universe: pd.DataFrame, config: str
) -> list[GhostRecord]:
```
This function would:
1. Accept the universe (which has `selected` column)
2. Identify non-selected rows at the latest timestamp
3. Determine which gate(s) each row failed
4. Return `GhostRecord` objects

The function is pure data transformation — no behavior change, no side effects.

### Rejection Reason Resolution

For each non-selected row, determine the first gate that failed:

```
relative_strength_continuation gates (in order):
1. ret_5d > 0              → rejection_reason = "recent_negative_return"
2. close_above_ma50         → rejection_reason = "below_50ma"
3. ret_20d_rank >= 0.85     → rejection_reason = "20d_momentum_too_weak"
4. ret_60d_rank >= 0.70     → rejection_reason = "60d_momentum_too_weak"
```

```
regime_conditioned_capitulation_v2 gates (in order):
1. ret_3d_z <= -1.5         → rejection_reason = "pullback_not_deep_enough"
2. volume_z_20 >= 1.0       → rejection_reason = "volume_not_elevated"
3. close_location >= 0.50   → rejection_reason = "close_too_low_in_range"
4. spy_drawdown_60d <= -0.0146 → rejection_reason = "spy_not_in_drawdown"
```

---

## 5. Do-Not-Touch List

| File | Reason |
|---|---|
| `src/research/momentum/relative_strength_continuation.py` | Contains scoring/threshold logic for research phase. Do not modify. |
| `src/research/regime_conditioned/capitulation_v2_drawdown.py` | Contains scoring/threshold logic. Do not modify. |
| `src/research/filters/volatility_filter.py` | Contains filter threshold logic. Do not modify. |
| `src/research/*/` (all subdirectories) | Research phase code — not part of active observation pipeline. |
| `src/paper/maturity_watchdog.py` | Maturity logic. Do not modify. |
| `src/paper/risk_gates.py` | Production safety gates. Do not modify. |
| `src/paper/strategy_manifest.py` | Shadow/broker configuration. Do not modify. |
| `config/backtest_integration_plan.yaml` | Research progress tracking. Do not modify. |
| `filter_graveyard/` | Static archives. Do not modify. |
| `event_tracker/` | Archived. Do not modify. |
| `src/reporting/maturity_scoreboard.py` | Maturity computation. Do not modify. |
| `src/reporting/retail_wording.py` | Wording layer. Do not modify. |

### Files That CAN Be Modified Safely

| File | Reason |
|---|---|
| `scripts/run_relative_strength_forward_observation_once.py` | Pure orchestration script, no strategy logic. Ideal hook point. |
| `scripts/run_forward_observation_once.py` | Mirror script for regime_conditioned system. Same safety level. |
| `src/reporting/ghost_ledger.py` (existing Phase 6 file) | Our own file — safe to extend with `build_ghost_records_from_universe()`. |

---

## 6. Minimal Future Wiring Plan (Phase 6G-B)

### Objective
Wire ghost recording so that every non-selected symbol at the latest signal timestamp gets a `GhostRecord` appended to the ghost ledger. No strategy behavior changes.

### Files to Modify

| File | Change | Risk |
|---|---|---|
| `scripts/run_relative_strength_forward_observation_once.py` | After line 30 (`latest_fresh_signals` returns `selected`), extract non-selected rows from `universe` and call `append_ghost_records()`. | None — pure additive side effect |
| `scripts/run_forward_observation_once.py` | Same pattern for regime-conditioned system. | None — pure additive side effect |

### Files to Add (tests)

| File | Content |
|---|---|
| `tests/reporting/test_ghost_recording_wiring.py` | Test that ghost records are created for non-selected symbols, that selected symbols do NOT get ghost records, that duplicate runs are idempotent, that strategy behavior is not affected. |

### Expected Ghost Record Fields

For each non-selected symbol at the latest signal timestamp:

| Field | Source |
|---|---|
| `ghost_id` | Hash of `symbol + signal_timestamp + strategy_id + failed_gate` |
| `source_observation_id` | Empty (no observation created) |
| `symbol` | From universe row |
| `strategy_id` | Config string |
| `setup_type` | "swing" |
| `signal_date` | Timestamp from universe |
| `rejection_reason` | First gate that failed (see Section 4 taxonomy) |
| `failed_gate` | Name of the gate condition |
| `score_if_available` | The rank/feature value that caused rejection |
| `price_at_signal` | `close` from universe row |
| `market_weather` | Empty (not available at observation time — filled later) |
| `data_status` | "PENDING" |

### Safety Assertions (to enforce in tests)

1. Ghost recording does not modify the `universe` DataFrame.
2. Ghost recording does not change which rows are `selected`.
3. Ghost recording does not change the observation ledger.
4. Ghost recording does not affect outcome computation.
5. Duplicate ghost_id (same symbol, same timestamp, same gate) is not re-appended.
6. Production/live/broker/shadow blocks remain BLOCKED.

### Rollback Plan

1. Revert the two script files: `git checkout -- scripts/run_relative_strength_forward_observation_once.py scripts/run_forward_observation_once.py`
2. Delete test file: `rm tests/reporting/test_ghost_recording_wiring.py`
3. Run all existing tests to verify no regression.

The rollback touches no strategy logic, no thresholds, no scoring, no broker code. It only touches orchestration scripts and tests.

---

## 7. Final Compliance Statement

- **No strategy behavior changed.** ✅ — Audit only, no code modifications.
- **No thresholds changed.** ✅
- **No scoring changed.** ✅
- **No maturity behavior changed.** ✅
- **No broker/live/shadow behavior changed.** ✅ (all blocks remain BLOCKED)
- **No staging/commit/push/delete occurred.** ✅
- **Audit only.** ✅ — One report generated: `docs/releases/GHOST_RECORDING_WIRING_AUDIT_2026-05-25.md`