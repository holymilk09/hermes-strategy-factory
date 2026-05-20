# Model Drift Rules

## Drift types

| Drift | Meaning |
|---|---|
| Feature drift | Input distribution changed. |
| Label drift | Outcome distribution changed. |
| Concept drift | Feature-outcome relationship changed. |
| Execution drift | Fill/slippage environment changed. |
| Regime drift | Macro/liquidity/volatility environment changed. |

## Drift controls

- Feature PSI/KL/KS tests.
- Rolling Signal IC.
- Calibration curves by month/quarter.
- Live-vs-backtest slippage comparison.
- Regime classification heatmap.
- Kill or reduce strategy when drift breaches hard thresholds.
