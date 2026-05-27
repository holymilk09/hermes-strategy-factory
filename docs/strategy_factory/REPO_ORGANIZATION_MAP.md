# Repository Organization Map

Asset: Hermes Strategy Factory
Updated: 2026-05-27

## Canonical Owner Map

| Concept | Owner | Path | Overlap Risk |
|---|---|---|---|
| Strategy candidate generation | `relative_strength_continuation.py` | `src/research/momentum/relative_strength_continuation.py` | LOW |
| Relative strength observation cycle | `relative_strength_observation_cycle.py` | `src/paper/relative_strength_observation_cycle.py` | LOW |
| Regime-conditioned observation cycle | `capitulation_v2_drawdown.py` | `src/research/regime_conditioned/capitulation_v2_drawdown.py` | LOW |
| Observation ledger | CSV at `data/paper_observation/*_observation_ledger.csv` | Written by `src/paper/relative_strength_observation.py` | LOW |
| Outcome ledger | CSV at `data/paper_observation/*_outcome_ledger.csv` | Written by `src/paper/relative_strength_observation.py` | LOW |
| Maturity watchdog | `maturity_watchdog.py` | `src/paper/maturity_watchdog.py` | LOW |
| Edge Sheet generation | `generate_edge_sheet.py` | `scripts/generate_edge_sheet.py` | LOW |
| Edge Sheet HTML rendering | `render_edge_sheet_html.py` | `scripts/render_edge_sheet_html.py` | LOW |
| Retail wording layer | `retail_wording.py` | `src/reporting/retail_wording.py` | LOW |
| Ghost ledger | `ghost_ledger.py` | `src/reporting/ghost_ledger.py` | LOW |
| Trust calibration | `trust_calibration.py` | `src/reporting/trust_calibration.py` | MEDIUM — also uses ghost ledger data |
| Trust calibration reports | `trust_calibration_reports.py` | `src/reporting/trust_calibration_reports.py` | LOW |
| Healthcheck | `run_feature_factory_healthcheck.py` | `scripts/run_feature_factory_healthcheck.py` | MEDIUM — overlaps with audit scripts |
| Forward observation | `forward_observation.py` | `src/paper/forward_observation.py` | LOW |
| Observation cycle orchestrator | `observation_cycle.py` | `src/paper/observation_cycle.py` | MEDIUM — base class, `relative_strength_observation_cycle.py` extends |
| Shadow orders | `shadow_orders.py` | `src/paper/shadow_orders.py` | LOW (research only) |
| Edge Sheet HTML template | `edge_sheet_html.py` | `src/reporting/edge_sheet_html.py` | LOW |
| Maturity scoreboard | `maturity_scoreboard.py` | `src/reporting/maturity_scoreboard.py` | LOW |
| Freshness gates | `freshness_gates.py` | `src/paper/freshness_gates.py` | LOW |
| Outcome gate | `outcome_gate.py` | `src/research/meta/outcome_gate.py` | LOW |
| Observation drift | `observation_drift.py` | `src/research/meta/observation_drift.py` | LOW |
| Hypothesis registry | `hypothesis_registry.py` | `src/research/meta/hypothesis_registry.py` | LOW |
| Config | `strategy_config.yaml`, `feature_config.yaml`, `config.yaml` | Root-level | MEDIUM — multiple config files, need consolidation plan |
| Daily ops script | `run_daily_observation_ops.sh` | `scripts/run_daily_observation_ops.sh` | LOW — orchestrator only |
| Compliance language | `retail_wording.py` (DISCLAIMER constant) | `src/reporting/retail_wording.py` | LOW |
| Commercial docs | (planned) | `docs/commercial/` | LOW |
| Reports (strategy_factory) | Generated | `reports/strategy_factory/` | N/A — runtime artifacts |
| Reports (edge_sheet) | Generated | `reports/edge_sheet/` | N/A — runtime artifacts |
| Reports (trust_calibration) | Generated | `reports/trust_calibration/` | N/A — runtime artifacts |
| Test suite (reporting) | Pytest | `tests/reporting/` | LOW |
| Test suite (feature factory) | Pytest | `tests/feature_factory/` | LOW |
| Test suite (integration) | Pytest | `tests/*.py` (root) | MEDIUM — split across root and subdirs |
| Scoring logic | `relative_strength_continuation.py` | `src/research/momentum/relative_strength_continuation.py` | LOW |
| Filter logic | Various `gates` in observation modules | Spread across `src/research/` | MEDIUM — filter definitions duplicated in ghost recording gates |

## Do-Not-Duplicate Rules

1. **Maturity engine** — `src/paper/maturity_watchdog.py` is canonical. Do not create a second maturity engine.
2. **Outcome ledger** — `data/paper_observation/*_outcome_ledger.csv` is canonical. Do not create a second outcome ledger.
3. **Edge Sheet generator** — `scripts/generate_edge_sheet.py` is canonical. Do not create a second Edge Sheet generator.
4. **Retail wording mapper** — `src/reporting/retail_wording.py` is canonical. Report renderers must call this, not replicate it.
5. **Ghost ledger** — `src/reporting/ghost_ledger.py` is canonical. Do not create a separate ghost tracking system.
6. **Trust engine** — `src/reporting/trust_calibration.py` is canonical. Do not create a separate trust scoring engine.
7. **Outcomes in renderers** — Report renderers must read pre-computed outcomes from ledgers. Do not recalculate outcomes inside HTML/email renderers.
8. **Product tiers and strategy logic** — Product tiers (Shopify, email, etc.) must read cached/generated outputs. They must never trigger fresh strategy runs per user.

## Proposed Folder Organization (documented only — no files moved)

```
src/
  paper/          — maturity/observation/execution logic (canonical
                    for after-signal lifecycle)
  reporting/      — output transformation, retail wording, ghost ledger,
                    trust calibration, HTML rendering
  research/       — strategy candidate generation, validation, filters,
                    walk-forward, backtest logic
  data/           — data loading helpers (if already present)
  features/       — feature computation/audit (if already present)
  safety/         — future planned (risk gates, execution audits)

scripts/
  run_*.py        — operator entrypoints only
  tmp_*.py        — marked as experimental/one-off
  *.sh            — shell orchestrators

tests/
  reporting/      — edge sheet, ghost, trust calibration tests
  feature_factory/— health contract tests
  safety/         — future planned
  integration/    — future planned

docs/
  strategy_factory/ — runbook, roadmap, organization map, contracts, guardrails
  releases/         — phase release notes
  commercial/       — future (Shopify copy, marketing samples)
  compliance/       — future (disclaimer versions, data license notes)

reports/
  edge_sheet/       — generated daily `YYYY-MM-DD_edge_sheet.*`
  trust_calibration/— generated `FILTER_IMPACT_AUDIT_*.md`, `GHOST_LEDGER_SUMMARY_*.md`
  strategy_factory/ — healthcheck, watchdog, observation status, build reports

examples/
  edge_sheet/       — curated public-safe sample Edge Sheets
```