# High-Level Aggregated Data Tactics

## Best tactic stack

1. Primary signal: simple and directly tied to price/flow/valuation logic.
2. Regime gate: aggregated market condition decides whether to allow signal.
3. Exposure throttle: aggregated risk state adjusts size.
4. Execution filter: aggregated liquidity/spread state decides order type and max size.
5. Review segmentation: aggregated buckets explain where the strategy works/fails.

## Example stack

```text
Signal: 20-day trend + 3-day pullback
Regime gate: market breadth > 50% and realized volatility below threshold
Exposure throttle: reduce size when VIX/realized vol rises
Execution filter: skip if spread or volume is bad
Review: segment by breadth, volatility, spread, sector, month
```

## High-value aggregate features

- Realized volatility regime
- Market breadth
- Dollar volume percentile
- Spread percentile
- Sector momentum
- Cross-asset risk regime
- Options IV rank/skew
- Macro event calendar proximity
- Funding/open interest for crypto
- Institutional/crowding proxy for longer horizons
