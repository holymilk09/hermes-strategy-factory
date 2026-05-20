# Heatmap Slippage and Execution Playbook

Source: 06_heatmaps_diagnostics/slippage_execution_heatmaps.md, 06_heatmaps_diagnostics/heatmap_playbook.md

## Key Concepts

Slippage and execution heatmaps stress-test whether a strategy survives realistic execution conditions. Backtest execution assumptions are always optimistic.

### Views

- Symbol x order type -> slippage
- Symbol x time of day -> slippage
- Volatility bucket x spread bucket -> implementation shortfall
- Order size bucket x liquidity bucket -> fill rate
- Broker/venue x symbol -> reject rate

### Execution Stress Matrix

| Axis | Values | Purpose |
|---|---|---|
| X-axis | Slippage multiplier (1x, 2x, 3x, 5x, 10x) | Scale assumed execution costs |
| Y-axis | Spread multiplier | Widen spread to stress limit |
| Cell | Expectancy or Sharpe | Does the edge survive? |

### Promotion Rule

A backtest candidate does not move to live until execution assumptions are stress-tested against worse-than-observed slippage.

### Interpretation

- **Edge survives 2x slippage**: Reasonably robust.
- **Edge dies at 1.5x slippage**: Fragile. Likely pre-cost noise.
- **Sharpe drops but still positive**: May be viable with lower turnover or different order types.
- **Expectancy goes negative**: Reject. No edge after costs.

## Implications

1. **Use the promotion rule as a hard gate**: No exceptions. A strategy that fails at 2x slippage will fail in live trading where real slippage exceeds backtest averages.
2. **Slippage is regime-dependent**: High-volatility periods have much wider effective spreads. Stress-test your worst-vol buckets separately (see [[Heatmap-Time-Regime]]).
3. **Order type matters**: Market orders have lower fill risk but higher slippage. Limit orders have lower slippage but partial fill risk and queue position uncertainty.
4. **Broker/venue differences**: The same strategy can have different fill quality across brokers. Test on the actual broker/venue you will use live.

## Failure Modes / Misinterpretations

- **Uniform slippage assumption**: Applying a flat slippage value across all symbols, times, and regimes ignores microstructure reality. Use distributional slippage models.
- **Ignoring partial fills in stress testing**: Slippage stress tests that assume full fills overstate edge.
- **Backtest slippage from historical averages**: Historical average slippage is too optimistic for forward-looking tests. Use the tail of the slippage distribution.
- **Spread widening without order behavior change**: Widening spreads in a backtest without also reducing fill probability creates unrealistic fills.
- **Testing only one broker**: Fill quality varies by broker routing, venue selection, and internalization practices.

## Cross-Links

- [[Execution-Metrics]] for the full set of execution quality measures
- [[Performance-Metrics]] for the impact of slippage on returns
- [[Heatmap-Parameter]] for parameter sets that minimize slippage
- [[Heatmap-Instrument]] for symbol-specific execution quality
