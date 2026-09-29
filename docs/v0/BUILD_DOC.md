# Strategy Factory v0 — Research Intelligence (build doc)

**Branch:** `v0-research-intel` · **Date:** 2026-09-29 · **Author:** Muse (with Matt)

## 1. Objective

Build a research-intelligence system that:

- **Adapts in real time** to what Matt is interested in (explicit ticker
  mentions + current holdings, with decay)
- **Knows the portfolio**, so every output is framed as "what this means for
  your book"
- **Reasons about relationships**: if one stock moves, which others likely
  follow — sector/thematic clusters (e.g. chip stocks), per-holding beta to
  SPY/QQQ, lead-lag event linkages (e.g. MU earnings → SKHY read-through)
- **Reduces to concise terms**: every output paints the picture and carries
  forward guidance (what to do / watch / avoid). Where the data gives no
  guidance, the system says so and interprets explicitly.

## 2. Non-goals

- No broker integration, no shadow execution, no live trading. The repo's
  production-BLOCKED posture applies here unchanged.
- No new validated signals. v0 consumes and interprets; it does not promote
  strategies through the validation gates.
- No modifications to `feature_factory/`, validation gates, thresholds,
  scoring, maturity logic, or Edge Sheet packaging on this branch.

## 3. Components

### 3.1 Interest graph (`src/research_intel/interest.py`)

Ranked watchlist answering "what should the system be paying attention to?"

- **Sources:** explicit ticker mentions (chat), current holdings, manual pins.
- **Decay:** exponential decay on mention-driven interest (half-life ~14 days,
  tunable); holdings do not decay; manual pins do not decay.
- **Output:** `ranked_watchlist(as_of) -> [(ticker, score, reason_codes)]`.
  Reason codes are mandatory — it must always be inspectable *why* something
  is watched.

### 3.2 Portfolio context (`src/research_intel/portfolio.py`)

- Positions, weights, cluster membership per holding.
- Frames every product output against the book
  ("you hold 201 SKHY — here's what this means for you").

### 3.3 Relationship engine (`src/research_intel/relationships.py`)

The quantitative core. Head start: `config/sector_etf_map.yaml` and the
sector-ETF residual machinery already in mainline.

- **Clusters:** sector/thematic membership per holding (chips, AI power,
  consumer, …), seeded from `sector_etf_map.yaml`, verified empirically.
- **Beta:** per-holding rolling beta to SPY and QQQ (60d and 120d windows).
- **Pairwise co-movement:** rolling correlations within clusters, measured
  point-in-time, never asserted.
- **Lead-lag notes:** event-driven linkages (earnings calendars, sector news)
  recorded as hypotheses with expiry dates, then scored.
- **Decoupling detection:** a historically-correlated pair breaking down is a
  first-class signal ("SKHY decoupling from MU into earnings — investigate"),
  not an error.

Public surface:

- `cluster(ticker) -> ClusterInfo`
- `beta(ticker, index="SPY", window=60) -> float`
- `pair_health(a, b) -> CorrelationHealth`
- `decouplings(since) -> [DecouplingEvent]`

All deterministic. No LLM inside this module.

### 3.4 Research loop (`src/research_intel/loop.py`)

- **Scheduled:** adaptive morning brief (interest-weighted, relationship-aware).
- **Event-triggered:** move alerts when a watched name crosses its threshold,
  framed by cluster/beta/event context.
- **Weekly:** relationship map regeneration.
- **LLM boundary:** deterministic data in; the LLM synthesizes the concise
  output and the guidance. The LLM never invents numbers and never triggers
  actions — there is nothing to trigger on this branch.

## 4. Products

| # | Product | Consumer | Cadence |
|---|---------|----------|---------|
| 1 | Adaptive morning brief | Matt | Daily premarket |
| 2 | Move alerts with relationship context | Matt | Intraday, threshold-gated |
| 3 | Weekly relationship map | Matt | Weekly |

These three are also the prototype subscription products: if they are valuable
to Matt, they are the product-development path for the Edge Sheet / Shopify
offering on mainline. Positioning while unvalidated: *intelligence*, not
*validated signals* — the "highly accurate" claim is earned by the mainline
validation pipeline, not this branch.

## 5. Data

- **Reuse:** feature factory outputs, `sector_etf_map.yaml`, existing ledgers.
- **New:** real-time quotes + news scoped to the *watchlist only* (bounded
  cost — watchlist-sized, not universe-sized).
- **Discipline:** every input carries an as-of timestamp; historical
  relationship runs use point-in-time data only.

## 6. Milestones

- **M1** — Branch scaffold + this build doc. *(this commit)*
- **M2** — Relationship engine offline: historical clusters, betas, and
  decouplings computed for current holdings; results reviewed against known
  market behavior (sanity gate).
- **M3** — Interest graph + portfolio context wired; watchlist generation live.
- **M4** — Morning brief product running for Matt daily.
- **M5** — Move alerts with relationship context.
- **M6** — Weekly relationship map.
- **M7** — Merge-back decision: does the intelligence layer earn a place in
  mainline?

## 7. Safety

Research-only. No execution paths exist on this branch and none will be
added here. Matches the repo's BLOCKED posture on production/live/shadow.
