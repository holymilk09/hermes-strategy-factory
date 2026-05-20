# Basic & Intermediate Strategies

> Synthesized reference for all 15 basic (Level 1-3) and 17 intermediate (Level 4-6) strategies. **CORE RULE: These are baselines, sanity checks, and hypothesis generators — not serious trading edges unless independently validated.** Every entry is a hypothesis, not a claim of profitability.

---

## Core Directives (Non-Negotiable)

1. **Every strategy is a hypothesis, not a money printer**
2. No card may claim: Works, Profitable, Validated, High win rate, Institutional edge
3. **These are baselines/sanity checks** — retail strategies must be validated against the full pipeline in [[Validation Framework]] before any capital deployment consideration
4. Indicator ≠ strategy. Indicator + hypothesis + execution + risk + validation = strategy
5. LLM output is not a trade
6. **ICT/SMC = retail pattern language** not institutional microstructure (no academic anchor)

---

## BASIC STRATEGIES (Level 1-3) — 15 Strategies

> Category: `basic` | Difficulty: 1-3 | Use: Sanity checks, educational scaffolds, naive baselines for validation

---

### S-BA-001: Buy & Hold

**Key Concepts**: Passive exposure to market beta. No timing, no selection beyond initial asset choice. Edge source: none (pure beta capture), or marginally [[structural]] via equity risk premium.

- **Edge source**: None (passive beta exposure)
- **Data needed**: Price history (single asset or index)
- **Test method**: Compare cumulative return vs index benchmark over full sample; check via buy-and-hold naive baseline in [[Validation Framework]]
- **Failure mode**: Extended bear markets, single-stock idiosyncratic risk, survivorship bias if not using current index constituents
- **Professional equivalent**: [[Total Return Index]] funds, passive index replication, buy-and-hold is the zero-skill baseline every active strategy must outperform after costs
- **Implications**: The benchmark all active strategies must beat net of fees and transaction costs
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]], [[Professional Equivalent Map]]

---

### S-BA-002: DCA (Dollar-Cost Averaging)

**Key Concepts**: Fixed-dollar periodic investment regardless of price. Smooths entry over time. Edge source: none — risk management technique, not alpha.

- **Edge source**: None (behavioral risk mitigation only)
- **Data needed**: Price history, fixed investment schedule
- **Test method**: Compare DCA cumulative return vs lump-sum entry; Monte Carlo simulation over entry dates
- **Failure mode**: Underperforms lump-sum in trending-up markets; creates false confidence about timing skill
- **Professional equivalent**: [[Systematic Reinvestment]] plans, payroll deduction 401(k) contributions — a savings discipline, not an edge
- **Implications**: Useful for savings behavior; zero predictive or exploitative content
- **Cross-links**: [[Schema and Taxonomy]], [[Master Index]]

---

### S-BA-003: Periodic Rebalancing

**Key Concepts**: Restore target asset weights at fixed intervals or drift thresholds. Edge source: [[mean_reversion]] (selling winners, buying losers) + implicit volatility targeting.

- **Edge source**: mean_reversion, structural (forced buying/selling)
- **Data needed**: Portfolio weights, price history for all holdings
- **Test method**: Compare rebalanced vs drift portfolio; test different rebalance frequencies (monthly, quarterly, threshold-based)
- **Failure mode**: Underperforms in strong trending regimes; tax events from forced sales; transaction cost drag at high frequency
- **Professional equivalent**: [[Risk Parity]], volatility-targeted overlay, liability-driven investing (LDI) rebalancing
- **Implications**: Rebalancing bonus exists empirically but is small and regime-dependent
- **Cross-links**: [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-BA-004: MA Crossover

**Key Concepts**: Entry on short MA crossing above long MA; exit on cross below. Edge source: [[trend]] — slow information diffusion, institutional flow persistence.

- **Edge source**: trend
- **Data needed**: OHLCV for moving average calculation
- **Test method**: IS/OOS split with parameter sweep (50/200, 20/50, etc); compare to buy-hold baseline
- **Failure mode**: Choppy/ranging markets (whipsaw death by 1000 cuts); lagging entry/exit; parameter overfitting
- **Professional equivalent**: [[Trend Following]] with regime filters, CTA systematic trend signals — professionals use cross-sectional momentum and time-series momentum with volatility scaling, not simple MA crosses
- **Implications**: The canonical basic trend signal. Useful as a trend regime detector, not as a standalone trading signal
- **Cross-links**: [[Indicator Catalog]], [[Validation Framework]], [[Professional Equivalent Map]]

---

### S-BA-005: RSI Mean Reversion

**Key Concepts**: Buy when RSI drops below oversold threshold (e.g., 30); sell when RSI rises above overbought (e.g., 70). Edge source: [[behavioral]] (overreaction/anchoring) + [[mean_reversion]].

- **Edge source**: behavioral, mean_reversion
- **Data needed**: OHLCV for RSI calculation
- **Test method**: Test across regimes; include transaction costs; compare naive baseline
- **Failure mode**: Trending regimes (RSI stays oversold while price keeps falling); threshold overfitting; no exit without additional rules
- **Professional equivalent**: [[Mean Reversion]] with statistical z-scores, not arbitrary oscillator thresholds. Professionals use cointegration residuals, not RSI
- **Implications**: RSI is an indicator, not a strategy. Requires entry, exit, position sizing, and risk controls to become testable
- **Cross-links**: [[Indicator Catalog]], [[Failure Mode Catalog]], [[Schema and Taxonomy]]

---

### S-BA-006: MACD Signal

**Key Concepts**: Entry on MACD line crossing above signal line; exit on cross below. Histogram divergence as secondary confirmation. Edge source: [[trend]] + [[momentum]].

- **Edge source**: trend
- **Data needed**: OHLCV for MACD calculation
- **Test method**: IS/OOS split; histogram divergence as filter; compare to MA crossover baseline
- **Failure mode**: Same as MA crossover — whipsaws in ranging markets; lagging; redundant with other trend signals
- **Professional equivalent**: [[Trading-System-Build-Doctrine]] with statistical return calculation, MACD is a smoothed MA difference
- **Implications**: MACD is a lagging indicator by construction. Useful as one component in a multi-factor system, not standalone
- **Cross-links**: [[Indicator Catalog]], [[Schema and Taxonomy]], [[Master Index]]

---

### S-BA-007: Bollinger Band Reversion

**Key Concepts**: Price touching/piercing lower BB band signals buy; upper band signals sell. Assumes reversion to the mean (middle band = SMA). Edge source: [[mean_reversion]] + [[volatility]] (band width reflects vol regime).

- **Edge source**: mean_reversion, volatility
- **Data needed**: OHLCV
- **Test method**: Test with/without ADX trend filter; regime segmentation test
- **Failure mode**: Strong trends produce multiple false reversions at expanding bands; no stop logic built in; band width itself is regime indicator
- **Professional equivalent**: [[Z-Score Mean Reversion]] using cross-sectional or rolling z-scores with regime detection. BB is a visualization tool, not a statistical test
- **Implications**: BB width IS a volatility regime filter — using band position without BBW check wastes information
- **Cross-links**: [[Indicator Catalog]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-BA-008: Donchian Breakout

**Key Concepts**: Enter long on breakout above N-day high; short on N-day low. Exit on opposite signal or trailing stop. Edge source: [[trend]] — momentum continuation.

- **Edge source**: trend
- **Data needed**: OHLCV (high/low series)
- **Test method**: Parameter sweep on lookback period (20, 50, 100); walk-forward test
- **Failure mode**: False breakouts in range-bound markets; low win rate with large payoff skew; requires discipline during long drawdowns
- **Professional equivalent**: [[Trend Following]] CTA signals with channel breakouts — professionals add volatility targeting, portfolio diversification, and risk overlay
- **Implications**: Classic trend signal. Works only with portfolio-level diversification and risk management
- **Cross-links**: [[Validation Framework]], [[Professional Equivalent Map]]

---

### S-BA-009: Support/Resistance Breakout

**Key Concepts**: Enter on break above identified resistance (sell) or below support (buy reversion). Edge source: [[behavioral]] (memory at key levels) + [[liquidity]] (stop runs).

- **Edge source**: behavioral, liquidity
- **Data needed**: OHLCV, S/R level identification (must be algorithmic, not subjective)
- **Test method**: Define S/R algorithmically (recent swing highs/lows, volume nodes); test breakout vs fade
- **Failure mode**: Subjective level selection is not testable; false breakouts; levels break down after multiple touches
- **Professional equivalent**: [[Liquidity Sweep]] models — professionals use order flow data, not drawn lines. See [[Professional Equivalent Map]] for ICT/SMC → microstructure translation
- **Implications**: S/R must be quantified into coordinates and thresholds. Subjective chart lines are not testable
- **Cross-links**: [[Professional Equivalent Map]], [[Schema and Taxonomy]], [[Feature Engineering Catalog]]

---

### S-BA-010: Trendline Breakout

**Key Concepts**: Draw trendline connecting swing lows/highs; enter on break. Edge source: [[behavioral]] (self-fulfilling prophecies at widely-watched levels) + [[trend]] reversal signal.

- **Edge source**: behavioral
- **Data needed**: OHLCV with algorithmic trendline detection
- **Test method**: Define trendline algorithmically (linear regression on swing points, angle thresholds); validate out-of-sample
- **Failure mode**: Trendline drawing is inherently subjective; angle sensitivity; self-selection bias in backtests
- **Professional equivalent**: [[Structural Break Tests]] — professionals use statistical change-point detection, not drawn lines
- **Implications**: Must be converted to algorithmic coordinates to be testable. Otherwise, this is a narrative, not a strategy
- **Cross-links**: [[Schema and Taxonomy]], [[Professional Equivalent Map]]

---

### S-BA-011: VWAP Reversion

**Key Concepts**: Intraday reversion to VWAP. Entry when price deviates X% or X standard deviations from VWAP; target = VWAP. Edge source: [[mean_reversion]] (intraday) + [[liquidity]] (institutional VWAP execution benchmarks).

- **Edge source**: mean_reversion, liquidity
- **Data needed**: Intraday OHLCV or tick data, volume
- **Test method**: Intraday backtest with VWAP calculation; test reversion vs continuation regimes
- **Failure mode**: Trending intraday sessions (price never reverts); VWAP itself is a benchmark so professional presence creates complex dynamics
- **Professional equivalent**: [[Trading-System-Build-Doctrine]] with intraday mean reversion; VWAP is itself a professional execution benchmark
- **Implications**: VWAP reversion works only when combined with regime identification and risk controls
- **Cross-links**: [[Indicator Catalog]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-BA-012: Opening Range Breakout (ORB)

**Key Concepts**: Define range from first N minutes of trading (e.g., 5, 15, 30 min). Enter on breakout above/below range. Edge source: [[volatility]] (vol expansion at open) + [[order_flow]] (overnight information digestion).

- **Edge source**: volatility, order_flow
- **Data needed**: Intraday tick or minute-level OHLCV
- **Test method**: Test different opening windows; test with volume filter; transaction cost model essential at intraday scale
- **Failure mode**: False breakouts; gap reversals; high transaction cost erodes edge at intraday frequency; latency disadvantage vs professionals
- **Professional equivalent**: [[Opening Auction Dynamics]], institutional order flow modeling at open — professionals have pre-market data and order flow intelligence retail lacks
- **Implications**: ORB is a volatility expansion signal, not directional. Works best as part of a broader intraday system
- **Cross-links**: [[Validation Framework]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-BA-013: Gap Fill

**Key Concepts**: Price gaps up/down at open; bet on price returning to pre-gap close. Edge source: [[behavioral]] (overreaction to overnight news) + [[mean_reversion]].

- **Edge source**: behavioral, mean_reversion
- **Data needed**: Daily or intraday OHLCV, gap identification
- **Test method**: Define gap threshold algorithmically (e.g., >1% gap); test fill rate and time-to-fill
- **Failure mode**: Gaps due to structural changes (earnings, M&A) do NOT fill; selection bias in "fill rate" statistics; trending gaps expand
- **Professional equivalent**: [[Overnight Anomaly]] research — studied academically. Professionals exploit the opposite (gap continuation) in some contexts
- **Implications**: Gap fill statistics are often cherry-picked. Must test across all gaps, not just the ones that filled
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]], [[Professional Equivalent Map]]

---

### S-BA-014: ATR Trailing Stop

**Key Concepts**: Dynamic trailing stop using ATR multiplier. Move stop up as price rises, never down. Edge source: [[trend]] (riding trends) + [[volatility]] (adaptive to current vol regime).

- **Edge source**: trend, volatility
- **Data needed**: OHLCV for ATR calculation
- **Test method**: Test as exit mechanism for trend strategies; parameter sweep on ATR multiplier; compare to fixed stop
- **Failure mode**: Whipsaws in volatile but ranging markets; ATR lag during vol regime shifts; not a standalone entry system
- **Professional equivalent**: [[Volatility Targeting]], Chandelier exit — professionals use ATR as one component of dynamic position sizing, not just a stop
- **Implications**: ATR trailing stop is an exit/risk tool, not a complete strategy. Must be paired with an entry signal
- **Cross-links**: [[Indicator Catalog]], [[Failure Mode Catalog]], [[Schema and Taxonomy]]

---

### S-BA-015: Momentum Rotation

**Key Concepts**: Rank assets by N-period return; buy top N, sell bottom N. Rebalance periodically. Edge source: [[trend]] + [[behavioral]] (slow diffusion) + [[cross-sectional]] ranking.

- **Edge source**: trend, behavioral, statistical
- **Data needed**: Cross-sectional price data for universe; universe definition
- **Test method**: Cross-sectional backtest; test different lookback periods and rebalance frequencies; compare to equal-weight benchmark
- **Failure mode**: Momentum crashes (sharp reversals); high turnover costs; crowding in popular momentum universes
- **Professional equivalent**: [[Trading-System-Build-Doctrine]] — Jegadeesh & Titman (1993). Professionals use residual momentum, risk adjustment, and sector neutrality
- **Implications**: The most studied anomaly. Robust but decaying. Must control for risk factors and transaction costs
- **Cross-links**: [[Validation Framework]], [[Professional Equivalent Map]], [[Master Index]]

---

## INTERMEDIATE STRATEGIES (Level 4-6) — 17 Strategies

> Category: `intermediate` | Difficulty: 4-6 | Use: Require full validation suite, not just IS/OOS. Not serious edges unless validated.

---

### S-IN-001: Multi-Timeframe Trend

**Key Concepts**: Trend must align across multiple timeframes (e.g., daily + weekly + monthly) before entry. Edge source: [[trend]] — confirmation reduces false signals.

- **Edge source**: trend
- **Data needed**: OHLCV across 3+ timeframes
- **Test method**: Test each timeframe individually first, then combined; regime segmentation
- **Failure mode**: Over-filtering misses valid signals; correlation across timeframes creates illusion of confirmation; parameter explosion
- **Professional equivalent**: [[Trading-System-Build-Doctrine]] with regime filters — professionals use formal regime detection, not visual multi-TF alignment
- **Implications**: Adding timeframes doesn't create edge; it filters. The edge is still trend, just more selective
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]]

---

### S-IN-002: Volatility Breakout

**Key Concepts**: Enter when vol expands beyond recent range (BB squeeze, ATR expansion). Edge source: [[volatility]] (vol clustering, vol breakouts precede price breakouts).

- **Edge source**: volatility
- **Data needed**: OHLCV, vol measures (BBW, ATR ratio, historical vol)
- **Test method**: Test with directional filter (e.g., enter long only if trend is up + vol expands); transaction cost model
- **Failure mode**: Vol expansion without directional move (vol spike both ways); false breakouts in choppy markets
- **Professional equivalent**: [[Volatility Risk Premium]] strategies, gamma scalping — professionals trade the vol itself via options, not just price breakout
- **Implications**: Vol breakout tells you "something is happening," not direction. Requires directional filter
- **Cross-links**: [[Indicator Catalog]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-IN-003: Mean Reversion + Regime Filter

**Key Concepts**: Apply mean reversion only when regime detector (ADX, HMM, vol state) confirms ranging market. Edge source: [[mean_reversion]] conditional on [[statistical]] regime.

- **Edge source**: mean_reversion, statistical
- **Data needed**: OHLCV, regime indicator (ADX, HMM state, vol measure)
- **Test method**: Test regime filter independently; test mean reversion with/without filter; walk-forward
- **Failure mode**: Regime filter lag (regime already changed when detected); overfitting regime parameters; false regime classification
- **Professional equivalent**: [[Bayesian Regime]] models, HMM-based allocation — professionals use probabilistic regime detection, not binary filters
- **Implications**: This is the key improvement that separates intermediate from basic. Regime awareness is essential
- **Cross-links**: [[Validation Framework]], [[Professional Equivalent Map]], [[Schema and Taxonomy]]

---

### S-IN-004: Sector Rotation

**Key Concepts**: Rotate capital between sectors based on relative strength, economic cycle position, or momentum ranking. Edge source: [[trend]] + [[structural]] (sector leadership persistence) + [[informational]].

- **Edge source**: trend, structural, informational
- **Data needed**: Sector-level price data, economic indicators, earnings data
- **Test method**: Cross-sectional sector backtest; test against sector ETF universe; include transaction costs
- **Failure mode**: Rapid regime changes; sector classification changes; economic cycle timing is unreliable; crowding in factor-based rotation
- **Professional equivalent**: [[Factor Models]] with sector neutrality, macro-driven allocation — professionals use fundamental factor models, not price-based sector timing
- **Implications**: Sector rotation requires fundamental justification, not just price momentum ranking
- **Cross-links**: [[Professional Equivalent Map]], [[Master Index]]

---

### S-IN-005: Relative Strength Rotation

**Key Concepts**: Rank individual stocks by relative strength vs benchmark; buy top decile, sell bottom. Edge source: [[trend]] + [[behavioral]] (slow diffusion) + [[statistical]] cross-sectional ranking.

- **Edge source**: trend, behavioral, statistical
- **Data needed**: Cross-sectional price data, benchmark index prices
- **Test method**: Cross-sectional backtest; test RS calculation method (1-month, 3-month, 6-month, 12-month skip-1); turnover analysis
- **Failure mode**: High turnover from frequent rebalancing; survivorship bias in universe construction; RS vs momentum confusion; momentum crashes
- **Professional equivalent**: [[Trading-System-Build-Doctrine]] — RS rotation IS momentum with a different name. Professionals use risk-adjusted momentum (residual momentum)
- **Implications**: RS rotation has been extensively studied since Jegadeesh & Titman (1993). The edge is real but small after costs in liquid markets
- **Cross-links**: [[Validation Framework]], [[Professional Equivalent Map]], [[Feature Engineering Catalog]]

---

### S-IN-006: Pairs Trading

**Key Concepts**: Identify two cointegrated securities; long the underperformer, short the overperformer when spread widens. Edge source: [[mean_reversion]] + [[statistical]] (cointegration).

- **Edge source**: mean_reversion, statistical
- **Data needed**: Price data for pairs universe, cointegration test (Engle-Granger, Johansen)
- **Test method**: Test cointegration stability over rolling windows; test entry/exit thresholds; transaction cost model
- **Failure mode**: Cointegration breakdown (structural break); pairs diverge permanently; high correlation ≠ cointegration; execution risk on short leg
- **Professional equivalent**: [[Trading-System-Build-Doctrine]] pairs/basket — professionals trade baskets of hundreds of pairs, not single pairs, with real-time cointegration monitoring
- **Implications**: High correlation does not imply cointegration. Must test statistically before deploying
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]], [[Professional Equivalent Map]]

---

### S-IN-007: Statistical Arbitrage

**Key Concepts**: Long/short portfolio of stocks ranked by predicted returns from statistical model (e.g., residuals from factor model). Edge source: [[statistical]] + [[mean_reversion]].

- **Edge source**: statistical, mean_reversion
- **Data needed**: Cross-sectional price + factor data, factor model (Fama-French, etc.)
- **Test method**: Factor model construction; residual calculation; portfolio backtest; transaction cost modeling
- **Failure mode**: Factor model misspecification; crowding in popular factors; regime change in factor premiums; overfitting
- **Professional equivalent**: [[Factor Models]] + [[Trading-System-Build-Doctrine]] — professionals use high-dimensional factor models with real-time optimization
- **Implications**: This is where intermediate meets professional. Requires statistical rigor
- **Cross-links**: [[Professional Equivalent Map]], [[Validation Framework]]

---

### S-IN-008: Earnings Gap Continuation / Fade

**Key Concepts**: Trade post-earnings announcement gaps. Either continue (gap continuation) or fade (gap reversal) based on historical pattern. Edge source: [[behavioral]] (underreaction / overreaction) + [[informational]].

- **Edge source**: behavioral, informational
- **Data needed**: Earnings announcement dates, surprise data, pre/post prices, volume
- **Test method**: Event study methodology; test continuation vs fade by surprise magnitude; include slippage for low-liquidity names
- **Failure mode": Selection bias (only testing winners); earnings quality variation; guidance effect; survivorship bias
- **Professional equivalent**: [[Post-Earnings Announcement Drift]] (PEAD) — academically documented. Professionals use NLP on earnings calls, not just price reactions
- **Implications**: PEAD is one of the strongest documented anomalies. Simple gap fade/continuation is a crude proxy
- **Cross-links**: [[Validation Framework]], [[Professional Equivalent Map]], [[Schema and Taxonomy]]

---

### S-IN-009: Intraday VWAP Reversion

**Key Concepts**: More sophisticated version of VWAP reversion with regime filters, time-of-day effects, and volume confirmation. Edge source: [[mean_reversion]] + [[liquidity]] + [[order_flow]].

- **Edge source**: mean_reversion, liquidity, order_flow
- **Data needed**: Intraday tick or minute data, volume, VWAP calculation
- **Test method**: Intraday backtest with time segmentation; test volume filter; slippage model
- **Failure mode": Latency disadvantage vs professionals; trend sessions; VWAP anchoring creates complex dynamics near VWAP
- **Professional equivalent**: [[Trading-System-Build-Doctrine]] intraday — professionals trade VWAP as a benchmark with sophisticated execution models
- **Implications**: Retail traders are competing against institutions who use VWAP as their own execution benchmark
- **Cross-links**: [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-IN-010: Breadth Momentum

**Key Concepts**: Use market breadth indicators (advance-decline, new highs-new lows) to gauge broad market strength. Trade when breadth confirms/diverges from price. Edge source: [[trend]] + [[behavioral]] (participation breadth).

- **Edge source**: trend, behavioral
- **Data needed**: Market breadth data (A/D line, new highs/lows, % above MAs)
- **Test method**: Breadth indicator calculation; regime segmentation; compare to price-only momentum
- **Failure mode": Breadth data availability and quality; index composition changes; breadth works at macro scale but noisy at micro
- **Professional equivalent**: [[Trading-System-Build-Doctrine]] with breadth as one input — professionals use breadth as a macro regime filter
- **Implications**: Breadth is a macro indicator. Using it for individual stock timing is a category error
- **Cross-links**: [[Indicator Catalog]], [[Master Index]]

---

### S-IN-011: Pullback in Trend

**Key Concepts**: In established trend, buy pullbacks to moving average or Fibonacci level. Edge source: [[trend]] + [[mean_reversion]] (within-trend retracement).

- **Edge source**: trend, mean_reversion
- **Data needed**: OHLCV, trend definition (MA, ADX, higher highs)
- **Test method**: Define trend algorithmically; define pullback magnitude; test entry on pullback completion
- **Failure mode": Trend reversal misidentified as pullback; subjective pullback definition; parameter sensitivity
- **Professional equivalent**: [[Trading-System-Build-Doctrine]] with entry timing optimization — professionals use statistical pullback detection
- **Implications**: "Buy the dip" requires defining "dip" and confirming "trend" algorithmically
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]]

---

### S-IN-012: Range Expansion

**Key Concepts**: After period of contraction (narrow range, low vol), expect expansion. Enter in direction of breakout. Edge source: [[volatility]] (vol clustering, mean reversion in vol) + [[behavioral]] (compression builds energy).

- **Edge source**: volatility, behavioral
- **Data needed**: OHLCV, range/vol measures
- **Test method**: Define contraction algorithmically (NR4, NR7, BB squeeze); test directional filter; walk-forward
- **Failure mode": False breaks from narrow ranges; direction unknown at expansion; overfitting contraction definition
- **Professional equivalent**: [[Volatility Breakout]] strategies — professionals trade vol expansion via options (long straddle), not just directionally
- **Implications": Range expansion tells you magnitude is coming, not direction. Requires directional filter
- **Cross-links**: [[Indicator Catalog]], [[Professional Equivalent Map]]

---

### S-IN-013: Squeeze Breakout

**Key Concepts**: Bollinger Bands inside Keltner Channels = volatility squeeze. Trade breakout when bands expand outside channels. Edge source: [[volatility]] + [[trend]].

- **Edge source**: volatility, trend
- **Data needed**: OHLCV, BB and Keltner Channel calculation
- **Test method**: Define squeeze condition algorithmically; test with/without directional bias; walk-forward
- **Failure mode": False breakouts; parameter sensitivity (BB period, Keltner multiplier); lag
- **Professional equivalent**: [[Volatility Risk Premium]] strategies — professionals trade vol expansion via options, understanding both direction and vol premium
- **Implications": The "squeeze" is a volatility regime indicator, not a directional signal
- **Cross-links**: [[Validation Framework]], [[Professional Equivalent Map]]

---

### S-IN-014: Divergence (RSI/MACD)

**Key Concepts**: Price makes new high/low but indicator does not = divergence, potential reversal. Edge source: [[behavioral]] (momentum exhaustion) + [[mean_reversion]].

- **Edge source**: behavioral, mean_reversion
- **Data needed**: OHLCV, RSI or MACD
- **Test method**: Define divergence algorithmically (peak/trough matching); test reversal rate; include false divergence handling
- **Failure mode": Subjective divergence identification; divergences can persist for extended periods; trend continuation after multiple divergences
- **Professional equivalent": [[Momentum Oscillator]] decay — professionals model momentum decay directly, not via indicator divergence
- **Implications": Divergence is a momentum decay signal, not a reversal guarantee. Trends ignore divergence.
- **Cross-links**: [[Schema and Taxonomy]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-IN-015: Anchored VWAP

**Key Concepts**: VWAP calculated from specific anchor point (earnings date, swing high, Fed announcement). Price interaction with anchored VWAP signals reaction. Edge source: [[mean_reversion]] + [[behavioral]] (memory from specific event) + [[liquidity]].

- **Edge source**: mean_reversion, behavioral, liquidity
- **Data needed**: Intraday or daily OHLCV, volume, event dates for anchoring
- **Test method": Define anchor points algorithmically; test price reaction at anchored VWAP; transaction cost model
- **Failure mode": Anchor point selection bias; multiple anchors create conflicting signals; VWAP relevance decays over time
- **Professional equivalent": [[Volume-Weighted Execution]] models — anchored VWAP is used by professionals as an execution reference, not a standalone signal
- **Implications": The anchor matters. Arbitrary anchors = arbitrary results
- **Cross-links**: [[Indicator Catalog]], [[Professional Equivalent Map]], [[Schema and Taxonomy]]

---

### S-IN-016: Volume Profile Reversion

**Key Concepts**: Trade reversion from volume profile extremes (high/low volume nodes) toward Point of Control (POC). Edge source: [[order_flow]] + [[mean_reversion]] + [[liquidity]].

- **Edge source**: order_flow, mean_reversion, liquidity
- **Data needed**: Intraday or daily OHLCV with volume distribution
- **Test method": Define POC and value areas algorithmically; test reversion from extremes; regime segmentation
- **Failure mode": Volume profile is descriptive, not predictive; POC shifts; trending markets ignore profile levels
- **Professional equivalent": [[Market Profile]] / [[Volume Profile]] analysis — professionals use this as auction context, not standalone signal
- **Implications": Volume profile provides context about where trading occurred, not where price will go
- **Cross-links**: [[Professional Equivalent Map]], [[Failure Mode Catalog]]

---

### S-IN-017: Market Profile

**Key Concepts**: TPO (Time Price Opportunity) charting identifies balance (range) vs imbalance (trend) conditions. Trade based on market context. Edge source: [[order_flow]] + [[structural]] (auction theory) + [[behavioral]].

- **Edge source": order_flow, structural, behavioral
- **Data needed**: Intraday OHLCV, TPO calculation, session data
- **Test method": Define balance/imbalance algorithmically; test within balance vs trend day rules; walk-forward
- **Failure mode": Subjective profile interpretation; auction theory is descriptive not predictive; data requirements for intraday profile
- **Professional equivalent": [[Market Profile]] — used by floor traders and auction market professionals. Retail implementations are simplified versions
- **Implications": Market Profile is a framework for market context, not a trading signal. Must be combined with specific entry/exit rules
- **Cross-links**: [[Professional Equivalent Map]], [[Schema and Taxonomy]], [[Master Index]]

---

## Summary Rules for Basic & Intermediate Strategies

### These Are NOT Edges Until Proven

Every strategy above is a **hypothesis generator**, not a proven edge. The purpose of cataloging them here is:

1. **Sanity check baseline**: Every new strategy should first be compared against these to ensure added complexity actually adds value
2. **Educational scaffolding**: Understanding these builds the intuition needed for professional strategies
3. **Component library**: Multiple basic/intermediate strategies can be combined into professional-level systems

### Validation Minimum

Before any of these strategies is used with capital, it must pass:

- **Naive baseline**: Must beat buy-and-hold
- **IS/OOS split**: Must work out-of-sample
- **Transaction costs**: Must survive realistic transaction costs
- **Regime segmentation**: Must be tested across bull/bear/choppy regimes

### Intermediate Additional Requirements

Intermediate strategies must additionally pass:

- **Random signal test**: Must beat random entries with same turnover
- **Turnover-matched random**: Must beat random with matched trade frequency
- **Multi-asset cross-validation**: Must work across multiple assets, not just cherry-picked
- **Walk-forward**: Must work in walk-forward testing

### Professional Equivalence

None of these strategies, even if validated, provides the same edge as professional equivalents. The gap is not in the idea — the gap is in:

- **Data quality and breadth**
- **Execution speed and cost**
- **Risk management sophistication**
- **Portfolio-level optimization**
- **Regime detection capabilities**

See [[Professional Equivalent Map]] for the full translation.

---

## Cross-References

- [[Schema and Taxonomy]] — 24-field card schema for each strategy
- [[Validation Framework]] — Required tests per difficulty level
- [[Professional Equivalent Map]] — Retail → professional translation
- [[Failure Mode Catalog]] — 11 failure types
- [[Indicator Catalog]] — All indicators referenced above
- [[Feature Engineering Catalog]] — For intermediate strategies transitioning to ML
- [[Master Index]] — Full encyclopedia overview
- ← Parent vault: [[Trading-System-Build-Doctrine]]
