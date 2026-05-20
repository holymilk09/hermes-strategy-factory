# Market Data Quality Checks

## Checks per symbol/timeframe

- Duplicate timestamp count
- Missing bar count
- Out-of-session bar count
- Zero/negative price count
- OHLC consistency: `low <= open <= high`, `low <= close <= high`
- Volume negative/zero anomaly
- Extreme return z-score
- Spread outlier
- Corporate-action mismatch
- Calendar mismatch
- Suspicious flatline
- Vendor gap vs backup source

## Dataset quality score

```text
quality_score = 100
  - 10 * missing_bar_rate
  - 10 * duplicate_rate
  - 20 * invalid_ohlc_rate
  - 10 * extreme_outlier_rate
  - 20 * corporate_action_error_flag
  - 10 * calendar_mismatch_flag
```

Do not use this score blindly. It is a triage score, not a guarantee.
