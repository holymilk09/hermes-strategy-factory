# Strategy Factory — what it is for, what its edge is, and how it reaches users

Branch `claude/v0-build` · 2026-10-09 · Claude (Anthropic). Evidence labels as in the repo.

## 1. The goal, as stated in this repo

- Mainline (`README.md`, `docs/commercial/`): a research-first quantitative workflow with
  strict safety boundaries and a cheap customer-facing output layer — the Edge Sheet,
  "see what's strong, weak, and too risky before you chase it", $5/month, research-only.
- v0 (`docs/v0/BUILD_DOC.md`, `MCP_BUILD_SPEC.md`): an intelligence layer that adapts to the
  user's holdings and interests, reasons about how names move together, and is consumed by
  personal AI agents over MCP; research tools now, signal tools only after a forward-test verdict.
- Matt: supply users directly and/or their personal AI agents; make it a side income.

## 2. The edge, honestly

**There is no demonstrated trading edge in this repository, and nothing here claims one.**
The frozen lineage has 13 forward observations (July cohort 1/6 winners, −10.4% mean); the
matched-window audit retired the only filter-lift claim; trend extension is in the graveyard;
residual reversion is event-blocked; the preregistered `ret5d+ma50` hypothesis has zero
resolved observations. Selling "picks" on that record would be false and, under the FTC's
deception standard, actionable (COMPLIANCE.md §2).

What the gates did show (VALIDATION_RESULTS.md), on 15 months the thresholds never saw:

- Same-day attribution works: the engine's beta-implied move beats a naive beta = 1 model on
  23/27 names (−20% error); adding an orthogonalised sector factor cuts unexplained variance
  for 24/24 names (−24% pooled).
- Abnormal-move flags mark genuinely abnormal periods (next-day ratio 1.37, CI 1.20–1.56).
- Decoupling flags are followed by lower co-movement (0.32 vs 0.48 over the next 60 sessions).
- A 95% one-day historical VaR on a six-name book was hit on 3.1% of sessions (in band).
- Two plausible-sounding claims did NOT survive and were removed (peer lists, peer-earnings
  read-through).

So the defensible edge is not alpha. It is **correctness and honesty in a market where the
buyer is an AI agent**:

1. Agents are fluent and numerically unreliable. They hallucinate prices, mix split-adjusted
   and raw closes, ignore corporate actions, and never state sample sizes. This layer is
   point-in-time, settled-close, corporate-action-audited (it caught a broken HON series and a
   spin-off that both an exchange feed and a naive audit missed), deterministic, and every
   number traces to a stated window and sample.
2. Every output says what it is: a same-day decomposition, a trailing statistic, a pro-forma
   risk figure, a flag with its threshold. Nothing is a forecast unless a registered forward
   test says so, and none does yet.
3. The forward-test ledger is the product's spine, not its marketing: preregistered bars,
   immutable rows, failures published. That is the one asset that compounds — a public,
   auditable record of which hypotheses survived — and it is the only honest road to a
   signal product later.

That combination is rare: raw-data APIs have no analytics or honesty layer; newsletters have
no auditability; "AI stock pickers" have neither.

## 3. The product (built on this branch; all IMPLEMENTED — CODE VERIFIED)

One methodology, applied identically to every request, selected by the user's own holdings,
pins and mentions (impersonal in substance — COMPLIANCE.md §1):

- **Daily brief** — abnormal-move flags with earnings context; decoupling/divergence flags;
  book beta and group exposure; why each name is shown.
- **Attribution** — each holding's and the book's session return split into market, sector
  and stock-specific (two-factor, orthogonalised sector ETF).
- **Risk panel** — realised vol, betas, HHI/effective names, average pairwise correlation,
  diversification ratio, max drawdown, 1-day historical VaR/ES, risk contribution. Pro forma.
- **Scoreboard** — the Edge Sheet promise as defined rules: trailing excess returns vs SPY,
  vol regime percentile, extension z-score, distance from the 120-session high.
- **Relationship map / weekly changes** — betas, group cohesion, flag transitions.
- **Research record** — cohort summaries and hypothesis status with sample sizes and bars.

Delivery, both paths in code:
- **Direct:** `python -m src.research_intel.cli report` → JSON + markdown + a self-contained
  phone-width HTML page (email/web).
- **Agents:** `python -m src.research_intel.server` → MCP (stdio) with tools `brief`, `report`,
  `attribution`, `risk`, `scoreboard`, `relationship_map`, `hypothesis_status`,
  `cohort_summary`, `data_status`. Read-only annotations; profiles are transient.

Enforced in code (tests): no calls to action or performance claims in any rendered text;
customer mode refuses to start on personal-use data or without an operator disclosure; every
response carries provenance, methodology, disclaimer and disclosure.

## 4. Business model that fits the law and the evidence

- **Tier 1 — direct subscription (the Edge Sheet, upgraded).** A daily/weekly report for a
  user-supplied book. Impersonal methodology, user-directed filter (the Seeking Alpha line).
  Price in the Edge Sheet's range; the cost that matters is licensed data (§5).
- **Tier 2 — agent access (MCP).** Per-seat or metered API keys for personal-agent platforms.
  The agent personalises on its side; this server never does. Highest leverage: one
  integration, many users.
- **Tier 3 — the ledger as a public good and a lead source.** Publish the forward-test record
  (with failures). It is the credibility engine for tiers 1–2 and the only path to a
  signal tier, which stays gated on a registered verdict.

What must happen before any paid customer (in order): (1) licensed, redistributable daily
data replaces Robinhood in the product path; (2) `disclosures.yaml` configured truthfully;
(3) terms of service + privacy policy flowing down vendor restrictions; (4) counsel-reviewed
adviser-status memo on file; (5) Phase 5 dogfood on Matt's own book, graded by Matt.

## 5. What is NOT done, and the decisions that are Matt's

- **Data licence.** Robinhood's Customer Agreement bars commercial use and redistribution of
  its market data (COMPLIANCE.md §3). The code refuses customer mode on it. Candidate vendors
  whose business terms permit end-user display of derived analytics are listed there with
  what could and could not be verified; pick one, budget it, and re-run Phase 1 on its data.
- **Flag threshold.** `flag_z` is now a profile setting (default 2.5 ≈ 3% of stock-days);
  the registered band question is logged, not silently resolved.
- **Hosting/metering/billing.** Not built; the stdio server is the local, dogfood form. A
  hosted gateway (auth, rate limits, metering) is the next engineering step after Phase 5.
- **Alpha.** Only through the ledger: register, run, resolve, publish. No shortcuts.
