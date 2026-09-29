# ChatGPT Strategy Factory handoff — verbatim

**Received:** 2026-09-29
**Source:** ChatGPT (design brain behind Strategy Factory; Hermes agent implemented the code)
**Purpose:** Backtrack anchor — the complete design rationale as ChatGPT recorded it.
**Companion:** `HANDOFF_DIGEST.md` (distilled reference)

> Everything below is ChatGPT's handoff, reproduced verbatim. Evidence labels
> (IMPLEMENTED — CODE VERIFIED, IMPLEMENTED — OPERATOR REPORTED, PLANNED,
> BLOCKED, HISTORICAL, RECONSTRUCTED / UNCONFIRMED) are ChatGPT's own and are
> defined in §1.1.

---

1. Project overview

1.1 What this handoff covers

This handoff distinguishes three things that must not be conflated:

1. The original residual mean-reversion research program, including the eight escalating validation gates and FMP event-risk sandbox.
2. The later relative-strength continuation observation program, which produced the AMD/ARM/CRWD/DDOG/MRVL/SEDG observations and the subsequent six-name July cohort.
3. The Strategy Factory Edge Sheet product, which packages research outputs without becoming a broker-connected trading system.

The original residual strategy and the later continuation strategy are different research lineages, not alternative names for the same signal. The repository's hypothesis registry explicitly contains multiple lineages, including canonical SPY residual, sector residual, factor residual, capitulation, and relative-strength continuation.

Evidence labels used in this document

Label	Meaning
IMPLEMENTED — CODE VERIFIED	I inspected the relevant committed source or configuration while preparing this handoff.
IMPLEMENTED — OPERATOR REPORTED	Hermes reported implementation or successful execution in this conversation; I have not independently rerun the VPS operation.
PLANNED	A design, specification, roadmap item, or proposed operating procedure—not proof of deployment.
BLOCKED	Explicitly prohibited or awaiting evidence, data, authorization, or implementation.
HISTORICAL	True of a particular earlier checkpoint; not necessarily the active production state.
RECONSTRUCTED / UNCONFIRMED	Recovered from prior context or memory but not fully corroborated by the inspected source.

Repository reference inspected: holymilk09/hermes-strategy-factory, branch trust-calibration-working, resolving to:

1f1a238eb8c17f2340699ed6d6a30017fe3eeb13
Rebaseline manifest for approved pending cohort

That branch head was checked directly for this handoff. The live VPS ledgers, environment variables, installed dependencies, and current data cache were not accessed or rerun here. Their latest operational status must therefore remain distinguished from the committed source.

1.2 What Strategy Factory is

Strategy Factory is a research-first quantitative development and accountability system.

Its intended job is to:

* Define a research hypothesis precisely.
* Compute features without using future information.
* Test the hypothesis against increasingly demanding baselines.
* Record both accepted and rejected candidates.
* Observe what happens after a signal without altering the original signal.
* Separate raw price appreciation from market, sector, and implementation effects.
* Translate the resulting evidence into understandable research artifacts.

The project is not simply a stock screener. The central idea is a controlled pipeline that can say:

"This setup qualified under these rules, with this information available at the time. Here is what subsequently happened, what the benchmarks did, and whether the filter added anything."

The README identifies the project as research-first, with strict safety boundaries and a customer-facing output layer.

1.3 The problem it is meant to solve

The project addresses two separate problems.

Research problem: Backtests and signal reports can look convincing because of leakage, favorable universes, market drift, repeated experimentation, unrealistic implementation, inconsistent return units, or selective reporting.

User problem: Retail traders often receive a conclusion without an inspectable process. They see a stock score or a favorable screenshot, but not the rejected candidates, deteriorating setups, subsequent outcomes, or uncertainty.

The intended differentiator is documented rules plus visible accountability, not an assertion that the system already possesses predictive superiority.

1.4 End vision: Strategy Factory Edge Sheet

PLANNED PRODUCT; PACKAGING IMPLEMENTED

The original product was:

Product:
Strategy Factory Edge Sheet — Founding Access
Price target:
$5/month
Core hook:
The 60-second stock setup sheet.
Marketing hook:
See what's strong, weak, and too risky before you chase it.

The intended initial cadence was a Monday research sheet and Friday accountability scoreboard. The $5 founding-access price is an actual documented product direction, not a price inferred from later competitor discussions.

The product should eventually help users understand:

* Which supported stocks qualify under the current research rules.
* Which do not qualify, and why.
* What changed since the previous report.
* Whether an observation is still awaiting its outcome window.
* How completed observations performed relative to appropriate baselines.
* Which conclusions remain unsupported.

BLOCKED: Proven-edge marketing, automatic execution, personalized portfolio advice, or a paid launch justified merely by a small set of positive observations.

---

2. Architecture

2.1 The four named layers

These layers are explicitly documented in the repository. They describe responsibility boundaries, not necessarily separate deployed services.

Layer	What belongs here	What must not happen here
Truth Layer	Research engine, feature calculations, candidate selection, forward observations, outcome resolution, ledgers, data-quality checks, audit calculations, healthchecks	Marketing language must not determine results; historical signals must not be rewritten to improve outcomes.
Artifact Layer	JSON, Markdown, scoreboard, static HTML, email previews, structured export	Renderers must not invent returns, recalculate strategy decisions independently, or silently replace missing values with favorable ones.
Commercial Packaging Layer	Product name, landing-page copy, FAQ, disclaimers, pricing copy, manual Shopify checklist	Packaging must not promote research labels into performance guarantees or trading instructions.
External Manual Layer	Initially, founder-operated Shopify setup, external delivery, legal review, account administration	External product tools must not become an uncontrolled route into strategy generation or broker execution.

A later hosted database/API architecture was planned around these layers. That did not eliminate their separation.

2.2 Canonical data flow

Market data and event-context sources
    │
    ├── OHLCV ingestion / calendar / completeness checks
    └── Event-risk sandbox, where applicable
    │
    ▼
Feature and strategy research
    │
    ├── Candidate universe
    ├── Fixed strategy rules
    └── Research validation gates
    │
    ▼
Approved forward-observation process
    │
    ├── Observation ledger: what was observed
    ├── Outcome ledger: what subsequently happened
    └── Ghost ledger: what was rejected
    │
    ▼
Economic sanity / drift attribution / filter-quality audit
    │
    ▼
Canonical research artifacts
    │
    ├── Edge Sheet JSON / Markdown
    ├── Maturity scoreboard
    ├── HTML / email preview
    └── Database-ready export
    │
    ▼
Planned approval and publication system
    │
    ▼
Customer-facing research product

The organization map explicitly prohibits duplicate maturity engines, outcome ledgers, ghost systems, trust-scoring engines, and independent renderer calculations. Product tiers should consume cached/generated outputs rather than trigger fresh research for each user.

2.3 Important code locations

Original feature/research infrastructure

feature_factory/
config/feature_registry.yaml
config/retail_portfolio_constraints.yaml
config/backtrader_retail_research.yaml
config/event_risk_blocker.yaml
config/fmp_sandbox.yaml
config/fmp_event_features.yaml
alpha_graveyard/
knowledge-base/

Later strategy and observation infrastructure

src/research/momentum/relative_strength_continuation.py
src/paper/relative_strength_observation.py
src/paper/relative_strength_observation_cycle.py
src/paper/maturity_watchdog.py
src/research/meta/hypothesis_registry.py
src/research/meta/observation_status.py
src/research/meta/observation_drift.py
src/research/meta/outcome_gate.py

Reporting and audit infrastructure

src/reporting/economic_sanity.py
src/reporting/drift_attribution.py
src/reporting/filter_quality_audit.py
src/reporting/ghost_ledger.py
src/reporting/trust_calibration.py
src/reporting/trust_calibration_reports.py
src/reporting/retail_wording.py
src/reporting/maturity_scoreboard.py
src/reporting/edge_sheet_html.py
src/reporting/market_calendar_freshness.py

Canonical operational paths

data/cache/ohlcv_1d/
data/paper_observation/
  relative_strength_continuation_observation_ledger.csv
  relative_strength_continuation_outcome_ledger.csv
data/trust_calibration/ghost_ledger.csv
reports/strategy_factory/
reports/edge_audit/
reports/edge_sheet/
reports/trust_calibration/

The owner map documents these responsibilities, while the current continuation module confirms the cache-discovery and observation paths.

2.4 The three-ledger contract

Observation ledger: Original observation identity, signal timestamp, symbol, initial price, lineage, configuration identity, and related research metadata.

Outcome ledger: Authoritative resolution status and measured future result.

Ghost ledger: Rejected candidates, rejection reasons, failed gates, and later outcomes.

A particularly important convention in the later implementation is:

Observation ledger:
Rows can retain outcome_status=PENDING permanently.
Outcome ledger:
Tracks actual PENDING / RESOLVED state.

Therefore, "all observation rows are PENDING" does not necessarily mean nothing has matured. Join by observation_id and inspect the correct ledger.

However, the committed resolver has an important preservation weakness described in Section 10: it rebuilds results from the observation ledger rather than treating the existing outcome ledger as an immutable historical source. The architecture's intended preservation rule is stronger than that implementation.

2.5 Read-only versus writing operations

Operation	Intended mutation boundary
Read-only maturity watchdog	May generate reports; must not change ledgers
Edge audit	May generate audit artifacts; must not change ledgers
OHLCV refresh/backfill	Changes market-data cache, not research ledgers
Outcome resolver	Changes approved outcome records; must preserve unrelated resolved results
Observation cycle	Can generate new observations and rejected candidates
Ghost CLI dry-run	Computes proposed updates without changing the ghost ledger
Ghost CLI --write	Explicitly authorized ghost outcome updates
Exporter	Reads research state and produces output artifacts; no live database writes in the reported Phase 7B implementation

Never substitute the full observation-cycle wrapper for a maturity check. That exact mistake previously generated an unintended cohort.

2.6 Phase 7B output store

IMPLEMENTED — OPERATOR REPORTED

Phase 7B added:

db/migrations/001_initial_strategy_factory_output.sql
src/reporting/output_store_schema.py
scripts/export_strategy_factory_outputs.py
tests/reporting/test_output_store_schema.py
tests/reporting/test_export_strategy_factory_outputs.py
docs/production/OUTPUT_STORE_RUNBOOK.md

Reported tables:

system_runs
setup_cards
maturity_results
edge_audit_results
ghost_rejections
approved_publications
user_ticker_selections

The key design decision was:

CSV ledgers remain authoritative; PostgreSQL is an output/publication store, not a second strategy engine.

The exporter reportedly emits JSONL or SQL, defaults to dry-run, and does not implement live database writes.

PLANNED: Hosted database provisioning, authenticated API, real ingestion, approval UI, publication rollback, billing, and delivery.

Do not interpret "migration file created" or "tables defined" as "database deployed."

---

3. The signal

3.1 Original research hypothesis

HISTORICAL — IMPLEMENTED RESEARCH

The original residual mean-reversion hypothesis was:

A stock that has fallen unusually far relative to what its sector relationship would explain may exhibit a temporary idiosyncratic dislocation rather than an ordinary sector decline.

The residual calculation attempted to remove the component explained by a sector ETF before assessing the unusual movement.

The frozen research candidate was:

residual_z <= -2.0
AND
residual_r2 >= 0.20

Its historical status was:

CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED

It was a strategy-conditioned filter candidate, not established standalone alpha. The saved decision state explicitly says standalone_alpha: false.

3.2 What residual_z actually is in the original feature engine

IMPLEMENTED — CODE VERIFIED

The original implementation is in:

feature_factory/residual.py
compute_residual_features()

For a stock and benchmark ETF, it fits:

r_stock_j = alpha_t + beta_t * r_ETF_j + epsilon_jt

using a rolling window ending at the current observation.

Defaults:

regression_window = 60
zscore_window = 20

Within the fitted window, it estimates beta as the covariance of ETF and stock returns divided by ETF return variance, alpha as mean stock return minus beta times mean ETF return, and epsilon as the fitted residual. It then sums the most recent k fitted residuals (normally 20):

C_t = sum of last k epsilons

and computes residual_z as (C_t - k * mean_epsilon) / (sd_epsilon * sqrt(k)).

This is not merely the stock's daily return divided by its volatility. It is a normalized cumulative residual over a recent portion of the regression window. The implementation uses NumPy's default standard deviation convention.

Other residual features produced: residual_z, residual_beta, residual_alpha, cumulative_residual, residual_half_life, residual_r2, residual_return.

The half-life estimate regresses changes in a cumulative residual path on its lagged level. A nonnegative estimated slope produces an infinite half-life rather than evidence of mean reversion. This is a research diagnostic, not a guarantee that an Ornstein-Uhlenbeck model accurately describes the stock.

3.3 What R² measures

R² = 1 - sum(epsilon²) / sum((r_stock - mean_r_stock)²).

The intended purpose of the fit gate is to reject cases in which the chosen ETF does not explain enough of the stock's variation to make its "residual" a useful relative-dislocation measure.

R² is not a probability of a profitable trade. A stock with R²=0.20 is not "20% likely to work." It means that, under that fitted model and window, approximately 20% of the sample variation is explained by the regression.

3.4 Why the threshold was -2.0

Documented parameter; rationale partly reconstructed.

The negative threshold seeks an unusually negative residual excursion. The practical reasoning was to focus on a substantial dislocation instead of reacting to ordinary fluctuations.

The historical research tested residual-dislocation variants and retained -2.0 for the controlled candidate. There is no evidence that this is a universally optimal threshold or that it was derived independently of all experimentation.

The correct interpretation is: "This is the frozen research threshold for this lineage." Not: "A minus-two residual guarantees a rebound," or "the event has a calibrated normal-tail probability."

The normalization's square-root-of-window scaling does not itself establish residual independence, normality, or stationarity.

3.5 Why R² ≥ 0.20 mattered

HISTORICAL — DOCUMENTED RESULTS

The Phase 12.5 report records a material distinction between the unrestricted residual filter and the GOOD/ACCEPTABLE-fit subset:

Historical test	Selected sample	Reported actual mean	Random p95	Recorded conclusion
Mean reversion / ALL	196	2.58%	10.49%	Borderline
Mean reversion / GOOD	188	2.65%	2.21%	Beats strategy random
Structural MR / ALL	71	3.19%	10.62%	Borderline
Structural MR / GOOD	67	3.26%	1.41%	Beats strategy random

The same historical report records portfolio profit factor of 1.93 versus random p95 1.66 for mean reversion, and 2.19 versus 1.26 for structural MR. These are historical research-report results, not independently reproduced performance in this handoff.

That is the strongest documented project-specific reason for the fit gate: it materially changed the comparison against strategy-conditioned random selection.

The saved diagnostic state also reported: Universe: 76 symbols; Median R²: 0.3723; Good-fit symbols: 42; Acceptable-fit symbols: 25; Low-fit symbols: 3; Blocked symbols: 6; Usable symbols: 67. Those are results from that historical diagnostic packet, not current universe statistics.

3.6 Benchmark fallback

The feature-factory orchestrator uses:

Configured sector ETF
    ↓ unavailable
SPY, explicitly identified as market-only
    ↓ unavailable
Residual fields unavailable / blocked metadata

A SPY fallback does not become a sector residual merely because it occupies the same field names. Benchmark identity must travel with the result.

3.7 Alternatives considered and their outcomes

Trend-extension reversal — REJECTED / FROZEN IN GRAVEYARD. Used MACD, moving-average slopes, momentum to identify less-extended versus more-extended stocks. Looked encouraging in an early restricted sample, weakened on the full universe, failed random-pruning. Explicit prohibition: no rescuing the same failed hypothesis through new decile cuts, seed hunting, stop combinations, relabeling, or different wording.

Standalone residual filtering — NOT ACCEPTED AS STANDALONE ALPHA. Did not pass the required random baseline; retained use was conditioned on an existing strategy's candidate pool.

Canonical SPY residual — IMPLEMENTED RESEARCH LINEAGE: residual_z <= -2.0, residual_r2 >= 0.20, lineage = canonical_spy_residual_phase22a. Distinguishes mean_reversion from structural_mr using RSI/regime conditions.

Sector-residual Phase 27A — SEPARATE IMPLEMENTED RESEARCH LINEAGE: lookback=60, min_obs=45, sector_residual_z <= -2.0, sector_model_r2 >= 0.15, forward_window=5. Its normalization is a current residual divided by rolling residual SD — NOT the same cumulative-20 formula. Do not change .15 to .20 to make files agree; determine which lineage is intended first.

Other researched families: factor-residual MR, price-volume capitulation variants, regime-conditioned capitulation. Existence ≠ passed gates.

3.8 The later active signal: relative-strength continuation

IMPLEMENTED — CODE VERIFIED; DIFFERENT FROM RESIDUAL MR

The forward-observation track uses:

ret_5d > 0
close > ma50
ret_20d_rank >= 0.85
ret_60d_rank >= 0.70

All four conditions must pass. Ranks are cross-sectional percentiles within each timestamp. 10-bar outcome window. phase28a_weak_pass is a lineage acceptance label, not a per-stock grade.

---

4. Validation gates

4.1 The original eight escalating gates

1. Feature computation and storage — features/labels reproducible. A statistical result is meaningless if the data cannot be reproduced.
2. Leakage audit — future info, target columns, centered windows, timestamp misalignment. Check before interpreting performance.
3. Standalone IC and decile analysis — cheap screen for plausible information.
4. Full-universe confirmation — survives expansion beyond a favorable subset.
5. Strategy-conditioned tests — incremental value to the base strategy, not all-market observations.
6. Retail-constrained simulation — capital, positions, cash drag, costs, opportunity cost. Good event returns can be economically unusable.
7. Backtrader random-pruning comparison — beats same-count random selections under the same simulator. Separates useful filtering from taking fewer trades.
8. Strategy-conditioned random pruning — filter beats random subsets of the correctly defined base-strategy candidate pool.

Phase-number warning: use gate name, lineage, artifact, and commit — not the phase number alone.

4.2 The critical Phase 12.5 correction

Earlier random-pruning used residual events without conditioning on the base strategy first. Correct order: base strategy candidates → residual threshold → fit threshold → compare with random same-count subsets of the same base-strategy candidate pool. Changing the candidate pool changes the question being tested.

4.3 Historical retail constraints (config present; enforcement must be verified in the simulator)

$100k starting cash; max 8 positions; 12.5% max per symbol; 30% max sector; no margin/short; cash drag included; equal-weight capped; max 3 new positions/day; no duplicate symbol entries; 10-day same-symbol cooldown; 2% max daily loss; 10% max strategy drawdown; 40% correlation-cluster exposure; slippage 2/5/10 bps; next-bar-open entries; no same-bar entry/exit. Config presence ≠ enforcement in every reporting path.

4.4 Passing gates did not authorize production

Residual candidate still required event-context evaluation. Continuation observations still required prospective evidence. The "30 observations / 10 signal dates" rule was an organizational evidence gate, not a theorem that 30 observations establish profitability.

---

5. Feature factory

5.1 What was built — IMPLEMENTED RESEARCH INFRASTRUCTURE

Pipeline: ingestion → cleaning/alignment → enabled categories → feature store → labels/validation → research selection/backtest interfaces.

Count discrepancy: historical docs say 16 modules; 15 explicitly named files recovered. The "16 modules" claim stays flagged for reconciliation, not repeated as verified.

Recovered module inventory: __init__ (orchestration), ingestion, technical, statistical, regime, residual, microstructure (OHLCV liquidity proxies, not order-book data), store (versioned persistence), selection (ranking incl. mutual information), label_factory (1/3/5/10/20-bar horizons; triple-barrier 5%/3%/10-bar defaults — research targets, not live exit rules), purged_cv (n_splits=5, horizon-aware purge+embargo, no shuffle), leakage_audit (metadata/name checks — NOT a complete leakage proof; timestamp_valid set True by comment; decision_dates unused), redundancy_analyzer (0.90 abs-correlation grouping, highest-variance representative — a convenience heuristic), feature_importance_runner (stability_by_regime explicitly returns "NOT_IMPLEMENTED"), feature_validation_report.

5.2 Feature counts and registry

Historical: 120 features/symbol (51 technical, 35 statistical, 10 regime, 7 residual, 17 microstructure proxies). Treat as historical until regenerated. Registry tests require per-feature metadata: category, subcategory, formula, input_data, lookback, known_at_time, point_in_time_safe, missing_policy, version, expected_use, risk_notes. The registry test asserted ≥100, not exactly 120.

5.3 Labels — IMPLEMENTED, CODE VERIFIED

Forward horizons 1/3/5/10/20 bars; simple/log returns, excess vs SPY and sector ETFs, cross-sectional ranks, decile labels, triple-barrier labels, strategy-conditioned meta-labels. Triple-barrier defaults: 5% profit / 3% stop / 10 bars — research targets, not authorized live exits.

5.4 Purged walk-forward CV — IMPLEMENTED, CODE VERIFIED

n_splits=5, label_horizon=20, purge=embargo=label_horizon, no shuffle, chronological train-before-test. Index-based; does not by itself prove correct multi-symbol panel assembly or train-only preprocessing.

5.5 Leakage audit — IMPLEMENTED, NOT A COMPLETE LEAKAGE PROOF

Checks metadata/names for future shifts, centered windows, target-like names, invalid lookbacks. Limitations: timestamp_valid=True by comment; decision_dates unused; label separation largely naming-based. "Leakage audit passed" = the implemented checks passed, not formal point-in-time safety.

5.6 Redundancy analysis — IMPLEMENTED, CODE VERIFIED

Greedy grouping at 0.90 absolute correlation; highest raw variance chosen as representative (unit-dependent convenience heuristic). Must be fit on training portion only.

5.7 Feature importance — IMPLEMENTED, PARTIAL

Computes rank IC, mutual information, decile spread, bucket outcomes, missingness, stability summaries. stability_by_regime returns "NOT_IMPLEMENTED" despite advertised capability.

---

6. Event risk blocker

6.1 Why it exists

A large negative residual can be temporary dislocation or rational repricing (earnings, guidance, dilution, accounting, takeover). The blocker distinguishes "unusually weak vs sector" from situations where fading the move is conceptually inappropriate.

6.2 FMP's permitted role — IMPLEMENTED CONFIG; HISTORICALLY BLOCKED DATA INTEGRATION

Allowed: block, warn, tag, segment/contextualize. Explicitly NOT: standalone alpha, automatic trade signal, production trigger, live-trading trigger, Alpaca replacement, mandatory production dependency. Sandbox requires caching, rate-limit protection, env-supplied key, no API calls without a key.

6.3 Event categories

Earnings day: hard block. Earnings within 5d: pre-event block/caution. Earnings within 10d: specification inconsistency — blocker file says blocked, feature file says warning; reconcile, don't pick conveniently. First 2 post-earnings days: avoid fading repricing. Surprises usable only after publication. Guidance cuts, fraud/accounting, dilution, M&A, halts, sector/macro shocks, abnormal gaps with news: repricing/event risk.

6.4 Point-in-time policy

Scheduled earnings date (known pre-event) vs actual EPS/surprise (only after publication) vs analyst changes/news (only after timestamps). A historical API query today ≠ what was available on the signal date.

6.5 Unknown event context

Default: CAUTION_NOT_BLOCK, status EVENT_CONTEXT_INCOMPLETE. Price-volume proxies (extreme day moves, gaps, unusual volume) do not prove absence of fundamental repricing. Unknown stays visible.

6.6 What was missing — HISTORICALLY BLOCKED: FMP_API_KEY. Key alone wouldn't validate the event overlay. RECONSTRUCTED/UNCONFIRMED: a later cached-earnings overlay experiment reportedly had weak/failed incremental results (EVENT_BLOCKER_REJECTED) — needs its Phase 14 artifact before being treated as definitive.

---

7. Edge Sheet

7.1 Founding-access product — DOCUMENTED DIRECTION

$5/month, Monday research sheet + Friday scoreboard, one-to-many distribution. Later $9–25/free-newsletter discussions were opinions, not replacements of the $5 spec.

7.2 What was built — IMPLEMENTED, DOCUMENTED RELEASE

Markdown/JSON generator, deterministic retail-wording mapper, maturity scoreboard, golden + determinism tests, HTML/email renderer, founding-access copy, FAQ, compliance copy, manual Shopify checklist, commercial preview. Explicitly excluded: Shopify integration, payments, email sending, live dashboard, broker execution.

7.3 Customer-facing sections

Market Weather, Top Bullish Swing Setups, Waiting-for-Proof Setups, No Edge / Weakening Names, Hype Trap Radar, Popular Ticker Pulse, Price Areas That Matter, Setup-Break Levels, What Changed This Week, Friday Scoreboard, Reject/Ghost accountability. Section names ≠ operational data sources ("Hype Trap Radar" must not imply validated social/news intel).

7.4 Setup-card contract

symbol, main_view, time_range, model_score, price_area_that_matters, setup_breaks_below/above, why_it_looks_strong_or_weak, main_risk, what_changed, maturity_status, plain_english, disclaimer. Presentation labels: "Waiting for Stronger Proof," "No Edge," "Weakening," "Too Stretched," "No Reliable Rating Yet." Five-stage presentation (Market Weather → Strength → Proof → Price Zone → Break Level) is NOT the eight research gates.

7.5 Compliance language

Positioning: research tracking and education — not buy/sell alerts, guaranteed performance, personalized advice, or broker execution. Prohibited: guaranteed returns, proven winners, beat-the-market, risk-free, prediction-engine claims, personalized advice. BLOCKED/NOT ESTABLISHED: legal clearance. Compliance docs ≠ legal opinion.

7.6 Shopify checklist — IMPLEMENTED DOCUMENT; EXTERNAL SETUP NOT CONFIRMED

Manual: create product, $5/month founding-access, add copy/FAQ/compliance, upload archives later, keep delivery manual. No confirmed deployment, checkout, entitlements, or email delivery.

7.7 Later product direction — PLANNED/DEFERRED

Hosted Postgres/Supabase, Vercel, auth, approval workflow, email, subscriptions. Fable recommended pausing storefront during audit fixes; suggested free email-first launch; questioned Shopify necessity. Recommendations ≠ adopted architecture.

---

8. Research decisions

8.1 Rejecting a failed signal was a valid outcome — the alpha graveyard exists deliberately. Trend-extension reversal: attractive early IC → weaker corrected IC → restricted-universe spread → broader-universe failure → pruning failure → archive. No rescuing via threshold/seed/cut shopping.

8.2 A filter must beat "doing less" randomly — fewer trades can improve a portfolio via lower costs/congestion alone. Hence Gates 7–8.

8.3 Strategy conditioning precedes residual filtering (Phase 12.5 correction) — experimental correctness fix, not permission to re-tune until it wins.

8.4 Event context is a veto/context layer, not another alpha engine — FMP constrained to block/warn/tag.

8.5 Candidate outcome returns ≠ investable portfolio returns — mean forward return over overlapping observations is not CAGR. Economic-sanity checks added; still lighter than full capital accounting.

8.6 Maturity ≠ edge — hierarchy: signal recorded ≠ horizon complete ≠ positive return ≠ benchmark outperformance ≠ filter improvement ≠ executable profit ≠ durable edge. "Matured edge" as "resolved observation" is misleading wording; do not carry forward.

8.7 Original observations must survive reinterpretation — signal immutable; outcome resolution controlled; revised attribution versioned; new code must not silently rewrite history. (Current resolver does not fully enforce this — §10.2.)

8.8 May 28 accidental observation cycle — HISTORICAL, OPERATOR REPORTED. A maturity-check task invoked the full observation cycle; 12 unintended rows (cohort 6→18). Response: don't normalize by changing tests; inventory, quarantine, restore affected ledgers only, keep the valid data-refresh repair. Lesson: separate read-only maturity checks from observation-generation commands.

8.9 Fable's fresh-clone review — HISTORICAL, OPERATOR REPORTED. VPS passed tests while GitHub lacked modules. Rule: working on the VPS is not enough; a fresh clone must contain runtime source and pass a defined source-only test tier.

8.10 Healthcheck hardening — two defects persisted despite "fixed" claims (child env inheritance; ledger-parse status in pass/fail). Fixed in reported fb587a3. Lesson: commit messages ≠ the code path that computes the verdict.

8.11 Universe freshness is strategy correctness — HISTORICAL. Refreshing only 6 observed stocks + SPY/QQQ collapsed the rank cross-section to 6 names; the 0.85 threshold then admitted only the top name. Repair: refresh discovered universe + benchmarks, 50-symbol floor. Floor catches collapse; doesn't prove correct membership or PIT universe construction.

8.12 Sector attribution overclaimed — HISTORICAL, OPERATOR REPORTED. Missing/stale SMH/IGV/TAN let market outperformance wear a sector-independent label. After repair: 6 Independent Strength, 1 Sector Drift (second MRVL downgraded — audit-window return below SMH). Defensible conclusion: "underperformed the selected sector benchmark over that convention," not causal proof.

8.13 Ghost ledger must measure outcomes — rejected candidates recorded but not resolved; a PENDING-full ghost ledger can't demonstrate filter separation. Controlled resolver added (dry-run CLI + explicit --write). Five-bar terminal-state limitation remains (§10.7).

8.14 Mixed-unit lift bug — HISTORICAL, REPRODUCIBLE FROM CODE DESIGN. Accepted returns were fractions; ghost returns percent strings; 0.30 vs 6.97 inverted the result. Normalized: accepted ~30.27% vs rejected 6.97% (+23.30pp). Arithmetic fix ≠ causal filter effect (time-misaligned samples, partial ghost outcomes, different entry conventions). Magnitude-based unit inference is unsafe generally.

8.15 Research evidence vs product building separated — the system can be a useful internal research tool before it can honestly sell an edge claim. Product must not push research to loosen thresholds for empty weeks. A zero-candidate run during a collapsed universe ≠ disciplined rejection.

8.16 Model-cost policy — PERSISTENT USER PREFERENCE. Fable ~$50/prompt. Fable/expert review: new architecture, subtle data/audit defects, statistical methodology, risky changes, merge review. Cheaper Hermes operator: approved commands, refreshes, hashes, backups, deterministic tests, routine reports. User approval: new observation cycles, sensitive writes, merges, pushes, scope changes, product decisions. User manually selects model; prompts must not instruct calling/avoiding another model.

8.17 Significant commits — 0d93279 residual event-blocked checkpoint; c149578 Edge Sheet packaging; 2fd25c6 org map/guardrails; d072dc0 missing source files; e827b53 test-tier reproducibility; 4901dba second MRVL outcome; b7fb542 Juneteenth maturity test; fb587a3 healthcheck hardening; 0c1574b filter contract; 398e526 golden rebaseline; 8cbaa30 production architecture docs; 607a75a dry-run output-store; aad05de Phase 7C data/audit repair; 612f925 outcome-return merge fix; 225b391 return-unit normalization; 65cab10 Phase 7C merge; 1f1a238 approved 13/7/6 manifest.

---

9. Current state

9.1 Confirmed — CODE VERIFIED: branch trust-calibration-working @ 1f1a238, manifest = 13 approved observations / 7 resolved / 6 pending. Main is an older packaging checkpoint — do not inspect main as latest. OPERATOR REPORTED (not live-rechecked): 497 full-suite tests passing, 409 source-only + 88 deselected, healthcheck passing.

9.2 Seven resolved observations — AMD, ARM, CRWD, DDOG, MRVL, SEDG (2026-05-20) + MRVL (2026-06-05). Best-documented: second MRVL — signal close 263.47, outcome 2026-06-22 close 307.86, return +16.85%. (An earlier compacted summary's 295.10/0.12/June-19 values were contradicted by the ledger; do not replay placeholder values.)

9.3 Six approved pending — ARQQ, ASML, LLY, MU, SNOW, UNH, all signal date 2026-07-01. IDs in committed manifest; prices operator-reported, not market-verified here.

9.4 Last reconciled ledger fingerprints (HISTORICAL OPERATOR SNAPSHOT) — observation: 37f6b3…a928281; outcome: b1f02f…5de8d62a9; ghost: d55510…1d75419a6. Ghost: 159 rows / 141 PENDING / 18 MATURE / 0 INSUFFICIENT_DATA. Hashes are comparison anchors, not permanent expected values.

9.5 Maturity ambiguity — last canonical checkpoint: six pending at five available future bars through July 10 cache (July 2 session missing). A later CONFIRM/CONTRADICT report was not accepted as canonical. No confirmed canonical Phase 7F resolution report. Status: 13/7/6 with maturity/data provenance needing verification — NOT "resolved because enough time passed."

9.6 Frozen (BLOCKED FROM INCIDENTAL CHANGE) — strategy thresholds and selection rules; scoring; lineage identity; maturity definitions; original observation records; resolved outcomes (except versioned corrections); broker/live/shadow activation; trend-extension graveyard decision.

9.7 Planned/blocked summary — residual candidate: historical event-blocked research, no production promotion. Continuation observations: active lineage, pending cohort needs reconciliation. Statistical edge: not established. Matched accepted-vs-rejected evaluation: incomplete. Generic return-unit contract: incomplete. Multi-horizon ghost progression: needs repair. Versioned historical outcomes: intended, resolver gap remains. Hosted DB, public API, approval workflow, email sending, Shopify/Stripe billing, legal review, off-box backup drills: planned or unconfirmed. Broker/live: explicitly blocked.

9.8 Safe next steps (requirements, not permission to execute) —
1. Reconcile repo ↔ VPS state (branch, commit, ledger paths/IDs/hashes).
2. Review resolver preservation behavior before another write.
3. Verify July cohort windows; backfill real missing sessions; don't silently extend horizons.
4. Verify recoverable backup + independently stored decryption key.
5. Resolve only the approved pending cohort, controlled, with row-level diff.
6. Re-run audit with labeled return conventions and matched windows.
7. Advance ghost outcomes by horizon; fix five-bar terminal-state problem.
8. Update approved state contract only after validated transition.
9. Resume prospective evidence collection under unchanged rules.
10. Keep paid launch and performance claims blocked.

---

10. Gotchas

10.1 Hypothesis ≠ observation ≠ outcome ≠ audit label ≠ setup card ≠ commercial product. Never use a positive result at one level as authorization at the next.

10.2 Outcome resolver can recompute previously resolved results — CODE-VERIFIED GAP. resolve_observation_outcomes() iterates the observation ledger (rows stay PENDING) without preserving existing outcome-ledger rows. Reruns can recompute all outcomes from current cache. Needs preflight + regression-tested preservation contract before unattended use.

10.3 Latest-date freshness ≠ historical completeness — SMH and July-2 gaps. For fixed ten-session outcomes, counting the tenth available row after a gap changes the economic horizon. Repair the window or classify incomplete; don't let an outage become a strategy change. (Earlier "move maturity to a later bar" guidance retracted as too permissive.)

10.4 Timestamp labels ≠ availability timestamps — midnight/04:00 UTC bar labels vs actual close availability. Use trading-session identity + known-at/available-at timestamps.

10.5 Rank universe is part of the strategy — cache-discovered CSVs (newly seeded IGV/TAN not in exclusion set) can enter the rank universe; adding benchmark data can change selection without threshold changes. Distinguish: files in cache / symbols refreshed / eligible universe / sufficient history / present at ranking timestamp / benchmark-only. "94/94 fresh" ≠ "94 eligible equities ranked correctly."

10.6 Residual arrays aligned by length, not timestamp, in the original engine — missing dates/inceptions can misalign stock vs ETF returns. Sector-residual module uses a different path; don't assume safety transfers across lineages.

10.7 Five-bar mature ghost may never get ten-bar results — CODE-VERIFIED GAP. Resolver marks MATURE at five bars and only fills 10/20/30-bar fields if present in the same run; INSUFFICIENT_DATA rows are skipped permanently. Needs per-horizon progression.

10.8 CLI dry-run ≠ function defaults — operator script defaults dry-run; resolve_ghost_outcomes() defaults dry_run=False. Importing and calling without an explicit argument is not read-only.

10.9 Ghost write is not atomic — mode "w" after processing; no temp-file + atomic replace. Hashes detect unexpected changes; they don't prevent partial writes.

10.10 Return normalization by magnitude is unsafe — "0.5"→50%, "1.5"→1.5%, "4.88%"→4.88% breaks on genuine +150% fractional, −100%, or sub-one point values. Parse by declared source schema and field unit.

10.11 "Delay-adjusted" is a flat deduction — cost_adjusted = raw − 0.15pp; delay_adjusted = raw − 0.05pp. Not a real delayed-entry simulation.

10.12 Entry conventions and cohorts must match — reports mixed signal-close outcomes, first-future-bar attribution, misaligned dates, partial ghost maturity, different benchmark windows. The +23.30pp pooled lift stays a historical descriptive number, not a performance headline.

10.13 "Independent Strength" ≠ regression alpha — reflects outperforming selected benchmarks under a chosen convention. Not beta-adjusted alpha, causality, or significance. LIFT_SIGNIFICANCE_THRESHOLD=0.5 is a pp comparison threshold, not a statistical test.

10.14 Sample counts ≠ independent evidence counts — 7 observations over 2 dates are not 7 independent experiments; but effective-N = 1 or 2 is also unjustified without dependence modeling. Preserve factual counts; use clustered analysis. 30 observations / 10 dates ≠ automatic edge.

10.15 Tests can go green without the defect fixed — immaturity tests stopped failing after maturation; import-order luck; golden fixtures replaced with current output; data-backed tests deselected; registry tests excluded. Require exact command, commit, collected/selected/passed/failed/skipped/deselected/warnings. Keep synthetic failure-case tests.

10.16 Golden tests must exercise the generator — fixed synthetic inputs → actual generator → normalized output → reviewed fixture. Don't fix mismatches by copying runtime output into the golden.

10.17 Legal wording ≠ safety mechanism — "no advice"/"research only" are boundaries, not legal review. Numeric grades or personalized selection can still shape understanding.

10.18 Backup survival ≠ recoverability — need usable backup + recoverable secret + tested restore. Key repeatedly VPS-only; one phase derived backup key from GITHUB_TOKEN (durability/security problem). Keep key status UNCONFIRMED.

10.19 Backup scope > archive size — ledger-only archive can be valid operational backup; >1MB file ≠ restorable backup. State recovery needs ledgers + manifest/config versions + exact code ref + recoverable keys.

10.20 "No strategy files changed" ≠ behavior unchanged — selection can shift via universe membership, data adjustments, gap repair, timestamp alignment, warmup, rank denominator, benchmark mapping, loader behavior, defaults.

10.21 Phase names/docs aren't authoritative alone — identify work by repo, branch, full commit, lineage, dataset/version, observation IDs, operation mode. Don't run an old runbook because it says "daily maturity."

10.22 Discard these overconfident shortcuts — "All tests pass, therefore the audit is trustworthy." / "The filter rejected names, therefore it is rejecting weak conditions correctly." / "Seven positive results are strong evidence of independent edge." / "A fixed basis-point deduction proves realistic delay robustness." / "Missing one bar can be handled by moving the outcome to a later session." / "Only one material risk remains." / "The research engine is 90% complete."

Durable principle: preserve the original experiment, verify the data and comparison being used, make missing evidence visible, and never let a favorable label substitute for a reproducible result.
