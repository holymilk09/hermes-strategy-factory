# Broker API Comparison

Comparison of broker and exchange APIs, their strengths, weaknesses, and normalization requirements for building order adapters.

## Comparison Matrix

| Broker/API | Best Use | Weakness |
|---|---|---|
| **Interactive Brokers (IBKR)** | Broad asset access (stocks, options, futures, FX, bonds), serious retail/pro account routing | API complexity, TWS/IB Gateway operational overhead. Connection drops and gateway restarts are common. |
| **Alpaca** | Simple REST-first API for stocks/options/crypto; excellent developer experience | Coverage and routing limitations vs IBKR. Fewer asset classes, less mature order types. |
| **Coinbase Advanced** | Regulated US crypto access with clean API. Good for BTC/ETH and major alts. | Crypto-only. Venue-specific constraints on order types and rate limits. |
| **CCXT** | Multi-exchange crypto research/execution abstraction layer. Unified interface to 100+ exchanges. | Exchange-specific quirks and uneven feature support across the abstraction. Not all methods work on all exchanges. |
| **Tradier** | Options-oriented retail API with straightforward options chain access. | Requires careful order/chain handling. Less mature for equities/other asset classes. |

## Order Adapter Requirements

Any trading system that connects to brokers must implement a normalization layer. Required adapter functions:

- **Normalize order types:** Each broker supports different order types (market, limit, stop, stop-limit, trailing, OCO, bracket). Adapter must map a canonical internal order type to broker-specific format.
- **Normalize time-in-force:** Day, GTC, IOC, FOK, GTD, session-based — each broker uses different naming and behavior.
- **Normalize order status:** Map broker-specific order status strings/enums to a unified internal state machine (pending, open, partially_filled, filled, cancelled, rejected, expired).
- **Normalize errors:** Broker error codes and messages vary wildly. Adapter must translate errors into a canonical error taxonomy (insufficient_margin, market_closed, invalid_price, etc.).
- **Store broker order ID and client order ID:** Track both for reconciliation. The client order ID (your UUID) lets you identify your orders; the broker order ID is needed for modifications and status queries.
- **Reconcile open orders on startup:** Any system must query the broker for outstanding orders on startup and reconcile with internal state. This is non-optional — stale internal state causes duplicate orders or missed fills.

## Implications

- The order adapter is where most live-trading bugs live. Normalize aggressively at the boundary and keep internal logic broker-agnostic.
- IBKR's TWS/IB Gateway requires operational monitoring: auto-restart scripts, connection health checks, and reconnection handling.
- CCXT's abstraction is leaky: test every method on every exchange you use. Do not assume uniform behavior.
- Alpaca's simplicity is a double-edged: great for prototyping, but routing limitations may cause execution degradation for larger orders.

## Failure Modes

- **Stale positions/orders on restart:** If reconciliation is skipped on startup, the system enters with wrong position data. Always reconcile.
- **Order type mismatch:** Submitting a stop-limit where the broker only supports stop-market causes silent rejections or worse, market orders.
- **Rate limit violations:** Paper fills are clean, but live API rate limits still matter. Hitting rate limits mid-trade can leave orders in limbo.
- **Paper/live divergence:** Paper fills are too clean and may not reproduce partial fills, slip pages, or rejections. [[LEAN-Live-Trading-Ops]] for the full paper/live difference checklist.
- **Exchange-specific behavior in CCXT:** CCXT abstracts but doesn't erase exchange differences. Always test behavior end-to-end.

## Cross-Links

- [[Framework-Comparison-Selection]] — broker selection within framework context
- [[NautilusTrader-Reference]] — adapters as pluggable broker connectors
- [[LEAN-Live-Trading-Ops]] — live operational checklist including reconciliation
- [[Execution-Metrics]] — measure execution quality across brokers
- [[Order-Adapter-Design]] — pattern for building the normalization layer
- [[LEAN-Algorithm-Framework-Mapping]] — the broker.py module boundary
