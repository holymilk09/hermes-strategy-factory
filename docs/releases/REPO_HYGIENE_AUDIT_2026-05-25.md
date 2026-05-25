# Repo Hygiene Audit — 2026-05-25

## Executive summary

Repository is **not clean** for a safe broad commit. It is pre-dirty with:
- 4 tracked modified files
- a very large untracked tree across many top-level paths
- mixed concerns (research artifacts, local runtime state, generated logs/caches, and product docs)

Phase 5C outcome: audit complete, no destructive actions, no commit/push.

## Current git status

### Branch / remote
- Branch: `main`
- Sync: up to date with `origin/main`
- Remote: `https://github.com/holymilk09/hermes-strategy-factory.git`

### Modified tracked files
- `checkpoints/.last_prune`
- `config/backtest_integration_plan.yaml`
- `reports/strategy_factory/feature_factory_healthcheck.json`
- `reports/strategy_factory/feature_factory_healthcheck_report.md`

### Diff stat
- `4 files changed, 37 insertions(+), 13 deletions(-)`

### Untracked top-level entries (high-level)
`.git-credentials`, `.gitconfig`, `.hermes`, `.hermes_history`, `.install_method`, `.restart_last_processed.json`, `.update_check`, `.zshrc`, `SOUL.md`, `auth.json`, `backtest_engine.py`, `bin`, `channel_directory.json`, `context_length_cache.yaml`, `data`, `data_sources`, `debug_signals.py`, `docs`, `event_tracker`, `factor_residual_bt.py`, `factor_residual_mr_strategy.py`, `feature_runner.py`, `filter_graveyard`, `hermes-agent`, `hermes.sh.bak`, `home`, `inelasticity_results.json`, `inelasticity_screener.py`, `mean_reversion_strategy.py`, `memories`, `ml_backtest_engine.py`, `ml_enhanced_strategy.py`, `ml_epoch_backtest.py`, `ml_results.json`, `ml_strategy.py`, `ml_symbol_bars.json`, `ml_train.py`, `models_dev_cache.json`, `momentum_swing_strategy.py`, `mr_backtest_engine.py`, `ollama_cloud_models_cache.json`, `param_sweep.py`, `param_sweep_results.json`, `quant-bot`, `qullamaggie_strategy.py`, `reports`, `research_backtests`, `run_labels.py`, `run_phase2_validation.py`, `run_phase3_real_data.py`, `run_phase4_5_audit.py`, `run_phase4_validation.py`, `run_validation.py`, `scripts`, `sessions`, `shared`, `skills`, `src`, `structural_mr_strategy.py`, `tests`, `validation_pipeline.py`

## Professional repo structure assessment

### Present
- `README.md`
- `docs/`
- `scripts/`
- `src/`
- `tests/`
- `reports/`
- `config/`
- `.gitignore`

### Missing / weak
- No clear package manager manifest in tracked root listing (`pyproject.toml` or `requirements.txt` not shown in `git ls-files` output).
- Heavy runtime/local directories are colocated with product source (`.hermes/`, sessions, logs, caches).
- Reports and generated artifacts policy is not clearly encoded in `.gitignore`.

## Edge Sheet release files found

### Release docs
- `docs/releases/EDGE_SHEET_RELEASE_2026-05-25.md`
- `docs/releases/EDGE_SHEET_CHANGELOG.md`
- `docs/releases/EDGE_SHEET_OPERATOR_RUNBOOK.md`
- `docs/releases/EDGE_SHEET_SAFETY_BOUNDARIES.md`
- `docs/releases/EDGE_SHEET_BACKUP_CHECKLIST.md`

### Commercial docs
- `docs/commercial/FOUNDING_ACCESS_PAGE.md`
- `docs/commercial/PRODUCT_COPY.md`
- `docs/commercial/FAQ.md`
- `docs/commercial/COMPLIANCE_LANGUAGE.md`
- `docs/commercial/MANUAL_SHOPIFY_SETUP_CHECKLIST.md`

### Edge Sheet artifacts
- `reports/edge_sheet/2026-05-25_edge_sheet.md`
- `reports/edge_sheet/2026-05-25_edge_sheet.json`
- `reports/edge_sheet/2026-05-25_scoreboard.md`
- `reports/edge_sheet/2026-05-25_scoreboard.json`
- `reports/edge_sheet/2026-05-25_edge_sheet.html`
- `reports/edge_sheet/2026-05-25_scoreboard.html`
- `reports/edge_sheet/2026-05-25_email_preview.html`
- `reports/edge_sheet/commercial_preview_page.html`

### Product code/tests (from prior phases)
- `src/reporting/edge_sheet_html.py`
- `scripts/render_edge_sheet_html.py`
- `tests/reporting/test_edge_sheet_html.py`
- `tests/reporting/test_commercial_packaging.py`
- plus existing Phase 3.5 reporting tests/fixtures

## Files that should be committed (safe inclusion set for Edge Sheet release)

Use explicit paths only; no broad globs.

1. Release docs:
- `docs/releases/EDGE_SHEET_RELEASE_2026-05-25.md`
- `docs/releases/EDGE_SHEET_CHANGELOG.md`
- `docs/releases/EDGE_SHEET_OPERATOR_RUNBOOK.md`
- `docs/releases/EDGE_SHEET_SAFETY_BOUNDARIES.md`
- `docs/releases/EDGE_SHEET_BACKUP_CHECKLIST.md`

2. Commercial docs:
- `docs/commercial/FOUNDING_ACCESS_PAGE.md`
- `docs/commercial/PRODUCT_COPY.md`
- `docs/commercial/FAQ.md`
- `docs/commercial/COMPLIANCE_LANGUAGE.md`
- `docs/commercial/MANUAL_SHOPIFY_SETUP_CHECKLIST.md`

3. Output-layer source/test:
- `src/reporting/edge_sheet_html.py`
- `scripts/render_edge_sheet_html.py`
- `tests/reporting/test_edge_sheet_html.py`
- `tests/reporting/test_commercial_packaging.py`
- `tests/reporting/test_edge_sheet_golden.py`
- `tests/reporting/test_edge_sheet_schema.py`
- `tests/reporting/test_edge_sheet_determinism.py`
- `tests/feature_factory/test_health_contract.py`

4. Optional, if intentionally versioned as golden/demo artifacts:
- `reports/edge_sheet/commercial_preview_page.html`
- possibly one date-stamped sample set (policy decision required below)

## Files that should NOT be committed (safe exclusion set)

- Local credentials/config:
  - `.git-credentials`, `.gitconfig`, `.env`, `auth.json`, `.zshrc`
- Runtime/session/state:
  - `.hermes/`, `sessions/`, `logs/`, `gateway*.pid`, `gateway*.lock`, `processes.json`
- Caches/build artifacts:
  - `__pycache__/`, `.pytest_cache/`, `.cache/`, `.npm/`, `*.pyc`, `*.log`
- Bulk generated research outputs unless intentionally curated:
  - most of `reports/strategy_factory/`, `reports/feature_factory/`, ad hoc JSON/CSV dumps
- Checkpoint/temp/scratch trees unless specifically part of a release package

## Generated artifacts policy (recommended)

For `reports/edge_sheet/`, choose one policy and encode it:

Option A (recommended):
- Commit **only** stable demo artifacts:
  - `commercial_preview_page.html`
  - optionally one pinned dated sample (e.g., `2026-05-25_*`)
- Ignore rolling date artifacts by default.

Option B:
- Commit all dated artifacts (less clean, larger history, noisy diffs).

Recommendation: Option A for professional release hygiene.

## .gitignore assessment and suggested additions (not applied)

`.gitignore` already includes many essentials (`__pycache__/`, `*.pyc`, `.venv/`, `node_modules/`, `.DS_Store`, `*.log`).

Still recommended to add explicit coverage for current noise patterns:

```gitignore
# pytest runtime cache
.pytest_cache/

# local Hermes runtime state
.hermes/
.hermes_history

# local auth/identity files
.git-credentials
.gitconfig
auth.json

# local shell/env noise
.zshrc
.install_method
.update_check
.restart_last_processed.json

# date-stamped edge-sheet artifacts (if not versioning all)
reports/edge_sheet/[0-9][0-9][0-9][0-9]-*-*_edge_sheet.*
reports/edge_sheet/[0-9][0-9][0-9][0-9]-*-*_scoreboard.*
reports/edge_sheet/[0-9][0-9][0-9][0-9]-*_email_preview.html
```

## README quality assessment

Current `README.md` is technically useful but narrowly focused on older phase narrative and not release/operator oriented.

### Recommended README outline (not applied)
1. Project purpose and safety stance (research-only, blocked live/broker)
2. Current product scope (Edge Sheet output layer + packaging)
3. Repo structure map (src/scripts/tests/docs/reports/config)
4. Quickstart commands (venv paths explicitly)
5. Release pipeline commands
6. Test scope and monorepo caveat
7. Artifact policy (`reports/edge_sheet` commit policy)
8. Safety boundaries and forbidden changes
9. Manual external layer note (Shopify/email not integrated)

## Safe next commit command plan (explicit paths only)

```bash
git add docs/releases/EDGE_SHEET_RELEASE_2026-05-25.md
git add docs/releases/EDGE_SHEET_CHANGELOG.md
git add docs/releases/EDGE_SHEET_OPERATOR_RUNBOOK.md
git add docs/releases/EDGE_SHEET_SAFETY_BOUNDARIES.md
git add docs/releases/EDGE_SHEET_BACKUP_CHECKLIST.md

git add docs/commercial/FOUNDING_ACCESS_PAGE.md
git add docs/commercial/PRODUCT_COPY.md
git add docs/commercial/FAQ.md
git add docs/commercial/COMPLIANCE_LANGUAGE.md
git add docs/commercial/MANUAL_SHOPIFY_SETUP_CHECKLIST.md

git add src/reporting/edge_sheet_html.py
git add scripts/render_edge_sheet_html.py

git add tests/reporting/test_edge_sheet_html.py
git add tests/reporting/test_commercial_packaging.py
git add tests/reporting/test_edge_sheet_golden.py
git add tests/reporting/test_edge_sheet_schema.py
git add tests/reporting/test_edge_sheet_determinism.py
git add tests/feature_factory/test_health_contract.py

# Optional sample artifact(s) only if policy approves:
# git add reports/edge_sheet/commercial_preview_page.html
# git add reports/edge_sheet/2026-05-25_edge_sheet.html
# git add reports/edge_sheet/2026-05-25_scoreboard.html
```

Then review staged diff before any commit:

```bash
git status --short
git diff --staged --stat
git diff --staged
```

## Risks / unknowns

- Pre-dirty tree is very large; accidental staging risk is high.
- Existing tracked modifications (`checkpoints/.last_prune`, `config/backtest_integration_plan.yaml`, healthcheck outputs) may be unrelated to Edge Sheet release and should stay unstaged unless intentionally included.
- Artifact versioning policy for `reports/edge_sheet` is not yet codified.

## Non-action confirmation

- No files were deleted.
- No files were moved.
- No files were renamed.
- No commit was made.
- No push was performed.
- No strategy/maturity/broker/live behavior was changed in this audit.
