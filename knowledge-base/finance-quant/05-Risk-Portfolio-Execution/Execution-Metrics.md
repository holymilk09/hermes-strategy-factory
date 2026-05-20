# Execution Metrics

**Source**: `02_quant_metrics_catalog/execution_metrics.md`, `all_quant_metrics_catalog.csv`

## Key Concepts

Execution metrics bridge the gap between theoretical strategy returns and actual realized returns. A strategy that looks profitable with ideal fills may lose money under realistic execution conditions.

### Order-Level Metrics

- **Submission Latency**: decision time to order submission — clock sync between systems required for measurement.
- **Acknowledgment Latency**: submission to broker acknowledgment — network/broker bottleneck detector.
- **Fill Latency**: submission to fill — determines time-based strategy viability.
- **Fill Rate**: `filled_qty / submitted_qty` — market orders trivially fill with high slippage; informative mainly for limit orders.
- **Partial Fill Rate**: orders partially filled / total orders — strategy must handle partial fills gracefully.
- **Cancel Rate**: `cancelled_orders / submitted_orders` — high rate may trigger broker/venue flagging or throttling.
- **Reject Rate**: `rejected_orders / submitted_orders` — any live reject needs immediate review; indicates API/order format issues.

### Slippage and Cost Metrics

- **Average Slippage**: `fill_price - arrival_price` (signed by side) — needs correct arrival price definition.
- **Median Slippage**: robust central tendency measure — less biased by outlier fills than average.
- **Tail Slippage**: e.g., 95th percentile slippage — captures the execution risk that matters (adverse outliers).
- **Effective Spread Paid**: actual spread around fill vs NBBO — needs quote data for measurement.
- **Implementation Shortfall**: `side_sign * (fill_price - decision_price) + fees + market_impact` — the true cost of execution; must include cancellations/partials.
- **Market Impact Proxy**: post-trade price move (signed by side) — confounded by alpha if measured wrong; requires careful event design.

### Strategy-Level Diagnostics

| Problem | Detection Method |
|---|---|
| Strategy profitable only with ideal fills | Compare ideal fills vs spread/slippage/impact fills |
| Slippage worse in high-volatility regimes | Heatmap: slippage by realized volatility bucket (see [[Heatmap-Slippage]]) |
| Excess rejects | Reject rate by broker/order type/symbol |
| Limit orders not filling | Fill rate by distance from mid and time-in-force |
| Live/paper mismatch | Compare paper fill model to actual live fills |

### Queue Position and Microstructure

- **Queue Position Proxy**: limit order fill rank or fill probability — hard without LOB (limit order book) data.
- **Spread**: `ask - bid` or `spread/mid` — quote source and timestamps matter; widening spreads in stress.

## Implications

1. **Implementation shortfall is the gold standard** for measuring true execution cost — includes slippage, fees, impact, and opportunity cost of unfilled orders.
2. **Backtests with ideal fills are fiction** — always compare with realistic slippage models. See [[Heatmap-Slippage]] for stress-testing execution assumptions.
3. **Live vs paper fill model mismatch** is the most common cause of live strategy failure — paper fills are overly optimistic about limit order fill probability.
4. **Tail slippage matters more than average** — one bad fill in a volatile market can wipe out months of average gains.
5. **Reject rates are canary indicators** — a spike in rejects often signals broker issues, API changes, or incorrect order formats before PnL is affected.

## Failure Modes / Misinterpretations

- **Using VWAP arrival price incorrectly**: VWAP arrival price can be manipulated by your own orders (circularity).
- **Market impact confounded with alpha**: If your strategy buys before the price rises, measuring impact as post-trade move conflates your edge with execution cost.
- **Paper fills assume full fill at mid**: Real limit orders don't fill at mid — they fill at the queue position, which depends on order flow.
- **Ignoring partial fills**: A strategy that depends on full fills fails silently when orders are partially filled, creating unintended position sizes.
- **Latency measurement without clock sync**: If decision and acknowledgment timestamps aren't from the same clock, latency is measured wrong.
- **Slippage as negative-only**: Slippage can be favorable (price improvement) in some market conditions; reporting only average masks the variance.

## Minimum Viable Execution Protocol

From [[Overfit-Detection-Metrics]] minimum viable anti-overfit protocol:
- Run before-cost AND after-cost performance.
- Stress-test execution assumptions (see [[Heatmap-Slippage]] promotion rule: "A backtest candidate does not move to live until execution assumptions are stress-tested against worse-than-observed slippage.")

## Cross-Links

- [[Performance-Metrics]] for the return impact of execution costs
- [[Risk-Metrics]] for liquidity-adjusted exposure
- [[Heatmap-Slippage]] for execution stress-testing views
- [[Heatmap-Trade-Failure]] for identifying which trades fail due to execution quality
