# Heatmap Diagnostics for Mean Reversion

## Required Diagnostic Heatmaps

A good MR system needs these:

1. PnL by residual_z bucket
2. PnL by RSI bucket
3. PnL by distance from VWAP
4. PnL by distance from 20 MA
5. PnL by market regime
6. PnL by VIX / volatility regime
7. PnL by sector
8. PnL by time of day
9. PnL by day of week
10. PnL by earnings proximity
11. PnL by gap size
12. PnL by volume spike
13. PnL by spread bucket
14. PnL by liquidity bucket
15. PnL by order-flow imbalance flip
16. PnL by stop distance
17. PnL by time-to-reversion

## Most Useful Heatmap (Build This First)

```
x-axis: deviation_z
y-axis: reclaim_strength
cell: median forward return / expectancy
```

**Key insight**: If high deviation WITHOUT reclaim loses money → the system learns that stretch alone is not enough. This is the single most important diagnostic.

## What This Would Show For Our Current Engine
We don't have reclaim_strength. We don't have deviation_z (we have RSI).
We CAN'T build the most important diagnostic because we lack the right features.

**This is diagnostic debt** — the engine can't tell us WHY trades fail because it doesn't track the right variables.

## Cross-Links
- [[05-Risk-Portfolio-Execution/Heatmap-Playbook-Diagnostics]] — master heatmap framework
- [[02-Deviation-Scoring]] — deviation measures for x-axis
- [[04-Exhaustion-And-Reclaim]] — reclaim signals for y-axis
