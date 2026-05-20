# Heatmap Diagnostics Overview

**Source**: `06_heatmaps_diagnostics/heatmap_playbook.md`

## Key Concepts

Heatmaps expose fragility faster than summary metrics. While a single Sharpe number can hide all the weaknesses of a strategy, a heatmap immediately reveals where performance is concentrated, fragile, or non-existent.

## Required Heatmaps

| Heatmap | X-axis | Y-axis | Cell Value |
|---|---|---|---|
| Parameter stability | parameter 1 | parameter 2 | Sharpe / CAGR / max DD / expectancy |
| Regime performance | volatility bucket | trend bucket | after-cost return |
| Symbol performance | symbol | month/quarter | PnL or Sharpe |
| Time performance | hour/day/month | regime | PnL/trade or hit rate |
| Cost sensitivity | slippage multiplier | spread multiplier | expectancy |
| Trade failure | entry reason | exit reason | PnL or loss rate |
| Execution quality | symbol | order type | slippage / fill rate |
| Feature drift | feature | month | PSI or KS statistic |

## What to Reject

- A parameter map where only one cell works.
- A strategy whose PnL is concentrated in one symbol.
- A strategy that dies under 2x slippage.
- A strategy with good Sharpe but terrible time-under-water.
- A signal whose IC vanishes outside one regime.

## Implications

1. **Heatmaps are a rejection tool first**: Their primary value is telling you what NOT to deploy, not what to deploy.
2. **Multiple heatmaps are required**: No single heatmap can catch all failure modes. At minimum, run parameter stability, regime, slippage, and instrument.
3. **Cell-level statistical significance matters**: Heatmap cells with fewer than 10-20 observations should be flagged as low-confidence.
4. **Heatmaps should be re-run periodically in live trading**: Live data reveals whether backtest heatmap patterns hold.

## Failure Modes / Misinterpretations

- **Heatmap resolution too low**: Coarse grids miss important detail; fine grids create noisy cells. Start with moderate resolution and refine.
- **Color scale manipulation**: Using a color scale optimized to show green cells can hide the magnitude of variation. Always show the scale.
- **Static heatmaps**: Market dynamics change. A heatmap from 2020-2021 may not represent 2024-2025. Update regularly.
- **Single-metric coloring**: Coloring cells only by Sharpe hides drawdown information. Use multiple metrics or composite scores.

## Cross-Links

- [[Heatmap-Parameter]] for parameter sweep methodology
- [[Heatmap-Time-Regime]] for regime and temporal analysis
- [[Heatmap-Slippage]] for execution stress testing
- [[Heatmap-Instrument]] for symbol and sector analysis
- [[Heatmap-Trade-Failure]] for trade-level diagnostics
- [[Overfit-Detection-Metrics]] for the anti-overfit protocol that requires heatmap reporting
- [[Execution-Metrics]] for the execution quality dimension
