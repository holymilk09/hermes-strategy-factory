# Heatmap Parameter Playbook

**Source**: `06_heatmaps_diagnostics/parameter_sweep_heatmaps.md`, `06_heatmaps_diagnostics/heatmap_playbook.md`

## Key Concepts

Parameter sweep heatmaps are the fastest way to distinguish real edges from lucky parameter selections. They visualize strategy performance across a grid of parameter values.

### Minimum Grid Record

Each heatmap grid point must store:
- `run_id`, `strategy_id`
- `parameter_1_name`, `parameter_1_value`
- `parameter_2_name`, `parameter_2_value`
- `CAGR`, `Sharpe`, `MaxDD`, `Expectancy`
- `Turnover`, `OOS_decay`

### Stable Edge Definition

**A stable edge has a neighborhood of acceptable cells around the best cell.** Single-cell spikes are almost always overfit noise.

### Heatmap Construction

| Axis | Description |
|---|---|
| X-axis | Parameter 1 (e.g., lookback window length) |
| Y-axis | Parameter 2 (e.g., entry threshold) |
| Cell value | Sharpe, CAGR, max drawdown, or expectancy |

### Interpretation Rules

- **Broad plateau of good performance**: Likely robust edge.
- **Single-cell spike**: Overfit to noise. Reject.
- **Gradual performance gradient**: Healthy. Suggests parameter has real, continuous effect.
- **Sharp cliffs**: Danger zone. Small parameter changes destroy performance = fragile strategy.
- **OOS_decay column matters**: A parameter region with good IS Sharpe but high OOS decay is overfit even if the IS heatmap looks great.

### Rejection Criteria

From [[Heatmap-Playbook-Diagnostics]]: "A parameter map where only one cell works" = reject.

## Implications

1. **Always run before choosing parameters** — the heatmap is a diagnostic, not a selection tool. Pick parameters from robust plateau regions, not peaks.
2. **Report turnover per cell** — high-turnover cells may appear profitable pre-cost but fail after costs.
3. **Include OOS decay in the grid record** — IS performance alone is insufficient. Cells with low OOS decay are the only deployable candidates.
4. **Use multiple metrics simultaneously** — a region with good Sharpe but terrible max drawdown represents path risk that Sharpe alone hides.

## Failure Modes / Misinterpretations

- **Grid resolution too coarse**: You might miss the plateau if parameters jump in large steps (e.g., testing only 10, 50, 100). Start wide, then zoom in.
- **Grid resolution too fine**: Overfitting risk increases as you test more discrete points. Each point is an implicit trial.
- **Interpolation illusion**: Heatmaps create visual continuity but adjacent cells are independent backtests. Do not assume smooth interpolation.
- **Cherry-picking the heatmap axes**: Testing parameters you already know work from prior runs inflates selection bias. Include the full search space.
- **Ignoring the turnover dimension**: A parameter set with great Sharpe but 10x turnover will fail in live trading.

## Cross-Links

- [[Overfit-Detection-Metrics]] for PBO, DSR as complementary validation
- [[Heatmap-Time-Regime]] for temporal robustness of parameter choices
- [[Heatmap-Slippage]] for execution-stress testing of parameter sets
- [[Overfit-Detection-Metrics#Minimum-Viable-Anti-Overfit-Protocol]] for mandatory reporting steps
