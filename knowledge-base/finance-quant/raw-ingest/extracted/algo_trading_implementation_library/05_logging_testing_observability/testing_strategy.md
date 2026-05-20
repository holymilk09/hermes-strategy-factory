# Testing Strategy

## Test layers

| Test layer | Purpose |
|---|---|
| Unit tests | Indicators, features, signals, sizing, risk rules. |
| Contract tests | Validate schemas and module I/O. |
| Integration tests | Data -> signal -> target -> order -> fill -> ledger. |
| Regression tests | Known strategy output must not change unexpectedly. |
| Simulation tests | Broker reject, partial fill, stale data, API outage. |
| Statistical tests | Backtest metrics and validation logic. |
| Smoke tests | Start bot, no-op strategy, logs, report. |
| Paper/live tests | Compare paper assumptions to real broker behavior. |

## Unit test examples

- Rolling indicator on known fixture.
- No signal emitted if feature missing.
- Position sizing respects max position limit.
- Risk engine vetoes max drawdown breach.
- Order state machine rejects invalid transition.
- Ledger cash equals starting cash minus buys plus sells minus fees.
