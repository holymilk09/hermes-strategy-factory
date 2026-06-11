# Testing Guide — Strategy Factory

## Test Suite Overview

The test suite is split into two tiers:

| Tier | Command | Requirements | When to use |
|------|---------|--------------|-------------|
| **Source-only** | `python -m pytest -m "not requires_data and not requires_ohlcv and not requires_reports and not requires_venv"` | No data files needed | Fresh clone, CI, code review, any developer machine |
| **Full (VPS)** | `python -m pytest tests/` | Production ledgers + OHLCV cache + reports | After a daily data refresh on the VPS |

## Fresh Clone — Source-Only Command

```bash
# After cloning the repo:
pip install -e ".[dev]"          # or: pip install pytest pandas numpy ...
python -m pytest -m "not requires_data and not requires_ohlcv and not requires_reports and not requires_venv"
```

Expected result: **~338 passed, 0 failed**. All source logic, unit tests, mock-based tests, and
parsing tests pass without any production data.

## VPS Full Command

```bash
# On the VPS after running refresh_stale_ohlcv.py and generating reports:
PYTHONPATH=/opt/data /opt/data/.venv/bin/python3 -m pytest tests/
```

Expected result: **~384+ passed** (some golden/report tests may have pre-existing known failures 
related to live-ledger state).

## Marker Definitions

| Marker | Meaning |
|--------|---------|
| `requires_data` | Needs production CSV ledgers: `data/paper_observation/*.csv`, `reports/strategy_factory/hypothesis_registry.csv`, `backups/` |
| `requires_ohlcv` | Needs local OHLCV cache: `data/cache/ohlcv_1d/` |
| `requires_reports` | Needs generated report files: `reports/edge_sheet/*.json/.md/.html` |
| `requires_venv` | Calls subprocess with `ROOT/.venv/bin/python` — only works on VPS with venv installed |
| `requires_network` | Makes live outbound calls to Alpaca API or GitHub |

## Data-Dependent Test Policy

Tests that read production data files (ledgers, OHLCV CSVs, generated reports) are intentionally
marked so they are **excluded from the default fresh-clone suite**. This is correct behaviour —
we do not commit production data to git.

- **Do not** remove these markers to make tests pass in CI without data.
- **Do not** create fake ledger fixtures that mimic production data shapes — the production invariant
  tests must run against real VPS data to be meaningful.
- **Do** add synthetic fixtures for tests that verify pure source logic unrelated to specific
  production data values (e.g., unit tests for parsing functions, schema validators, classifiers).

## Focused VPS Operational Suite

For daily maturity check runs, use the focused set:

```bash
PYTHONPATH=/opt/data /opt/data/.venv/bin/python3 -m pytest \
  tests/test_feature_factory_invariants.py \
  tests/test_market_calendar_freshness.py \
  tests/test_ohlcv_refresh_hardening.py \
  tests/reporting/test_drift_attribution.py \
  tests/test_maturity_watchdog.py \
  tests/test_observation_drift.py \
  -q
```

## Pre-existing Known Failures (VPS Full Suite)

These 4 tests fail on the VPS due to live ledger state and are pre-existing, unrelated to source
changes committed in Phase 6K-REPO-REPRODUCIBILITY:

- `tests/reporting/test_edge_sheet_golden.py::test_scoreboard_is_honest_and_immature_clearly_marked` — MRVL observation at 3 bars triggers "Setup Broke" vs golden "Still Maturing"
- `tests/reporting/test_edge_sheet_golden.py::test_current_output_matches_golden_shape_after_normalization` — golden has 6 rows, live ledger has 7
- `tests/reporting/test_edge_sheet_html.py::test_scoreboard_html_no_fake_immature_outcomes` — same root cause
- `tests/test_edge_sheet_output_layer.py::test_scoreboard_immature_rows_marked_still_maturing_when_under_5_days` — same root cause

These will self-resolve when MRVL matures (10 future bars) and the golden file is updated per
the Phase 6L contract procedure.
