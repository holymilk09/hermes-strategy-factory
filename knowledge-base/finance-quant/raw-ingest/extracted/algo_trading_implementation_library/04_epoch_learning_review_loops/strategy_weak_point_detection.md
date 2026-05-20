# Strategy Weak-Point Detection

## Weak-point categories

| Category | Detection method |
|---|---|
| Parameter fragility | parameter heatmap cliff, low neighborhood stability |
| Regime fragility | poor performance in volatility/liquidity/trend buckets |
| Symbol concentration | PnL dominated by few instruments |
| Time concentration | PnL dominated by month/day/session bucket |
| Trade concentration | top 5 trades explain most profit |
| Cost fragility | edge disappears after higher slippage/spread |
| Execution fragility | high rejects, partial fills, live/paper slippage gap |
| Data fragility | quality flags correlate with profits |
| Model drift | feature distribution or signal IC changes over time |

## Weak-point score

```text
weakness_score =
  0.25 * parameter_fragility
+ 0.20 * regime_concentration
+ 0.15 * trade_concentration
+ 0.15 * cost_sensitivity
+ 0.10 * symbol_concentration
+ 0.10 * model_drift
+ 0.05 * data_quality_risk
```

Use as prioritization, not truth.
