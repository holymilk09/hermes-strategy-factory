# LEAN Reference Index

QuantConnect / LEAN is useful as a reference architecture even when you do not use QuantConnect directly. LEAN provides a production-grade, event-driven backtesting and live-trading engine with the Algorithm Framework pattern for modular strategy design.

## Source Links

| Topic | URL |
|---|---|
| LEAN Engine | https://www.quantconnect.com/docs/v2/lean-engine/getting-started |
| Algorithm Framework | https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/overview |
| LEAN CLI | https://www.quantconnect.com/docs/v2/lean-cli |
| Local Backtesting | https://www.quantconnect.com/docs/v2/lean-cli/backtesting/deployment |
| Research Environment | https://www.quantconnect.com/docs/v2/research-environment |
| Research Key Concepts | https://www.quantconnect.com/docs/v2/research-environment/key-concepts/getting-started |
| Dataset Look-Ahead Warning | https://www.quantconnect.com/docs/v2/research-environment/datasets/key-concepts |
| Machine Learning | https://www.quantconnect.com/docs/v2/research-environment/machine-learning/key-concepts |
| Backtest Reports | https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/report |
| GitHub Organization | https://github.com/quantconnect |

## What to Study First (Ordered)

1. LEAN Engine overview — understand the architecture, data flow, and execution model.
2. Algorithm Framework overview — module separation (universe → alpha → portfolio → risk → execution).
3. Research Environment — notebook-based exploration with QuantBook.
4. Local backtesting with LEAN CLI — reproducible backtesting workflow.
5. Backtest reports and statistics — interpret performance metrics.
6. Risk management and execution models — production safety.

## Vault Notes

| Note | Description |
|---|---|
| [[LEAN-Local-Backtesting]] | Local backtesting workflow with LEAN CLI: init, deploy, parameter sweeps, result management. |
| [[LEAN-Live-Trading-Ops]] | Live trading operational checklist: connections, reconciliation, kill switches, paper vs live differences. |
| [[LEAN-Backtesting-Gotchas]] | Common pitfalls: data access differences, framework misuse, options complexity, model versioning. |
| [[LEAN-Research-Environment]] | Notebook-based research workflow: when to use and when not to use notebooks, notebook-to-code rule. |
| [[LEAN-Algorithm-Framework-Mapping]] | Algorithm Framework module mapping, recommended solo-founder module structure, discipline patterns. |

## Core Concepts

- **Event-driven engine:** LEAN processes market events chronologically, simulating order fills, slippage, and portfolio updates.
- **Algorithm Framework:** Modular strategy structure that separates universe selection, alpha generation, portfolio construction, risk management, and execution into independent components.
- **LEAN CLI (`lean`):** Command-line tool for local backtesting, project management, cloud deployment, and data management.
- **Data providers:** LEAN supports QuantLock data, Databento, local CSV data, and custom data source plugins.
- **Brokerage models:** Simulated brokerage models for accurate slippage and fee modeling across different broker environments.

## Implications

- LEAN works as both a platform and a reference architecture. Even if you build your own engine, studying LEAN's module separation and event loop design is valuable.
- The Algorithm Framework pattern prevents "strategy spaghetti" and maps directly to a recommended solo-founder module structure ([[LEAN-Algorithm-Framework-Mapping]]).
- Local backtesting gives reproducibility and code ownership — essential for agentic development loops and rigorous scientific methodology.
- LEAN's data model requires explicit setup: local data or cloud provider configuration. Data gaps will cause silent failures or incorrect results.

## Failure Modes

- **Data access divergence:** Research notebooks can access data differently from backtests. Results from notebooks don't always translate to algorithm execution.
- **Local data setup failures:** Missing or incorrectly formatted local data produces empty backtests without clear error messages.
- **Options/futures complexity:** Derivatives require extra care around chains, expiries, roll logic, and contract selection.
- **Framework misuse:** Algorithm Framework modules are powerful but misuse can obscure where decisions are actually made.
- **Model transfer drift:** Object Store/model transfer should be versioned like any other model artifact. Drifted models produce different results than trained versions.
- **Statistics illusion:** Backtest statistics are not a substitute for custom weak-point diagnostics. A good Sharpe ratio does not mean a robust strategy.

## Cross-Links

- [[LEAN-Local-Backtesting]] — detailed local backtesting workflow
- [[LEAN-Live-Trading-Ops]] — live trading operational checklist
- [[LEAN-Backtesting-Gotchas]] — common pitfalls and gotchas
- [[LEAN-Research-Environment]] — notebook-based research workflow
- [[LEAN-Algorithm-Framework-Mapping]] — module structure and discipline
- [[Framework-Comparison-Selection]] — why LEAN is the recommended validation engine
- [[Trading-System-Component-Architecture]] — broader system architecture context
- [[Overfit-Detection-Metrics]] — validate LEAN backtest results properly
- [[Data-Vendor-Comparison]] — data source options for LEAN
