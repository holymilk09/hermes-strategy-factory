# Official Documentation Index

Catalog of framework, data vendor, and broker API documentation links referenced in the research papers collection and build doctrine.

## QuantConnect / LEAN

- LEAN Engine Overview: https://www.quantconnect.com/docs/v2/lean-engine/getting-started
- Algorithm Framework (Alpha → Portfolio → Execution): https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/overview
- LEAN CLI: https://www.quantconnect.com/docs/v2/lean-cli
- Local Backtesting: https://www.quantconnect.com/docs/v2/lean-cli/backtesting/deployment
- Research Environment: https://www.quantconnect.com/docs/v2/research-environment
- Dataset key concepts / look-ahead bias: https://www.quantconnect.com/docs/v2/research-environment/datasets/key-concepts
- Backtest Reports: https://www.quantconnect.com/docs/v2/cloud-platform/backtesting/report

## Backtesting / Live Trading Frameworks

- NautilusTrader Concepts: https://nautilustrader.io/docs/latest/concepts/
- NautilusTrader Backtesting: https://nautilustrader.io/docs/latest/concepts/backtesting/
- NautilusTrader Live Trading: https://nautilustrader.io/docs/latest/concepts/live/
- vectorbt: https://vectorbt.dev/
- Backtrader: https://www.backtrader.com/
- Zipline Reloaded: https://zipline.ml4trading.io/

## Data and Broker APIs

- Databento Historical API: https://databento.com/docs/api-reference-historical
- Databento Reference API: https://databento.com/docs/api-reference-reference
- OpenBB ODP Python: https://docs.openbb.co/odp/python
- OpenBB Data Sources: https://docs.openbb.co/odp/cli/data-sources
- Alpaca Orders: https://docs.alpaca.markets/docs/orders-at-alpaca
- Alpaca Trading API: https://docs.alpaca.markets/us/docs/trading-api
- IBKR Order Submission: https://interactivebrokers.github.io/tws-api/order_submission.html
- IBKR Open Orders: https://interactivebrokers.github.io/tws-api/open_orders.html
- CCXT Unified Crypto API: https://docs.ccxt.com/

## Implications

- Official docs are Tier 4 sources per [[Source-Quality-Rules]], the highest rank for implementation guidance.
- Framework selection should be guided by [[Framework-Comparison-Selection]] and the [[Trading-System-Build-Doctrine]] implementation phases.
- All framework references in papers ([[Papers-Docs-Synthesis]]) link back to these official sources for implementation details.

## Failure Modes

- **Outdated docs**: framework documentation changes between versions; always check version numbers.
- **Marketing vs reality**: vendor docs highlight capabilities but may gloss over limitations or performance constraints.
- **Incomplete examples**: official examples often show the happy path, not edge cases like broker rejects or stale data.

## Cross-Links

- [[Framework-Comparison-Selection]] — framework evaluation and selection criteria
- [[Trading-System-Build-Doctrine]] — Phase 1-2 implementation uses these frameworks
- [[Data-Pipeline-Architecture]] — vendor adapter layer connects to these APIs
- [[Research-Papers-Index]] — papers reference these as implementation sources
