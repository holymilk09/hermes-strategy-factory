# Event Loop and State Machine

## Event-driven loop

```text
on_start
  -> load config
  -> load state
  -> reconcile broker
  -> subscribe data

on_market_data
  -> update feature cache
  -> generate signal
  -> build target portfolio
  -> risk veto/clip
  -> generate orders
  -> submit/cancel/replace
  -> log decision

on_order_update
  -> update order state
  -> validate transition
  -> log broker event

on_fill
  -> update ledger
  -> update position
  -> update cash
  -> update risk state
  -> log fill

on_timer
  -> heartbeat
  -> reconciliation
  -> metric snapshot
  -> risk checks

on_stop
  -> cancel unsafe orders
  -> write final reports
```

## Order state machine

```text
NEW -> SUBMITTED -> ACKNOWLEDGED -> PARTIALLY_FILLED -> FILLED
                         |                   |
                         |                   -> CANCEL_PENDING -> CANCELLED
                         -> REJECTED
                         -> EXPIRED
```

## Invalid transitions

- `FILLED -> CANCELLED`
- `REJECTED -> FILLED`
- `CANCELLED -> PARTIALLY_FILLED`
- `NEW -> FILLED` without simulated/broker acknowledgment in live mode

Invalid transitions should raise a system incident, not silently patch state.
