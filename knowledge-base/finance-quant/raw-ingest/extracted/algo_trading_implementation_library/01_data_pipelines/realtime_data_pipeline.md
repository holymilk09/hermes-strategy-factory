# Realtime Data Pipeline

## Live feed requirements

- Heartbeat per venue/provider.
- Last message timestamp.
- Market-data latency measurement.
- Stale-data threshold.
- Reconnect policy.
- Replay-safe event ordering.
- Duplicate message handling.
- Out-of-order message handling.

## Live action policy

| Data condition | Action |
|---|---|
| Feed delayed but under threshold | continue and log warning |
| Feed stale over threshold | block new entries |
| Feed disconnected | cancel unsafe open orders if risk policy says so |
| Feed recovered | reconcile state before new orders |
| Out-of-order data | reject event or reorder deterministically |
| Price spike beyond guardrail | require secondary validation or risk veto |

## Live/research parity

Use the same feature calculation code for backtest and live. Differences should be limited to the data adapter and execution adapter.
