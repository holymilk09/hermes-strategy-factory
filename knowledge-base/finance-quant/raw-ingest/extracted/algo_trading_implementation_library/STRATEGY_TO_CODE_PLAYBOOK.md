# Strategy-to-Code Playbook

## Convert an idea into a testable hypothesis

Bad form:

> RSI plus volume should work.

Good form:

> When realized volatility is below its 60-day median and 20-day momentum is positive, pullbacks with short-term oversold readings have positive expected return over the next 5 sessions after costs.

## Required hypothesis fields

| Field | Example |
|---|---|
| Asset class | US equities, liquid top 500 by dollar volume |
| Horizon | 5 trading days |
| Signal | 20-day momentum + 3-day pullback |
| Regime filter | Realized volatility below 60-day median |
| Entry | Next bar after signal close |
| Exit | 5 bars, stop, or signal invalidation |
| Costs | Commission + spread + slippage |
| Falsification | No positive OOS expectancy after costs; parameter cliff; only works in one symbol |

## Implementation conversion

1. Write signal function independent of portfolio/execution.
2. Write feature function independent of signal.
3. Write sizing function independent of broker.
4. Write risk veto independent of alpha.
5. Write test fixtures for features, signal, sizing, and risk.
6. Run baseline with no optimization.
7. Run sensitivity map.
8. Run OOS epoch.
9. Write review before changing parameters.
