# Aggregated Data Tactics

Aggregated data is high-level data that compresses many raw observations into decision-useful features. It is useful, but dangerous: aggregation hides timing, missingness, survivorship, and leakage.

## Useful aggregated data families

| Family | Examples | Best use |
|---|---|---|
| Multi-timeframe price | 1m/5m/1h/daily/weekly features | trend, mean reversion, volatility regime |
| Cross-asset | SPY, QQQ, VIX, rates, dollar, oil, gold | regime filters and risk-on/risk-off context |
| Market breadth | advancers/decliners, % above moving average | equity market participation |
| Volume/liquidity | relative volume, dollar volume, spread, depth | execution feasibility and signal confirmation |
| Order flow | imbalance, aggressor volume, book pressure | microstructure edge, short-horizon execution |
| Options-derived | IV rank, skew, term structure, put/call ratios | volatility and dealer-positioning context |
| Macro | CPI, jobs, rates, PMIs, liquidity, credit spreads | regime classification and event avoidance |
| Holdings/13F | delayed institutional holdings, crowding | longer-horizon positioning and clone studies |
| Sentiment/news | headlines, transcripts, social, search trends | event/risk overlay; requires strict timestamp control |
| Crypto flows | funding, open interest, liquidations, exchange reserves | leverage-cycle and liquidation-risk signals |

## Aggregation rules

1. Record exact source timestamp.
2. Record exact release timestamp for macro/fundamental data.
3. Never use revised values unless testing with revised-data assumptions explicitly.
4. Use lag buffers for scraped or delayed sources.
5. Compare raw vs aggregated data drift.
6. Check if aggregation creates hidden look-ahead.

## High-level tactical uses

### 1. Regime gate

Trade a strategy only when the macro/volatility/liquidity regime matches the strategy's edge.

Examples:

- Momentum only when market breadth is broad.
- Mean reversion only when realized volatility is below threshold.
- Breakouts only when relative volume confirms.

### 2. Exposure throttle

Scale position size based on aggregate risk state.

Examples:

- Reduce gross exposure when VIX or realized volatility spikes.
- Reduce single-name exposure around earnings.
- Reduce crypto leverage when funding and open interest are extreme.

### 3. Signal confirmation

Use aggregated data as a second layer, not the primary reason to trade.

Examples:

- Long signal requires price momentum plus positive sector breadth.
- Short-volatility strategy requires stable realized volatility and no macro event block.

### 4. Weak-point diagnosis

After each epoch, segment results by aggregated features:

- High vs low volatility
- High vs low spread
- High vs low volume
- Bull vs bear market
- Before vs after macro events
- Trend vs chop regimes
