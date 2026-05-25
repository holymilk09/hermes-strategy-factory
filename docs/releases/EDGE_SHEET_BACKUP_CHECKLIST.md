# EDGE SHEET BACKUP CHECKLIST

## Pre-push release checklist

1. Run generator.
2. Run HTML renderer.
3. Run focused tests.
4. Run health check.
5. Confirm generated artifacts exist.
6. Confirm hard blocks are active.
7. Review `git status`.
8. Review `git diff --stat`.
9. Commit with clear message.
10. Push to GitHub if configured.
11. Record commit hash.

Suggested commit message:

`Strategy Factory Edge Sheet output and commercial packaging release`

## Commands

- `PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/generate_edge_sheet.py`
- `PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/render_edge_sheet_html.py`
- `PYTHONPATH=/opt/data /opt/data/.venv/bin/pytest -q tests/reporting tests/feature_factory`
- `PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/run_feature_factory_healthcheck.py`
- `git status`
- `git diff --stat`
