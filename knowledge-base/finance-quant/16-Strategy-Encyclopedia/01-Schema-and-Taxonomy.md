# Schema and Taxonomy

> Core structural specification for the Strategy Encyclopedia. Defines every field in a strategy card, the 10-level difficulty ladder, the 10 edge source taxonomy, and the strategy family tree. Every card must complete all 24 fields before advancing from research.

---

## 1. Strategy Card Schema (24 Fields — All Required)

Every strategy card is a structured hypothesis, not a claim of profitability. No card may contain: "Works", "Profitable", "Validated", "High win rate", "Institutional edge".

| # | Field | Type | Purpose |
|---|---|---|---|
| 1 | `strategy_id` | string (S-XXX) | Unique identifier. Format: `S-001` through `S-999`. Prefix family: `S-BA-001` (Basic), `S-IN-001` (Intermediate), `S-PR-001` (Professional). |
| 2 | `strategy_name` | string | Human-readable name. Descriptive, not promotional. |
| 3 | `category` | enum | One of: `basic`, `intermediate`, `professional` — maps to difficulty tier. |
| 4 | `difficulty` | int (1–10) | Difficulty level from ladder. See Difficulty Ladder below. |
| 5 | `edge_source[]` | string[] (1+ of 10) | What market inefficiency this claims to exploit. See Edge Sources below. |
| 6 | `asset_classes[]` | string[] | Markets this applies to: equities, forex, crypto, bonds, commodities, options, futures. |
| 7 | `timeframes[]` | string[] | Applicable timeframes: 1m, 5m, 15m, 1h, 4h, 1d, 1w+. |
| 8 | `data_required[]` | string[] | Minimum data inputs: OHLCV, order_book, options_chain, fundamentals, sentiment, tick_data, options_greeks. |
| 9 | `entry_logic` | text | Precise, algorithmic entry conditions. Must be coded without subjective judgment. |
| 10 | `exit_logic` | text | Precise exit conditions. Must include stop-loss, take-profit, or time-based exits. |
| 11 | `position_sizing` | text | How position size is calculated. Kelly fraction, fixed fractional, volatility-adjusted, etc. |
| 12 | `risk_controls` | text | Maximum drawdown limits, correlation caps, exposure limits, circuit breakers. |
| 13 | `indicators_used` | string[] | [[Indicator Catalog]] references. Indicator ≠ strategy. |
| 14 | `features_used` | string[] | [[Feature Engineering Catalog]] references. Derived features beyond indicators. |
| 15 | `validation_tests[]` | string[] | Required tests from [[Validation Framework]]. Minimum: naive baseline, OOS split, turnover-matched random. |
| 16 | `failure_modes[]` | string[] | Known failure modes from [[Failure Mode Catalog]]. |
| 17 | `professional_equivalent` | text | [[Professional Equivalent Map]] — how professionals express the same idea with different tools. |
| 18 | `paper_references[]` | string[] | Academic or practitioner papers supporting or discussing the edge. |
| 19 | `implementation_notes` | text | Code-level considerations: libraries, data formats, edge cases, look-ahead traps. |
| 20 | `live_trading_risk` | text | Risks specific to live execution: slippage, liquidity, latency, gap risk. |
| 21 | `status` | enum | `research_only` \| `testable` \| `code_template_ready` \| `deprecated` |
| 22 | `related_strategies[]` | string[] | Strategy IDs with overlapping logic or shared edge sources. |
| 23 | `code_template` | string | Reference to template from code template library. |
| 24 | `last_reviewed` | date | When the card was last reviewed/updated. |

### Field Constraints
- **entry_logic** and **exit_logic** must be falsifiable. If you cannot write if/then statements, the strategy is not testable.
- **edge_source[]** must reference at least one edge from the 10-edge taxonomy.
- **validation_tests[]** must include minimum baselines per [[Validation Framework]].
- No field may be left blank on a card with status != `research_only`.

### Anti-Cookie-Cutter Insight
A strategy card with vague entry/exit logic is not a strategy — it is a narrative. The card schema forces operationalization. If you cannot fill all 24 fields with precision, you do not yet have a strategy, only a hypothesis worth exploring.

---

## 2. Difficulty Ladder (10 Levels)

Each level has increasing data requirements, infrastructure complexity, and theoretical depth.

### Level 1 — Basic Discretionary / Educational
- **Examples**: Buy & hold, DCA (dollar-cost averaging), simple trend following
- **Skills needed**: Understanding of market mechanics
- **Data**: Price history only
- **Validation**: Compare to index benchmark
- **Edge source**: None (passive) or basic behavioral

### Level 2 — Rule-Based Technical
- **Examples**: RSI mean-reversion, MACD crossover, MA crossover, Bollinger band breakout
- **Skills needed**: Technical indicator knowledge, basic backtesting
- **Data**: OHLCV
- **Validation**: In-sample/out-of-sample split, naive baseline
- **Edge source**: behavioral, trend, mean_reversion

### Level 3 — Multi-Factor Technical
- **Examples**: Multi-timeframe trend, volatility breakout with ATR filter, RSI + ADX combo
- **Skills needed**: Multi-timeframe analysis, correlation awareness
- **Data**: OHLCV across multiple timeframes
- **Validation**: Multi-asset cross-validation, turnover-matched random
- **Edge source**: trend, volatility, behavioral

### Level 4 — Statistical / Cross-Sectional
- **Examples**: Pairs trading, statistical arbitrage, factor models (value, momentum, quality)
- **Skills needed**: Statistics (cointegration, stationarity, regression), portfolio construction
- **Data**: Cross-sectional price + fundamentals
- **Validation**: Randomization tests, walk-forward, cointegration tests
- **Edge source**: statistical, structural

### Level 5 — ML-Assisted
- **Examples**: XGBoost signal, HMM regime detection, meta-labeling, random forest feature selection
- **Skills needed**: Machine learning fundamentals, feature engineering, overfitting awareness
- **Data**: OHLCV + derived features
- **Validation**: 4-baseline ML minimum (naive, linear, random, turnover-matched random), k-fold + time-series split
- **Edge source**: statistical, behavioral, order_flow

### Level 6 — Portfolio of Strategies
- **Examples**: Ensemble allocation, Kelly portfolio, risk-parity overlay, correlation-weighted ensemble
- **Skills needed**: Portfolio optimization, correlation matrix management, allocation theory
- **Data**: Multiple strategy return streams
- **Validation**: Out-of-sample ensemble performance, stress testing, correlation breakdown tests
- **Edge source**: Multiple combined edges

### Level 7 — Microstructure / Execution Alpha
- **Examples**: Order flow imbalance (OFI), market making, queue position models, tick-level scalping
- **Skills needed**: Market microstructure theory, LOB dynamics, latency awareness
- **Data**: Tick data, order book (L2/L3), trade tapes
- **Validation**: Tick-level simulation, slippage modeling, queue position models
- **Edge source**: order_flow, liquidity, structural

### Level 8 — Options Volatility / Relative Value
- **Examples**: Volatility risk premium (VRP) harvesting, gamma scalping, dispersion trades, calendar spreads
- **Skills needed**: Options pricing (Black-Scholes, Greeks), volatility surfaces, vol arbitrage
- **Data**: Options chain, IV surfaces, historical vol, Greeks
- **Validation**: Greeks-neutral testing, vol surface stress tests, model risk assessment
- **Edge source**: volatility, carry, statistical

### Level 9 — Adaptive AI/ML Research System
- **Examples**: Regime-adaptive models, online learning, reinforcement learning agents, self-modifying strategies
- **Skills needed**: Advanced ML, online learning, regime detection, research methodology
- **Data**: All available + alternative data
- **Validation**: Regime-change stress tests, online performance monitoring, drift detection
- **Edge source**: All edges combined

### Level 10 — Institutional Multi-Strategy Platform
- **Examples**: Multi-strategy fund architecture, capital allocation across uncorrelated edges, risk overlay systems
- **Skills needed**: Institutional portfolio management, risk governance, infrastructure at scale
- **Data**: All data types, alternative data, proprietary data
- **Validation**: Full production validation pipeline, live paper trading, institutional risk limits
- **Edge source**: All edges combined with structural and informational advantages

---

## 3. Edge Source Taxonomy (10 Edges)

Each strategy must identify which market inefficiency (edge) it claims to exploit. Multiple edges per strategy are allowed.

### behavioral
- Exploits systematic human biases: anchoring, overreaction, recency, loss aversion
- Examples: RSI extremes, post-earnings drift, January effect
- Decay risk: Awareness reduces edge; adaptive markets hypothesis

### trend
- Exploits persistence in price direction due to slow information diffusion, herding, institutional flows
- Examples: Moving average crossovers, momentum carry, breakouts
- Decay risk: Regime changes (trending → mean-reverting), increased algorithmic trading

### mean_reversion
- Exploits tendency of prices/ratios to return to equilibrium after deviation
- Examples: Bollinger band fade, pairs trading, statistical mean reversion
- Decay risk: Structural breaks, trending regimes

### liquidity
- Exploits temporary imbalances in market depth, spread, and order book dynamics
- Examples: OFI models, spread capture, market making
- Decay risk: Competition from HFT, regulatory changes

### volatility
- Exploits mispricing or predictability in volatility (IV vs RV, vol clustering)
- Examples: VRP harvesting, gamma scalping, volatility breakouts
- Decay risk: Vol surface efficiency, model risk

### carry
- Exploits yield/return differential between long and short positions
- Examples: FX carry, futures roll yield, dividend capture
- Decay risk: Carry crashes, regime shifts, convergence

### statistical
- Exploits statistical regularities in cross-sectional or time-series data
- Examples: Factor models, cointegration pairs, statistical arbitrage
- Decay risk: Overfitting, multiple testing, regime change

### order_flow
- Exploits information in the order book, trade flow, and market participant behavior
- Examples: Order flow imbalance, volume profile, delta divergence
- Decay risk: Obfuscation (iceberg orders, dark pools), competition

### structural
- Exploits permanent or semi-permanent market structure features
- Examples: Index rebalancing effects, expiry dynamics, ETF creation/redemption
- Decay risk: Structural changes, awareness/arbitrage

### informational
- Exploits information asymmetry or faster information processing
- Examples: News sentiment, alternative data, earnings timing
- Decay risk: Competition, data access costs, latency

### Implications for Trading Systems
- A strategy with no identified edge source is gambling, not trading
- Multiple edge sources provide diversification but must be independently validated
- Edge decay is not a failure mode — it is an expected lifecycle. Monitor and adapt.
- Professional edge always includes structural or informational advantages not available to retail

### Anti-Cookie-Cutter Insight
Most retail traders conflate "I found a pattern" with "I found an edge." An edge requires: (1) a mechanism explaining why the pattern should persist, (2) evidence it survives transaction costs, (3) understanding of how it decays. Without these three, it is a pattern, not an edge.

---

## 4. Strategy Family Tree

Strategies organized by conceptual family. Each family shares underlying logic but differs in implementation.

### Family 1: Trend Following
- **Core idea**: Prices in motion stay in motion
- **Edges**: trend
- **Members**: Single MA crossover, dual MA crossover, Donchian channel breakout, ADX trend filter, triple screen, multi-timeframe trend
- **Related indicators**: MA, EMA, ADX, MACD, SuperTrend
- **Failure modes**: Choppy/ranging markets, whipsaws, delayed entries

### Family 2: Mean Reversion
- **Core idea**: Prices return to equilibrium
- **Edges**: mean_reversion
- **Members**: RSI overbought/oversold, Bollinger band fade, z-score mean reversion, pairs trading, Kalman filter pairs
- **Related indicators**: RSI, Bollinger Bands, z-score, cointegration tests
- **Failure modes**: Trending regimes, structural breaks, momentum crashes

### Family 3: Momentum
- **Core idea**: Winners keep winning, losers keep losing
- **Edges**: trend, behavioral
- **Members**: Cross-sectional momentum, time-series momentum, relative strength rotation, earnings momentum
- **Related indicators**: Rate of change, momentum oscillator, relative strength
- **Failure modes**: Momentum crashes, reversals after extreme moves

### Family 4: Volatility
- **Core idea**: Volatility is predictable and mean-reverting
- **Edges**: volatility
- **Members**: ATR breakout, Bollinger squeeze, VIX strategies, vol targeting, gamma scalping
- **Related indicators**: ATR, Bollinger Bands, historical vol, IV rank
- **Failure modes**: Vol regime shifts, gap risk, vol-of-vol spikes

### Family 5: Carry
- **Core idea**: Earn yield differential
- **Edges**: carry
- **Members**: FX carry trade, futures roll yield, dividend capture, term structure carry
- **Related indicators**: Yield curves, forward rates, dividend yield
- **Failure modes**: Carry crashes, adverse FX moves, roll cost spikes

### Family 6: Statistical / Factor
- **Core idea**: Statistical relationships in cross-sectional data
- **Edges**: statistical, structural
- **Members**: Factor models (value, momentum, quality, size, low vol), stat arb, PCA-based models
- **Related indicators**: Factor scores, PCA components, regression weights
- **Failure modes**: Factor crowding, regime change, overfitting, data mining

### Family 7: Order Flow / Microstructure
- **Core idea**: Trade flow and order book contain predictive information
- **Edges**: order_flow, liquidity
- **Members**: OFI, volume profile, delta divergence, tape reading, footprint analysis
- **Related indicators**: Volume, CVD, footprint charts, order flow delta
- **Failure modes**: Dark pool hiding, latency disadvantage, spoofing

### Family 8: Pattern Recognition
- **Core idea**: Chart patterns encode supply/demand psychology
- **Edges**: behavioral
- **Members**: Head & shoulders, double tops/bottoms, triangles, flags, candlestick patterns
- **Related indicators**: Pattern detection algorithms, support/resistance levels
- **Failure modes**: Subjectivity, survivorship bias, no statistical edge without quantification

### Family 9: Options / Volatility Arbitrage
- **Core idea**: Options mispricing creates relative value opportunities
- **Edges**: volatility, statistical, carry
- **Members**: Iron condor, butterfly spreads, straddles/strangles, calendar spreads, dispersion
- **Related indicators**: IV surface, Greeks, volatility cone, skew
- **Failure modes**: Tail risk, model risk, gamma risk, margin requirements

### Family 10: Machine Learning / AI
- **Core idea**: Non-linear models capture complex relationships
- **Edges**: statistical, behavioral, order_flow (varies by features)
- **Members**: XGBoost signal, HMM regime, meta-labeling, RL agents, neural network predictors
- **Related indicators**: Engineered features, embeddings, latent states
- **Failure modes**: Overfitting, look-ahead bias, regime drift, data leakage

### Cross-Family Relationships
- **ICT/SMC** → Not a family. Retail pattern language. Components map to: Family 8 (patterns) + Family 7 (order flow interpretation). See [[Professional Equivalent Map]].
- **Multi-strategy systems** → Combine families 1–10. See [[#Strategy Portfolio Systems]] in [[Master Index]].

---

## 5. Strategy Taxonomy by Difficulty Level

### Level 1–3: Basic/Intermediate (Retail)
- Strategy families: Trend Following, Mean Reversion, Momentum, Volatility (basic), Pattern Recognition
- Data: OHLCV, standard indicators
- Validation: In-sample/out-of-sample split, basic baselines
- Professional equivalent: These are simplified versions of statistical edges

### Level 4–5: Intermediate/Professional (Quant)
- Strategy families: Statistical/Factor, ML-Assisted, Carry (advanced), Volatility (advanced)
- Data: Cross-sectional, fundamentals, options data
- Validation: Full validation suite including walk-forward, randomization tests

### Level 6–7: Professional (Systematic)
- Strategy families: Portfolio Systems, Microstructure/Order Flow
- Data: Tick, order book, multi-asset
- Validation: Production-grade testing, slippage modeling

### Level 8–9: Advanced Professional
- Strategy families: Options/VA, Adaptive AI/ML
- Data: Full options chain, alternative data
- Validation: Model risk assessment, regime stress tests

### Level 10: Institutional
- Strategy families: Multi-strategy platform
- Data: All + proprietary
- Validation: Full institutional pipeline

---

## 6. Core Rules (Non-Negotiable)

1. **Every strategy is a hypothesis, not a money printer**
2. **No card may claim**: Works, Profitable, Validated, High win rate, Institutional edge
3. **Every card must state**: what it claims to exploit, data needed, how to test, why it may fail, professional equivalent, related indicators/features
4. **Indicator ≠ strategy**. Indicator + hypothesis + execution + risk + validation = strategy
5. **No subjective chart pattern is testable** until converted into coordinates, thresholds, and timestamps
6. **LLM output is not a trade** — LLM output is input to validation
7. **No ML strategy passes** without beating: naive baseline, linear baseline, random signal, turnover-matched random
8. **ICT/SMC = retail pattern language** not institutional microstructure (no academic anchor)

---

## Cross-References
- [[Indicator Catalog]] — 200+ indicators organized by category
- [[Validation Framework]] — 14 required validation tests
- [[Professional Equivalent Map]] — Retail concepts → professional equivalents
- [[Failure Mode Catalog]] — 11 failure types with mechanisms
- [[Feature Engineering Catalog]] — 15 feature types + leakage tests
- [[Master Index]] — Full encyclopedia overview
