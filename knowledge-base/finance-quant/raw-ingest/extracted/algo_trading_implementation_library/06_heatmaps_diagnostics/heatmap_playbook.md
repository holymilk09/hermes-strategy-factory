# Heatmap Diagnostics Playbook

Heatmaps expose fragility faster than summary metrics.

## Required heatmaps

| Heatmap | X-axis | Y-axis | Cell |
|---|---|---|---|
| Parameter stability | parameter 1 | parameter 2 | Sharpe / CAGR / max DD / expectancy |
| Regime performance | volatility bucket | trend bucket | after-cost return |
| Symbol performance | symbol | month/quarter | PnL or Sharpe |
| Time performance | hour/day/month | regime | PnL/trade or hit rate |
| Cost sensitivity | slippage multiplier | spread multiplier | expectancy |
| Trade failure | entry reason | exit reason | PnL or loss rate |
| Execution quality | symbol | order type | slippage/fill rate |
| Feature drift | feature | month | PSI or KS statistic |

## What to reject

- A parameter map where only one cell works.
- A strategy whose PnL is concentrated in one symbol.
- A strategy that dies under 2x slippage.
- A strategy with good Sharpe but terrible time-under-water.
- A signal whose IC vanishes outside one regime.
