# Performance Metrics

**Source**: `02_quant_metrics_catalog/quant_metrics_catalog.md`, `all_quant_metrics_catalog.csv`, `metric_formulas.md`

## Key Concepts

Performance metrics quantify the return profile of a strategy, but none are meaningful in isolation from risk context, sample length, and cost assumptions.

### Core Metrics

- **Total Return**: `(ending_equity / starting_equity) - 1` — meaningless without time period and risk context.
- **CAGR**: `(ending/start)^(1/years) - 1` — geometric growth rate; hides drawdown path.
- **Sharpe Ratio**: `annualized_excess_return / annualized_volatility` — the standard but easily inflated by non-normality, short samples, and selection bias from repeated parameter search.
- **Sortino Ratio**: `annualized_excess_return / downside_deviation` — penalizes only downside volatility; useful for strategies with asymmetric payoff profiles.
- **Calmar/MAR Ratio**: `CAGR / abs(max_drawdown)` — return per unit max drawdown; unstable for short samples.
- **Omega Ratio**: `sum(gains over threshold) / abs(sum(losses below threshold))` — full-distribution view; threshold choice matters.
- **Information Ratio**: `active_return / tracking_error` — active return vs benchmark; benchmark choice can distort interpretation.
- **Tracking Error**: `std(strategy_returns - benchmark_returns) * sqrt(AF)` — deviation from benchmark; not a risk measure for absolute-return systems.
- **Alpha**: intercept from factor/benchmark regression — residual return; regression model specification matters.
- **Beta**: `cov(strategy, benchmark)/var(benchmark)` — regime-dependent.
- **Treynor Ratio**: `excess_return / beta` — invalid when beta is near zero or unstable.

### Drawdown Family

- **Max Drawdown**: `min(equity/running_max - 1)` — path-dependent, not captured by volatility.
- **Drawdown Duration**: time from peak to recovery — capital lock-up.
- **Time Under Water**: % time equity below prior high — psychological and capital efficiency cost; high TUW kills deployability.
- **Ulcer Index**: `sqrt(mean(drawdown_pct²))` — depth + duration weighting.
- **Pain Index**: `mean(abs(drawdowns))` — average pain; can underweight rare crashes.
- **Pain Ratio**: `excess_return / pain_index` — return per unit drawdown pain.
- **Recovery Factor**: `net_profit / abs(max_drawdown)` — can be gamed by long samples.

### Trade Quality

- **Hit Rate**: `winning_trades / total_trades` — useless without payoff ratio.
- **Profit Factor**: `gross_profit / abs(gross_loss)` — good diagnostic; weak if trade count is small; can be inflated by few large wins.
- **Expectancy**: `hit_rate * avg_win - loss_rate * avg_loss` — must include fees and slippage; the single most important per-trade metric.
- **MAE/MFE**: max adverse/favorable excursion — requires intratrade data; MFE capture (`realized_pnl / MFE`) measures exit efficiency but can punish trend-following exits.
- **Turnover**: `sum(abs(trade_notional)) / portfolio_value` — high turnover eats edge.

## Implications

1. **Always report after-cost performance.** Pre-cost Sharpe inflates unrealistically.
2. **Use the Pain Ratio and Time Under Water** alongside Sharpe to capture the lived experience of holding a strategy.
3. **Calmar and MAR are useful for CTA-style systems** but meaningless for high-frequency, high-frequency mean-reversion with deep frequent drawdowns.
4. **Omega Ratio at varying thresholds** gives a fuller distribution picture than Sharpe alone.
5. **Always pair hit rate with profit factor or expectancy** — a 70% hit rate strategy with poor payoff ratio loses money.

## Failure Modes / Misinterpretations

- **Sharpe inflation via selection bias**: If you tried 100 parameter variants and report the best Sharpe, the true Sharpe is likely much lower (see [[Overfit-Detection-Metrics]] for DSR/PSR).
- **Anomalies in small samples**: Metrics on fewer than 30 trades are nearly meaningless. Bootstrap CI is essential ([[Metric-Formulas]]).
- **Non-normality**: Sharpe assumes roughly normal returns. Fat-tailed strategies (e.g., short vol) produce misleading Sharpe values.
- **CAGR hiding path risk**: A 20% CAGR with 60% max drawdown is fundamentally different from 20% CAGR with 15% max DD. Always report the drawdown pair.
- **Benchmark-gaming Alpha**: Changing the benchmark changes Alpha. Use [[Risk-Metrics#Factor-Exposure]] context.

## Cross-Links

- [[Risk-Metrics]] for tail risk, concentration, and dynamic controls
- [[Execution-Metrics]] for the full cost picture
- [[Overfit-Detection-Metrics]] for Sharpe correction (DSR, PSR)
- [[Metric-Formulas]] for exact formula definitions
