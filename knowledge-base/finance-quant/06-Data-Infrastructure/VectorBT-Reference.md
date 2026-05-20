# vectorbt Reference

vectorbt is a Python library for fast vectorized backtesting and quantitative research. It operates on pandas/NumPy-style arrays, enabling rapid exploration and parameter sweeps. **It is an exploration tool, not a production trading engine.**

## Core Concepts

- **Vectorized computation:** Entire time-series operations execute as array computations, not event loops.
- **Portfolio matrix:** Simultaneously tests thousands of strategy variants by computing all combinations in parallel.
- **pandas/NumPy integration:** Works directly with standard data science tooling; easy to combine with research workflows.
- **Built-in charting:** Provides quick exploratory visualizations for equity curves, drawdowns, heatmaps.
- **No event loop:** Skips the event-driven simulation entirely, which is both the source of its speed and its weakness.

## Best Use Cases

- Screening indicators for predictive signal strength.
- Fast parameter sweeps across grids of entry/exit thresholds.
- Feature sanity checks (does this signal have any edge at all?).
- Exploratory charts and quick equity-curve visualization.
- Research-phase hypothesis generation.

## Implications

- Vectorbt compresses weeks of manual testing into minutes. This makes it ideal for early-stage research.
- The "portfolio matrix" output reveals parameter sensitivity patterns — flat regions suggest robust strategies; sharp peaks suggest overfitting.
- Results from vectorbt are **not** ready for deployment. Every promising finding must graduate to [[LEAN-Local-Backtesting]] event-driven backtesting with realistic fills, slippage, and transaction costs.
- The vectorized paradigm cannot model order-state, partial fills, queue position, latency, or market impact.

## Failure Modes

- **Overfitting at machine speed:** Sweeping thousands of parameter combinations guarantees finding spurious winners. This is data mining, not discovery. Every vectorbt winner needs event-driven validation with realistic costs.
- **Impossible fill assumptions:** Vectorized backtests typically assume you fill at close of the signal bar, with infinite liquidity and zero slippage. Live trading does not work this way.
- **No state machine:** Cannot model order lifecycle, position tracking across bars, or conditional exits based on prior fills.
- **Survivorship bias and data leakage:** Easy to feed adjusted data without understanding split/dividend/delisting handling. Combine with [[Feature-Leakage-Prevention]] for safeguards.
- **False confidence from speed:** Fast iteration feels productive but can accelerate confirmation bias. The [[Lean-Backtesting-Gotchas]] dataset-look-ahead warning applies equally here.

## Cross-Links

- [[Framework-Comparison-Selection]] — framework selection guide
- [[VectorBT-Reference]] is exploration-only; validation requires [[LEAN-Local-Backtesting]]
- [[Backtrader-Reference]] — event-driven alternative for learning
- [[NautilusTrader-Reference]] — production execution architecture
- [[Feature-Leakage-Prevention]] — must apply before trusting any vectorbt result
- [[Overfit-Detection-Metrics]] — detect when vectorbt sweeps find noise patterns
- [[LEAN-Backtesting-Gotchas]] — pitfalls that also apply to vectorbt research
- [[Schema-Catalog]] — data schemas that vectorbt inputs should conform to
