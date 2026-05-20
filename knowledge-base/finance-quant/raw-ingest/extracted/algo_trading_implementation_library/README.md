# Algo Trading Implementation Library

Companion library for building algorithmic trading systems. This package is intentionally implementation-first: architecture, data pipelines, quant metrics, backtesting discipline, epoch learning, logging, testing, review loops, heatmaps, and high-level aggregated data tactics.

## Embedded research assets

This package includes embedded open-access PDFs in `12_research_papers_and_docs/papers/`. They were verified with `%PDF-` headers and `pdfinfo` page counts. The docs also retain source URLs and a download manifest so the files can be refreshed later.

This is an implementation-first library: it is not a replacement for live broker docs, tax/legal review, or institutional data agreements. Treat vendor docs as the source of truth when APIs change.

## Main folder map

| Folder | Purpose |
|---|---|
| `00_core_bot_structure/` | Core components and module contracts for a trading bot. |
| `01_data_pipelines/` | Historical, live, feature-store, and aggregated-data pipeline design. |
| `02_quant_metrics_catalog/` | Practical metric catalog across performance, risk, execution, model, and overfit diagnostics. |
| `03_backtesting_engineering/` | How to prevent false alpha and broken simulations. |
| `04_epoch_learning_review_loops/` | Walk-forward, epoch learning, retraining, strategy review, and weak-point detection. |
| `05_logging_testing_observability/` | Logs, audit trails, test layers, monitoring, and run review. |
| `06_heatmaps_diagnostics/` | Heatmap diagnostics for parameters, time, symbols, regimes, slippage, and trade failure. |
| `07_quantconnect_lean_docs/` | LEAN/QuantConnect implementation map and local workflow. |
| `08_frameworks_and_tools/` | Framework, data vendor, and broker/tool comparison. |
| `09_agentic_coding_workflows/` | Guardrails for Codex/Cursor/Windsurf-style building. |
| `10_templates/` | Code, JSON, YAML, and review templates. |
| `11_data_tactics_aggregated/` | High-level aggregated-data tactics: cross-asset, macro, 13F, regime, volume/flow. |
| `12_research_papers_and_docs/` | Source-linked papers and official documentation manifest. |

## Build doctrine

1. Separate signal, portfolio construction, risk, execution, data, logging, and review.
2. Never trust a backtest without cost modeling, leakage checks, run metadata, and out-of-sample diagnostics.
3. Treat each strategy as a hypothesis with a falsification path.
4. Every run needs a run ID, data version, code commit, config hash, parameter set, metric pack, and review note.
5. Use heatmaps to find fragility: parameter cliffs, regime dependency, calendar dependency, symbol concentration, execution decay.
6. Use epoch learning to improve the system, not to repeatedly overfit the strategy.
