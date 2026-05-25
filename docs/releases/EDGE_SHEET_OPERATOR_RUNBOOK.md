# EDGE SHEET OPERATOR RUNBOOK

## Purpose

Operate the Strategy Factory Edge Sheet artifact pipeline safely without touching research/trading behavior.

## Exact commands

1) Generate latest markdown/json artifacts

`PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/generate_edge_sheet.py`

2) Render HTML/email-preview artifacts

`PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/render_edge_sheet_html.py`

3) Run focused verification tests

`PYTHONPATH=/opt/data /opt/data/.venv/bin/pytest -q tests/reporting tests/feature_factory`

4) Run feature-factory healthcheck

`PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/run_feature_factory_healthcheck.py`

## Expected health decision

`HEALTHCHECK_PASS_CONTINUE_WAITING`

## Environment note

If raw `python`/`pytest` is missing, use venv binaries exactly as shown above.

## Failure policy

- Do not patch strategy or maturity logic in this runbook.
- Fix only output/docs/tests scope for release pipeline tasks.
