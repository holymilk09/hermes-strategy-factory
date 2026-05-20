# Framework Comparison & Selection Guide

Synthesized selection matrix and decision guide for choosing a quantitative trading framework. Derived from the framework selection matrix and per-framework notes.

## Comparison Matrix

| Framework | Best Use | Weakness | Solo-Founder Fit |
|---|---|---|---|
| [[LEAN-Reference]] | Serious multi-asset research, backtesting, live trading | Platform conventions and data costs | High |
| [[NautilusTrader-Reference\|NautilusTrader]] | Production-grade event-driven architecture, live execution | Heavier engineering overhead | Medium-high (execution-focused) |
| [[VectorBT-Reference\|vectorbt]] | Fast vectorized research, large parameter sweeps | Easy to overfit; assumes impossible fills | High (exploration only) |
| [[Backtrader-Reference\|Backtrader]] | Learning, simple Python strategies, reusable indicators/analyzers | Older ecosystem, weak production path | Medium |
| Zipline Reloaded | Event-driven equity research lineage | Legacy constraints | Medium |
| Custom engine | Full control | Massive bug surface area | Low (only if you know exactly why) |

## Recommended Hybrid Workflow

1. **Exploration** → [[VectorBT-Reference\|vectorbt]] or pandas for fast screening, indicator sanity checks, and parameter sweeps.
2. **Validation** → [[LEAN-Reference]] for serious event-driven backtesting with realistic fills, slippage models, and algorithm-framework discipline.
3. **Production Execution** → [[NautilusTrader-Reference\|NautilusTrader]] when execution architecture, order-state reconciliation, and multi-venue live trading become the core edge.

## Decision Tree

```
Are you learning the basics?
  → Yes: [[Backtrader-Reference\|Backtrader]] for simple event-driven practice
  → No:
     Is your bottleneck fast exploration / parameter sweeps?
       → Yes: [[VectorBT-Reference\|vectorbt]]
       → No:
          Do you need multi-asset research + cloud + live in one platform?
            → Yes: [[LEAN-Reference]]
            → No:
               Is execution complexity your core edge (crypto, perps, multi-venue)?
                 → Yes: [[NautilusTrader-Reference\|NautilusTrader]]
                 → No: Start with LEAN, reconsider custom engine later.
```

## Implications for Trading Systems

- **No single framework does it all.** The hybrid approach matches tools to pipeline stages: vectorbt for feature research, LEAN for backtest validation, NautilusTrader for live execution at scale.
- **Early vectorbt speed is deceptive.** A sweeping parameter search produces false confidence; every winner must graduate to [[LEAN-Local-Backtesting\|event-driven backtesting]] before live capital is touched.
- **LEAN's Algorithm Framework imposes discipline.** The module separation (universe → alpha → portfolio → risk → execution) prevents "strategy spaghetti" and maps directly to a recommended solo-founder file structure: [[LEAN-Algorithm-Framework-Mapping]].

## Failure Modes

- **Overfitting at machine speed:** vectorbt sweeps can find spurious winners across thousands of parameter combos. Always validate in an event-driven engine with realistic costs.
- **Framework lock-in:** Don't embed framework-specific code inside strategy logic. Isolate the strategy core so it can port between exploration, validation, and execution engines.
- **Production gap:** Backtrader's aging ecosystem makes it fragile for production. Don't attempt to harden it if your goal is live trading beyond simple equities.
- **Custom engine temptation:** Building a backtesting engine from scratch has a massive bug surface. Only do this after you know exactly what existing frameworks fail to provide.

## Cross-Links

- [[VectorBT-Reference]] — fast vectorized exploration
- [[Backtrader-Reference]] — learning and prototyping
- [[NautilusTrader-Reference]] — production execution architecture
- [[LEAN-Reference]] → [[LEAN-Reference]] — platform index
- [[LEAN-Local-Backtesting]] — event-driven validation workflow
- [[LEAN-Algorithm-Framework-Mapping]] — algorithm discipline reference
- [[Broker-API-Comparison]] — broker connectivity options
- [[Data-Vendor-Comparison]] — data source evaluation
- [[Trading-System-Component-Architecture]] — broader system design
