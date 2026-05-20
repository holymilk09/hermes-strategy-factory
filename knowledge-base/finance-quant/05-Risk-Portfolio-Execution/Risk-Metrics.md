# Risk Metrics

**Source**: `02_quant_metrics_catalog/risk_metrics.md`, `all_quant_metrics_catalog.csv`

## Key Concepts

Risk metrics go beyond volatility to capture the full spectrum of portfolio vulnerability: exposure concentration, tail losses, and dynamic de-risking controls.

### Portfolio Risk

- **Gross Exposure**: `sum(abs(position_values)) / equity` — total leverage footprint; does not show net directional risk.
- **Net Exposure**: `sum(position_values) / equity` — directional market exposure; market beta may differ from net exposure.
- **Leverage**: borrowed capital multiplier — amplifies both gains and losses; margin calls create non-linear risk.
- **Margin Utilization**: fraction of margin used — high utilization = fragility to adverse moves.
- **Concentration / Herfindahl Index**: `sum(weight_i²)` — single-number concentration measure; weights must include hidden factor exposure.
- **Sector/Factor Exposure**: aggregated exposure by sector or risk factor — diversification illusion when factors are correlated in crisis.
- **Correlation Concentration**: average pairwise correlation — diversification breaks when correlations spike to 1 during stress.
- **Liquidity-Adjusted Exposure**: exposure weighted by average daily volume — positions in illiquid names carry hidden exit costs.

### Loss Risk

- **Max Drawdown**: worst peak-to-trough loss — one sample path only; actual future DD may be worse.
- **Expected Shortfall / CVaR**: `mean(losses beyond VaR)` — average tail loss; needs enough tail observations for reliability.
- **VaR**: `quantile(losses, confidence_level)` — loss threshold at X% confidence; critically, does *not* show the tail beyond the threshold.
- **Stress Loss**: portfolio loss under scenario shock — scenario design is subjective; must include historical and hypothetical scenarios.
- **Gap Risk**: overnight/intraday price gaps — especially severe in earnings, macro announcements, or low-liquidity instruments.
- **Risk of Ruin**: probability capital falls below ruin threshold — requires distribution assumptions; useful for position sizing limits.
- **Worst-Day/Week/Month**: maximum observed loss at each horizon — sets realistic expectations for position limits.

### Dynamic Risk Controls

- **Volatility Targeting**: scale position size by inverse of realized volatility — stabilizes risk contribution but can increase turnover.
- **Drawdown-Based De-Risking**: reduce exposure when portfolio falls X% below peak — prevents compounding losses but may cut at the bottom.
- **Position Cap by Liquidity**: max position as % of ADV (average daily volume) — prevents market impact risk.
- **Symbol/Sector/Max Order Size Caps**: concentration limits — diversification enforcement.
- **Max Daily Loss**: circuit breaker per day — prevents blowup from cascading errors or extreme events.
- **Kill Switch**: emergency stop — must be executable without human intervention (automated).

## Implications

1. **VaR is necessary but insufficient** — always pair VaR with Expected Shortfall (CVaR) because the tail beyond VaR is where blowups happen.
2. **Gross/Net exposure pair** — net exposure tells you directional view; gross exposure tells you total risk footprint. A market-neutral strategy with 300% gross exposure still has severe risk.
3. **Concentration risk is multiplicative in crises** — correlations spike to 1.0 under stress, making diversification metrics useless exactly when needed.
4. **Dynamic controls should be automated** — manual risk management fails under stress due to psychological paralysis.
5. **Liquidity-adjusted exposure > nominal exposure** — a $1M position in a $100M ADV stock is very different from the same position in a $5M ADV stock.

## Failure Modes / Misinterpretations

- **VaR underestimation from short samples**: If your sample lacks a crisis period, VaR will be systematically wrong.
- **Correlation assumptions are fragile**: Correlations are regime-dependent; see [[Heatmap-Time-Regime]] for regime-aware diagnostics.
- **Drawdown controls that trigger at the bottom**: If your de-risking triggers after a crash, you sell at the worst time. Use forward-looking vol targeting instead.
- **Herfindahl of weights misses factor concentration**: A portfolio of 10 uncorrelated stocks across sectors may all load on the same hidden factor (e.g., quality).
- **Kelly Fraction misuse**: Full Kelly is theoretically optimal but practically dangerous for real-world non-stationary returns. Always use fractional Kelly (0.25–0.5x).
- **Risk of ruin assumes stationarity**: Market regime shifts change the distribution, making historical ruin probability inapplicable.

## Cross-Links

- [[Performance-Metrics]] for drawdown-based performance ratios
- [[Execution-Metrics]] for liquidity and slippage impacts on risk
- [[Overfit-Detection-Metrics]] for stress-testing risk under parameter uncertainty
- [[Heatmap-Parameter]] for parameter stability checks
- [[Heatmap-Time-Regime]] for regime-dependent risk behavior
