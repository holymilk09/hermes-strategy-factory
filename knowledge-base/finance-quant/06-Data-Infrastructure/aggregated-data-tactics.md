# Aggregated Data Tactics

## Key Concepts

Aggregated data compresses many raw observations into decision-useful features. It is powerful but dangerous — aggregation hides timing, missingness, survivorship, and leakage.

### Useful Aggregated Data Families

| Family | Examples | Best Use |
|---|---|---|
| Multi-timeframe price | 1m/5m/1h/daily/weekly features | Trend, mean reversion, volatility regime |
| Cross-asset | SPY, QQQ, VIX, rates, dollar, oil, gold | Regime filters, risk-on/risk-off context |
| Market breadth | Advancers/decliners, % above MA | Equity market participation |
| Volume/liquidity | Relative volume, dollar volume, spread, depth | Execution feasibility, signal confirmation |
| Order flow | Imbalance, aggressor volume, book pressure | Microstructure edge, short-horizon execution |
| Options-derived | IV rank, skew, term structure, put/call ratios | Volatility and dealer-positioning context |
| Macro | CPI, jobs, rates, PMIs, liquidity, credit spreads | Regime classification, event avoidance |
| Holdings/13F | Delayed institutional holdings, crowding | Longer-horizon positioning |
| Sentiment/news | Headlines, transcripts, social, search trends | Event/risk overlay; requires strict timestamp control |
| Crypto flows | Funding, open interest, liquidations, exchange reserves | Leverage-cycle, liquidation-risk signals |

### The Tactic Stack Architecture

Aggregated data is used in four tactical patterns:

**1. Regime Gate** — Trade only when the macro/volatility/liquidity regime matches the strategy's edge.
- Momentum only when market breadth is broad
- Mean reversion only when realized volatility is below threshold
- Breakouts only when relative volume confirms

**2. Exposure Throttle** — Scale position size based on aggregate risk state.
- Reduce gross exposure when VIX or realized vol spikes
- Reduce single-name exposure around earnings
- Reduce crypto leverage when funding and OI are extreme

**3. Signal Confirmation** — Use aggregated data as a second layer, not the primary reason to trade.
- Long signal requires price momentum plus positive sector breadth
- Short-volatility strategy requires stable realized vol and no macro event block

**4. Weak-Point Diagnosis** — After each epoch, segment results by aggregated features:
- High vs low volatility
- High vs low spread
- High vs low volume
- Bull vs bear market
- Before vs after macro events
- Trend vs chop regimes

### Regime Feature Map

| Regime | Features | Strategy Implication |
|---|---|---|
| Low vol uptrend | Low realized vol, rising breadth, positive index momentum | Trend/pullback strategies may work |
| High vol downtrend | High realized vol, negative breadth, widening spreads | Reduce size, avoid mean reversion without stops |
| Choppy range | Low trend strength, mean-reverting returns | Mean-reversion possible, trend signals weak |
| Liquidity stress | Wide spreads, low depth, high volatility | Reduce order size, avoid market orders |
| Event regime | Macro/earnings/high news density | Block entries or lower exposure |

### Aggregation Rules

1. Record exact source timestamp
2. Record exact release timestamp for macro/fundamental data
3. Never use revised values unless testing revised-data assumptions explicitly
4. Use lag buffers for scraped or delayed sources
5. Compare raw vs aggregated data drift
6. Check if aggregation creates hidden look-ahead

## Implications for Real Trading Systems

- **Regime gates are the highest-leverage feature**: a mediocre signal in the right regime outperforms a great signal in the wrong regime
- **The tactic stack order matters**: primary signal → regime gate → exposure throttle → execution filter → review segmentation
- **Aggregated data should confirm, not lead**: used as a second opinion, not the primary reason to trade
- **Segmentation is diagnostic gold**: splitting PnL by regime, volatility, spread, etc. reveals hidden fragilities that aggregate metrics hide
- **Simplicity beats breadth**: 2-3 well-tested aggregated features outperform a dashboard of 10 weakly understood ones

## Failure Modes

- **Aggregation hides timing**: a "daily" feature computed at midnight using 16:15 data leaks 15 minutes into the next day
- **Revised data masquerading as first release**: macro datasets often store only the latest revision; if you don't track releases, you test on impossible data
- **Survivorship in alt data coverage**: sentiment databases often drop coverage for delisted stocks, making historical coverage appear better than it was
- **Circular regime features**: if the regime detector uses the same features as the signal, you're double-counting the same information
- **Aggregate feature dimensionality creep**: adding every aggregated feature available without a causal story inflates overfit risk
- **Regime hindsight bias**: using end-of-period regime labels to label training data when the regime was only clear in retrospect

## Cross-Links

- [[Data Pipeline Architecture]] — aggregated data flows through the quality checker and feature calculator stages
- [[Feature Store Design]] — cross-asset, macro, and regime features are feature classes in the store
- [[Regime Detection Features]] — the regime feature map drives the regime gate tactic
- [[Feature Leakage Prevention]] — aggregation is a primary source of hidden look-ahead; timestamp discipline is essential
- [[Model Drift Detection]] — regime drift is one of five drift types that trigger retraining
- [[Strategy Weak-Point Detection]] — aggregated features are used to segment and diagnose strategy fragility
