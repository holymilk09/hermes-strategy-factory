# Heatmap Trade Failure Playbook

Source: 06_heatmaps_diagnostics/trade_failure_heatmaps.md, 06_heatmaps_diagnostics/heatmap_playbook.md

## Key Concepts

Trade failure heatmaps identify exactly which trade archetypes lose money. This allows targeted improvement by removing or resizing weak trade types, but only if the filter is knowable at entry time.

### Axes

- Entry reason code
- Exit reason code
- Holding period bucket
- MAE bucket (max adverse excursion)
- MFE bucket (max favorable excursion)
- Regime bucket
- Slippage bucket

### Cell Values

- PnL
- Loss rate
- Expectancy
- Average MAE
- Average MFE capture
- Stop-out rate

### Interpretation Rule

Identify which trade archetypes fail. Remove or resize weak archetypes ONLY after confirming the filter is knowable at entry time.

### Heatmap Construction

| Axis | Example Values |
|---|---|
| X-axis | Entry reason (breakout, mean-reversion, signal cross) |
| Y-axis | Exit reason (stop-loss, take-profit, time stop, signal reversal) |
| Cell | PnL, loss rate, expectancy |

Use additional dimensions by creating separate heatmaps for holding period, MAE, regime, or slippage.

## Implications

1. **Entry-exit matrix is the most actionable diagnostic**: It tells you exactly which signal/exit combinations work and which don't.
2. **High MAE with low MFE capture**: These trades are suffering from poor entry timing and/or poor exit timing.
3. **Stop-out rate by entry reason**: Some entry signals consistently trigger stops; these may represent false breakouts or noise entries.
4. **Regime-specific trade failures**: If trades fail only in high-vol regime, the strategy may need regime-dependent position sizing.
5. **Slippage bucket analysis**: Trades that are profitable with low slippage but losing with high slippage are candidates for limit orders or larger spreads.

## Failure Modes / Misinterpretations

- **Hindsight filtering**: Removing failing trade types based on post-hoc analysis (e.g., "I should have exited on day 3") is overfitting unless the exit condition was part of the original strategy.
- **Small sample per trade archetype**: If a particular entry/exit combination has only 5 trades, its loss rate is not statistically meaningful.
- **Ignoring trade interaction effects**: Removing one trade type may change the overall portfolio exposure in ways that reduce performance elsewhere.
- **Confounding MAE with stop placement**: High MAE may indicate stop levels are too tight, not that the entry is bad.
- **MFE capture penalizing trend-following**: MFE capture (realized pnl / MFE) is high for mean-reversion strategies but naturally lower for trend-following where the goal is to let winners run beyond their max favorable excursion.

## Cross-Links

- [[Execution-Metrics]] for execution quality by trade type
- [[Heatmap-Parameter]] for parameter sensitivity of trade types
- [[Heatmap-Time-Regime]] for regime-specific trade failures
- [[Performance-Metrics]] for overall expectancy and profit factor
- [[Overfit-Detection-Metrics]] for validating that removing trade types is not overfitting on trade-level noise
