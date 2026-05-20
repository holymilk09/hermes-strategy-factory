# Local Backtesting with LEAN

## Why it matters

Local backtesting gives reproducibility, code ownership, and tighter agentic development loops.

## Minimal workflow concept

```text
lean init
lean create-project "StrategyName"
lean backtest "StrategyName"
lean backtest "StrategyName" --parameter key value
```

## Required additions around LEAN

- Store run manifest outside the platform output.
- Add your own experiment registry.
- Add weak-point review notes.
- Add parameter heatmap exports.
- Add data-quality assumptions to the report.
