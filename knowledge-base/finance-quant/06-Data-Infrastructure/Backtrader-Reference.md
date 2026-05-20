# Backtrader Reference

Backtrader is a Python-based backtesting framework. It remains useful for learning and Python strategy prototyping but is not the default choice for a modern production-grade trading system.

## Core Concepts

- **Event-driven architecture:** Strategies react to market events (bars, trades) in chronological order.
- **Indicators:** Built-in technical indicators applied to data feeds; reusable across strategies.
- **Analyzers:** Post-run analysis modules that compute performance statistics (Sharpe, drawdown, trade lists).
- **Data feeds:** CSV files, Yahoo Finance, or broker APIs serve as data sources.
- **Strategy lifecycle:** `__init__`, `next`, `notify_order`, `notify_trade` hooks define the flow.

## Best Use Cases

- Learning event-driven backtesting concepts.
- Quick local backtests with simple strategies.
- Building reusable indicator/analyzers libraries.
- Strategy prototyping before moving to a production engine.

## Implications

- Excellent for understanding how event-driven backtesting works: order lifecycle, data alignment, trade notification.
- Indicators and analyzers are reusable artifacts you can port conceptual understanding to other frameworks.
- The mental model maps cleanly to [[LEAN-Reference]] strategy structure (OnData → trading decisions → order management).
- Treat it as a stepping-stone: graduate working ideas to a more robust framework for live trading.

## Failure Modes

- **Aging ecosystem:** Maintenance is sporadic. Dependency conflicts with newer Python/NumPy versions are common.
- **Weak production path:** No built-in reconciliation, live-state management, or multi-venue support. Production deployment requires significant bolt-on engineering.
- **Data quality assumptions:** CSV-based data feeds silently skip bad rows. No built-in schema validation or data-quality reporting.
- **Performance ceiling:** Pure Python event loop limits throughput on large datasets or high-frequency scenarios.
- **Broker integration limitations:** Limited to a small set of supported brokers, with varying maturity.

## Cross-Links

- [[Framework-Comparison-Selection]] — framework selection guide
- [[VectorBT-Reference]] — contrast with fast vectorized exploration
- [[NautilusTrader-Reference]] — contrast with production-grade event-driven architecture
- [[LEAN-Local-Backtesting]] — next-step validation workflow
- [[Trading-System-Component-Architecture]] — broader system architecture context
- [[Feature-Leakage-Prevention]] — common pitfalls that apply regardless of framework
