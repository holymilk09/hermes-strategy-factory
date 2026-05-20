# Leakage and Survivorship Controls

## Common leakage patterns

- Computing rolling features with future-filled missing values.
- Using full-sample normalization before train/test split.
- Selecting universe using future market cap/liquidity.
- Using post-event revised macro/fundamental data.
- Using future split-adjusted data in a way that changes entry conditions.
- Testing parameter changes repeatedly on the final test set.

## Controls

- Transform train and test separately where necessary.
- Use walk-forward windows.
- Lag all event/fundamental/macro features by release timestamp.
- Use delisting-aware datasets.
- Store universe selection rule as code and config.
- Count every experiment.
