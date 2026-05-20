# LEAN Live Trading Operations

Live trading operational checklist and paper/live difference guidelines for LEAN deployments.

## Core Concepts

- **Live state management:** Before any live trading begins, all system state must be reconciled with the broker.
- **Required live-state checks:**
  - Broker connected and authenticated
  - Market data connected and streaming
  - Open orders reconciled with broker
  - Positions reconciled with broker
  - Cash and margin reconciled
  - Risk limits loaded and enforced
  - Kill switch tested and operational
  - Heartbeat emitting and monitored
- **Paper vs live divergence:** Paper trading environments produce overly clean fills that do not reflect live market conditions.

## Paper/Live Difference Checklist

| Paper Trading | Live Trading |
|---|---|
| Paper fills are often too clean — instant fill at signal price | Fills happen at actual market prices with spread, slippage, and queue position |
| Paper may not reproduce partial fills | Partial fills are common, especially for larger orders or less liquid instruments |
| API rate limits may not be enforced | API rate limits still matter and will cause order delays or rejections if violated |
| Orders rarely get rejected in normal conditions | Live rejected orders reveal invalid assumptions about order validity, market state, or account |
| Slippage is modeled mathematically | Slippage must be measured from actual fills, not guessed from models |

## Implications

- The startup reconciliation checklist is non-optional. Starting live trading without reconciled positions causes duplicate orders or wrong position calculations.
- Paper trading is useful for smoke-testing logic (does the strategy place orders correctly?), but it cannot validate execution quality.
- The kill switch is the most important safety mechanism: it must be tested before live deployment. If the strategy goes into a loop or malfunctions, the kill switch is the only fast stop.
- Slippage measurement in live trading feeds back into backtest model calibration: update your fill models with actual live slippage data.
- Heartbeat monitoring enables external process supervision. If the heartbeat stops, assume the strategy is dead or in an unknown state.

## Failure Modes

- **Stale positions on restart:** If the system restarts and does not reconcile positions, it will compute wrong targets and may double-down on existing positions or close them inadvertently.
- **Paper-to-live shock:** Strategies that work flawlessly in paper often degrade significantly in live due to fill quality, slippage, partial fills, and rejections [[LEAN-Backtesting-Gotchas]].
- **Kill switch untested:** A kill switch that hasn't been tested is not a kill switch — it's a placebo. Test it during paper trading before going live.
- **Rate limit cascade:** If rate limits are hit, orders queue up, the strategy logic continues generating more orders, and you hit a cascade where the system's internal state diverges from the broker state.
- **Heartbeat false alarms:** Network jitter or API latency may cause transient heartbeat gaps. Design heartbeat monitoring with grace periods.
- **Missing risk limits:** If risk limits are not loaded on startup, there is no safety net for position sizing or exposure. Defaults should be conservative.

## Cross-Links

- [[LEAN-Reference]] — LEAN platform index
- [[LEAN-Local-Backtesting]] — validate strategies locally before going live
- [[LEAN-Backtesting-Gotchas]] — gotchas that will surprise you when backtest goes live
- [[Broker-API-Comparison]] — broker-specific operational considerations
- [[Execution-Metrics]] — measure live execution quality vs backtest assumptions
- [[Risk-Metrics]] — risk limits that must be loaded on startup
- [[NautilusTrader-Reference]] — NautilusTrader formalizes many of these live ops patterns
