# Historical Data Pipeline

## Process

1. Pull raw data.
2. Write immutable raw snapshot.
3. Normalize schema.
4. Normalize timestamps.
5. Map vendor symbols to internal symbols.
6. Apply declared adjustment policy.
7. Validate gaps, duplicates, extreme values, and calendar alignment.
8. Generate bars/features only after quality checks.
9. Lock dataset version before backtest.

## Historical data traps

- Split-adjusted OHLCV mixed with raw trades.
- Vendor survivorship filters.
- Ticker reuse.
- Delisting omissions.
- Time zone shift at daylight savings boundaries.
- Futures continuous-contract roll logic not recorded.
- Options chain snapshots missing expired contracts.
- Crypto exchange outages hidden by resampled bars.

## Dataset version naming

```text
assetclass_vendor_dataset_adjustment_calendar_start_end_hash

example:
us_equity_databento_ohlcv_splitdivadj_nyse_20150101_20251231_ab12cd
```
