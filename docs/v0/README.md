# v0 — Research Intelligence (branch)

**Branch:** `v0-research-intel`
**Status:** scaffold + build doc (M1); research record complete 13/13 resolved as of 2026-10-04 — see `HANDOFF_NEXT_OPERATOR.md`

## What this is

An adaptive research-intelligence layer on top of Strategy Factory: it watches
what Matt is interested in, knows his portfolio, and reasons about how stocks
move together (sector clusters, SPY/QQQ beta, lead-lag event linkages). Output
is concise, plain-English, and always carries forward guidance.

## What this is not

- Not a new signal, not a strategy promotion path
- No broker integration, no shadow execution, no live trading — the repo's
  BLOCKED posture on production applies to this branch unchanged
- No changes to `feature_factory/`, validation gates, scoring, maturity logic,
  or Edge Sheet packaging

## Relationship to mainline

Mainline keeps the full Strategy Factory vision: the five-stage validation
pipeline backing "highly accurate data" sold as low-cost Shopify subscriptions,
with Edge Sheet as the retail-readable reporting layer.

This branch borrows mainline's shared spine (data discipline, ledgers, sector
maps, research tooling) and builds the intelligence products on top:

1. Adaptive morning brief
2. Move alerts with relationship context
3. Weekly relationship map

**Merge-back rule:** if the products prove out in daily use, the intelligence
layer merges into mainline as the product-development path for the subscription
offering. If not, this branch is deleted and mainline never knew.

## Docs

- **`HANDOFF_NEXT_OPERATOR.md` — START HERE (2026-10-04).** Canonical state (13/13 resolved), recovered-bundle hashes, QC gate, traps, open gaps. Any new operator/LLM begins here; Hermes/VPS is no longer required.
- `RESOLUTION_2026-10-04.md` — July cohort resolution: procedure, per-name results, preservation diff, test counts.
- `AUDIT_MATCHED_WINDOW_2026-10-05.md` — accepted vs ghost matched-window audit: no consistent filter lift; old +23.30pp lift claim retired; gate-level split (`ret_5d` useful-looking, `ret_20d_rank` non-separating). Script: `tools/matched_window_audit.py`.
- `HYPOTHESIS_momentum_ret5d_ma50_v1.md` — NEW preregistered hypothesis (simple `ret_5d>0` + close>ma50 rule), split off 2026-10-05 after the audit. Forward test only; scanner: `tools/momentum_ret5d_ma50_scanner.py`. Does not modify the frozen lineage.
- `RECOVERY_2026-10-04.md` — how the ledgers/caches/backups were recovered and verified; what remains VPS-only.
- `QC_CONTINUITY_2026-10-04.md` — ChatGPT QC continuity reference reconciled by Muse: rules, error catalogue, traps, gaps, and deviation log governing any ledger work. Standing guidance, not scripture — better verified evidence overrides it (see its §9).
- `BUILD_DOC.md` — the full build document: components, interfaces, math,
  milestones, safety
- `HANDOFF_DIGEST.md`, `RECONCILIATION.md`, `RECOVERY.md`, `RESOLUTION_RUNBOOK.md` — original 2026-09-29→10-03 working docs (RESOLUTION_RUNBOOK is executed/historical, correction header on file).
- `chatgpt-handoff-2026-09-29.md` — verbatim original handoff (648 lines), historical anchor.
- `tools/resolve_pending_guarded.py` — the guarded resolver used 2026-10-04 (operator script, not wired into src/).
