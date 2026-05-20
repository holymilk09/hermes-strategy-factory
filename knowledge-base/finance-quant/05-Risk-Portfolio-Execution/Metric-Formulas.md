# Metric Formulas

**Source**: `02_quant_metrics_catalog/metric_formulas.md`, `all_quant_metrics_catalog.csv`

## Key Concepts

This note collects essential metric formulas with usage notes and warnings. Every formula below has conditions under which it fails or misleads.

---

### Sharpe Ratio

```
Sharpe = annualized_excess_return / annualized_volatility
```

**Use with caution**: Non-normal returns, short samples, and repeated parameter search inflate it. See [[Overfit-Detection-Metrics]] for corrections (DSR, PSR).

### Sortino Ratio

```
Sortino = annualized_excess_return / downside_deviation
```

**Useful when**: upside volatility should not be penalized (e.g., options strategies, trend-following with large positive outliers). Sensitive to the downside threshold choice.

### Maximum Drawdown

```
drawdown_t = equity_t / max(equity_0...equity_t) - 1
max_drawdown = min(drawdown_t)
```

Max drawdown is a **path metric**. It is not captured by volatility alone and depends on the exact sequence of returns.

### Profit Factor

```
profit_factor = gross_profit / abs(gross_loss)
```

Good as a trade diagnostic. Weak if trade count is small — a single large win can inflate the ratio dramatically.

### Expectancy

```
expectancy = hit_rate * avg_win - loss_rate * abs(avg_loss)
```

**Must include fees and slippage.** Pre-cost expectancy is fiction for strategies with meaningful turnover.

### Implementation Shortfall

```
shortfall = side_sign * (fill_price - decision_price) + fees + market_impact
```

For buys, higher fill price = bad. For sells, lower fill price = bad. This is the gold standard of execution cost measurement. See [[Execution-Metrics]].

### Information Coefficient

```
IC = corr(signal_score_t, future_return_t+h)
RankIC = spearman(signal_score_t, future_return_t+h)
```

**Critical rules**:
- Use exact horizon alignment (no overlapping-window false confidence)
- IC decay over time is normal; what matters is the IC at the prediction horizon
- RankIC is more robust to outliers than Pearson IC
- ICIR (`mean(IC) / std(IC)`) measures signal stability — a low ICIR with high mean IC suggests the signal is noisy

### Additional Formulas from Catalog

| Metric | Formula | Key Warning |
|---|---|---|
| Calmar | `CAGR / abs(max_drawdown)` | Unstable for short samples |
| Treynor | `excess_return / beta` | Invalid if beta near zero |
| VaR | `quantile(losses, confidence_level)` | Does not show tail beyond threshold |
| CVaR/ES | `mean(losses beyond VaR)` | Needs enough tail observations |
| Kelly Fraction | `edge / odds` or generalized | Full Kelly usually too aggressive; use 0.25-0.5x |
| Omega Ratio | `sum(gains) / abs(sum(losses))` | Threshold choice drives interpretation |
| Hurst Exponent | scaling of variance with lag | Unstable on short samples |
| Half-life | `-ln(2) / ln(phi)` for AR(1) process | Assumes specific model form |

## Implications

1. **Formulas are simplifications of reality** — each one has distributional and stationarity assumptions. Always verify these hold for your data.
2. **Expectancy is the single actionable metric** because it directly connects to position sizing (via Kelly) and frequency (via turnover).
3. **IC alignment is the most common error in signal research** — even a one-bar offset creates look-ahead bias that survives all downstream validation.
4. **Implementation shortfall must include all costs**: commissions, exchange fees, borrow costs for shorts, and opportunity cost of unfilled size.
5. **Sharpe, Sortino, and Calmar tell different stories**: Sharpe punishes all volatility, Sortino only downside, Calmar only peak-to-trough losses. Use all three for a complete picture.

## Failure Modes / Misinterpretations

- **Overlapping window IC inflation**: Using rolling 20-day future returns computed with a 1-day step creates strong serial correlation in IC, inflating statistical significance. Use non-overlapping windows.
- **Annualization factor errors**: Annualizing daily returns with `* sqrt(252)` assumes 252 trading days and IID returns. Crypto with 365 days or strategies with variable trading days need custom factors.
- **Kelly fraction naivety**: Full Kelly maximizes expected log growth under stationarity. Real markets are non-stationary; even slight estimation error in edge makes full Kelly ruinous.
- **Drawdown formula edge case**: If the first return is negative, `running_max` is the initial capital. Ensure your formula handles this correctly.
- **Shortfall circularity**: If your arrival price is VWAP and your own order affects VWAP, you're measuring self-impact as cost. Use pre-arrival snapshot prices.

## Cross-Links

- [[Performance-Metrics]] for interpretation context
- [[Risk-Metrics]] for tail risk formulas
- [[Execution-Metrics]] for implementation shortfall in detail
- [[Overfit-Detection-Metrics]] for Sharpe corrections
