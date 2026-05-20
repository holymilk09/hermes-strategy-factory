# Event Loop and State Machine

**Source**: `algo_trading_implementation_library/00_core_bot_structure/event_loop_and_state_machine.md`

---

## Core Concept

The trading bot operates as an **event-driven finite-state machine**. The event loop dispatches discrete event types, each triggering a specific, bounded sequence of actions:

| Event Handler | Trigger | Pipeline Step |
|---------------|---------|---------------|
| `on_start` | Bot launch | Load config → load state → reconcile broker → subscribe data |
| `on_market_data` | New tick/bar/book | Update features → generate signal → build portfolio → risk veto/clip → generate orders → submit/cancel/replace → log decision |
| `on_order_update` | Broker order status change | Update order state → validate transition → log broker event |
| `on_fill` | Broker fill notification | Update ledger → update position → update cash → update risk state → log fill |
| `on_timer` | Scheduled heartbeat | Heartbeat → reconciliation → metric snapshot → risk checks |
| `on_stop` | Bot shutdown | Cancel unsafe orders → write final reports |

**Order State Machine** — valid transitions only:

```
NEW → SUBMITTED → ACKNOWLEDGED → PARTIALLY_FILLED → FILLED
                   ↓                      ↓
                   CANCEL_PENDING        CANCELLED
                   ↓
                   REJECTED
                   EXPIRED
```

**Invalid transitions** (must raise a system incident, never silently patch):
- `FILLED → CANCELLED`
- `REJECTED → FILLED`
- `CANCELLED → PARTIALLY_FILLED`
- `NEW → FILLED` (without broker acknowledgment in live mode)

---

## Implications for Trading Systems

- **Idempotency requirement**: Events can fire out of order or duplicate (network retries, broker re-sends). Each handler must be safe to re-execute without corrupting state.
- **Reconciliation as a safety net**: `on_timer` performs periodic reconciliation. Divergences between internal and broker state are caught here — but the window between reconciliations is a vulnerability.
- **Graceful degradation**: `on_stop` must cancel all open orders. If the cancel itself fails (network partition during shutdown), the system risks holding positions with no active management.
- **Deterministic ordering**: When `on_market_data` and `on_fill` fire simultaneously, the processing order matters. Processing a fill before a market data event may generate a stale signal.
- **State validation gates**: Invalid order transitions are treated as incidents. This means the order state machine doubles as an early warning system for broker API anomalies or internal bugs.

---

## Potential Failure Modes and Critiques

- **Event storm vulnerability**: A burst of market data (flash crash, high-vol regime) can flood `on_market_data` handlers faster than they complete, causing queue buildup and stale signals. No backpressure mechanism is defined in the architecture (cf. [[Failure-Mode-Taxonomy|Live-Failure]]).
- **Reconciliation gap**: If `on_timer` is 60s and a broker outage occurs, the system operates on stale positions for up to 60 seconds before detection.
- **Invalid transition masking**: If an invalid transition is logged as an incident but not halted, the bot continues trading with corrupted order state. The architecture requires a halting-on-incident policy.
- **State reconciliation races**: The `on_start` reconciliation assumes the broker is alive. If the broker is unreachable at startup, the system must decide: abort, or start with unknown positions.
- **Missing backout path**: If `on_market_data` crashes mid-pipeline (e.g., after generating orders but before submitting), orphaned orders may exist without ledger records.
- **Timer drift**: If `on_timer` handlers are blocked by long `on_market_data` processing, heartbeat gaps go unnoticed.

---

**Related**: [[Trading-System-Component-Architecture]] · [[Core-Module-Contracts]] · [[Failure-Mode-Taxonomy]]
