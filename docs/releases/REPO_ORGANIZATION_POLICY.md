# Repo Organization Policy

## Purpose

Keep the public repository surface professional while preserving strict research safety boundaries.

## Commit-eligible content

- Source code (`src/`)
- Operator scripts (`scripts/`)
- Tests and fixtures (`tests/`, `tests/fixtures/`)
- Documentation and release notes (`docs/`, `docs/releases/`, `docs/commercial/`)
- Curated public-safe examples (`examples/`)
- Required configuration templates (`config/`)

## Usually non-commit content

- Runtime-generated reports
- Cache files and build artifacts
- Checkpoint noise
- Logs
- Local auth files
- Agent session/runtime state

## Edge Sheet artifact policy

- `reports/edge_sheet/YYYY-MM-DD_*` are runtime artifacts by default.
- Dated generated reports should not be committed as normal repo source unless explicitly promoted.
- Curated showcase artifacts may be copied into `examples/edge_sheet/`.

## Pre-dirty repository safety policy

- Use explicit file-path staging only.
- Avoid broad staging (`git add .`, `git add -A`) until repo cleanliness improves.
- Review staged diff before each commit.

## Guardrails

- Do not change strategy logic, thresholds, scoring, maturity logic, or broker/live/shadow behavior during repo-surface phases.
- Do not add Shopify/payment/email automation in repo-surface phases.
