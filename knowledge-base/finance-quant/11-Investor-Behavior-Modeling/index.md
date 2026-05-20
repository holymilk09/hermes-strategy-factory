# 11: Investor Behavior Modeling

> Synthesizes research from Groups A, B, C, D of the quant research library on reverse-engineering institutional investor decision logic.

---

## Cluster Overview

This cluster addresses the core question: **how do we infer what investors and institutions are doing, why they're doing it, and how they'll behave next?**

Four complementary approaches:

| Letter | Topic | Approach | Key Strength | Key Weakness |
|---|---|---|---|---|
| [[A-Reverse-Engineering-Investor-Decision-Logic]] | Demand Systems | Structural econometrics from holdings + market clearing | Identification from positions, not psychology | Data lag, confounding shocks |
| [[B-Inverse-Reinforcement-Learning-in-Finance]] | IRL in Finance | Recover objective functions from observed trading trajectories | Goal-based inference, not just action prediction | Partial observability, non-stationarity |
| [[C-Foundational-IRL-Imitation-Learning]] | Core IRL/IL Algorithms | Foundational algorithms (IRL, GAIL, AIRL, MaxEnt, Bayesian) | Rigoreous theoretical grounding | Identifiability, feature engineering bottleneck |
| [[D-Model-Extraction-Black-Box-Reverse-Engineering]] | Black-Box Extraction | Substitute models, query-based extraction, subspace discovery | Works with limited observations | Non-stationary targets, terrible SNR |

---

## Synthesis: The Four-Layer Inference Stack

These four groups form a complete stack for investor behavior modeling:

1. **Holdings Level (Layer 1)** — [[A-Reverse-Engineering-Investor-Decision-Logic]]: Koijen-Yogo demand systems estimate aggregate demand elasticities from disclosed positions. This tells you *which* investors matter and *how much* their flows move prices.

2. **Objective Level (Layer 2)** — [[B-Inverse-Reinforcement-Learning-in-Finance]]: GIRL and finance-specific IRL recover the goal function that investors are optimizing. This tells you *what* they're trying to achieve (target volatility, liability matching, alpha generation).

3. **Algorithm Level (Layer 3)** — [[C-Foundational-IRL-Imitation-Learning]]: Core IRL/imitation algorithms provide the machinery for behavior replication and reward recovery. AIRL for transferable rewards, MaxEnt for ambiguous behavior, Bayesian IRL for uncertainty-aware inference.

4. **Extraction Level (Layer 4)** — [[D-Model-Extraction-Black-Box-Reverse-Engineering]]: Black-box extraction techniques work at the observation layer, recovering behavioral patterns from market data without assuming any internal structure. This is the most model-agnostic but least principled layer.

---

## Key Cross-Cutting Insights

### The Identifiability Problem is Everywhere

Every approach in this cluster faces a version of the same fundamental problem:

- **Demand systems (A):** Koijen-Yogo elasticities are confounded with supply shocks and mechanical flows
- **IRL (B, C):** Multiple reward functions explain the same observed behavior — the problem is inherently ill-posed (Ng & Russell 2000)
- **Model extraction (D):** You recover behavioral equivalence, not the true decision function

**Implication:** Never build a trading signal on a single inferred objective. Build robustness across the posterior of possible explanations.

### Partial Observability is the Killer Constraint

- IRL assumes full state observability — markets don't provide it
- Demand systems require complete holdings data — only disclosed periodically
- Model extraction assumes identifiable query responses — market data is an aggregate

**Implication:** Every method needs a POMDP extension or an explicit model of hidden state. This is an active research frontier.

### The Adversarial Feedback Loop

- If you successfully predict an institution's behavior and trade on it, you degrade their alpha
- They notice and adapt
- Your model becomes wrong
- This is different from traditional ML where the data distribution is fixed

**Implication:** IR and model-extraction systems need continuous re-inference and explicit adversary modeling. The target moves because *you move it*.

### ICT Has Zero Academic Support

The demand-system (A) and extraction (D) literature provides the closest rigorous framework to what "Inner Circle Trader" concepts claim. However:
- ICT provides post-hoc visual pattern matching
- The academic approaches provide structural identification with explicit failure modes
- Nothing in the academic literature supports the concepts of order blocks, fair value gaps, or liquidity pools as defined by ICT

**Implication:** Use the rigorous frameworks (demand systems, IRL, substitute models). Avoid post-hoc pattern matching without identification guarantees.

---

## Practical Pipeline for a Trading System

Combining all four groups into a working system:

```
13F/Filings + Market Data
         |
         v
  [Layer 1: Demand System]  ← Koijen-Yogo elasticity estimation
         |                          Identify price-moving investors
         v
  [Layer 2: Objective Inference]  ← GIRL/Bayesian IRL
         |                          Recover what they're optimizing
         v
  [Layer 3: Behavior Replication]  ← AIRL/GAIL
         |                          Build substitute policies
         v
  [Layer 4: Extraction Monitoring]  ← LoRD/Substitute models
         |                          Continuously track policy drift
         v
  Trading Signals + Execution
```

---

## Related Clusters

- [[K-Asset-Pricing-ML-Frontier]] — AI asset pricing benchmarks (Kelly et al.) validate demand-system and IRL signals
- [[08-Market-Microstructure-LOB-Execution-Synthesis]] — Order-level execution connects demand shocks to actual trade costs
- [[Q-Hedge-Fund-Analysis-13F-Literature]] — 13F data is the primary input for Layer 1 demand systems
- [[08-RL-Deep-Direct-RL-Portfolio-Management]] — Forward RL methods that IRL methods invert
- [[07-02-LLM-Trading-Agents]] — LLM trading agents as targets for extraction and IRL
- [[N-Volume-Order-Flow-Academic-Microstructure]] — Trade-level data complements holdings-level demand systems

---

*Created: 2026-05-17 | Source: Groups A, B, C, D research library | Status: Synthesized*
