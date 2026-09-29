# v0 — Research Intelligence (branch)

**Branch:** `v0-research-intel`
**Status:** scaffold + build doc (M1)

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

- `BUILD_DOC.md` — the full build document: components, interfaces, math,
  milestones, safety
