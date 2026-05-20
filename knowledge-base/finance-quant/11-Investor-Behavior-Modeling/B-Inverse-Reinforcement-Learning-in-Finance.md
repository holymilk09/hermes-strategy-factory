# B: Inverse Reinforcement Learning in Finance

> Synthesized from Group B of the quant research library. Source: `raw-ingest/quant_research_library/B_inverse_reinforcement_learning_finance/`

---

## Key Papers

### Tier 1 — Finance-Specific IRL

1. **Halperin (2018)** — *QLBS Q-Learner Goes NuQLear: Fitted Q Iteration, Inverse RL, and Option Pricing* (arXiv 1801.06077)
   - Bridges mathematical finance (Black-Scholes) with RL control; shows option pricing, hedging, and RL in a unified framework
   - Introduces inverse-RL ideas into the derivatives workflow
   - Status: `FREE_DIRECT_PDF`

2. **Roa-Vicens, Chtourou, Filos, Rullan, Gal & Silva (2019)** — *Towards Inverse Reinforcement Learning for Limit Order Book Dynamics* (arXiv 1906.04813)
   - Directly recovers latent agent objectives from order-book behavior
   - More aligned with execution/microstructure recovery than portfolio-level inference
   - Status: `FREE_DIRECT_PDF`

3. **Dixon & Halperin (2020)** — *G-Learner and GIRL: Goal-Based Wealth Management with RL and IRL* (arXiv 2002.10990)
   - One of the clearest finance-specific IRL papers
   - Targets investor objective *inference* (GIRL), not just return optimization
   - Goal-based wealth management: infers what goal an investor is optimizing toward
   - Status: `FREE_DIRECT_PDF`

4. **Halperin, Kolm & Ritter (2025)** — *RL and IRL: A Practitioner's Guide for Investment Management* (CFA Institute Research Foundation, Chapter 6)
   - High-signal bridge from RL theory to investment workflows
   - Helps avoid academic RL toy problems that fail under execution costs and real portfolio constraints
   - Status: `FREE_LANDING`

### Tier 2 — Supporting Methods

5. **Hendricks, Harmon, Demirel, Yun, Sanderson & Rohde (2017)** — *Inferring Agent Objectives at Different Scales of a Complex System* (arXiv 1712.01137)
   - Multi-scale objective inference: micro (order-level) vs. macro (portfolio-level) objectives
   - Important framing because trading systems operate at multiple temporal scales simultaneously
   - Status: `FREE_DIRECT_PDF`

6. **Geng, Nassif, Manzanares, Jaegle & Bengio (2020)** — *Deep PQR: Solving IRL Using Anchor Actions* (ICML, arXiv 2007.07443)
   - Not finance-specific, but anchor-action structure maps well to constrained trading action spaces
   - Useful when demonstrations are sparse or ambiguous
   - Status: `FREE_DIRECT_PDF`

7. **Roa-Vicens (2024)** — *Bayesian and Adversarial IRL for Limit Order Book Simulators* (UCL PhD thesis)
   - Thesis-length treatment of LOB simulators using IRL
   - Relevant for simulating trader populations, not just predicting individual actions
   - Status: `FREE_LANDING`

### Tier 3 — Paywalled / Emerging

8. **Sun, Gong & Si (2023)** — *Transaction-Aware IRL for Trading in Stock Markets* (Applied Intelligence)
   - Uses transaction-aware constraints rather than idealized state/action loops
   - Status: `PAYWALLED`

9. **Zhang et al. (2025)** — *Heuristic-Guided IRL for Portfolio Optimization* (IJCAI 2025)
   - Directly targets portfolio optimization with IRL guidance
   - Status: `FREE_LANDING` — confirm PDF access

---

## Core Theses

- **Investor objectives are recoverable from behavior.** GIRL (Dixon & Halperin) demonstrates that you can reverse-engineer what goal function an investor is optimizing, given their observed trading trajectory. This is distinct from predicting their next trade — it's inferring their utility function.
- **Scale matters.** The Hendricks paper shows that agent objectives differ at different scales. An institutional trader may optimize P&L at the portfolio scale while their execution algorithm optimizes market impact at the order scale. IRL must operate at the right scale to recover meaningful objectives.
- **Finance is not a toy MDP.** The Halperin-Kolm-Ritter practitioner guide emphasizes that RL/IRL methods designed for robotics or games fail in finance because of transaction costs, portfolio constraints, non-stationarity, and the adversarial nature of markets.
- **Bayesian IRL carries uncertainty.** The Roa-Vicens PhD thesis develops Bayesian IRL specifically for LOB settings, showing that uncertainty-aware objective inference is more robust than point estimates.
- **Anchor actions constrain the action space.** Deep PQR shows that when the action space has natural "anchor" points (e.g., full rebalance, cash-only position, benchmark tracking), IRL becomes more tractable and less ambiguous.

---

## Implications for Trading Systems

- **Objective-inference layer for execution algos.** Use GIRL-type methods to infer the objective functions of other market participants' execution algorithms from their observed order-flow patterns. This gives you predictive edge on their future orders.
- **Multi-scale IRL pipeline.** Build two parallel IRL models: (1) order-level model inferring execution objectives from LOB data, (2) portfolio-level model inferring investment objectives from holdings/rebalancing data. Combine them for a complete picture.
- **GIRL as a signal generator.** Instead of predicting price direction, use GIRL to infer the *goal state* that institutional investors are targeting (e.g., target volatility, benchmark outperformance, liability-driven matching). Position changes that move toward those inferred goals are informative even before the portfolio update.
- **Adversarial IRL for population simulation.** Use the Roa-Vicens adversarial IRL approach to build realistic trader population simulators. Train your strategies against populations of simulated agents whose objectives were recovered from real market data.
- **Transaction-aware constraints.** The Sun et al. paper's transaction-aware framing means any IRL system for trading must model bid-ask spread, slippage, and execution constraints as part of the reward structure, not as after-the-fact transaction costs.

---

## Failure Modes

- **Partial observability is fatal.** IRL assumes you can observe the state and action sequences of the agent. In markets, you observe only public order flow and periodic holdings disclosures. The true state (total positions, risk limits, internal mandates) is hidden. Standard IRL algorithms collapse under partial observability — you need POMDP-IRL variants.
- **Non-stationarity breaks recovered rewards.** Markets change regime. An IRL model that recovers investor objectives in Q1 2024 may learn objectives that were specific to that regime. When conditions shift, the recovered reward function is obsolete.
- **Multiple reward functions explain the same behavior.** The fundamental identifiability problem of IRL: many different reward functions can produce identical optimal policies. MaxEnt IRL (from Group C) helps but doesn't fully solve this in finance.
- **Adversarial adaptation.** If institutional traders know you're inferring their objectives, they can adversarially modify their execution patterns to mislead your model. The market is a two-player game, not a passive observation problem.
- **Compute-cost mismatch.** GIRL requires solving forward RL problems as part of the inference loop. In high-frequency or even daily-rebalanced settings, this is computationally expensive. Real-time IRL inference is not currently feasible without severe approximation.

---

## Anti-Cookie-Cutter Insight

IRL in finance is fundamentally a **game-theoretic problem**, not a supervised learning problem. Every time you successfully infer an institutional trader's objective, you create adverse selection if you trade on it. They will notice their alpha degrading and change their behavior. This means IRL systems need continuous re-inference and an explicit model of *how the target agent adapts when being observed*. This is the equivalent of model extraction in Group D, but operating in a live adversarial environment.

---

## Cross-Links

- [[A-Reverse-Engineering-Investor-Decision-Logic]] — Demand systems provide a structural/complementary approach to objective inference from holdings
- [[C-Foundational-IRL-Imitation-Learning]] — Core IRL algorithms (Ng & Russell, MaxEnt, Bayesian IRL, GAIL, AIRL) that underpin every finance IRL application
- [[08-Market-Microstructure-LOB-Execution-Synthesis]] — Roa-Vicens IRL work connects directly to LOB dynamics and execution modeling
- [[07-02-LLM-Trading-Agents]] — Multi-agent IRL frameworks extend to LLM agent populations
- [[D-Model-Extraction-Black-Box-Reverse-Engineering]] — Model extraction techniques provide the conceptual framework for adversarial policy inference
- [[08-RL-Deep-Direct-RL-Portfolio-Management]] — Forward RL methods that IRL methods are inverting

---

*Created: 2026-05-17 | Source: Groups B research library | Status: Synthesized*
