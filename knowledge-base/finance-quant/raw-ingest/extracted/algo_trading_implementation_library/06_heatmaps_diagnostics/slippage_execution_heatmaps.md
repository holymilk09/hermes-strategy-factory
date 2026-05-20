# Slippage and Execution Heatmaps

## Views

- Symbol x order type -> slippage
- Symbol x time of day -> slippage
- Volatility bucket x spread bucket -> implementation shortfall
- Order size bucket x liquidity bucket -> fill rate
- Broker/venue x symbol -> reject rate

## Execution promotion rule

A backtest candidate does not move to live until execution assumptions are stress-tested against worse-than-observed slippage.
