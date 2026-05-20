# Feature Engineering Catalog

> Catalog of 15 feature types for quantitative strategy development. Each feature type includes definition, construction method, leakage risks, and decay characteristics. This bridges the gap between raw data and [[Validation Framework]]-ready model inputs.

---

## Core Principle

**Features are the raw materials of ML strategies.** Good features capture market state, predict future returns, or encode risk. Bad features are noisy, leaked, or redundant. The feature engineering process determines the ceiling of what any model can learn — no model can create signal from noise.

---

## Feature 1: Price Returns

**Definition**: Normalized price change over a lookback window.
**Construction**: `R_t = (P_t - P_{t-n}) / P_{t-n}` for window n.
**Window variants**: 1-bar, 5-bar, 20-bar, 60-bar, 252-bar (daily).
**Timeframe scaling**: Use geometric returns for multi-bar: `ln(P_t / P_{t-n})`.

**Leakage risk**: NONE — using past prices only. Safe.
**Decay rate**: LOW — returns are the fundamental market data.
**Transformations**: Log returns, signed returns, absolute returns (for vol), rolling mean, rolling std.

**Notes**: Raw close-to-close returns. Cross-sectional ranking (z-score) removes trend bias.

---

## Feature 2: Momentum (Cross-Sectional)

**Definition**: Relative performance ranking across a universe of assets.
**Construction**: Rank assets by R_t-n to R_t. Assign z-scores or percentile ranks.
**Skip recent period**: Exclude most recent 1 week/month to avoid reversal effect.
**Lookback**: Typically 12-1 month momentum.

**Leakage risk**: LOW — ensure skip period and universe are contemporaneous.

**Decay rate**: MEDIUM — momentum factor has decayed but persists.
**Transformations**: Sector-neutral ranking, volatility scaling, residual momentum.

---

## Feature 3: Volatility Features

**Definition**: Measures of price or return dispersion.
**Construction**:
- Realized vol: `sqrt(sum(r_i^2))` over window
- ATR: rolling average of true range
- GARCH/PARCH modeled vol
- Parkinson vol: high-low based (more efficient)
- Yang-Zhang vol: open-to-close + high-low composite

**Leakage risk**: NONE if using past data only.
**Decay rate**: LOW — volatility clustering is a persistent feature.
**Transformations**: Log vol, vol-of-vol, vol spread (IV vs RV), vol regime.

---

## Feature 4: Volume Features

**Definition**: Trading activity measures.
**Construction**:
- Raw volume normalized by average volume: `V_t / mean(V_t-n:t-1)`
- Volume-price correlation: corr(price change, volume) over window
- Volume imbalance: (buy_vol - sell_vol) / total_vol
- VWAP deviation: `(P_t - VWAP_t) / VWAP_t`
- Volume trend: volume MA ratio (short/long)

**Leakage risk**: LOW — use point-in-time volume data. Be careful with session-end volume.

**Decay rate**: MEDIUM — volume patterns may decay with algorithmic trading.
**Transformations**: Relative volume, volume surge detection, volume profile weights.

---

## Feature 5: Order Flow Features

**Definition**: Microstructure-level trade flow measures.
**Data needed**: Tick data, order book (L2/L3).
**Construction**:
- Order Flow Imbalance (OFI): signed volume at best bid/ask changes
- Cumulative Volume Delta (CVD): running buy-sell difference
- Trade size distribution: mean, median, percentile of trade sizes
- Aggressor side: classify trades as buyer/seller initiated
- Order book slope: volume at each level of book
- Micro-price: volume-weighted mid price

**Leakage risk**: MEDIUM — tick data can have timing issues. Ensure proper timestamp alignment.
**Decay rate**: MEDIUM — order flow is competitive and decays with participation.

**Professional Note**: This is the most information-rich feature category for short-term strategies. It requires tick-level data and careful implementation.

---

## Feature 6: Technical Indicator Features

**Definition**: Mathematical transforms of price/volume data.
**Construction**: Compute indicator values. Use raw indicator, not binary signals.
**Examples**:
- RSI value (0-100) — NOT "RSI < 30 = signal"
- MACD line value — NOT "MACD crossover"
- ATR value — NOT "ATR > threshold"

**Leakage risk**: LOW if indicator is computed correctly. Check for repainting.
**Decay rate**: MEDIUM — indicator values as features work better than indicator signals because the model can find non-linear relationships.

**Key Insight**: Feed indicator values as FEATURES, not signals. Let the model decide how to combine them. An RSI of 72 might mean different things in different volatility regimes.

---

## Feature 7: Regime Features

**Definition**: Market state classification features.
**Construction**:
- Volatility regime: high/low based on rolling vol percentile
- Trend regime: ADX, MA slope, linear regression trend
- Range regime: low vol + no trend
- Risk-on/risk-off: breadth, credit spreads, VIX level
- HMM hidden states: probabilistic regime labels
- GARCH regime: conditional vol state

**Leakage risk**: MEDIUM — regime labels can leak if computed using future data. Use expanding window.

**Decay rate**: LOW — regimes are structural, not transient.
**Use**: As interaction features (momentum × trend_regime, vol × vol_regime).

---

## Feature 8: Cross-Asset Features

**Definition**: Spreads, ratios, and relationships between different assets.
**Construction**:
- Index vs component: asset return minus market return
- Sector relative: sector return minus market return
- Pairs: price ratio, spread, cointegration residual
- Futures curve: nearby vs next expiry (contango/backwardation)
- Yield curve: 2Y vs 10Y, 3M vs 10Y
- Currency carry: interest rate differential
- Commodity term structure: spot vs forward

**Leakage risk**: LOW if using contemporaneous prices from different assets.
**Decay rate**: MEDIUM — cross-asset relationships can shift.
**Professional Note**: Cross-asset features often capture structural relationships that single-asset features miss.

---

## Feature 9: Alternative Data Features

**Definition**: Non-price data sources.
**Types**:
- News sentiment: NLP-based polarity scores
- Social media: Twitter, Reddit sentiment and volume
- Web traffic: Google Trends, SimilarWeb
- Satellite data: parking lot fills, crop health
- Credit card data: consumer spending patterns
- ESG scores: environmental, social, governance ratings

**Leakage risk**: HIGH — alternative data often has publication delays, revisions, and restatements. Critical to use point-in-time versions.

**Decay rate**: HIGH — alternative data alpha decays quickly as more participants access it.
**Professional Note**: Most alternative data does NOT generate alpha. The cost often exceeds the benefit. Only a few (news sentiment, some credit card data) have demonstrated persistent outperformance.

---

## Feature 10: Calendar / Time Features

**Definition**: Temporal features encoding time-of-day, day-of-week, seasonal patterns.
**Construction**:
- Hour of day (intraday)
- Day of week
- Week of year
- Month of year
- Days until expiry (options/futures)
- Session indicator (Asia, London, NY)
- Pre/post earnings indicator
- Days to month-end (window dressing effect)

**Leakage risk**: NONE — time features are strictly exogenous.
**Decay rate**: HIGH — calendar anomalies decay as they become known.
**Professional Note**: Some calendar effects (January effect, turn-of-month, opening hour volatility) are well-documented but often disappear after transaction costs.

---

## Feature 11: Microstructure Features

**Definition**: Order book and execution-level features.
**Construction**:
- Bid-ask spread: `(ask - bid) / mid`
- Order book depth: volume at N levels from mid
- Order book imbalance: bid_volume / (bid_volume + ask_volume)
- Queue position: relative queue length at best level
- Trade-to-cancel ratio
- Latency: time from signal to fill
- Execution quality: VWAP fill vs arrival price
- Market impact: price movement from trade size

**Leakage risk**: MEDIUM — LOB data can have synchronization issues across exchanges.
**Decay rate**: LOW — microstructure patterns are persistent but competitive.

---

## Feature 12: Options-Derived Features

**Definition**: Features extracted from options data.
**Construction**:
- IV vs RV spread: implied minus realized volatility
- IV rank: percentile of current IV in historical range
- Volatility skew: difference in IV across strikes
- Put/call ratio: volume or open interest
- Open interest by strike
- Gamma exposure: dealer gamma position by strike
- Max pain: strike with maximum option writer pain
- Dispersion: index IV vs weighted component IV

**Leakage risk**: LOW — options data is time-stamped.
**Decay rate**: MEDIUM — vol surface patterns are competitive.

---

## Feature 13: Fundamentals Features

**Definition**: Company/instrument fundamental data.
**Construction**:
- Earnings surprise: EPS - expected EPS
- Revenue growth: YoY change
- P/E, P/B, EV/EBITDA ratios
- ROE, ROA, profit margin
- Free cash flow yield
- Debt/equity ratio
- Dividend yield
- Analyst estimate revisions

**Leakage risk**: HIGH — fundamental data is published with delay and often restated. Must use point-in-time databases. Avoid current-quarter data that may be estimated, not actual.

**Decay rate**: LOW — fundamental factors (value, quality) persist over long horizons.
**Professional Note**: Fundamental features work best with quarterly or annual rebalancing, not high-frequency trading.

---

## Feature 14: Sentiment / Positioning Features

**Definition**: Market participant positioning and sentiment.
**Construction**:
- COT net position: commercial vs speculative positioning
- Short interest ratio
- Fund flows: net inflows/outflows
- Margin debt levels
- Insider trading: net insider buying/selling
- Put/call ratio (options sentiment)
- VIX level and term structure
- Social media sentiment score

**Leakage risk**: MEDIUM — positioning data has publication lag (COT is weekly, reported Friday for Tuesday).

**Decay rate**: MEDIUM — sentiment signals are short-lived due to rapid adoption.

---

## Feature 15: Label / Target Engineering

**Definition**: How the prediction target is constructed.
**Construction**:
- Raw return: R_t+1, R_t+n, cumulative return over horizon
- Directional: sign(R_t+n), 1 if positive
- Triple-barrier labeling: hit take-profit OR stop-loss OR time barrier first
- Meta-labeling: first model predicts direction, second model predicts confidence
- Volatility-adjusted return: R_t+n / std(R)
- Excess return: R_t+n - benchmark return
- Cross-sectional ranking: relative performance across universe

**Leakage risk**: CRITICAL — labels must not use future information. The label for time t can only use data from t+1 onward, never from t or before.
**Decay rate**: N/A — this is the target, not a predictor.

**Professional Note**: Label construction is as important as feature engineering. Poor labels create impossible prediction tasks. Triple-barrier labeling from Advances in Financial Machine Learning is a professional-standard approach.

---

## Leakage Test Protocol

Every feature must pass these tests before deployment:

### Test 1: Temporal Leakage Check
- Verify feature at time t uses only data from t-1 or earlier
- No future price, future volume, future fundamentals
- Event-driven replay test: simulate signal generation as if live

### Test 2: Point-in-Time Data Check
- Fundamental data: publication date, not reporting date
- Revisions: use first-published value, not current revised value
- Alternative data: latency from source availability to signal availability

### Test 3: Feature-Target Independence
- Correlation between features and targets in OOS data should be consistent with IS data
- Sharp degradation suggests target leakage
- Permutation test: shuffle target, verify feature predictive power drops to zero

### Test 4: Cross-Validation Leakage
- Standard k-fold CV shuffles data — creates temporal leakage
- Must use time-series CV or purged k-fold (CPCV)
- Embargo period between train and test sets

### Test 5: Preprocessing Leakage
- Scaling, imputation, feature selection must be fit on training data ONLY
- Apply transformation to test data
- Pipeline: fit_transform on train, transform on test

---

## Feature Decay Monitoring

Features decay as more participants discover and trade on them. Monitor:

- **Information Coefficient (IC)**: Correlation between feature and forward returns. Track over rolling windows.
- **Rank IC**: Spearman correlation. More robust to outliers.
- **IC decay**: Plot IC over time. Look for declining trend.
- **Feature importance drift**: In ML models, track feature importance over rolling windows.
- **Signal half-life**: Time for feature predictive power to halve.

**When to act**: When IC drops below threshold (e.g., IC < 0.02 for daily data), the feature may have decayed below signal noise. Investigate and potentially replace.

---

## Feature Redundancy Analysis

Before adding features to a model:

1. **Correlation matrix**: Remove features with >0.8 correlation
2. **Variance Inflation Factor (VIF)**: Remove if VIF > 5
3. **Permutation importance**: In ML models, if permuting a feature doesn't change predictions, it's redundant
4. **PCA**: Reduce feature set to principal components
5. **Mutual information**: Detect non-linear redundancy

**Rule**: 10 non-redundant features > 50 redundant features.

---

## Anti-Cookie-Cutter Insight

**Feature engineering is where edge is created, not in model selection.** A simple linear model on great features will beat a deep neural network on bad features. The most common mistake is spending months tuning model hyperparameters while feeding the model garbage features. Spend 80% of your time on feature engineering, 20% on model tuning.

---

## Cross-References
- [[Schema and Taxonomy]] — Strategy card field 14: features_used
- [[Validation Framework]] — Leakage tests (Tests 5, 7)
- [[Failure Mode Catalog]] — Look-ahead bias (failure 2), data mining (failure 6)
- [[Indicator Catalog]] — Source of technical indicator features
- [[Professional Equivalent Map]] — Retail indicators → ML features
- [[Master Index]] — Full encyclopedia overview
