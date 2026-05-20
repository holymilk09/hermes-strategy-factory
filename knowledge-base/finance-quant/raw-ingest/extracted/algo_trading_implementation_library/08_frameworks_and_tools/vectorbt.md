# vectorbt Notes

vectorbt is strong for fast exploration because it works with pandas/NumPy-style arrays and can test many variants quickly.

## Best use

- Screening indicators.
- Fast parameter sweeps.
- Feature sanity checks.
- Exploratory charts.

## Danger

Fast parameter sweeps create overfitting at machine speed. Every vectorized winner needs event-driven validation with realistic costs and fills.
