# LEAN Local Backtesting

Local backtesting with LEAN provides reproducibility, code ownership, and tighter agentic development loops. It is the validation step between vectorized exploration and live trading.

## Core Concepts

- **LEAN CLI workflow:** The `lean` command-line tool manages projects, backtesting, and deployment locally.
- **Minimal workflow:**
  ```shell
  lean init                                    # Initialize project directory
  lean create-project "StrategyName"           # Create strategy project
  lean backtest "StrategyName"                 # Run backtest
  lean backtest "StrategyName" --parameter key value  # Parameter sweep
  ```
- **Data requirements:** Local backtests require correct local data setup or cloud data provider configuration. Missing data = silent failures or empty results.
- **Docker-based execution:** LEAN CLI runs the engine inside Docker containers for reproducibility and isolation.
- **Parameter injection:** Parameters can be passed via CLI flags, enabling automated parameter sweeps and optimization.

## Required Additions Around LEAN

LEAN's default backtest output is insufficient for rigorous research. Add these around LEAN:

- **Store run manifest outside the platform output:** LEAN generates backtest reports but does not track experiment identity. Store your own manifest with run_id, config hash, data version, and parameter values.
- **Add your own experiment registry:** Track every backtest run with its parameters, data version, code commit hash, and results for reproducibility.
- **Add weak-point review notes:** Every backtest result should include a review of its weakest points: worst drawdown, worst regime, data gaps, parameter sensitivity.
- **Add parameter heatmap exports:** Visualize the parameter space to identify robust regions vs overfitting peaks.
- **Add data-quality assumptions to the report:** Document which data was used, its time range, any gaps, and corporate action handling.

## Implications

- Local backtesting is the critical bridge between fast vectorized exploration ([[VectorBT-Reference]]) and live trading. It is where overfitting gets caught.
- The `lean backtest --parameter` interface enables automated optimization, but every parameter sweep increases overfitting risk. Use [[Overfit-Detection-Metrics]] and [[Deflated-Sharpe-Ratio]] to validate.
- Storing run manifests outside LEAN creates an experiment registry that LEAN itself does not provide. This is essential for tracking model lineage.
- Docker-based execution means environment is reproducible, but data versioning is your responsibility.
- The experiment registry should cross-reference the [[Schema-Catalog]] to track which data schemas each run used.

## Failure Modes

- **Silent data gaps:** If local data is missing or incomplete, LEAN may backtest on fewer data points than expected, producing deceptively strong results. Always validate data completeness.
- **Missing data setup:** Local backtests require correct local data setup or cloud data provider configuration. The [[Lean-Backtesting-Gotchas]] has details.
- **Untracked parameter changes:** Changing parameters without recording them makes it impossible to reproduce or audit a backtest. Use a formal experiment registry.
- **Container drift:** LEAN CLI Docker images may update, changing engine behavior between runs. Pin LEAN versions.
- **Parameter sweep overfitting:** Automated parameter sweeps via `--parameter` flags create the same false discovery problem as vectorbt. [[VectorBT-Reference]] overfitting warning applies.
- **Missing weak-point diagnostics:** LEAN's default statistics (Sharpe, drawdown, returns) don't reveal regime-specific weaknesses. You must add custom diagnostics.

## Cross-Links

- [[LEAN-Reference]] — LEAN platform index
- [[LEAN-Backtesting-Gotchas]] — common pitfalls in LEAN backtesting
- [[LEAN-Live-Trading-Ops]] — next step after local backtesting
- [[VectorBT-Reference]] — earlier exploration step; local backtesting validates vectorbt winners
- [[Overfit-Detection-Metrics]] — validate parameter sweep results
- [[Framework-Comparison-Selection]] — LEAN as the recommended validation engine
- [[Data-Vendor-Comparison]] — data source options for LEAN local backtesting
- [[Execution-Metrics]] — measure execution quality that LEAN backtests simulate
- [[Experiment-Registry-Design]] — pattern for tracking LEAN runs
