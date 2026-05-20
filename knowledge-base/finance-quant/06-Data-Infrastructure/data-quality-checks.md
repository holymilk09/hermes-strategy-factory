# Data Quality Checks

## Key Concepts

### Dataset Quality Score

A triage (not guarantee) scoring system applied per symbol/timeframe:

```
quality_score = 100
  - 10 * missing_bar_rate
  - 10 * duplicate_rate
  - 20 * invalid_ohlc_rate
  - 20 * extreme_outlier_rate
  - 10 * corporate_action_error_flag
  - 10 * calendar_mismatch_flag
```

### Mandatory Checks Per Symbol/Timeframe

- **Duplicate timestamp count** — catch vendor double-sends
- **Missing bar count** — detect feed gaps
- **Out-of-session bar count** — flag data outside market hours
- **Zero/negative price count** — impossible prices indicate corruption
- **OHLC consistency**: must satisfy `low <= open <= high` and `low <= close <= high`
- **Volume negative/zero anomaly** — negative volume is impossible; zero volume may indicate halted security
- **Extreme return z-score** — catches unadjusted corporate actions and data spikes
- **Spread outlier** — abnormally wide or tight spreads indicate feed issues
- **Corporate-action mismatch** — split/dividend adjustments not applied correctly
- **Calendar mismatch** — data present on non-trading dates or missing on trading dates
- **Suspicious flatline** — price not moving for too many consecutive bars
- **Vendor gap vs backup source** — compare primary feed against independent vendor

### Quality Score Caveats

The quality score is a **triage tool, not a guarantee**. A dataset can score 85/100 but still have a subtle corporate action error that corrupts returns in a specific ticker. Always inspect flagged instruments individually.

## Implications for Real Trading Systems

- **Quality checks run before feature calculation**: bad data propagates silently into features and signals; catch it early
- **Quality reports are per-run artifacts**: store them alongside backtest outputs so you can trace why a model performed poorly
- **Missing-data handling is strategy-dependent**: some strategies (momentum) degrade gracefully with gaps; others (stat arb) break entirely
- **Calendar mismatches cause silent leakage**: if a holiday is misclassified as a trading day, features computed on that "day" leak information from the next real bar

## Failure Modes

- **False confidence from high scores**: a dataset scoring 95/100 can still have a critical bug in one instrument's corporate action history
- **Ignoring out-of-session bars**: treating after-hours data as regular-hours data creates phantom entries
- **Not checking backup sources**: single-vendor data has hidden failure modes; cross-vendor comparison catches vendor-specific bugs
- **Suspicious flatline ignored**: halted securities with zero volume often appear as flat prices — entering on these is entering on fake data

## Cross-Links

- [[Data Pipeline Architecture]] — the quality checker stage sits after the bar/tick/book aggregator
- [[Feature Leakage Prevention]] — poor-quality data is a primary source of hidden look-ahead bias
- [[Fill and Transaction Cost Models]] — quality issues in spread data directly impact slippage modeling
- [[Schema Catalog]] — the bar schema defines valid fields that quality checks validate against
- [[Logging-Audit-Monitoring]] — quality reports are part of the run manifest's quality artifacts
