# Master Index

## Core system design

- `00_core_bot_structure/core_components.md` — trading bot anatomy.
- `00_core_bot_structure/event_loop_and_state_machine.md` — event-driven bot loop and state machine.
- `00_core_bot_structure/module_contracts.md` — contracts between data, signal, sizing, risk, execution, and logs.
- `00_core_bot_structure/failure_modes.md` — failure map for strategy and system bugs.

## Data pipelines

- `01_data_pipelines/data_pipeline_architecture.md` — batch/live pipeline structure.
- `01_data_pipelines/historical_data_pipeline.md` — historical research and backtest pipeline.
- `01_data_pipelines/realtime_data_pipeline.md` — live market-data handling.
- `01_data_pipelines/aggregated_data_tactics.md` — high-level aggregated data tactics.
- `01_data_pipelines/feature_store_design.md` — feature registry and point-in-time safety.
- `01_data_pipelines/market_data_quality_checks.md` — vendor and data validation checks.

## Metrics

- `02_quant_metrics_catalog/all_quant_metrics_catalog.csv` — broad practical metric catalog.
- `02_quant_metrics_catalog/metric_formulas.md` — formulas and implementation notes.
- `02_quant_metrics_catalog/overfit_detection_metrics.md` — PBO, PSR, DSR, multiple-testing controls.
- `02_quant_metrics_catalog/execution_metrics.md` — fill, slippage, latency, routing metrics.

## Backtesting

- `03_backtesting_engineering/backtest_architecture.md` — event-driven backtest components.
- `03_backtesting_engineering/leakage_survivorship_controls.md` — leakage and survivorship control checklist.
- `03_backtesting_engineering/fill_slippage_transaction_costs.md` — cost and fill modeling.
- `03_backtesting_engineering/walkforward_purged_cv.md` — validation structure.

## Review and learning

- `04_epoch_learning_review_loops/epoch_learning_model.md` — epoch protocol.
- `04_epoch_learning_review_loops/strategy_weak_point_detection.md` — weak-point discovery logic.
- `04_epoch_learning_review_loops/review_and_learn_loop.md` — review loop for code, data, strategy, and live ops.

## Ops

- `05_logging_testing_observability/logging_contract.md` — required logs.
- `05_logging_testing_observability/testing_strategy.md` — unit, integration, regression, simulation, smoke, paper/live tests.
- `05_logging_testing_observability/monitoring_alerting.md` — production monitoring.

## Heatmaps

- `06_heatmaps_diagnostics/heatmap_playbook.md` — diagnostic matrix.
- `06_heatmaps_diagnostics/python_heatmap_template.py` — template script.

## QuantConnect / LEAN

- `07_quantconnect_lean_docs/quantconnect_lean_index.md` — LEAN docs map.
- `07_quantconnect_lean_docs/algorithm_framework_mapping.md` — map serious bot components to LEAN modules.
- `07_quantconnect_lean_docs/local_backtesting.md` — local LEAN workflow.

## Templates

- `10_templates/src/` — minimal strategy/data/metrics/review skeleton.
- `10_templates/tests/` — pytest skeleton.
- `10_templates/configs/` — strategy and risk YAML.
- `10_templates/schemas/` — JSON contracts.

## Research and docs

- `12_research_papers_and_docs/papers_index.md` — paper annotations.
- `12_research_papers_and_docs/official_docs_index.md` — official docs index.
- `12_research_papers_and_docs/PDF_DOWNLOAD_QUEUE.csv` — lawful direct download queue.


## Embedded PDF research layer

See `12_research_papers_and_docs/EMBEDDED_PDFS.md` and `12_research_papers_and_docs/embedded_pdfs_index.csv` for verified local PDFs. Core themes: backtest overfitting, multiple testing, Sharpe/metric uncertainty, stylized facts, technical-analysis validation, tactical investment algorithms, and DRL trading architectures.
