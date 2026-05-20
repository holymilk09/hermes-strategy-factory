# Backtest Architecture

## Minimum event-driven components

```text
HistoricalDataFeed -> EventQueue -> Strategy -> Portfolio -> Risk -> ExecutionSimulator -> FillModel -> Ledger -> Metrics
```

## Why event-driven matters

Vectorized research is useful for fast exploration, but event-driven simulation is closer to live trading. Event-driven simulation forces timestamp order, order state, fills, cash, and position state to exist explicitly.

## Required simulation realism

- Commissions
- Spread
- Slippage
- Partial fills
- Order rejection
- Market holidays
- Corporate actions
- Delistings where relevant
- Position/cash/margin accounting
- Intrabar assumptions documented

## Backtest outputs

- Equity curve
- Trade ledger
- Order ledger
- Fill ledger
- Position ledger
- Cash ledger
- Metric pack
- Run manifest
- Quality report
- Review report
