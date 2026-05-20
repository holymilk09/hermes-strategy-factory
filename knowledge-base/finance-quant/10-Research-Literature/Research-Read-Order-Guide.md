# Research Read-Order Guide

**Scope**: 8-stage reading sequence from the quant_research library, designed for technical founders building algorithmic trading systems — *not* PhD literature reviewers. The goal is judgment: what is inferable, what is tradable, what is overfit, and what is executable.

---

## Stage 1 — Core Decision-Logic Inference

| Paper | Authors | Year | Venue |
|---|---|---|---|
| A Demand System Approach to Asset Pricing | Koijen & Yogo | 2019 | JPE / NBER |
| Asset Embeddings | Gabaix, Koijen, Richmond & Yogo | 2025 | NBER |
| Inelastic Markets Hypothesis | Gabaix & Koijen | 2021 | QJE / NBER |
| Theory and Econometrics of Demand System Asset Pricing | Koijen & Yogo | 2025 | SSRN |
| Which Investors Matter? | Koijen, Richmond & Yogo | 2024 | Restud (paywalled) |

**Rationale**: This is the strongest academic route from observed holdings to latent investor demand. Before touching LLM agents, understand how holdings encode decision logic.

**Key Concepts**:
- **Demand-system asset pricing**: prices emerge from investor demand curves, not abstract equilibrium. Holdings data + market clearing → estimated demand elasticities and substitution effects.
- **Asset embeddings**: assets and investors can be placed in latent spaces from portfolio behavior. A system should ask *which investors will demand this asset* and *what they substitute away from*.
- **Inelastic markets hypothesis**: demand curves are not infinitely elastic — flows move prices more than frictionless models imply. Concentrated, price-insensitive buyers create persistent pressure.
- **Heterogeneous investor impact**: not all flows are equal. A benchmarked institution's constrained buying matters more than an equal-sized passive index rebalance.

**Implications for Trading Systems**:
- Reverse-engineering strategy should identify *who* is behind a signal, not just whether a stock has alpha.
- 13F/holdings data reveals skill, conviction, or strategic deception — treat as partial and contaminated evidence.
- Build investor-identification layers into any flow-based strategy.

**Failure Modes**:
- Treating reported holdings as complete truth (hedge funds strategically misreport timing/sizing).
- Assuming demand elasticities are stable across regimes — they shift with leverage constraints and margin calls.
- Confusing flow-driven price moves with fundamental alpha.

---

## Stage 2 — Statistical Discipline Before Strategy Generation

| Paper | Authors | Year |
|---|---|---|
| Empirical Properties of Asset Returns | Cont | 2001 |
| Probability of Backtest Overfitting | Bailey et al. | 2014 |
| Deflated Sharpe Ratio | Bailey & López de Prado | 2014 |
| ...and the Cross-Section of Expected Returns | Harvey, Liu & Zhu | 2016 |
| The Statistics of Sharpe Ratios | Lo | 2002 |

**Rationale**: Without this layer, every LLM-generated or pattern-generated strategy will look better than it is. Markets are hostile to naive validation.

**Key Concepts**:
- Returns are fat-tailed, non-normal, regime-dependent, serially distorted.
- **Multiple testing**: testing 100 candidate strategies inflates false discovery rate far beyond single-test intuition.
- **Deflated Sharpe Ratio**: corrects for selection bias, backtest overfitting, and non-normality.
- **Probability of backtest overfitting (PBO)**: CSCV method to estimate likelihood an "optimal" backtest is a false positive.

**Implications for Trading Systems**:
- The validation layer must become as automated as the hypothesis-generation layer.
- LLMs that generate infinite candidate signals require equally aggressive hypothesis destruction.
- This is the **major failure mode of vibe-coded quant systems**: automating generation without automating falsification.

**Failure Modes**:
- Optimizing on a single backtest without PBO/DSR correction.
- Ignoring fat-tail distributions when computing confidence intervals.
- Treating cross-validation like i.i.d. data — financial time series are neither.

---

## Stage 3 — Market Microstructure and Execution Reality

| Paper | Authors | Year |
|---|---|---|
| Optimal Execution of Portfolio Transactions | Almgren & Chriss | 2000 |
| Price Impact of Order Book Events | Cont, Kukanov & Stoikov | 2014 |
| High-Frequency Trading in a Limit Order Book | Avellaneda & Stoikov | 2008 |
| Microstructure in the Machine Age | Easley, López de Prado, O'Hara & Zhang | 2020 |
| Empirical Market Microstructure | Hasbrouck | 2007 |

**Rationale**: A signal that cannot survive impact, spread, queue priority, and execution is not a strategy.

**Key Concepts**:
- **Implementation shortfall**: real trading costs = impact + spread + timing risk, not just commissions.
- **Order-flow imbalance**: measurable features from the book predict short-term moves (order-book event impact).
- **Inventory risk**: market-making requires balancing position against adverse selection.
- **Machine-age microstructure**: algorithmic trading changed the nature of liquidity and information flow.

**Implications for Trading Systems**:
- Convert every backtest from signal toy into a trading problem with realistic costs.
- Strategy edge must exceed: spread + fees + slippage + market impact + latency disadvantage.
- Order-book features (imbalance, queue position, spread behavior) are more robust than price-only patterns.

**Failure Modes**:
- Strategies failing not because the signal is imaginary, but because edge < execution costs.
- Ignoring adverse selection — getting picked off by informed flow.
- Simulating market orders that would never fill at mid prices in reality.

---

## Stage 4 — Machine Learning Asset Pricing

| Paper | Authors | Year |
|---|---|---|
| Empirical Asset Pricing via ML | Gu, Kelly & Xiu | 2020 |
| Characteristics Are Covariances | Kelly, Pruitt & Su | 2019 |
| Deep Learning in Asset Pricing | Chen, Pelger & Zhu | 2024 |
| AI Asset Pricing Models | Kelly et al. | 2025 |
| Machine Learning in Asset Pricing | Nagel | 2021 |

**Rationale**: This is the adult version of AI alpha discovery. Most retail/LMM demos are not competing against nothing — they compete against a mature literature with strict baselines.

**Key Concepts**:
- Cross-sectional structure, factor exposures, pricing errors, and characteristic interactions are the real battleground.
- Characteristic interactions (nonlinear combinations of firm-level features) matter more than raw factor returns.
- Stochastic discount factor estimation via ML provides a rigorous pricing benchmark.

**Implications for Trading Systems**:
- Any ML alpha claim must face Gu-Kelly-Xiu as a baseline.
- Feature engineering should focus on characteristic *interactions*, not just individual signals.
- Use ML for cross-sectional ranking and relative value, not absolute return prediction.

**Failure Modes**:
- Treating an LLM-generated feature as novel when it's a known characteristic interaction.
- Ignoring factor model controls — isomorphic to running a CAPM regression with one variable.
- Overfitting the cross-section by testing on the same universe used for feature discovery.

---

## Stage 5 — IRL and Imitation Learning

| Paper | Authors | Year |
|---|---|---|
| Algorithms for IRL | Ng & Russell | 2000 |
| Apprenticeship Learning via IRL | Abbeel & Ng | 2004 |
| Maximum Entropy IRL | Ziebart et al. | 2008 |
| GAIL | Ho & Ermon | 2016 |
| G-Learner and GIRL | Dixon & Halperin | 2020 |
| IRL for LOB Dynamics | Roa-Vicens et al. | 2019 |

**Rationale**: How to infer objectives from behavior, and why finance-specific constraints make it difficult.

**Key Concepts**:
- IRL asks: *what reward function would make observed behavior rational?* — sharper than supervised prediction.
- **Finance is harder**: demonstrations are partial, state is hidden, other agents react, expert behavior reflects mandates/taxes/liquidity/career risk.
- **Constrained IRL with uncertainty** is the open opportunity, not generic reward recovery.

**Implications for Trading Systems**:
- Use IRL frameworks to reverse-engineer trader/fund objectives from trades and holdings.
- Design IRL for partial observability: posterior uncertainty over reward functions, not point estimates.
- Finance-specific IRL needs causal discipline — correlation between trades and outcomes ≠ revealed preference.

**Failure Modes**:
- Assuming all observed behavior is rational (trades may reflect bias, liquidity need, or noise).
- Ignoring that multiple reward functions can explain the same behavior (identification problem).
- No causal discipline — confusing coincidental correlation with learned objective.

---

## Stage 6 — LLM Agents as Research Assistants, Not Autonomous Traders

| Paper | Authors | Year |
|---|---|---|
| Can LLMs Trade? | Lopez-Lira | 2025 |
| GPT-Signal | 2024 | |
| TradingAgents | 2024 | |
| LLM Trading in Experimental Markets | Henning et al. | 2025 |
| Behavioral Consistency Validation | Li et al. | 2026 |
| LiveTradeBench | Yu et al. | 2025 |

**Rationale**: LLMs are credible for research summarization, feature ideation, and hypothesis generation — not direct autonomous trading.

**Key Concepts**:
- LLM agents are useful upstream: summarizing filings, generating features, building hypothesis queues.
- **Behavioral consistency**: an agent that changes policy after wording changes is not robust.
- LLM agents should coordinate specialized agents under strict validation, not bypass deterministic risk systems.

**Implications for Trading Systems**:
- Position LLM agents as research accelerators, not execution engines.
- Implement behavioral-consistency tests before deploying any agent loop.
- Use LLMs for hypothesis generation, but require deterministic validation before any trade.

**Failure Modes**:
- Trusting an LLM agent that has not passed behavioral consistency validation.
- Wording-dependent trading policies indicate the agent is learning prompt patterns, not market structure.
- LLMs hallucinate rationales that sound professional but contain logical errors.

---

## Stage 7 — Options/Volatility for Derivatives

| Paper | Authors | Year |
|---|---|---|
| Black-Scholes | Black & Scholes | 1973 |
| Rational Option Pricing | Merton | 1973 |
| Stochastic Volatility | Heston | 1993 |
| Pricing with a Smile | Dupire | 1994 |
| FFT Option Valuation | Carr & Madan | 1999 |
| The Volatility Surface | Gatheral | 2006 |
| Stochastic Volatility Modeling | Bergomi | 2016 |

**Rationale**: Derivatives strategies require model risk literacy — a surface-fitting error can look like alpha until it gets repriced.

**Key Concepts**:
- Volatility surface contains forward-looking information — fitting it poorly creates phony edge.
- Local vs. stochastic volatility models produce different hedging outcomes.
- Model risk is the dominant risk in options strategies.

**Implications for Trading Systems**:
- Any options-related strategy must include model risk assessment alongside market risk.
- Volatility surface interpolation and extrapolation are where real errors live.
- FFT-based pricing (Carr-Madan) is the practical baseline for speed.

**Failure Modes**:
- Surface-fitting errors creating phantom alpha.
- Ignoring that implied vol ≠ realized vol — the vol risk premium exists for a reason.
- No understanding of how model assumptions break during regime shifts.

---

## Stage 8 — Technical Analysis Under Academic Discipline

| Paper | Authors | Year |
|---|---|---|
| Foundations of Technical Analysis | Lo, Mamaysky & Wang | 2000 |
| Simple Technical Trading Rules | Brock, Lakonishok & LeBaron | 1992 |
| Data-Snooping and Bootstrap | Sullivan, Timmermann & White | 1999 |
| Price Impact of Order Book Events | Cont et al. | 2014 |
| Micro-trading pattern papers (Group R) | Various | — |

**Rationale**: Retail pattern language must be translated into testable features, then attacked with data-snooping controls.

**Key Concepts**:
- ICT/fair-value-gap language has **weak academic support** as standalone evidence.
- Defensible route: translate pattern claims into measurable variables (order-flow imbalance, liquidity gaps, volume clusters, event sequencing).
- Apply multiple-testing controls — pattern recognition is a severe multiple-comparison problem.

**Implications for Trading Systems**:
- Any pattern-based strategy must pass through microstructure feature translation.
- Combine pattern features with regime awareness — patterns are regime-dependent.
- Use bootstrap-based significance testing, not naive p-values.

**Failure Modes**:
- Treating chart patterns as mechanical signals without statistical validation.
- Data snooping — finding patterns that exist only in hindsight.
- Ignoring that patterns may work for one asset/regime and fail universally elsewhere.

---

## Priority Summary

The **load-bearing papers** across all 8 stages:
1. Koijen & Yogo (2019) — holdings-to-demand framework
2. Gabaix et al. (2025) Asset Embeddings — learned latent representations from investor behavior
3. Gu, Kelly & Xiu (2020) — ML asset-pracing benchmark
4. Cont et al. (2014) — order-book event impact
5. Bailey & López de Prado — overfitting/Deflated Sharpe
6. Ziebart (2008) and Ho & Ermon (2016) — IRL foundations
7. Lo, Mamaysky & Wang (2000) — academic pattern recognition

---

*Synthesized from [[Research-Library-Synthesis]], [[Research-Paywall-Strategy]], and the quant_research_library READ_ORDER.md.*
