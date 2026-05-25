# Hermes Strategy Factory

Research-first quantitative workflow with strict safety boundaries and a customer-facing output layer.

## Strategy Factory Edge Sheet

**Product direction:** Strategy Factory Edge Sheet — Founding Access  
**Price target:** $5/month  
**Core hook:** *The 60-second stock setup sheet.*  
**Marketing hook:** *See what’s strong, weak, and too risky before you chase it.*

## What this is

A weekly **research-only** setup sheet that translates Strategy Factory observations into plain-English setup views.

## What this is not

- Not a trading bot
- Not broker execution
- Not buy/sell alerts
- Not personalized financial advice
- Not proven performance claims

## Current build state

- Research engine: frozen for this release track
- Forward-observation/maturity phase: active (`PENDING_MATURITY`)
- Edge Sheet output layer: complete
- Retail wording mapper: complete
- Maturity scoreboard: complete
- HTML/email preview renderer: complete
- Commercial packaging docs: complete

## Architecture layers

### 1) Truth Layer
- Research engine
- Forward observation
- Maturity tracking
- Ledgers
- Health checks

### 2) Artifact Layer
- Markdown report
- JSON report
- Scoreboard
- HTML/email preview

### 3) Commercial Packaging Layer
- Product copy
- FAQ
- Compliance language
- Manual Shopify checklist

### 4) External Manual Layer
- Shopify setup later on your own computer
- No Shopify integration inside Hermes yet

## Operator commands

Generate reports:

```bash
PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/generate_edge_sheet.py
PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/render_edge_sheet_html.py
```

Run focused tests:

```bash
PYTHONPATH=/opt/data /opt/data/.venv/bin/pytest -q tests/reporting tests/feature_factory
```

Run health check:

```bash
PYTHONPATH=/opt/data /opt/data/.venv/bin/python /opt/data/scripts/run_feature_factory_healthcheck.py
```

## Environment notes

- Use `/opt/data/.venv/bin/python` and `/opt/data/.venv/bin/pytest`
- Raw `python` / `pytest` may not exist in PATH

## Test-scope caveat

Full monorepo `pytest` may fail on unrelated `hermes-agent` dependency trees due to missing external dependencies.  
Release target is focused Strategy Factory suites (`tests/reporting`, `tests/feature_factory`).

## Safety boundaries

Do not change in packaging/reporting phases:
- Strategy logic
- Thresholds
- Scoring
- Maturity logic
- Broker/live/shadow behavior

## Research-only disclaimer

Research-only: This project output is for research tracking and education only. It is not investment advice. No live trading. No broker execution. No production activation.
