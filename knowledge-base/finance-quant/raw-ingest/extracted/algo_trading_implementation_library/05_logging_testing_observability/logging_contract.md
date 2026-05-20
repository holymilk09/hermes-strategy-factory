# Logging Contract

## Required log streams

| Stream | Contents |
|---|---|
| `run_log` | run start/end, config, data versions, environment |
| `data_log` | source, timestamp, quality flags, gaps, anomalies |
| `feature_log` | feature version, calculation timestamp, nulls/drift |
| `signal_log` | signal score, reason codes, horizon, confidence |
| `risk_log` | approved/clipped/vetoed targets and reasons |
| `order_log` | submitted/cancelled/rejected/acknowledged orders |
| `fill_log` | fills, fees, slippage, venue |
| `position_log` | holdings, cash, exposure, leverage |
| `metric_log` | periodic performance/risk/execution metrics |
| `incident_log` | system failures, data errors, broker/API issues |
| `review_log` | human/agent review decisions |

## Minimum event fields

- `run_id`
- `timestamp`
- `event_type`
- `component`
- `severity`
- `payload`
- `hash_prev` if using audit chain

## Rule

Logs are part of the trading system. If a trade was not logged, it is not explainable.
