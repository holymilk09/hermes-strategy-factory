# Strategy Factory Edge Sheet Release — 2026-05-25

## Current product state

Strategy Factory Edge Sheet release is in artifact/commercial-packaging readiness mode with frozen research behavior.

Completed phases:
- Phase 1: Edge Sheet generator
- Phase 2: Retail wording mapper
- Phase 3: Maturity scoreboard
- Phase 3.5: Golden output QA
- Phase 4: HTML/email-ready renderer
- Phase 5A: Commercial packaging docs

## Generated artifact paths

- reports/edge_sheet/2026-05-25_edge_sheet.md
- reports/edge_sheet/2026-05-25_edge_sheet.json
- reports/edge_sheet/2026-05-25_scoreboard.md
- reports/edge_sheet/2026-05-25_scoreboard.json
- reports/edge_sheet/2026-05-25_edge_sheet.html
- reports/edge_sheet/2026-05-25_scoreboard.html
- reports/edge_sheet/2026-05-25_email_preview.html
- reports/edge_sheet/commercial_preview_page.html

## Release verification commands

- `PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/generate_edge_sheet.py`
- `PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/render_edge_sheet_html.py`
- `PYTHONPATH=/opt/data /opt/data/.venv/bin/pytest -q tests/reporting tests/feature_factory`
- `PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/run_feature_factory_healthcheck.py`

## Environment notes

- Raw `python` / `pytest` may not exist in PATH.
- Use `/opt/data/.venv/bin/python` and `/opt/data/.venv/bin/pytest`.

## Full-monorepo pytest caveat

Unrelated hermes-agent dependency trees may fail collection due missing external dependencies. Strategy Factory focused tests (`tests/reporting`, `tests/feature_factory`) are the release target.

## What changed

- Output-layer artifacts and renderers
- QA/golden/snapshot tests
- Commercial packaging docs and static preview
- Release/runbook/safety/backup documentation

## What did not change

- Strategy logic
- Thresholds
- Scoring
- Research engine behavior
- Maturity logic
- Ledgers writeback behavior
- Broker/live/shadow behavior
- Shopify/payment/email automation integration

## Safety boundaries

See `docs/releases/EDGE_SHEET_SAFETY_BOUNDARIES.md`.

## Next allowed phase

- Phase 6: Email delivery pipeline (after manual packaging signoff)

## Next forbidden phase

- Any strategy/maturity/broker/live behavior change
- Shopify API or payment automation integration inside Hermes
