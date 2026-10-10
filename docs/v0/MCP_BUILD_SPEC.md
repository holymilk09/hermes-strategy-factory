# Strategy Factory — MCP Server Build Spec (Research Layer)

Date: 2026-10-08 | Status: SPEC — no code yet | Evidence standard: same QC bar as everything in this branch

## 1. What this is

An MCP server that exposes Strategy Factory's **research-intel layer** to personal AI agents (Grok, OpenAI-based agents, bots, news agents). The agent calls the server, gets honest research ranked by the user's interest profile, and renders it in the user's own conversation.

This is the distribution mechanism for the v0 research-intel goal: interest graph, portfolio context, relationship engine — not a new signal, not a path to live trading.

## 2. Product order (non-negotiable)

1. **Research tools now** — relationships, betas, cohort summaries with caveats. Shippable without a proven edge.
2. **Signal tools only after the forward test verdict** — `scan_setups` stays gated behind `momentum_continuation_ret5d_ma50_v1`'s success/kill bars. A failed hypothesis never gets an endpoint.

## 3. Architecture

```
Personal agent (any platform)
        │  MCP (stdio for local, SSE for hosted)
        ▼
Strategy Factory MCP server ── read-only, no execution, no broker
        │
        ├─ research data (local ledgers, relationship maps, forward-test state)
        └─ gateway (auth, rate limits, metering) — separate deployable
```

The server itself holds no credentials and performs no writes to ledgers. The gateway handles API keys, per-call metering, and tier enforcement.

## 4. Interest profile (input, per request)

The agent sends a distilled profile — never raw chat history:

```json
{
  "tickers": [{"symbol": "MU", "weight": 0.9, "last_mentioned": "2026-10-07"}],
  "sectors": [{"sector": "semiconductors", "weight": 0.7}],
  "holdings": [{"symbol": "SKHY", "weight": 1.0}],
  "lookback_days": 30
}
```

Weights decay with time (explicit decay function, documented in the tool description). The server uses the profile only to **rank and filter** research — it changes what's shown first, never what's true.

## 5. Tool surface (research layer)

### `brief`
Interest-ranked research brief. Inputs: interest profile, optional date. Output: ranked items (setups-if-ungated, relationship notes, beta moves), each with evidence label, sample size, and caveat line.

### `cohort_summary`
Resolved forward-observation record: n, mean, median, hit rate, per-cohort breakdown. Always includes the "13 observations is not a validated edge" style caveat with current n. No performance claim may omit sample size.

### `relationship_map`
Sector/thematic clusters, per-holding beta to SPY/QQQ, lead-lag linkages (e.g. MU earnings → SKHY). Point-in-time correlations only, never asserted causally — a decoupling is reported as its own signal.

### `hypothesis_status`
Current forward-test state: hypothesis ID, rule, n resolved / pending, success/kill bars, next resolution date, verdict if taken.

### `scan_setups` — GATED, not in v1
Returns rule-based selections with features and the completeness guarantee. Ships only if the hypothesis passes its preregistered bars. Until then, calls return the hypothesis status and the reason for gating.

## 6. Honesty requirements (enforced in code, not docs)

- Every tool response includes: evidence label per claim, sample sizes, horizon conventions, and known limitations.
- Interest ranking must be explainable: each ranked item carries `why_shown` (e.g. "matches tickers MU, SKHY in profile").
- No tool may emit a buy/sell recommendation. Research outputs only. `brief` headlines pass a
  runtime compliance lint (`docs/v0/tools/mcp_server/compliance.py`) that rejects calls to
  action and performance claims; every response carries the research-only disclaimer.
  Basis: the compliance analysis in `docs/claude-v0/COMPLIANCE.md` on the sibling branch
  (Advisers Act / Lowe impersonal-publication line) — adopted here as code, not copy.
- Rate-limited, logged; anomalous usage patterns are visible to the operator.
- Data licensing: the P1 prototype reads Yahoo Finance (research use). Yahoo's terms, like
  Robinhood's, restrict commercial redistribution — a licensed, redistributable daily-data
  vendor must replace Yahoo in the product path before any paid distribution, and Phase 1
  data-integrity checks must be re-run on the vendor's feed. This is a Matt decision (§10).

## 7. Security boundaries

- Read-only. The server cannot place orders, move money, or modify ledgers. `sent_to_broker` is always False everywhere in this branch.
- No secrets in the repo, chat, or tool configs. Gateway keys live in the deploy environment.
- The interest profile is transient per request; the server does not retain user data.

## 8. Monetization sketch

- Metering at the gateway: per-call pricing with monthly tiers (research calls cheap, bulk brief generation metered higher).
- Agent platforms can bundle: one integration, per-seat billing passed through.
- Pricing is TBD — needs Matt's call after the prototype exists. Not a Shopify sheet; the product is the API.

## 9. Build phases

- **P0** — this spec. Done 2026-10-08.
- **P1** — prototype MCP server (Python, `mcp` package): `brief`, `cohort_summary`, `relationship_map`, `hypothesis_status` backed by local research data. Local stdio first. **Done 2026-10-08** — `docs/v0/tools/mcp_server/` (server, README, requirements pinning `mcp<2`); self-test passes against the live forward ledgers.
- **P2** — hosted SSE + gateway: auth, rate limits, metering, usage dashboard.
- **P3** — pilot integrations: one agent platform, dogfooded on Matt's own briefs first (the proactive-brief crons are the natural first consumer).

## 10. Open questions for Matt

1. Pricing: per-call vs per-seat vs flat tiers?
2. Which agent platform gets the first pilot integration?
3. Data licensing: confirm Yahoo-grade data is acceptable for research outputs (it is not execution-grade — research-only labeling covers this, but confirm).
4. Does the forward-test verdict gate the *whole* MCP launch, or does the research layer ship independently? (Recommendation: research ships independently.)

## 11. Relation to existing work

- Builds on: `HYPOTHESIS_momentum_ret5d_ma50_v1.md` (gated signals), `AUDIT_MATCHED_WINDOW_2026-10-05.md` (honesty baseline), `QC_CONTINUITY_2026-10-04.md` (evidence labels), `HANDOFF_NEXT_OPERATOR.md` (operator start-here).
- Changes nothing in the frozen lineage, ghost ledger, or recovered bundles.
