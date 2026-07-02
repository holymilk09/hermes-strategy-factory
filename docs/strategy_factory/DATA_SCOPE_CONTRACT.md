# Data Scope Contract — Strategy Factory

**Phase:** 7C-DATA-REPAIR
**Status:** Active
**Applies to:** OHLCV refresh, relative-strength ranking, drift attribution, ghost resolution

---

## 1. Why this contract exists

The relative-strength continuation filter selects candidates by **cross-sectional
rank** (`ret_20d_rank >= 0.85`, `ret_60d_rank >= 0.70`). A percentile rank is only
meaningful against a broad cross-section. During Phases 6J–6M the refresh scope
collapsed to the 6 approved observation symbols plus SPY/QQQ. With a 6-symbol
cross-section, "top 15% by momentum" means "best 1 of 6" — statistically
meaningless and structurally biased.

**Rule: A six-symbol refresh is INVALID for ranking. Full universe refresh is
required before any new observation cycle.**

## 2. Universe source

There is no separate hardcoded universe list. The research universe is derived
from the OHLCV cache, exactly as the observation code discovers it:

- **Canonical source:** every `*.csv` in `data/cache/ohlcv_1d/`
  (see `discover_symbol_paths()` in `src/paper/relative_strength_observation.py`).
- **Refresh scope:** `resolve_refresh_universe(root)` in
  `scripts/refresh_stale_ohlcv.py` = cached symbols ∪ {SPY, QQQ} ∪ {SMH, IGV, TAN}
  ∪ the 6 approved observation symbols.
- As of Phase 7C the cache holds ~92 symbols (stocks + sector ETFs).

**Known limitation (documented deliberately):** the universe is defined by
"what has a CSV in the cache." Adding/removing CSVs changes the ranking
cross-section. This is the least-risky derivation available — it matches the
exact discovery mechanism the filter itself uses — but it is not a curated
index membership list. A future phase may pin an explicit universe manifest.

## 3. Universe freshness floor (fail-closed)

- **Minimum fresh cross-section: 50 symbols** at the latest completed session.
- `scripts/refresh_stale_ohlcv.py` exits non-zero with
  `UNIVERSE_FLOOR_VIOLATION` when fewer than 50 symbols are fresh after refresh.
- `scripts/run_feature_factory_healthcheck.py` fails
  (`Universe freshness floor: FAIL`) when the latest cross-section has < 50
  fresh symbols.
- **Do not weaken the floor to get a green check.** A failing floor means the
  data is not fit for ranking; that failure is the correct signal.

## 4. Benchmark and sector ETF requirements

| ETF | Role | Required for |
|-----|------|--------------|
| SPY | Market benchmark | Drift attribution (market vs stock) |
| QQQ | Tech-heavy benchmark | Drift attribution (beta) |
| SMH | Semiconductors | AMD, MRVL, ARM sector verification |
| IGV | Software/cloud | CRWD, DDOG sector verification |
| TAN | Solar/clean energy | SEDG sector verification |

- Sector ETFs are ALWAYS part of the refresh scope.
- **Sector ETF freshness is required for full "Independent Strength" labels.**
  When a symbol's mapped sector ETF data is missing or stale, drift attribution
  downgrades to the conservative label
  `"Independent Strength vs SPY/QQQ; sector verification pending"`.
  It never silently grants full Independent Strength (Phase 7C overclaim guard,
  `classify_drift(..., sector_expected=True)` in
  `src/reporting/drift_attribution.py`).
- If IGV/TAN have no cache CSV yet, the refresh script seeds them with full
  daily history from Alpaca (`seed_symbol_csv`). Seeding never overwrites an
  existing file.

## 5. Ghost ledger requirements

- The ghost ledger (`data/trust_calibration/ghost_ledger.csv`) is the product's
  accountability differentiator. **A populated ghost baseline is required for
  any filter-quality claim** (`ghost_baseline_return`,
  `accepted_vs_rejected_lift`).
- Ghost outcomes are resolved ONLY by the explicit operator command:

  ```
  python scripts/update_ghost_outcomes.py          # dry-run (default)
  python scripts/update_ghost_outcomes.py --write  # explicit write mode
  ```

- Ghost resolution is intentionally NOT wired into
  `run_relative_strength_observation_cycle.py` so the approved cycle can never
  mutate the ghost ledger as a side effect.
- Status transitions: `PENDING → MATURE` (≥ 5 forward bars),
  `PENDING → INSUFFICIENT_DATA` (impossible to resolve), otherwise stays
  `PENDING`. Row count never changes. Observation/outcome ledgers are hash-
  verified unchanged after every write run.

## 6. Recommended operating order

1. `scripts/refresh_stale_ohlcv.py` — full-universe data refresh (fails closed
   below the floor)
2. `scripts/run_relative_strength_observation_cycle.py` — ONLY when an
   observation cycle is intentionally approved
3. `scripts/update_relative_strength_observation_outcomes.py`
4. `scripts/update_ghost_outcomes.py --write` — controlled ghost resolution
5. `scripts/run_edge_audit.py`
6. `scripts/run_feature_factory_healthcheck.py`

## 7. Confidence degradation rules

Missing data must LOWER confidence and must be VISIBLE:

- Missing/stale sector ETF → conservative Independent Strength label +
  edge-audit warning naming the blocked ETF.
- Unresolved ghost outcomes → `ghost_baseline_return = null`,
  `accepted_vs_rejected_lift = null`, filter lift assessment stays
  `Filter Lift Inconclusive`.
- Universe below floor → refresh and healthcheck FAIL; ranks from that
  cross-section must not be used for new observations.

Never weaken a label, invent a value, or hide a gap to make results look
better.

---

*Phase 7C-DATA-REPAIR. No strategy thresholds, scoring, or maturity rules were
changed by this contract. Broker/live/shadow/production remain BLOCKED.*
