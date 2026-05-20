# Overfit Detection Metrics

## Required questions

1. How many strategy variants were tried?
2. How correlated are the variants?
3. Did validation/test data influence parameter choice?
4. Does the signal survive transaction costs?
5. Does performance survive nearby parameter changes?
6. Does performance survive different calendar windows?
7. Does performance survive different symbols/markets?

## Core metrics

| Metric | Purpose |
|---|---|
| Probabilistic Sharpe Ratio | Estimate probability true Sharpe exceeds a benchmark. |
| Deflated Sharpe Ratio | Correct observed Sharpe for selection bias, multiple tests, non-normality. |
| PBO | Estimate probability that selected strategy is overfit. |
| OOS decay | Compare in-sample to out-of-sample metric. |
| Parameter stability score | Detect parameter cliffs. |
| Bootstrap confidence interval | Estimate uncertainty around returns/Sharpe/drawdown. |
| Newey-West t-stat | Adjust significance for autocorrelation/heteroskedasticity. |

## Minimum viable anti-overfit protocol

- Lock test window.
- Run baseline before optimization.
- Count every variant.
- Report parameter heatmap.
- Report OOS performance.
- Report after-cost performance.
- Report worst-regime performance.
