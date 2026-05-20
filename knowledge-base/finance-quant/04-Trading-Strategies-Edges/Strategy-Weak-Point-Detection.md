# Strategy Weak-Point Detection

A scoring framework to identify which fragilities in a strategy deserve attention first.

## Key Concepts

### Weak-Point Categories

| Category | Detection Method |
|---|---|
| Parameter fragility | Parameter heatmap shows cliff edges; low neighborhood stability |
| Regime fragility | Poor performance in volatility/liquidity/trend buckets |
| Symbol concentration | PnL dominated by few instruments |
| Time concentration | PnL dominated by specific month/day/session bucket |
| Trade concentration | Top 5 trades explain majority of profit |
| Cost fragility | Edge disappears after higher slippage/spread assumptions |
| Execution fragility | High reject rate, partial fills, live-vs-paper slippage gap |
| Data fragility | Quality flags correlate with profits |
| Model drift | Feature distribution or signal IC changes over time |

### Weak-Point Score

```
weakness_score =
  0.25 * parameter_fragility
+ 0.20 * regime_concentration
+ 0.15 * trade_concentration
+ 0.15 * cost_sensitivity
+ 0.10 * symbol_concentration
+ 0.10 * model_drift
+ 0.05 * data_quality_risk
```

**Use as prioritization, not truth.** The weights reflect typical risk contribution, but individual strategies may differ.

## Implications for Trading Systems

- **Parameter fragility is #1 by weight**: a strategy that only works at exactly fast_ma=12 is likely overfit.
- **Regime fragility is #2**: a strategy that only works in low-vol uptrend has a narrow edge; add a regime gate or restrict use to that regime.
- **Trade concentration**: if 3 trades explain 80% of profit, you don't have a strategy — you have lottery tickets.
- **Heatmaps are essential**: without parameter and regime heatmaps, you can't detect fragility.
- **Weak-point review board**: track each identified weakness with ID, evidence, severity, owner, and next experiment.

## Failure Modes

- **Ignoring low scores**: a 0.05 data_quality_risk could mask a catastrophic data bug in one symbol.
- **Over-optimizing the score**: tweaking a strategy to lower the weak-point score is itself a form of overfitting.
- **Static weights**: the weights may not apply to all strategies; a market-making strategy is more sensitive to execution fragility than to regime fragility.
- **Heatmap overinterpretation**: a single heatmap run doesn't prove fragility; repeat across epochs.
- **Fixing symptoms, not causes**: a parameter cliff might be caused by insufficient data, not a bad strategy.

## Cross-Links

- [[Epoch-Learning-Retraining]] — weak-point scores are recorded per epoch
- [[Walk-Forward-Epoch-Protocol]] — heatmaps in Step 6 feed weak-point detection
- [[Review-And-Learn-Loop]] — review questions 3-4 reference weak-point changes
- [[Trading-System-Build-Doctrine]] — Phase 3 stress testing includes weak-point analysis
- [[Trading-System-Build-Doctrine]] — Weak-Point Review Board table format
- [[Logging-Audit-Monitoring]] — live performance monitoring catches regime and execution fragility
- [[Epoch-Learning-Retraining]] — model drift is one of nine weak-point categories
