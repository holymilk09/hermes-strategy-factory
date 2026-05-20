# A: Reverse-Engineering Investor Decision Logic

> Synthesized from Group A of the quant research library. Source: `raw-ingest/quant_research_library/A_reverse_engineering_investor_decision_logic/`

---

## Key Papers

### Tier 1 — Load-Bearing Framework

1. **Koijen & Yogo (2019)** — *A Demand System Approach to Asset Pricing* (J Political Economy / NBER 21749)
   - Builds an estimable demand system from investor-level holdings data + market clearing
   - Converts observed portfolio positions into latent demand elasticities
   - Status: `FREE_DIRECT_PDF`

2. **Gabaix & Koijen (2021)** — *The Inelastic Markets Hypothesis* (Q J Econ / NBER 28967)
   - Demand shocks move prices because market demand curves are inelastic — flows don't get absorbed
   - This is the *economic reason* investor-decision inference matters for price impact
   - Status: `FREE_DIRECT_PDF`

3. **Gabaix, Koijen, Richmond & Yogo (2025)** — *Asset Embeddings* (NBER 33651)
   - Learns latent representations of assets and investors from portfolio holdings
   - Directly maps embeddings to demand, substitution, and equilibrium pricing behavior
   - Status: `FREE_DIRECT_PDF`

4. **Kelly, Kuznetsov, Malamud & Xu (2025)** — *Artificial Intelligence Asset Pricing Models* (NBER 33351)
   - Transformer-based SDF estimation; benchmark for when AI price-factors are genuine vs. curve-fit
   - Status: `FREE_DIRECT_PDF`

5. **Scholl, Mahfouz, Calinescu & Farmer (2025)** — *Learning to Manage Portfolios beyond Simple Utility Functions* (arXiv 2510.26165)
   - Challenges the mean-variance assumption; real investors optimize messy multi-objective path-dependent rules
   - Status: `PREPRINT_ONLY`

6. **Koijen & Yogo (2025)** — *On the Theory and Econometrics of Demand System Asset Pricing* (SSRN 5274709)
   - Technical econometrics companion to Koijen-Yogo 2019; covers identification, estimation, failure modes
   - Status: `PREPRINT_ONLY`

### Tier 1 — Paywalled

7. **Koijen, Richmond & Yogo (2024)** — *Which Investors Matter for Equity Valuations and Expected Returns?* (Rev Economic Studies)
   - Directly maps which investor classes have price-moving power
   - Status: `PAYWALLED` — OUP/institutional access needed

### Tier 2 — Practical Benchmarks

8. **Angelini, Iqbal & Jivraj (2019)** — *Systematic 13F Hedge Fund Alpha* (SSRN 3459526)
   - Tests systematic strategies from 13F filings; practical ceiling for what public holdings can deliver
   - Status: `PREPRINT_ONLY`

9. **Anton, Cohen & Polk (2021)** — *Best Ideas* (SSRN HBS 21-004)
   - Concentrated positions = highest manager conviction; bridge between holdings and trade-selection logic
   - Status: `PREPRINT_ONLY`

---

## Core Theses

- **Demand systems are measurable.** Koijen-Yogo proves you can estimate investor demand elasticities from holdings data plus market-clearing constraints. This is not speculative — it's a structural econometric framework.
- **Markets are inelastic to flows.** The Gabaix-Koijen inelastic markets hypothesis explains *why* this matters: even moderate flow changes move prices because the aggregate demand curve is steep. This is the causal chain: observed flow → inferred demand shift → expected price impact.
- **Assets and investors have latent embeddings.** The 2025 asset embeddings paper shows that holdings data can be treated like word embeddings: positions reveal latent similarity structure between assets and investor preferences.
- **Utility functions are wrong.** The Scholl et al. paper demonstrates that investors don't optimize clean mean-variance objectives. Real decision rules are multi-objective, path-dependent, and messy.
- **Which investors matter is heterogeneous.** Not all flows move prices equally. The paywalled Koijen-Richmond-Yogo paper provides the taxonomy.

---

## Implications for Trading Systems

- **Flow-aware alpha:** Build signals that estimate demand elasticities from position disclosures (13Fs, form 13F-HR, etc.) and feed them into a demand-system model. When a large holder's position changes, the demand-system model predicts the price impact needed to clear the market.
- **Embedding-based stock selection:** Use the asset embeddings approach as a feature engineering layer. If two stocks have similar demand-embedding coordinates, they likely share the same investor base and will move together under flow shocks.
- **13F decay modeling:** The Angelini et al. paper provides a practical benchmark — systematic 13F strategies decay quickly. The edge comes from *timing* inference (predicting rebalancing before it happens based on mandate constraints, index flows) rather than blind following.
- **Multi-objective demand inference:** The Scholl et al. result means you should model investors as optimizing multiple objectives simultaneously (risk, liquidity, benchmark tracking, career concerns) rather than fitting a single utility function.
- **Target the price-moving investors.** Use Koijen-Richmond-Yogo's taxonomies to weight signals by investor class (active mutual funds, CTAs, sovereign wealth funds etc.) and focus inference effort on investors whose flows actually move prices.

---

## Failure Modes

- **Data lag kills edge.** 13F filings are 45 days old by filing deadline. By the time you see the position, the market has often adjusted. Strategies built purely on lagged 13F data have near-zero live alpha.
- **Identification failures.** The Koijen-Yogo 2025 econometrics note warns about identification problems: demand elasticities may be confounded with supply shocks, index rebalancing, and mechanical flows.
- **Overfitting the demand system.** With high-dimensional holdings data, there are many ways to fit noisy demand curves. The Kelly et al. AI asset pricing paper shows how transformer SDF models can dramatically reduce pricing errors — but also demonstrates the curve-fitting danger zone.
- **Ignoring inelasticity assumptions.** The inelastic markets hypothesis requires that demand curves *are* inelastic. In liquid, highly arbitraged instruments, this assumption breaks down. The framework works best in less-efficient segments (small-caps, credit, EM, illiquid alternatives).
- **Utility function misspecification.** If you assume investors are mean-variance optimizers, you will systematically mispredict their behavior. The Scholl paper shows this is empirically false.

---

## Anti-Cookie-Cutter Insight

The demand-system approach is powerful *because* it sidesteps the classic "what do investors think?" problem. You never need to know an investor's beliefs, thesis, or view. You only need to observe what they *hold* and apply market clearing. The demand elasticity is identified positionally, not psychologically. This is radically different from sentiment analysis, earnings-call NLP, or "smart money" following — it's structural econometrics, not behavior guessing.

---

## Cross-Links

- [[B-Inverse-Reinforcement-Learning-in-Finance]] — IRL provides an alternative framework for inferring investor objectives from observed behavior (complementary to demand systems)
- [[C-Foundational-IRL-Imitation-Learning]] — Core algorithms that power objective inference from demonstrations
- [[K-Asset-Pricing-ML-Frontier]] — Kelly et al. AI asset pricing provides the SDF benchmark for demand-system validation
- [[Q-Hedge-Fund-Analysis-13F-Literature]] — 13F strategies and conviction extraction as practical data sources
- [[08-Market-Microstructure-LOB-Execution-Synthesis]] — Flow impact connects demand shocks to actual execution costs
- [[N-Volume-Order-Flow-Academic-Microstructure]] — Order-flow analysis provides the trade-level lens to complement holdings-level demand systems

---

*Created: 2026-05-17 | Source: Groups A research library | Status: Synthesized*
