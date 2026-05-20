# Audit and Lineage

## Lineage chain

```text
raw_data_hash -> normalized_data_hash -> feature_hash -> signal_hash -> order_hash -> fill_hash -> metric_hash -> review_hash
```

## Run manifest fields

- Run ID
- Strategy ID
- Code commit
- Config hash
- Data version/hash
- Feature version/hash
- Model version/hash
- Start/end time
- Random seed
- Environment
- Broker/paper/live mode
- Risk limits
- Metric pack version

## Tamper detection

A hash chain is optional at MVP level but useful later. The simple version is to hash each artifact and store the hash in the run manifest.
