# Failure Modes

## Strategy failure

- Edge only exists before transaction costs.
- Edge exists only in one instrument.
- Edge exists only in one market regime.
- Parameter heatmap has a cliff.
- Returns depend on a few outlier trades.
- Win rate is high but payoff ratio is poor.
- Strategy is short volatility unintentionally.
- Strategy is long beta unintentionally.

## Data failure

- Look-ahead leakage.
- Survivorship bias.
- Corporate actions mishandled.
- Delisted names excluded.
- Time zone mismatch.
- Missing bars treated as zero movement.
- Vendor data changed without versioning.
- Features calculated on future-adjusted data when they should not be.

## Backtest failure

- Bar-close signal fills at same bar close.
- No spread/slippage.
- No partial fills.
- No borrow, margin, fees, or funding cost.
- Unrealistic liquidity.
- No rejection path for invalid orders.
- Parameter search uses test set repeatedly.

## Live failure

- Broker order state diverges from internal state.
- Duplicate order sent after retry.
- API outage creates stale positions.
- Kill switch fails or is not tested.
- Latency changes execution quality.
- Paper fills are unrealistic.
- Position reconciliation is skipped.
