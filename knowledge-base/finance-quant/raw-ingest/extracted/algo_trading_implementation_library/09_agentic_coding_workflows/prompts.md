# Prompt Templates

## Convert paper to hypothesis

```text
Read the attached/source paper summary. Extract only testable trading hypotheses.
For each hypothesis, output JSON with: asset_class, universe, horizon, signal, regime_filter, entry_rule, exit_rule, cost_model, falsification_test, required_data, implementation_difficulty.
Do not invent performance claims.
```

## Implement strategy module

```text
Implement the strategy described in strategy_contract.md.
Only modify src/strategies/<strategy_id>.py and tests/test_<strategy_id>.py.
Do not modify data pipeline, metrics, or execution code.
Use existing contracts.
```

## Debug backtest discrepancy

```text
Compare expected ledger vs actual ledger for run_id=<id>.
Trace data -> signal -> target -> order -> fill -> cash -> position -> metric.
Return the first divergent event and likely cause.
```

## Weak-point review

```text
Given metric_pack.json, trade_ledger.csv, parameter_grid.csv, and regime_report.csv, identify the top 5 weak points.
Classify each as strategy, data, execution, risk, code, or overfit.
Recommend the next falsification test only.
```
