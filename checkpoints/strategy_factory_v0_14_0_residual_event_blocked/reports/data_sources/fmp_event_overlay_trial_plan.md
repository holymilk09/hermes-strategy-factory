# FMP Event Overlay Trial Plan

## Trial Comparisons
1. residual_z <= -2.0 + GOOD/ACCEPTABLE fit (baseline)
2. + earnings_within_5d BLOCK
3. + earnings_day BLOCK
4. + post_earnings_2d BLOCK
5. + downgrade/news warning if available

## Strategy Contexts
- mean_reversion + residual filter
- structural_mr + residual filter

## Metrics
- n_trades, mean return, median return, hit rate
- cost-adjusted return, drawdown
- random-pruning baseline
- blocked trade quality (missed winners vs avoided losers)

## Success
- FMP blocker reduces bad trades
- does not remove too many good trades
- improves cost-adjusted return
- passes random-pruning

## Failure
- blocks too many trades
- does not improve residual filter
- leaks future data
- sample too small

## Status: PLAN_DEFINED — execution pending FMP_API_KEY
