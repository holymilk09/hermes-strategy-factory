# Data Pipeline Architecture

## Three data paths

| Path | Use | Required controls |
|---|---|---|
| Historical research | hypothesis discovery, exploration | raw snapshots, point-in-time features, anti-leakage rules |
| Backtest feed | deterministic simulation | fixed data version, calendar, corporate actions, symbol map |
| Live feed | execution and monitoring | heartbeat, latency checks, stale-data policy, reconnection |

## Canonical pipeline

```text
vendor adapter
  -> raw store
  -> schema validator
  -> timestamp normalizer
  -> symbol mapper
  -> corporate-action adjuster
  -> bar/tick/book aggregator
  -> quality checker
  -> feature calculator
  -> point-in-time feature store
  -> backtest/live consumer
```

## Storage design

- Raw vendor payloads: immutable.
- Normalized data: versioned.
- Features: timestamped and point-in-time.
- Run data: linked to `data_version` and `feature_version`.
- Quality reports: stored per dataset and per run.

## Mandatory metadata

- Source vendor
- Dataset name
- Ingest timestamp
- Market timestamp
- Time zone
- Symbol format
- Adjustment method
- Data version/hash
- Missing-data flags
- Corporate-action version
