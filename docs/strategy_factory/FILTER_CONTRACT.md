# Filter Contract — Relative Strength Continuation Strategy

> **Document version:** 1.0  
> **Date:** 2026-07-01  
> **Status:** READ-ONLY DOCUMENTATION — describes current behavior, does not change it  
> **Source files referenced:**
> - `src/paper/relative_strength_observation.py` — selection logic + config
> - `src/reporting/ghost_ledger.py` — ghost recording infrastructure
> - `scripts/run_relative_strength_forward_observation_once.py` — gate definitions
> - `scripts/run_relative_strength_observation_cycle.py` — cycle orchestrator

---

## 1. Strategy Identity

| Attribute | Value |
|---|---|
| Strategy ID | `relative_strength_continuation` |
| Lineage | `relative_strength_continuation_phase28a_weak_pass` |
| Setup type | `swing` |
| Timeframe | 1D (daily bars) |
| Direction | Long only |
| Outcome window | 10 trading bars |
| Status | Paper observation only — no broker/live/shadow |

---

## 2. Universe Construction

### 2.1 Symbol Discovery

Symbols are **dynamically discovered** from `data/cache/ohlcv_1d/*.csv`. The following are explicitly excluded (benchmarks, not tradable candidates):

```
SPY, QQQ, IWM,
XLK, XLF, XLV, XLY, XLC, XLI,
XLE, XLP, XLU, XLB, XLRE,
SMH, IBB, ARKK
```

**Current effective universe (as of 2026-06-30):** AMD, ARM, CRWD, DDOG, MRVL, SEDG

> **Phase 7C warning — this collapsed universe is INVALID for ranking.**
> The 2026-06-30 cross-section contained only the 6 symbols whose CSVs had
> been refreshed. Percentile ranks (`ret_20d_rank`, `ret_60d_rank`) computed
> over 6 symbols are meaningless — "top 15%" of 6 symbols is "best 1 of 6".
> The full research universe (≥ 50 fresh symbols) MUST be refreshed before
> any future observation cycle. See
> `docs/strategy_factory/DATA_SCOPE_CONTRACT.md` for the universe source,
> the 50-symbol fail-closed freshness floor, and required sector ETFs
> (SMH/IGV/TAN). Ghost baselines from resolved ghost outcomes are required
> for any filter-quality claim; missing sector/ghost data lowers confidence
> and must be visible in reports — never hidden.

There is no hardcoded symbol list for the tradable universe — it expands automatically when new OHLCV CSVs appear.

### 2.2 Feature Computation (per symbol, per bar)

| Feature | Formula | Purpose |
|---|---|---|
| `ret_5d` | `close / close.shift(5) - 1` | Short-term momentum / pullback detection |
| `ret_20d` | `close / close.shift(20) - 1` | 1-month momentum |
| `ret_60d` | `close / close.shift(60) - 1` | 3-month momentum |
| `ma50` | `close.rolling(50).mean()` | Medium-term trend anchor |
| `close_above_ma50` | `close > ma50` | Trend direction (boolean) |
| `ret_20d_rank` | Cross-sectional percentile rank of `ret_20d` within each timestamp | Relative strength vs peers |
| `ret_60d_rank` | Cross-sectional percentile rank of `ret_60d` within each timestamp | Sustained relative strength |

---

## 3. Selection Gates (QUALIFYING SETUP = all 4 must pass)

The `selected` column is a **logical AND** of four gates. A stock qualifies as an observation candidate only when ALL four pass simultaneously at the latest timestamp.

| # | Gate | Condition | Threshold | Constraint Type |
|---|---|---|---|---|
| G1 | **5-day momentum** | `ret_5d > 0` | > 0.0 | Must have positive momentum over the past week — no recent pullback |
| G2 | **Trend direction** | `close_above_ma50 == True` | `close > ma50` | Must be trading above its 50-day moving average — uptrend confirmed |
| G3 | **20-day relative strength** | `ret_20d_rank >= 0.85` | ≥ 85th percentile | Must be in the top 15% of the universe by 1-month momentum |
| G4 | **60-day relative strength** | `ret_60d_rank >= 0.70` | ≥ 70th percentile | Must be in the top 30% of the universe by 3-month momentum |

### 3.1 Source

Defined at `src/paper/relative_strength_observation.py` lines 151–156:

```python
universe["selected"] = (
    (universe["ret_20d_rank"] >= config.ret_20d_rank_threshold)    # 0.85
    & (universe["ret_60d_rank"] >= config.ret_60d_rank_threshold)  # 0.70
    & (universe["close_above_ma50"].astype(bool))
    & (universe["ret_5d"] > 0)
)
```

### 3.2 Config

Defined at `src/paper/relative_strength_observation.py` lines 13–20:

```python
@dataclass(frozen=True)
class RelativeStrengthObservationConfig:
    ret_20d_rank_threshold: float = 0.85
    ret_60d_rank_threshold: float = 0.70
    outcome_window: int = 10
    max_stale_calendar_days: int = 5
    strategy: str = "relative_strength_continuation"
    lineage: str = "relative_strength_continuation_phase28a_weak_pass"
```

**There is no composite score, no scoring formula, no weighting, and no ranking within selected symbols.** Selection is purely binary: all 4 gates AND-ed. Any selected symbol becomes an observation. There is no "strong pass" vs "weak pass" distinction at the individual symbol level.

---

## 4. Ghost Rejection Reasons (priority order)

When a symbol does NOT qualify (`selected=False`) at the latest timestamp, the ghost ledger records WHY. The first gate that fails (checked in priority order) determines the rejection reason.

Defined at `scripts/run_relative_strength_forward_observation_once.py` lines 35–40.

| Priority | Gate Column | Pass Condition | Gate Label | Rejection Label | Plain-English Meaning |
|---|---|---|---|---|---|
| 1 (highest) | `ret_5d` | `> 0.0` | `ret_5d_positive` | `recent_negative_return` | Stock declined over the past week |
| 2 | `close_above_ma50` | `> 0.5` (i.e., `True`) | `close_above_ma50` | `below_50ma` | Stock is below its 50-day moving average |
| 3 | `ret_20d_rank` | `>= 0.85` | `ret_20d_rank` | `20d_momentum_too_weak` | 1-month momentum isn't in the top 15% of the universe |
| 4 (lowest) | `ret_60d_rank` | `>= 0.70` | `ret_60d_rank` | `60d_momentum_too_weak` | 3-month momentum isn't in the top 30% of the universe |

**Priority semantics:** If a stock fails gate 3 AND gate 4, it's recorded as `20d_momentum_too_weak` because gate 3 is checked first. Similarly, a stock that recently declined AND is below its 50-MA will be recorded as `recent_negative_return` (gate 1 fires first).

### 4.1 Source

```python
RELATIVE_STRENGTH_GATES = [
    ("ret_5d",          lambda v: v > 0.0,   "ret_5d_positive",  "recent_negative_return"),
    ("close_above_ma50", lambda v: v > 0.5,   "close_above_ma50",  "below_50ma"),
    ("ret_20d_rank",    lambda v: v >= 0.85,  "ret_20d_rank",      "20d_momentum_too_weak"),
    ("ret_60d_rank",    lambda v: v >= 0.70,  "ret_60d_rank",      "60d_momentum_too_weak"),
]
```

The ghost recording function (`record_observation_rejections` in `src/reporting/ghost_ledger.py` line 406) calls `_resolve_first_failed_gate`, which checks these gates in order against non-selected rows and returns the first failure.

---

## 5. Freshness Gate (additional: stale data blocks all observations)

| Condition | Threshold | Effect |
|---|---|---|
| Signal age | ≤ `max_stale_calendar_days` (default: 5) | If latest signal timestamp is more than 5 calendar days old, ALL observations are blocked — returns empty |

Applied in `latest_fresh_signals()` at `src/paper/relative_strength_observation.py` line 192:

```python
fresh = age_days <= config.max_stale_calendar_days
if not fresh:
    return selected.iloc[0:0].copy(), freshness   # empty
```

---

## 6. Maturity Gate (outcome resolution)

| Attribute | Value |
|---|---|
| Outcome window | 10 trading bars |
| Resolution condition | ≥ 10 future trading bars available after `signal_timestamp` |
| Pending condition | < 10 future bars |
| Error states | `PENDING_NO_OHLCV` (no CSV), `PENDING_OHLCV_ERROR` (load failure) |

Outcome return formula: `outcome_close / signal_close - 1.0`

Applied in `resolve_observation_outcomes()` at `src/paper/relative_strength_observation.py` lines 308–398.

---

## 7. Lifecycle Classifications

### 7.1 Cycle-Level

From `classify_cycle()` in `src/paper/relative_strength_observation_cycle.py`:

| Classification | Meaning |
|---|---|
| `OBSERVATION_CYCLE_ACTIVE_PENDING` | Observations exist, outcomes not yet resolved |
| `OBSERVATION_CYCLE_ACTIVE_RESOLVED` | Observations exist, all outcomes resolved |
| `OBSERVATION_CYCLE_READY_NO_SIGNALS` | No qualifying setups (0 observations) |
| `OBSERVATION_CYCLE_PASS` | Cycle ran clean, no issues, no observations |
| `OBSERVATION_CYCLE_FAIL` | Subprocess crashed or returned non-zero |
| `OBSERVATION_CYCLE_HARD_FAIL_BROKER_FLAG` | Broker fields populated (safety violation) |

### 7.2 Ghost Data Status

From `resolve_ghost_outcomes()` in `src/reporting/ghost_ledger.py`:

| Status | Meaning |
|---|---|
| `PENDING` | < 5 future bars available |
| `MATURE` | ≥ 5 future bars, outcomes computed |
| `INSUFFICIENT_DATA` | No signal date, no OHLCV, or no price |

### 7.3 Ghost Published Status

| Status | Meaning |
|---|---|
| `GHOST_ONLY` | Never published as an observation — rejected at filter gate |

### 7.4 Setup Broke

| Value | Meaning |
|---|---|
| `YES` | Any future bar's low ≤ `signal_price * 0.96` (4% stop breach) |
| `NO` | Price never hit the 4% stop level |

---

## 8. Terminology Reference

### 8.1 Retail / Product Wording

| Term | Plain-English Definition |
|---|---|
| **Qualifying setup** | A stock that passes all 4 selection gates (positive momentum, above 50-MA, top-15% 1-month RS, top-30% 3-month RS) |
| **Weak condition** | The strategy lineage (`phase28a_weak_pass`) indicates this filter combination passed a weak validation gate during research — it's screening for continuation but with known limitations |
| **Rejection** | A stock that failed one or more gates and was NOT selected for observation |
| **Ghost candidate** | A rejected stock recorded in the ghost ledger for audit — its forward returns are tracked to measure what the filters are excluding |
| **Observation candidate** | A selected stock that becomes a paper observation — no broker action, no live trading |
| **Matured edge** | An observation with ≥ 10 future trading bars available, outcome resolved |

### 8.2 Internal Audit Wording

| Term | Definition |
|---|---|
| `selected` | Boolean column in universe DataFrame — `True` when all 4 gates pass |
| `ghost_id` | Deterministic SHA256 hash from `{symbol}|{signal_date}|{setup_type}|{failed_gate}|{rejection_reason}` |
| `observation_id` | Deterministic SHA256 hash from `{timestamp}|{symbol}|{strategy}|forward_observation` |
| `failed_gate` | Which gate caused rejection (e.g., `ret_20d_rank`, `ret_5d_positive`) |
| `rejection_reason` | Human-readable label for the failure (e.g., `20d_momentum_too_weak`, `recent_negative_return`) |
| `score_if_available` | The raw value of the first failing gate's column — not a composite score, just the measured value |

### 8.3 Forbidden Claims

Per Strategy Factory operator rules (Phase 6J–6M):

| Forbidden | Reason |
|---|---|
| "Profitable" / "Validated" / "Ready to trade" | Research only — no commercial edge claim |
| "High confidence" / "Guaranteed" | No statistical basis for confidence claims |
| "Strong pass" / "Weak pass" at individual symbol level | No intra-cohort scoring — all selected symbols are equals |
| "Edge confirmed" | n=7 same-day cohort = correlated evidence, not independent |
| "Risk-free" | All trading carries risk |
| Calling the lineage "weak_pass" without context | The lineage refers to the research phase gate, not per-symbol quality |

---

## 9. Examples from the 2026-06-30 Cycle

**Cycle classification:** `OBSERVATION_CYCLE_ACTIVE_RESOLVED`  
**New observations generated:** 0  
**Non-selected symbols at 2026-06-30 close:** 6 (all)

| Symbol | Failing Gate (priority) | Rejection Reason | Interpretation |
|---|---|---|---|
| AMD | Gate 3 — `ret_20d_rank` | `20d_momentum_too_weak` | 1-month momentum below 85th percentile |
| ARM | Gate 1 — `ret_5d` | `recent_negative_return` | Declined over the past 5 trading days |
| CRWD | Gate 3 — `ret_20d_rank` | `20d_momentum_too_weak` | 1-month momentum below 85th percentile |
| DDOG | Gate 3 — `ret_20d_rank` | `20d_momentum_too_weak` | 1-month momentum below 85th percentile |
| MRVL | Gate 1 — `ret_5d` | `recent_negative_return` | Declined over the past 5 trading days |
| SEDG | Gate 3 — `ret_20d_rank` | `20d_momentum_too_weak` | 1-month momentum below 85th percentile |

**What this means:** As of the 2026-06-30 close, none of the 6 symbols in the universe satisfied all 4 gates simultaneously. Two symbols (ARM, MRVL) had negative 5-day returns — immediate disqualification. The other four (AMD, CRWD, DDOG, SEDG) passed the 5d and MA50 gates but lacked sufficient 20-day relative strength (below the 85th percentile threshold).

All 6 symbols were recorded as ghost entries. No new observations were appended. The 7 existing observations (all resolved) were preserved unchanged.

---

## 10. Architecture Diagram

```
OHLCV CSVs (any symbols in cache/)
        │
        ▼
build_current_relative_strength_universe()
  ├─ Discover symbols (exclude ETFs)
  ├─ Compute features: ret_5d, ret_20d, ret_60d, ma50, close_above_ma50
  ├─ Cross-sectional rank: ret_20d_rank, ret_60d_rank
  └─ Apply SELECTED = G1 & G2 & G3 & G4  (binary AND)
        │
        ├── selected=True  ──▶  latest_fresh_signals()  ──▶  build_observation_rows()  ──▶  Observation Ledger
        │                              │
        │                              └── stale (>5d) → empty (no observations)
        │
        └── selected=False ──▶  record_observation_rejections()  ──▶  Ghost Ledger
                                       │
                                       └── Gate priority: G1 → G2 → G3 → G4
                                           (first failing gate = rejection reason)
```

---

## 11. Change Log

| Date | Version | Change |
|---|---|---|
| 2026-07-01 | 1.0 | Initial documentation — extracted from source at commit `fb587a3`. No behavior changed. |
