# Research Library Synthesis

**Scope**: Intellectual lineage map, cross-domain connections, and open research questions synthesized from the quant_research library's SYNTHESIS.md, MASTER_INDEX.md, and PROGRESS_BY_TOPIC.md. The central intellectual line: from observable market traces to latent decision logic.

---

## Core Thesis

Raw traces (holdings, trades, orders, quotes, prices, news, narratives, agent communications) → latent objects (investor demand curves, reward functions, beliefs, constraints, risk budgets, execution objectives, regime-dependent heuristics).

A serious trading system cannot stop at return prediction. It must ask:
- *Whose behavior created the signal?*
- *What constraints made that behavior repeatable?*
- *How much capital can exploit it?*
- *How will execution change the signal after deployment?*

---

## Eight Intellectual Lineages

### Lineage 1: Demand-System Asset Pricing

**Bridge**: Holdings data → investor demand → pricing effects

Koijen-Yogo's framework is the cleanest route from holdings to decision logic. Prices are not mysterious equilibrium outputs; they emerge from demand elasticities estimated via market clearing. Asset Embeddings (Gabaix, Koijen, Richmond & Yogo, 2025) extends this to learned latent spaces of assets and investors.

**Connection to hedge-fund literature**: Best Ideas, 13F alpha, hidden-holdings research all ask whether public portfolio traces reveal skill or deception. 13F data is useful but strategically contaminated — funds misreport timing and hide positions.

**Non-obvious insight**: The question is not "does this stock have alpha?" but "which investors are likely to demand it, what do they substitute away from, and which flows actually matter for valuation." This reframes alpha discovery as *investor identification*.

**Key papers**: Koijen & Yogo (2019), Gabaix et al. (2025) Asset Embeddings, Gabaix & Koijen (2021) Inelastic Markets.

### Lineage 2: Empirical Asset Pricing with ML

**Bridge**: Characteristic interactions → cross-sectional returns

Gu-Kelly-Xiu, Kelly-Pruitt-Su, Chen-Pelger-Zhu, and the AI Asset Pricing Models paper form the benchmark for serious ML return prediction. This literature cares about cross-sectional structure, factor exposures, pricing errors, and characteristic *interactions*.

**Connection to other lineages**: ML asset pricing depends on Lineage 3 (statistical hygiene) to avoid overfitting, and connects to Lineage 1 because demand-system features are valid ML inputs.

**Key warning**: Most LLM or retail-AI strategy demos are competing against this mature literature, not starting from scratch.

**Key papers**: Gu, Kelly & Xiu (2020), Kelly, Pruitt & Su (2019), Chen, Pelger & Zhu (2024).

### Lineage 3: Statistical Hygiene

**Bridge**: Strategy generation → hypothesis destruction

Cont's stylized facts, Bailey & López de Prado's backtest-overfitting work, Deflated Sharpe Ratio, Harvey-Liu-Zhu multiple testing, and Lo's Sharpe-ratio stats.

**Connection as foundation**: This line is the prerequisite for everything else. Any system generating many candidate strategies — especially with LLMs — needs this layer first.

**Critical insight**: Vibe-coded quant systems automate hypothesis generation but do *not* automate hypothesis destruction. That asymmetry is the dominant failure mode.

**Key papers**: Cont (2001), Bailey et al. (2014) PBO, Bailey & López de Prado (2014) DSR, Harvey, Liu & Zhu (2016).

### Lineage 4: Market Microstructure and Execution

**Bridge**: Signal → tradable strategy

Almgren-Chriss optimal execution, Cont-Kukanov-Stoikov order-book impact, Avellaneda-Stoikov market making, Easley et al. machine-age microstructure.

**Connection**: Converts ML/IRL signals from backtest toys into real trading problems. The dominant failure isn't fake signals — it's real signals that are smaller than spread + fees + slippage + impact + latency.

**Key papers**: Almgren & Chriss (2000), Cont et al. (2014), Easley et al. (2020).

### Lineage 5: Inverse Reinforcement Learning

**Bridge**: Observed behavior → inferred objectives

IRL asks what reward function makes observed behavior rational. CS foundations (Ng-Russell, Abbeel-Ng, Ziebart, Ho-Ermon, AIRL) applied to finance by Halperin, Dixon, Roa-Vicens.

**Finance makes it harder**: Demonstrations are partial, state is hidden, other agents react, expert behavior reflects mandates/taxes/liquidity/career constraints. The open opportunity is constrained, uncertainty-aware IRL over financial traces.

**Key papers**: Dixon & Halperin (2020) G-Learner, Ziebart et al. (2008) MaxEnt IRL, Ho & Ermon (2016) GAIL.

### Lineage 6: Behavioral Finance & Psychometric Inference

**Bridge**: Biases → predictable but fragile patterns

Barber-Odean, Odean, Barberis, Shiller, Tetlock. Investors overtrade, hold losers, chase narratives, react to media tone, and show stable biases.

**Connection to IRL**: Supports decision-logic inference from behavior, but warns that actions may reflect bias, tax needs, liquidity pressure, mandate constraint, or noise. Good inference must output *uncertainty*, not personality fan fiction.

**Key papers**: Barber & Odean (2000), Tetlock (2007), Shiller (2017) Narrative Economics.

### Lineage 7: LLM Agents & Multi-Agent Orchestration

**Bridge**: Research acceleration ≠ autonomous trading

TradingAgents, FinMem, GPT-Signal, Trading-R1, LiveTradeBench. Strongest use case: summarizing filings, generating features, building hypothesis queues. Fragile as autonomous traders.

**Critical vulnerability**: Behavioral consistency — agents that change policy after prompt wording changes are not robust strategies.

**Key papers**: Lopez-Lira (2025), Li et al. (2026) Behavioral Consistency, Xiao et al. (2024) TradingAgents.

### Lineage 8: Pattern Recognition Under Academic Filters

**Bridge**: Retail patterns → testable features

Lo-Mamaysky-Wang, Brock-Lakonishok-LeBaron, Sullivan-Timmermann-White. ICT/fair-value-gap language has weak academic support. Defensible route: translate pattern claims into measurable microstructure variables, then apply multiple-testing controls.

**Key gap**: Not chart recognition itself, but mapping micro order-flow patterns into macro economic regimes without overfitting.

**Key papers**: Lo, Mamaysky & Wang (2000), Sullivan et al. (1999), Kong et al. (2020) micro-trading patterns.

---

## Cross-Domain Connections

The library's cross-refs in MASTER_INDEX reveal deep interconnections:

| Cross-domain link | Example |
|---|---|
| Demand → ML pricing | Asset embeddings (A) feed characteristic models (K) |
| IRL → Microstructure | LOB dynamics IRL (B, Group H) combines reward inference with order-book features |
| Behavioral → LLM agents | Investor psychometrics (E) inform agent behavior validation (F) |
| Statistics → All lineages | Multiple-testing controls (M) apply to ML, IRL, pattern recognition, TA |
| Microstructure → Execution | Order-flow features (H, N) directly define implementation costs in any strategy |
| Hedge funds → Holdings analysis | 13F literature (Q) connects to demand-system pricing (A) and behavioral finance (E) |
| Options → Risk | Volatility models (L) require statistical hygiene (M) to avoid model-risk blowups |

---

## Open Research Questions

1. **Can demand-system pricing and asset embeddings become near-real-time inference** from public holdings, flows, and filings? Literature is rigorous but often slower than tradable systems need.

2. **Can IRL work under financial partial observability?** Real traders don't reveal state, constraints, beliefs, or motives. Finance-specific IRL needs posterior uncertainty and causal discipline.

3. **Can LLM agents be made behaviorally stable** for research workflows? Useful for synthesis and ideation, but fragile as deciders. Behavioral consistency validation (Li et al. 2026) is the first real gate.

4. **How should strategy-generation systems price multiple testing in real time?** LLMs create infinite candidate signals. Validation must match generation speed.

5. **Can pattern-recognition connect microstructure features to macro regimes?** The thin area isn't chart recognition — it's mapping order-flow patterns into economic states without overfitting.

---

## Practical Build Conclusion

The highest-value build is **not an LLM trader**. It is a research-control system combining:
- Investor-demand inference (Lineage 1)
- Strict statistical validation (Lineage 3)
- Execution-aware simulation (Lineage 4)
- LLM-assisted feature generation under guardrails (Lineage 7)

**Core product advantage**: not finding more ideas, but *killing bad ideas faster* and preserving the few that survive demand logic, microstructure, and out-of-sample reality.

---

## Library Coverage at a Glance

| Topic Group | Records | Free PDFs | Paywalled/Book |
|---|---:|---:|---:|
| A: Investor Decision Logic | 9 | 5 | 1 |
| B: IRL in Finance | 9 | 5 | 1 |
| C: Foundational IRL | 8 | 8 | 0 |
| D: Model Extraction | 5 | 5 | 0 |
| E: Behavioral Finance | 11 | 2 | 7 |
| F: LLM Trading Agents | 15 | 15 | 0 |
| G: RL for Trading | 10 | 6 | 3 |
| H: Market Microstructure | 10 | 3 | 6 |
| I: Renaissance/Simons | 6 | 0 | 2 |
| J: Andrew Lo / MIT | 8 | 2 | 6 |
| K: ML Asset Pricing | 8 | 5 | 2 |
| L: Options/Volatility | 10 | 2 | 7 |
| M: Risk/Statistics | 9 | 2 | 4 |
| N: Volume/Order Flow | 7 | 1 | 5 |
| O: Technical Analysis | 8 | 2 | 6 |
| P: Prediction Markets | 9 | 4 | 1 |
| Q: Hedge Fund/13F | 10 | 0 | 6 |
| R: Pattern Recognition | 10 | 4 | 3 |

**Total**: 162 indexed records across 18 topic groups. Strongest open-access coverage in IRL, LLM agents, and recent pattern-recognition. Weakest coverage in options foundations, behavioral finance journals, and hedge-fund factor literature.

---

*Cross-links: [[Research-Read-Order-Guide]], [[Research-Paywall-Strategy]], [[Agentic-Workflow-Patterns]], [[Trading-System-Build-Doctrine]]*
