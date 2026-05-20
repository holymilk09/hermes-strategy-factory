# Metric Formulas and Notes

## Sharpe ratio

```text
Sharpe = annualized_mean_excess_return / annualized_volatility
```

Use with caution. Non-normal returns, short samples, and repeated parameter search inflate it.

## Sortino ratio

```text
Sortino = annualized_excess_return / downside_deviation
```

Useful when upside volatility should not be punished.

## Maximum drawdown

```text
drawdown_t = equity_t / max(equity_0..equity_t) - 1
max_drawdown = min(drawdown_t)
```

Max drawdown is a path metric. It is not captured by volatility alone.

## Profit factor

```text
profit_factor = gross_profit / abs(gross_loss)
```

Good as a trade diagnostic. Weak if trade count is small.

## Expectancy

```text
expectancy = hit_rate * avg_win - loss_rate * abs(avg_loss)
```

Must include fees and slippage.

## Implementation shortfall

```text
shortfall = side_sign * (fill_price - decision_price) + fees + market_impact
```

For buys, higher fill price is bad. For sells, lower fill price is bad.

## Information coefficient

```text
IC = corr(signal_score_t, future_return_t+h)
RankIC = spearman(signal_score_t, future_return_t+h)
```

Use exact horizon alignment. Avoid overlapping-window false confidence.
