# Trading System Component Architecture

**Source**: `algo_trading_implementation_library/00_core_bot_structure/core_components.md` + `trading_system_component_map.csv`

---

## Core Concept

An algorithmic trading system is decomposed into **10 distinct layers**, each with a narrow responsibility and defined input/output contract. The architecture follows a unidirectional data-flow pipeline from raw market data to post-trade review:

| Layer | Responsibility | Core Tests |
|-------|---------------|------------|
| **1. Data Layer** | Raw ingestion, vendor adapters, timestamp normalization, symbol mapping, corporate actions, bar/tick/ob aggregation, quality checks, versioned storage | Schema validation, timestamp normalization, missing data flags |
| **2. Feature Layer** | Technical, volatility, volume/liquidity, cross-asset, macro/event features; regime labels; point-in-time snapshots | No future timestamps, feature reproducibility, drift checks |
| **3. Signal Layer** | Forecast scores, directional signals, relative-value signals, probability/confidence estimates, decay horizons | Known input fixture, reason-code coverage, no portfolio mutation |
| **4. Portfolio Construction** | Position sizing, target weights, capital allocation, rebalancing rules, correlation/exposure controls, leverage/margin rules | Position caps, cash constraints, correlation limits |
| **5. Risk Engine** | Max gross/net exposure, max position/daily loss/drawdown/leverage, sector/symbol caps, volatility targeting, kill-switch policy | Max loss, max size, max leverage, kill switch |
| **6. Execution Engine** | Order type selection, TIF, routing/broker selection, retry and cancel/replace, partial-fill handling, slippage/impact controls | Order state transitions, duplicate prevention, cancel/replace |
| **7. Broker Adapter** | Authentication, order submission/status sync, fills/positions/cash/margin retrieval, error normalization | Auth error, rejected order, partial fill, stale API |
| **8. Ledger** | Orders, fills, positions, cash, fees, borrow costs, margin, realized/unrealized PnL | Cash/position reconciliation, realized PnL calculation |
| **9. Metrics Engine** | Return, risk, drawdown, trade, execution, model, overfit, regime metrics | Known returns fixtures, formula validation |
| **10. Review & Learning** | Run comparison, weak-point detection, heatmaps, epoch learning, strategy decay review, incident review, promotion/rejection | Review schema, promotion criteria, failure labels |

The pipeline enforces **separation of concerns**: signals have no knowledge of portfolio state, portfolio construction has no knowledge of execution mechanics, and risk acts as a pure gating function between portfolio and execution.

---

## Implications for Trading Systems

- **Independent velocity**: Each layer can be iterated, backtested, or replaced without changing other layers. A new signal model requires zero changes to execution or risk.
- **Testability**: Every layer has a deterministic contract, enabling unit and integration tests at each boundary (see [[Core-Module-Contracts]]).
- **Auditability**: The [[Trading-System-Component-Architecture|Ledger]] provides a single source of truth for all financial state, decoupled from the decision-making layers.
- **Composability**: Strategies can share infrastructure — the same data layer feeds multiple signal engines, and the same risk engine gates multiple portfolios.
- **Kill-switch placement**: Risk sits *between* portfolio construction and execution, meaning it can veto any order before it hits the market, but cannot retroactively stop a sent order.

---

## Potential Failure Modes and Critiques

- **Leaky abstractions**: If the signal layer receives non-[[Failure-Mode-Taxonomy|Point-in-Time]] data (e.g., future-adjusted prices), the entire pipeline's results are invalid. This is the most common source of silent backtest inflation.
- **Coupling through shared state**: Components must communicate only through their defined contracts. Shared mutable state between layers (e.g., a global position dictionary) breaks testability and creates race conditions in the [[Event-Loop-and-State-Machine]].
- **Missing feedback loops**: The review layer depends on metrics, which depend on the ledger, which depends on the broker adapter. A broken link anywhere means the review layer receives garbage.
- **Versioning gaps**: If vendor data changes schema or corporate-action logic without version bumps, the data layer returns incorrect data that propagates silently through all downstream layers.
- **Scalability limits**: Each layer runs synchronously in the default pipeline. At scale, the feature layer may become a bottleneck unless caching and batching are introduced.

---

**Related**: [[Event-Loop-and-State-Machine]] · [[Core-Module-Contracts]] · [[Failure-Mode-Taxonomy]]
