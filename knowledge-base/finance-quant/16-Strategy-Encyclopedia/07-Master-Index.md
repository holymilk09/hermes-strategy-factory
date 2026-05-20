# Strategy Encyclopedia — Master Index

> Complete structural overview of the Strategy Encyclopedia. This is the entry point and navigation hub. All strategy cards, validation protocols, and supporting frameworks link back to this index.

---

## Purpose

The Strategy Encyclopedia is not a list of profitable strategies. It is a **strategy ontology** — a structured framework for representing, testing, and evolving trading hypotheses. Every entry is a hypothesis with data requirements, failure modes, and validation gates.

---

## Core Rules (Non-Negotiable)

1. **Every strategy is a hypothesis, not a money printer**
2. **No card may claim**: Works, Profitable, Validated, High win rate, Institutional edge
3. **Every card must state**: what it claims to exploit, data needed, how to test, why it may fail, professional equivalent, related indicators/features
4. **Indicator ≠ strategy**. Indicator + hypothesis + execution + risk + validation = strategy
5. **No subjective chart pattern is testable** until converted into coordinates, thresholds, and timestamps
6. **LLM output is not a trade** — LLM output is input to validation
7. **No ML strategy passes** without beating: naive baseline, linear baseline, random signal, turnover-matched random
8. **ICT/SMC = retail pattern language** not institutional microstructure (no academic anchor)

---

## Encyclopedia Structure

```
16-Strategy-Encyclopedia/
├── 01-Schema-and-Taxonomy.md          ← Card schema, difficulty, edges, family tree
├── 02-Indicator-Catalog.md            ← 200+ indicators, redundancy, ≠ strategy rule
├── 03-Validation-Framework.md         ← 14 tests, strategy-test matrix, 4 baselines
├── 04-Professional-Equivalent-Map.md  ← Retail → professional translation
├── 05-Failure-Mode-Catalog.md         ← 11 failure types + mitigations
├── 06-Feature-Engineering-Catalog.md  ← 15 feature types + leakage tests
└── 07-Master-Index.md                 ← This file — encyclopedia overview
```

---

## Strategy Categories

### Basic Strategies (Difficulty 1-3) — Retail
- **Trend Following**: MA crossovers, Donchian breakout, ADX filter, SuperTrend
- **Mean Reversion**: RSI fade, Bollinger band reversion, z-score reversion
- **Momentum**: Rate of change, ROC breakouts, relative strength
- **Volatility**: ATR breakout, BB squeeze, vol targeting
- **Pattern Recognition**: Head & shoulders (quantified), triangles, flags
- **Carry**: Dividend capture, simple FX carry
- **Entry**: These are starting points for hypothesis testing, not complete strategies

### Intermediate Strategies (Difficulty 4-6) — Quant
- **Statistical**: Pairs trading, cointegration, factor models
- **ML-Assisted**: XGBoost signal, HMM regime detection, meta-labeling
- **Advanced Momentum**: Cross-sectional momentum, time-series momentum with regime filter
- **Advanced Volatility**: VRP harvesting, vol cone positioning, dispersion trade basics
- **Multi-Strategy**: Portfolio of 3-10 uncorrelated strategies, Kelly allocation
- **Carry Advanced**: Term structure carry, futures roll optimization
- **Entry**: Requires full validation suite, not just IS/OOS split

### Professional Strategies (Difficulty 7-10) — Institutional
- **Microstructure**: OFI, market making, tick-level scalping, queue position
- **Options Volatility**: VRP systematic, gamma scalping, vol arb, correlation trading
- **Adaptive AI/ML**: Regime-adaptive models, online learning, RL agents
- **Multi-Strategy Platform**: Institutional allocation across uncorrelated edges, risk overlay
- **Entry**: Requires production-grade validation, paper trading, model risk assessment

---

## Strategy Families (10 Families)

| # | Family | Core Edge | Difficulty Range | Notes |
|---|---|---|---|---|
| 1 | Trend Following | trend | 1-4 | Lagging by nature; edge in regime filter |
| 2 | Mean Reversion | mean_reversion | 2-5 | Fails in trending regimes |
| 3 | Momentum | trend, behavioral | 3-6 | Most studied anomaly; robust across assets |
| 4 | Volatility | volatility | 2-8 | Vol is mean-reverting; VRP is persistent |
| 5 | Carry | carry | 3-8 | Earn yield; carry crashes are catastrophic |
| 6 | Statistical / Factor | statistical, structural | 4-6 | Requires cross-sectional data |
| 7 | Order Flow / Microstructure | order_flow, liquidity | 7-8 | Requires tick data |
| 8 | Pattern Recognition | behavioral | 1-3 | Must be quantified to be testable |
| 9 | Options / Vol Arb | volatility, statistical, carry | 8-9 | Options Greeks required |
| 10 | ML / AI | statistical, behavioral, order_flow | 5-10 | Must beat 4 baselines minimum |

---

## Supporting Frameworks

### [[Schema and Taxonomy]]
- 24-field strategy card schema (all fields required)
- 10-level difficulty ladder
- 10 edge source taxonomy
- Strategy family tree
- **Use when**: Creating or validating a new strategy card

### [[Indicator Catalog]]
- 200+ indicators in 10 categories
- Indicator ≠ strategy rule
- Redundancy map and failure modes
- **Use when**: Selecting indicators for strategy or feature engineering

### [[Validation Framework]]
- 14 required validation tests
- Strategy-test matrix by difficulty level
- 4 minimum baselines for ML strategies
- **Use when**: Testing any strategy hypothesis

### [[Professional Equivalent Map]]
- ICT/SMC → microstructure translation
- Indicators → features translation
- Chart patterns → statistical tests translation
- Options retail → professional vol translation
- **Use when**: Understanding the gap between retail and professional approaches

### [[Failure Mode Catalog]]
- 11 failure types with mechanisms and mitigations
- Failure mode decision tree
- Quick reference table
- **Use when**: Completing the failure_modes[] field of a strategy card

### [[Feature Engineering Catalog]]
- 15 feature types with construction methods
- Leakage test protocol (5 tests)
- Feature decay monitoring
- **Use when**: Building features for ML strategies

---

## Strategy Card Fields (24 Required)

Every strategy card has these fields (defined in [[Schema and Taxonomy]]):

1. `strategy_id` — Unique identifier
2. `strategy_name` — Human-readable name
3. `category` — basic/intermediate/professional
4. `difficulty` — Level 1-10
5. `edge_source[]` — From 10-edge taxonomy
6. `asset_classes[]` — Applicable markets
7. `timeframes[]` — Applicable timeframes
8. `data_required[]` — Minimum data inputs
9. `entry_logic` — Algorithmic entry conditions
10. `exit_logic` — Exit conditions with stops/targets
11. `position_sizing` — Size calculation method
12. `risk_controls` — Drawdown/correlation/exposure limits
13. `indicators_used` — [[Indicator Catalog]] references
14. `features_used` — [[Feature Engineering Catalog]] references
15. `validation_tests[]` — [[Validation Framework]] tests
16. `failure_modes[]` — [[Failure Mode Catalog]] references
17. `professional_equivalent` — [[Professional Equivalent Map]] reference
18. `paper_references[]` — Academic/practitioner papers
19. `implementation_notes` — Code-level considerations
20. `live_trading_risk` — Live execution risks
21. `status` — research_only/testable/code_template_ready/deprecated
22. `related_strategies[]` — Overlapping strategy IDs
23. `code_template` — Template reference
24. `last_reviewed` — Date of last review

---

## Validation Pipeline (Sequential)

```
Research Only → Testable → Code Template Ready → (Live Trading)

Step 1: HYPOTHESIS FORMULATION
  - All 24 fields drafted
  - Edge source identified
  - Entry/exit logic specified algorithmically

Step 2: INITIAL VALIDATION
  - IS/OOS split test
  - Naive baseline (buy-and-hold)
  - Transaction cost analysis
  - Parameter sensitivity

Step 3: FULL VALIDATION
  - All 14 validation tests (or subset per difficulty)
  - 4-baseline minimum for ML strategies
  - Walk-forward, cross-validation, Monte Carlo
  - Regime segmentation test

Step 4: CODE TEMPLATE READY
  - Production-quality code
  - Unit tests passing
  - Paper trading ready

Step 5: PAPER TRADING
  - 3-6 months minimum
  - Performance within 20% of backtest
  - Operational issues resolved

Step 6: LIVE TRADING (NOT PART OF ENCYCLOPEDIA)
  - Small capital deployment
  - Continuous monitoring
  - Regular review and update
```

---

## Edge Sources (10 Types)

| Edge | Description | Strategy Families |
|---|---|---|
| behavioral | Human biases: anchoring, overreaction, herding | Momentum, Pattern Recognition, ML |
| trend | Slow info diffusion, institutional flow persistence | Trend Following, Momentum |
| mean_reversion | Price return to equilibrium | Mean Reversion, Statistical |
| liquidity | Order book imbalances, spread dynamics | Order Flow, Microstructure |
| volatility | Vol mispricing, clustering, IV vs RV | Volatility, Options |
| carry | Yield/return differentials | Carry, Options |
| statistical | Cross-sectional regularities, factor models | Statistical, Factor, ML |
| order_flow | Trade flow and order book information | Order Flow, Microstructure |
| structural | Permanent market structure features | Carry, Statistical, Options |
| informational | Information asymmetry or faster processing | ML, Statistical, Pattern Recognition |

---

## Difficulty Ladder Quick Reference

| Level | Description | Validation Minimum |
|---|---|---|
| 1 | Basic discretionary/educational | Naive baseline only |
| 2 | Rule-based technical | Naive + IS/OOS + transaction costs |
| 3 | Multi-factor technical | Above + linear baseline + regime test |
| 4 | Statistical/cross-sectional | Full validation suite |
| 5 | ML-assisted | Full + 4-baseline minimum |
| 6 | Portfolio of strategies | Portfolio-level validation |
| 7 | Microstructure/execution alpha | Tick-level simulation |
| 8 | Options volatility | Greeks-neutral testing |
| 9 | Adaptive AI/ML research | Regime stress, drift detection |
| 10 | Institutional platform | Full production pipeline |

---

## Strategy Inventory (Actual Structure)

Strategy cards are organized as synthesized strategy notes (not individual card files):

```
16-Strategy-Encyclopedia/
├── 01-Schema-and-Taxonomy.md              ← Card schema (24 fields), 10-level ladder, 10 edges
├── 02-Indicator-Catalog.md                ← 200+ indicators, 10 categories, redundancy map
├── 03-Validation-Framework.md             ← 14 tests, 4-baseline rule, decision tree
├── 04-Professional-Equivalent-Map.md      ← ICT→microstructure, indicators→features, etc.
├── 05-Failure-Mode-Catalog.md             ← 11 failure types with mechanism/mitigation
├── 06-Feature-Engineering-Catalog.md      ← 15 feature types, leakage/decay tests
├── 07-Master-Index.md                     ← This file (encyclopedia overview)
├── Basic-Intermediate-Strategies.md       ← 32 strategy cards (S-BA-001 through S-IN-017)
├── Professional-Quant-Strategies.md        ← 24 strategy cards (S-PR-001 through S-PR-024)
├── AI-ML-Strategies.md                     ← 17 agent roles (AG-001-017) + 24 ML models (ML-001-024)
├── Options-Trading-Strategies.md           ← 28+ options strategies (OPT-001 through OPT-028)
├── Multi-Strategy-Patterns-ICT-SMC.md      ← 14 multi-strategy + 12 patterns + 16 ICT + 21 vol/order-flow
├── Code-Templates-LLM-Prompts-Datasets.md  ← 8 code templates + 10 LLM prompts + dataset tiers
```

Each strategy note contains individual strategy cards with: strategy_id, strategy_name, difficulty level, edge_source, data_required, entry_logic, exit_logic, failure_modes, professional_equivalent, and required validation_tests.

---

## How to Use This Encyclopedia

### For Strategy Development
1. Read [[Schema and Taxonomy]] to understand the card format
2. Select a hypothesis from the strategy families above
3. Complete all 24 fields with precision
4. Run the validation pipeline from [[Validation Framework]]
5. Fill in [[Failure Mode Catalog]] applicable modes
6. Map to professional equivalent in [[Professional Equivalent Map]]
7. Engineer features from [[Feature Engineering Catalog]]
8. Check indicator redundancy in [[Indicator Catalog]]

### For Strategy Review
1. Verify all 24 fields are complete
2. Check edge source is identified and justified
3. Validate all required tests per difficulty level
4. Ensure failure modes are documented
5. Verify entry/exit logic is algorithmic, not subjective
6. Confirm no prohibited claims (Works, Profitable, Validated)

### For ML Strategy Approval
1. Must beat ALL 4 baselines (naive, linear, random, turnover-matched random)
2. Must pass leakage tests from [[Feature Engineering Catalog]]
3. Must pass parameter sensitivity analysis
4. Must document feature importance and model interpretability
5. Must have drift detection plan for live deployment

---

## Anti-Cookie-Cutter Insight

The Strategy Encyclopedia exists because most retail traders treat strategies as static objects — "I found one that works → I'm rich." In reality, strategies are living hypotheses that require continuous testing, monitoring, and adaptation. The encyclopedia's structure forces rigor at every step. If you resist filling out all 24 fields, you are resisting the very process that would make your strategy survivable.

**Edge is not found. It is validated.**

---

## Cross-References
- [[Schema and Taxonomy]] — Complete card schema
- [[Indicator Catalog]] — All 200+ indicators
- [[Validation Framework]] — 14 validation tests
- [[Professional Equivalent Map]] — Retail → professional translation
- [[Failure Mode Catalog]] — 11 failure types
- [[Feature Engineering Catalog]] — 15 feature types
- ← Parent vault: [[Trading-System-Build-Doctrine]]
