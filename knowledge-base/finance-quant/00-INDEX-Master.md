# Finance & Quantitative Knowledge Base — Master Index

**Purpose**: High-performance reference system for critical, logical, and creative reasoning when designing advanced trading systems. Transcends cookie-cutter strategies through first-principles thinking, cross-domain synthesis, and anti-fragile design.

**Last Updated**: 2026-05-17
**Vault Path**: `/opt/data/knowledge-base/finance-quant/`
**Total Notes**: 135+ (after MR Doctrine Batch)

---

## Vault Structure

### 00. Meta & Navigation (5 notes)
- [[00-INDEX-Master]] ← You are here
- [[00-Knowledge-Philosophy]] — How to think with this system, not just store
- [[00-Quick-Reference-Cheatsheets]] — Formulas, mental models
- [[00-Anti-Cookie-Cutter-Insights]] — Non-obvious lessons that separate good vs great systems
- [[01-Knowledge-Ingestion-Organization]] — SOP for processing all incoming material

### 03. Quantitative Finance Core (4 notes) — Batch 1
- [[Trading-System-Component-Architecture]] — 10-layer separation (data, signal, portfolio, risk, execution, broker, ledger, metrics, review)
- [[Event-Loop-and-State-Machine]] — State machines for order lifecycle, position tracking
- [[Core-Module-Contracts]] — Explicit I/O contracts between every layer
- [[Failure-Mode-Taxonomy]] — Strategy, data, backtest, and live failure catalogs

### 04. Trading Strategies & Edges (5 notes) — Batch 1
- [[Trading-System-Build-Doctrine]] — 6-phase build from spine to live trading with pass/fail gates
- [[Strategy-to-Code-Playbook]] — Bad vs good hypothesis formulation, 9-step implementation sequence
- [[Walk-Forward-Epoch-Protocol]] — Walk-forward validation, parameter stability
- [[Strategy-Weak-Point-Detection]] — Systematic strategy diagnostics
- Research Read Order (see [[Research-Read-Order-Guide]] in 10)

### 05. Risk, Portfolio & Execution (12 notes) — Batch 1
- [[Performance-Metrics]], [[Risk-Metrics]], [[Execution-Metrics]] — Full metric catalog
- [[Overfit-Detection-Metrics]] — PSR, DSR, PBO, CSCV with anti-overfit protocol
- [[Metric-Formulas]] — Exact formulas for all core metrics
- [[Heatmap-Playbook-Diagnostics]] — Master guide: 8 required heatmaps, 5 rejection criteria
- [[Heatmap-Parameter]], [[Heatmap-Time-Regime]], [[Heatmap-Slippage]], [[Heatmap-Instrument]], [[Heatmap-Trade-Failure]]
- [[INDEX-Metrics-Diagnostics]] — Cross-reference with promotion gate decision flows

### 06. Data, Infrastructure & Implementation (19 notes) — Batch 1
- **Data Pipelines**: [[Data-Pipeline-Architecture]], [[Data-Quality-Checks]], [[Feature-Store-Design]]
- **Feature Engineering**: [[Cross-Asset-Feature-Engineering]], [[Regime-Detection-Features]], [[Multi-Timeframe-Features]], [[Feature-Leakage-Prevention]], [[13f-macro-altdata-tactics]], [[Aggregated-Data-Tactics]]
- **Epoch Learning**: [[Epoch-Learning-Retraining]], [[Review-And-Learn-Loop]]
- **Frameworks**: [[Framework-Comparison-Selection]], [[Backtrader-Reference]], [[NautilusTrader-Reference]], [[VectorBT-Reference]], [[Broker-API-Comparison]], [[Data-Vendor-Comparison]]
- **Schema Catalog**: [[Schema-Catalog]] — All event schemas

### 07. Platform Reference — LEAN (6 notes) — Batch 1
- [[LEAN-Reference]] — Master index for QuantConnect/LEAN
- [[LEAN-Local-Backtesting]], [[LEAN-Live-Trading-Ops]], [[LEAN-Backtesting-Gotchas]], [[LEAN-Research-Environment]], [[LEAN-Algorithm-Framework-Mapping]]

### 07. Behavioral Finance (3 notes) — Batch 2
- [[07-01-Behavioral-Finance]] — Odean, Barber, Tetlock sentiment, Shiller narratives, prospect theory
- [[07-02-LLM-Trading-Agents]] — TradingAgents, GPT-Signal, LiveTradeBench, behavioral consistency, QuantAgent
- [[07-Index]] — Cross-cutting connections

### 08. Market Microstructure (4 notes) — Batch 2
- [[08-Market-Microstructure-LOB-Execution-Synthesis]] — Almgren-Chriss, Avellaneda-Stoikov, Cont price impact
- [[01-Order-Flow-Microstructure-Synthesis]] — Kyle, Glosten-Milgrom, VPIN
- Indexes in folder

### 08. RL & Portfolio Management (2 notes) — Batch 2
- [[08-RL-Deep-Direct-RL-Portfolio-Management]] — Async dueling Q-learning, deep RL portfolio, diffusion world models
- Index in folder

### 09. Implementation Guardrails (6 notes) — Batch 1
- [[Ai-Coding-Guardrails]] — Anti-bloat rules, project constraints, prompt protections
- [[Strategy-Backtest-Contracts]] — Strategy contract (12 fields), backtest contract reproducibility
- [[Agentic-Workflow-Patterns]] — Task sequences, prompt templates
- [[Strategy-Templates-Standards]] — README structures, hypothesis mapping, review reports
- [[Code-Templates-Schemas]] — Python contracts, sample strategy, YAML configs, JSON schemas, test patterns
- [[00-INDEX]] — Master guardrails index

### 10. Research Literature (14 notes) — Batch 1 + Batch 2
- **Papers & Docs**: [[INDEX-Papers-Docs]], [[Source-Quality-Assessment]], [[Research-Papers-Index]], [[Official-Docs-Index]]
- **Batch 2 Synthesis**: [[Research-Read-Order-Guide]] (8 stages), [[Research-Library-Synthesis]], [[Research-Paywall-Strategy]]
- **K-L-M Groups**: [[ML-Asset-Pricing-Synthesis]], [[Options-Volatility-Synthesis]], [[Risk-Statistical-Modeling-Synthesis]], [[Groups-KLM-Research-Index]]

### 11. Investor Behavior Modeling (5 notes) — Batch 2
- [[A-Reverse-Engineering-Investor-Decision-Logic]] — Koijen-Yogo demand systems, inelastic markets
- [[B-Inverse-Reinforcement-Learning-in-Finance]] — GIRL, QLBS, LOB IRL
- [[C-Foundational-IRL-Imitation-Learning]] — Ng & Russell, Abbeel, MaxEnt, GAIL
- [[D-Model-Extraction-Black-Box-Reverse-Engineering]] — Model stealing, subspace extraction
- [[Index]] — Four-layer inference stack

### 11. Quant Foundations (2 notes) — Batch 2
- [[11-Quant-Foundations-Kelly-Adaptive-Markets]] — Kelly criterion, Thorp, Simons, Lo's AMH
- [[Index]]

### 12. Technical Analysis Evidence (2 notes) — Batch 2
- [[01-Technical-Analysis-Academic-Evidence]] — Lo/Mamaysky/Wang, Brock, Sullivan/Timmermann/White data-snooping
- Index

### 13. Prediction Markets (2 notes) — Batch 2
- [[01-Prediction-Markets-AI-Forecasting-Synthesis]] — Kalshi, Polymarket, LiveTradeBench, Hanson LMSR
- Index

### 14. Hedge Fund Analysis (2 notes) — Batch 2
- [[01-Hedge-Fund-13F-Synthesis]] — 13F systematic alpha, strategic misreporting, hidden holdings
- Index

### 15. Pattern Recognition (2 notes) — Batch 2
- [[01-Pattern-Recognition-Synthesis]] — ML pricing baseline, agent-based markets, micro-pattern discovery
- Index

---

## Empty / Reserved Sections

| Section | Status |
|---|---|
| **01. Mathematics Foundations** | Reserved — Linear algebra, stochastic calculus, optimization, information theory (awaiting dedicated ingests) |
| **02. Probability, Statistics & Inference** | Reserved — Bayesian, causal inference, time series (partially covered by [[Risk-Statistical-Modeling-Synthesis]] in 10, and [[Source-Quality-Assessment]]) |

---

### 16. Strategy Encyclopedia (13 notes) — Batch 3
- **Core Architecture**: [[01-Schema-and-Taxonomy]] (24-field card schema, 10-level difficulty, 10-edge taxonomy), [[02-Indicator-Catalog]] (200+ indicators, 10 categories, redundancy map), [[03-Validation-Framework]] (14 tests, 4-baseline rule), [[04-Professional-Equivalent-Map]] (ICT→microstructure, indicators→features, patterns→stats), [[05-Failure-Mode-Catalog]] (11 failure types), [[06-Feature-Engineering-Catalog]] (15 feature types, leakage tests), [[07-Master-Index]] — Encyclopedia overview
- **Strategy Cards**: [[Basic-Intermediate-Strategies]] (32 strategies, levels 1-3), [[Professional-Quant-Strategies]] (24 strategies, levels 4-7), [[AI-ML-Strategies]] (17 agent roles + 24 ML models, levels 5-9), [[Options-Trading-Strategies]] (28+ strategies with Greeks), [[Multi-Strategy-Patterns-ICT-SMC]] (14 multi-strategy systems + 12 patterns + 16 ICT/SMC concepts + 21 volumetric/order flow concepts)
- **Implementation**: [[Code-Templates-LLM-Prompts-Datasets]] (8 code templates, 10 LLM prompts for strategy analysis, dataset requirements, sample strategy card format)

### 18. Pattern & Situational Alpha (12 notes) — Pattern Alpha Batch
- **Doctrine**: [[PATTERN_ALPHA_RULES]] — Prime directive, status labels, visual→numeric conversion, event study rule, data snooping guard
- **Lexicon**: [[pattern-categories]] (A-G pattern taxonomy), [[macro-event-patterns]] (event calendar + features), [[wave-swing-patterns]] (non-subjective swing detection)
- **Features**: [[feature-schema]] (candle geometry, trend, expansion, pullback, calendar features), [[correlation-features]] (clustering, HRP, rolling correlation stability)
- **Event Study**: [[event-study-schema]] — condition/outcome/universe/metrics/baseline comparison framework
- **Pattern Mining**: [[sequence-miner-design]] — swing detection, motif search, parameter grid logging
- **Validation**: [[validation-rules]] — White's Reality Check, Deflated Sharpe, alpha graveyard, AI/ML validation gates
- **Alerts**: [[alert-schema]] — structured pattern alert output with CANDIDATE_ONLY status
- **Doctrine**: [[NO_PATTERN_CLAIM_WITHOUT_TEST]] — blocking rule

### 19. Mean Reversion Doctrine (13 notes) — MR Doctrine Batch
- **Doctrine**: [[19-Mean-Reversion-Doctrine/00-INDEX]] — Master navigation
- **Foundations**: [[01-Edge-Sources-And-Fair-Value-Anchors]] (9 edge sources, 8 anchor types), [[02-Deviation-Scoring]] (6 vol-normalized measures), [[03-Regime-Filter]] (good/bad regimes, academic backing)
- **Entry Logic**: [[04-Exhaustion-And-Reclaim]] (8 confirmation signals), [[05-Two-Stage-Entry-Template]] (detect → confirm), [[06-Strategy-Variants]] (6 types A-F)
- **Combinations**: [[07-Best-Combos]] (5 proven combos), [[08-Filters-And-No-Trade-Logic]] (8-filter framework)
- **Risk/Exit**: [[09-Time-Stops-And-Sizing]] (by strategy type), [[10-Failure-Modes]] (11 failure types)
- **Diagnostics**: [[11-Heatmap-Diagnostics]] (17 required heatmaps), [[12-Strategy-Template-Config]] (full YAML)
- **Operational**: [[13-Hermes-Operational-Rules]] — rules Hermes follows for all MR reasoning

### 17. Arbitrage Framework (9 notes) — Batch 5
- [[17-Arbitrage-Research/]] — 9 notes covering arb hard rules, 18-strategy pack, feasibility ranking, alert schema

---

## Cross-Domain Connections Map

**New (Pattern Alpha)**:
- **Pattern Engine** (18) → **Qullamaggie Screener** (16) → **Backtest Engine** (active)
- **Event Study** (18) → **Validation Framework** (16) → **Overfit Detection** (05)
- **Correlation/Cluster** (18) → **Risk Portfolio** (05) → **HRP Portfolio Construction** (10)
- **Calendar Patterns** (18) → **Macro Event** (18) → **Pre-FOMC Drift** (10)
- **Swing/Wave Detection** (18) → **Technical Evidence** (12) → **Pattern Recognition ML** (15)
- **AI/ML Validation** (18) → **ML Strategies** (16) → **Data Snooping Guard** (10)

**Existing (Batches 1-2)**:
- **Demand Systems** (11) → **ML Pricing** (10) → **Risk Controls** (05)
- **Behavioral Biases** (07) → **Feature Engineering** (06) → **Signal Generation** (03)
- **Microstructure** (08) → **Execution** (05) → **RL Portfolio** (08)
- **IRL** (11) → **Pattern Recognition** (15) → **LLM Agents** (07)
- **Options/Vol** (10) → **Heatmaps** (05) → **Hedge Fund Analysis** (14)

**New (MR Doctrine)**:
- **MR Doctrine** (19) → **Microstructure** (08) → **Order Flow Exhaustion** signals
- **MR Regime Filter** (19) → **Regime Features** (06) → **Heatmap Diagnostics** (05)
- **MR Residual Reversion** (19) → **PCA/ETF Stat Arb** (17) → **Factor Features** (06)
- **MR Variants** (19) → **Strategy Encyclopedia** (16) → **Professional Quant Strategies**
- **MR Entry Template** (19) → **Pattern Alpha** (18) → **Event Study Engine**
- **MR Hermes Rules** (19) → **Anti-Cookie-Cutter Insights** (00) → all strategy building

**New (Batch 3)**:
- **Strategy Encyclopedia** (16) → **All existing pillars** (references them via wikilinks)
- **ICT/SMC→Microstructure** (16) bridges to [[08-Market-Microstructure]]
- **Options Cards** (16) extends [[Options-Volatility-Synthesis]] (10)
- **ML Strategy Cards** (16) operationalizes [[AI-ML-Strategies]] (Batch 2) into actionable tests
- **Feature Engineering** (16) extends [[Feature-Engineering-Catalog]] (06) with 15 professional feature types
- **Validation Framework** (16) extends [[Overfit-Detection-Metrics]] (05) and [[Heatmap-Playbook-Diagnostics]] (05)

---

*This vault is not a library. It is a thinking partner.*
