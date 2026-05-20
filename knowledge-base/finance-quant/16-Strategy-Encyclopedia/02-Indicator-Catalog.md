# Indicator Catalog

> Complete catalog of 200+ technical indicators organized by category. This is NOT a list of strategies. An indicator is a function that transforms data. A strategy requires hypothesis + execution + risk + validation. An indicator alone is not a strategy.

---

## Indicator ≠ Strategy Rule

**Indicator**: A mathematical function applied to price/volume/data → produces a signal or value
**Strategy**: Indicator(s) + entry logic + exit logic + position sizing + risk controls + validation

### The Gap Between Indicator and Strategy
An indicator tells you "RSI is 25". A strategy tells you:
- WHEN to act (RSI crosses below 30 after 5+ down days)
- HOW MUCH to risk (0.5% account, ATR-based stop)
- WHEN TO EXIT (take profit at RSI 50, stop at entry - 2 ATR)
- HOW TO VALIDATE (beat naive baseline across 20 instruments)

**If you cannot fill all 24 fields of a [[Schema and Taxonomy]] card, you do not have a strategy.**

---

## Category 1: Trend Indicators (25)

Trend indicators smooth price data to identify direction. They lag by construction.

### Moving Averages
| Indicator | Type | Params | Notes |
|---|---|---|---|
| Simple Moving Average (SMA) | Lagging | period | Equal weight smoothing |
| Exponential Moving Average (EMA) | Lagging | period, alpha | Recent weight emphasis |
| Weighted Moving Average (WMA) | Lagging | period | Linear weight |
| Hull Moving Average (HMA) | Lagging | period | Reduced lag via WMA/EMA combo |
| Volume-Weighted MA (VWMA) | Lagging | period | Volume-weighted smoothing |
| Adaptive Moving Average (AMA/Kaufman) | Adaptive | period, efficiency ratio | Adjusts to volatility |
| Variable Moving Average (VMA) | Adaptive | period | Volatility-adjusted |

### Trend Following Systems
| Indicator | Type | Params | Notes |
|---|---|---|---|
| MACD | Momentum/Trend | fast(12), slow(26), signal(9) | EMA convergence-divergence |
| MACD Histogram | Momentum | derived | Rate of MACD change |
| Parabolic SAR | Trend | step, max | Stop-and-reverse levels |
| Ichimoku Cloud | Multi-component | 9, 26, 52 | Support/resistance + momentum |
| Average Directional Index (ADX) | Trend strength | period(14) | Non-directional trend strength |
| +DI / -DI | Trend direction | period(14) | Directional components |
| DMI (Directional Movement Index) | Trend | period(14) | +DI, -DI, ADX combined |
| SuperTrend | Trend | period, multiplier | ATR-based trend channel |
| Choppiness Index | Regime | period(14) | Trending vs ranging |
| Mass Index | Reversal | period | Expansion/contraction cycles |
| Vortex Indicator | Trend | period | Directional movement ratio |
| Aroon | Trend | period | Time since high/low |
| Balance of Power | Trend | period | Bull/bear pressure |
| Coppock Curve | Trend | 11, 14, 10 | Long-term momentum |
| Detrended Price Oscillator | Cycle | period | Removes trend to show cycles |
| Ehler's MESA | Adaptive | various | Instantaneous trendline |
| Fractal Adaptive MA (FRAMA) | Adaptive | period | Fractal dimension based |
| KAMA (Kaufman Adaptive) | Adaptive | period | Efficiency ratio adaptive |
| McGinley Dynamic | Trend | period, smoothing | Self-adjusting MA |
| TEMA (Triple EMA) | Trend | period | Triple-smoothed EMA |
| Trix | Momentum | period | Rate of change of triple EMA |
| VIDYA | Adaptive | period, CMO | Volatility-indexed MA |

### Professional Note
Trend indicators are lagging by mathematical necessity. They identify trends AFTER they exist. The edge comes not from the indicator but from: regime filtering (avoiding chop), risk management (surviving whipsaws), and portfolio construction (diversifying across uncorrelated trend-following systems).

---

## Category 2: Momentum Indicators (30)

Momentum indicators measure the rate of price change.

| Indicator | Type | Params | Notes |
|---|---|---|---|
| RSI (Relative Strength Index) | Momentum | period(14) | Normalized 0-100 |
| Stochastic RSI | Momentum | RSI period, Stoch period | RSI of RSI |
| True Strength Index (TSI) | Momentum | short(13), long(25), signal(13) | Double-smoothed momentum |
| Rate of Change (ROC) | Momentum | period | Percentage price change |
| Momentum Oscillator | Momentum | period | Absolute price change |
| Williams %R | Momentum | period(14) | Overbought/oversold |
| Commodity Channel Index (CCI) | Momentum | period(20) | Deviation from mean |
| Fisher Transform | Momentum | period | Normalizes to Gaussian |
| Know Sure Thing (KST) | Momentum | 10,15,10,15,9,9 | Double-smoothed ROC |
| Price Oscillator (PPO) | Momentum | 12,26,9 | Percentage MACD |
| Relative Vigor Index (RVI) | Momentum | period(10) | Close vs open momentum |
| Ultimate Oscillator | Momentum | 7,14,28 | Multi-timeframe momentum |
| Chaikin Oscillator | Momentum | 3,10 | ADL momentum |
| Schaff Trend Cycle | Momentum | 10,23,10 | MACD + Stochastic hybrid |
| QStick | Momentum | period | Close-open MA |
| Coppock Buy Signal | Momentum | derived | Zero-cross signal |
| Ehler's RVI | Momentum | period | Smoothed RVI |
| Ehler's Stochastic RSI | Momentum | various | Smoothed StochRSI |
| Momentum Divergence | Momentum | custom | Price/momentum divergence |
| Price Momentum Indicator | Momentum | period | Simple momentum |
| ROC Rate Indicator | Momentum | period, threshold | Threshold-based ROC |
| Speed Resistance Lines | Momentum | derived | Acceleration measure |
| Trend Intensity Index | Momentum | period | Bull/bear momentum ratio |
| Volume Rate of Change | Momentum | period | Volume momentum |
| DeMark Sequential | Momentum | complex | Counting-based exhaustion |
| DeMark Combo | Momentum | derived | Sequential variant |
| Ehler's Cyber Cycle | Momentum | alpha | Cyclical momentum |
| Ehler's Leading Indicator | Momentum | various | Predictive momentum |
| Gains-Losses Oscillator | Momentum | period | Gain/loss ratio |
| Momentum Ranking | Momentum | cross-sectional | Cross-sectional momentum |

### Professional Note
Momentum is the most studied anomaly in academic finance. Simple momentum (12-1 month) has robust cross-asset evidence. The retail usage of RSI/Stochastic as "overbought=sell" is NOT validated. Momentum works through cross-sectional ranking and proper holding periods, not oscillator crossovers.

---

## Category 3: Volatility Indicators (20)

| Indicator | Type | Params | Notes |
|---|---|---|---|
| Average True Range (ATR) | Volatility | period(14) | Average price range |
| Bollinger Bands | Volatility | period(20), std(2) | MA ± standard deviations |
| Bollinger Band Width | Volatility | derived | BB squeeze/expansion |
| %B | Volatility | derived | Position within BB |
| Standard Deviation | Volatility | period | Price volatility |
| Historical Volatility | Volatility | period | Annualized std dev |
| Implied Volatility (IV) | Volatility | options | Market expectation |
| IV Rank | Volatility | derived | IV percentile over lookback |
| IV Percentile | Volatility | derived | Alternative IV measure |
| VIX | Volatility | index | S&P 500 implied vol |
| Volatility Cone | Volatility | multiple periods | Realized vol distribution |
| Keltner Channel | Volatility | period(20), ATR mult | MA ± ATR |
| Donchian Channel | Volatility | period | Highest high / lowest low |
| Ulcer Index | Volatility | period | Drawdown-focused vol |
| Chaikin Volatility | Volatility | period | Range expansion |
| Volatility Ratio | Volatility | short, long | Short vs long term vol |
| Normalized ATR | Volatility | period | ATR normalized by price |
| Average Daily Range | Volatility | period | Daily range avg |
| GARCH Volatility | Volatility | P, Q | Conditional vol model |
| Realized Volatility | Volatility | period | Sum of squared returns |

---

## Category 4: Volume Indicators (25)

| Indicator | Type | Params | Notes |
|---|---|---|---|
| Volume | Raw | - | Raw trading volume |
| On-Balance Volume (OBV) | Cumulative | derived | Cumulative volume |
| Volume-Weighted Average Price (VWAP) | Average | session | Intraday VWAP |
| VWAP Bands | Volatility | derived | VWAP ± std |
| Anchored VWAP | Average | anchor point | Volume avg from specific point |
| Money Flow Index (MFI) | Momentum | period(14) | Volume-weighted RSI |
| Volume Profile | Distribution | period | Volume at price levels |
| Volume Oscillator | Momentum | short, long | Volume MA difference |
| Ease of Movement (EOM) | Volume | period(14) | Price movement vs volume |
| Negative Volume Index (NVI) | Trend | derived | Volume-decrease days |
| Positive Volume Index (PVI) | Trend | derived | Volume-increase days |
| Chaikin Money Flow (CMF) | Flow | period(20) | ADL-based flow |
| Accumulation/Distribution Line (ADL) | Cumulative | derived | Volume-based flow |
| Force Index | Momentum | period(13) | Price change × volume |
| Volume Flow Indicator (VFI) | Flow | period | Zero-centered volume flow |
| Klinger Oscillator | Flow | 34, 55, 13 | Volume-driven trend |
| Volume Price Trend (VPT) | Trend | derived | Volume × price change |
| Accumulation Swing Index | Volume | derived | Accumulation measure |
| Chaikin AD Oscillator | Flow | 3, 10 | ADL oscillator |
| On-Balance Volume SMA | Trend | period | Smoothed OBV |
| Volume-Weighted MA | Average | period | Volume-weighted SMA |
| Tick Volume | Raw | - | Number of trades |
| Cumulative Delta | Flow | session | Buy-sell volume difference |
| Volume Rate of Change | Momentum | period | Volume momentum |
| Volume Profile POC | Level | derived | Point of control |

---

## Category 5: Support/Resistance & Structure Indicators (20)

| Indicator | Type | Notes |
|---|---|---|
| Pivot Points (Standard) | Support/Resistance | Floor pivots |
| Pivot Points (Fibonacci) | Support/Resistance | Fib retracement pivots |
| Pivot Points (Camarilla) | Support/Resistance | Camarilla levels |
| Pivot Points (Woodie) | Support/Resistance | Woodie modification |
| Fibonacci Retracement | Support/Resistance | Key ratios |
| Fibonacci Extension | Levels | Price targets |
| Fibonacci Fan | Levels | Angular support/resistance |
| Fibonacci Arc | Levels | Curved support/resistance |
| Pivot Point Support/Resistance | Levels | S1-S3, R1-R3 |
| Swing High/Low | Levels | Local extrema |
| Support/Resistance Zones | Levels | Price clusters |
| Market Profile (TPO) | Distribution | Time at price |
| Value Area High/Low | Levels | 70% value area |
| Point of Control (POC) | Level | Most traded price |
| Composite POC | Level | Multi-session POC |
| Moving Average Support | Dynamic | MA as support |
| Previous Day High/Low | Levels | Reference levels |
| Supply/Demand Zones | Levels | Imbalance zones |
| Order Block | Level | Pre-impulse candle range |
| Fair Value Gap (FVG) | Level | Imbalance gap |

### ICT/SMC Note
Fair Value Gap, Order Block, Breaker Block, and liquidity concepts are retail pattern language from ICT/SMC. They are not institutional terminology and have no academic anchor. They may describe real phenomena (order book imbalances, liquidity pools) but must be translated into testable, quantitative definitions before they become strategies. See [[Professional Equivalent Map]] for mappings to professional concepts.

---

## Category 6: Oscillators (20)

| Indicator | Type | Params | Notes |
|---|---|---|---|
| RSI | Momentum | period(14) | Normalized momentum |
| Stochastic %K/%D | Momentum | 14,3,3 | Position in range |
| Stochastic RSI | Momentum | derived | Stochastic of RSI |
| CCI | Momentum | period(20) | Deviation from mean |
| Williams %R | Momentum | period(14) | Inverted stochastic |
| Awesome Oscillator | Momentum | 5,34 | Histogram of MA diff |
| Balance of Power | Flow | period(14) | Buyer/seller balance |
| Center of Gravity | Oscillator | period | Weighted average price center |
| Coppock Curve | Momentum | 11,14,10 | Long-term momentum |
| DeMarker | Momentum | period(14) | DeMark oscillator |
| Detrended Price Osc | Cycle | period | Cycle extraction |
| Ehler's Stochastic | Oscillator | various | Smoothed stochastic |
| Fisher Transform | Oscillator | period | Gaussian transform |
| Gator Oscillator | Oscillator | derived | Alligator component |
| IBS (Inside Bar Strength) | Oscillator | 1 bar | Close position in bar |
| Momentum Oscillator | Momentum | period | Price rate of change |
| Price Oscillator | Momentum | 12,26,9 | MACD variant |
| QStick | Momentum | period | Close-open ratio |
| ROC | Momentum | period | Rate of change |
| TRIX | Momentum | period | Triple-smoothed ROC |

---

## Category 7: Cycle Indicators (15)

| Indicator | Type | Notes |
|---|---|---|
| Ehler's Dominant Cycle | Cycle | Identifies primary cycle |
| Ehler's Instantaneous Trendline | Cycle | Adaptive trend extraction |
| Ehler's MESA | Cycle | Cycle analysis |
| Ehler's Homodyne | Cycle | Differentiation filter |
| Ehler's Sine Wave | Cycle | Leading/lagging sine |
| Hilbert Transform | Cycle | Phase analysis |
| Moving Average Convergence | Cycle | MACD variant |
| Price Cycles | Cycle | Cycle detection |
| Time Cycle | Cycle | Temporal analysis |
| Cycle Identifier | Cycle | Primary cycle length |
| Sinewave Indicator | Cycle | Cycle oscillation |
| Center of Gravity | Cycle | Price center oscillation |
| Fisher Inverse | Cycle | Inverse Fisher transform |
| Band Pass Filter | Cycle | Frequency isolation |
| Gaussian Filter | Cycle | Smoothed extraction |

---

## Category 8: Market Breadth Indicators (15)

| Indicator | Type | Notes |
|---|---|---|
| Advance-Decline Line | Breadth | Cumulative A-D |
| Advance-Decline Ratio | Breadth | A/D ratio |
| Arms Index (TRIN) | Breadth | Volume-weighted A/D |
| McClellan Oscillator | Breadth | EMA of net advances |
| McClellan Summation | Breadth | Cumulative McClellan |
| New Highs - New Lows | Breadth | 52-week high/low diff |
| Up/Down Volume Ratio | Breadth | Volume breadth |
| Advance-Decline Volume | Breadth | Volume-weighted A/D |
| Bullish Percent Index | Breadth | % above signal |
| Percent Above MA | Breadth | % above moving average |
| Equal Weight Index vs Cap-Weight | Breadth | Breadth divergence |
| VIX/VXV Ratio | Sentiment | Term structure sentiment |
| Put/Call Ratio | Sentiment | Options sentiment |
| High-Low Index | Breadth | Normalized H-L difference |
| Breadth Thrust | Breadth | Rapid breadth improvement |

---

## Category 9: Sentiment & Positioning Indicators (12)

| Indicator | Type | Notes |
|---|---|---|
| VIX | Volatility/Sentiment | Fear gauge |
| VVIX | Vol of Vol | VIX volatility |
| Put/Call Ratio | Options sentiment | Total or equity-only |
| COT (Commitment of Traders) | Positioning | Futures positioning |
| COT Net Position | Positioning | Net commercial/speculative |
| Fear Greed Index | Sentiment | CNN composite |
| AAII Sentiment Survey | Sentiment | Retail sentiment |
| Insider Buying/Selling | Positioning | SEC filings |
| Short Interest Ratio | Positioning | % short float |
| Margin Debt | Positioning | Leverage indicator |
| Fund Flows | Positioning | ETF/mutual fund flows |
| Social Media Sentiment | Sentiment | NLP-based |

---

## Category 10: Statistical & Derived Indicators (18)

| Indicator | Type | Notes |
|---|---|---|
| Z-Score | Statistical | Normalized deviation |
| Cointegration Test | Statistical | Long-run relationship |
| Correlation Coefficient | Statistical | Linear relationship |
| Beta | Statistical | Market sensitivity |
| Alpha | Statistical | Excess return |
| Sharpe Ratio | Risk/Return | Risk-adjusted return |
| Sortino Ratio | Risk/Return | Downside-adjusted return |
| Calmar Ratio | Risk/Return | Return/drawdown |
| Maximum Drawdown | Risk | Peak-to-trough |
| Value at Risk (VaR) | Risk | Tail risk measure |
| Expected Shortfall | Risk | CVaR |
| Autocorrelation | Statistical | Self-correlation |
| Hurst Exponent | Statistical | Trending vs mean-reverting |
| Skewness | Statistical | Distribution asymmetry |
| Kurtosis | Statistical | Tail thickness |
| Linear Regression Slope | Statistical | Trend slope |
| Linear Regression R² | Statistical | Fit quality |
| Information Coefficient | Statistical | Prediction accuracy |

---

## Redundancy Map

### High Redundancy (Use One, Not All)
- **SMA, EMA, WMA, DEMA, TEMA** → All are weighted averages. EMA already accounts for recency. Multiple MAs = not diversification.
- **RSI, Stochastic, Williams %R** → All measure position in recent range. RSI is more robust.
- **MACD, PPO, MACD Histogram** → All derive from EMA convergence. MACD is canonical.
- **ATR, Standard Deviation, Historical Volatility** → All measure volatility. ATR handles gaps better.
- **OBV, CMF, ADL, MFI** → All volume-based flow measures. OBV is simplest, MFI adds price normalization.

### Complementary (Can Combine)
- Trend + Volatility filter (e.g., ADX trend + ATR position sizing) ✓
- Momentum + Mean reversion filter (e.g., RSI in trend direction only) ✓
- Volume + Price structure (e.g., VWAP + support levels) ✓

### Redundancy Trap
Using 5 trend indicators that all confirm the same trend does NOT increase confidence. It increases confirmation bias. Each indicator in a system should measure a DIFFERENT property of the market.

---

## Indicator Failure Modes

### Look-Ahead Bias
Indicators that use future data (e.g., repainting indicators) create false signals. Always verify: does the indicator value at time t use data only available at time t?

### Repainting / Recalculating Indicators
Some indicators recalculate their past values as new data arrives. ZigZag, Supertrend (some implementations), and fractal-based indicators are known repainters.

### Parameter Overfitting
Optimizing indicator parameters (RSI period, BB standard deviations) on historical data creates a curve-fit strategy. Use walk-forward optimization or parameter stability tests.

### Regime Dependency
Indicators perform differently across market regimes. Trending indicators fail in ranging markets; mean-reversion indicators fail in trending markets. Regime filtering is essential.

### Multicollinearity
Using correlated indicators (e.g., RSI + Stochastic + Williams %R) creates false diversification. Apply feature selection to remove redundant inputs.

---

## Anti-Cookie-Cutter Insight

The most common retail mistake is "indicator stacking" — loading 10 indicators onto a chart and waiting for them to all agree. This is analysis paralysis, not edge creation. Professional quants use 2-4 well-chosen features per model. The edge is in hypothesis quality, risk management, and validation rigor — not indicator count.

---

## Cross-References
- [[Schema and Taxonomy]] — Strategy card schema (field 13: indicators_used)
- [[Validation Framework]] — Testing indicator-based hypotheses
- [[Failure Mode Catalog]] — Overfitting, regime dependency, redundancy failures
- [[Feature Engineering Catalog]] — Transforming indicators into ML features
- [[Professional Equivalent Map]] — Retail indicators → professional features
- [[Master Index]] — Full encyclopedia overview
