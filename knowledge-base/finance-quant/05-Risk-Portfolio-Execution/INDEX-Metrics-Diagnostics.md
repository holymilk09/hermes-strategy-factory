# Index: Metrics & Diagnostics

**Pillar**: 05 - Risk, Portfolio & Execution
**Source**: `raw-ingest/extracted/algo_trading_implementation_library/02_quant_metrics_catalog/` (6 files) and `06_heatmaps_diagnostics/` (8 files)
**Ingested**: 2026-05-17

## Notes Overview

### Core Metrics

| Note | Covers | Key Takeaway |
|---|---|---|
| [[Performance-Metrics]] | Return, drawdown, and trade quality metrics | Always report after-cost; pair Sharpe with Pain Ratio and Time Under Water |
| [[Risk-Metrics]] | Exposure, tail risk, and dynamic controls | VaR is insufficient without CVaR; dynamic controls must be automated |
| [[Execution-Metrics]] | Order-level and strategy-level execution quality | Implementation shortfall is the gold standard; tail slippage matters more than average |
| [[Overfit-Detection-Metrics]] | PSR, DSR, PBO, OOS decay, parameter stability | Every backtest is a survivor of selection; count every trial honestly |
| [[Metric-Formulas]] | Exact formulas with usage notes and warnings | IC alignment is the most common error in signal research |

### Heatmap Playbooks

| Note | Covers | Key Takeaway |
|---|---|---|
| [[Heatmap-Playbook-Diagnostics]] | Required heatmaps and rejection criteria | Heatmaps are a rejection tool first — they expose fragility faster than summary stats |
| [[Heatmap-Parameter]] | Parameter sweep and stability analysis | A stable edge has a neighborhood of acceptable cells; single-cell spikes are overfit |
| [[Heatmap-Time-Regime]] | Temporal and regime robustness | Edge is deployable only if the regime filter is measurable before the trade |
| [[Heatmap-Slippage]] | Execution stress-testing | Backtest candidates must survive worse-than-observed slippage before promotion to live |
| [[Heatmap-Instrument]] | Symbol, sector, and liquidity analysis | Broad edges diversify; concentrated edges may be idiosyncratic noise |
| [[Heatmap-Trade-Failure]] | Trade-level diagnostics by entry/exit type | Remove failing trade archetypes only if the filter is knowable at entry time |

## Cross-Reference Diagram

```
Performance-Metrics
  ├── Sharpe, CAGR, Calmar, Sortino → inputs to overfit validation
  ├── Drawdown family → Risk-Metrics for monitoring and control
  ├── Trade quality → Execution-Metrics for cost-aware metrics
  └── Heatmap-Trade-Failure for per-trade diagnostics

Risk-Metrics
  ├── VaR/CVaR → stress scenarios informed by Heatmap-Time-Regime
  ├── Dynamic controls → execution kill switches in Execution-Metrics
  ├── Concentration → Instrument heatmaps for diversification checks
  └── Kelly/sizing → Expectancy from Performance-Metrics

Execution-Metrics
  ├── Slippage/impact → Heatmap-Slippage for stress testing
  ├── Fill quality → Heatmap-Trade-Failure for fill-dependent losses
  ├── Latency → not directly heatmap-visible, but affects all metrics
  └── Live/paper mismatch → Overfit-Detection-Metrics for validation

Overfit-Detection-Metrics
  ├── PSR/DSR → corrections to Performance-Metrics Sharpe values
  ├── Parameter stability → Heatmap-Parameter for visual analysis
  ├── OOS decay → Time-Regime heatmap cross-validation
  ├── Mandatory protocol → requires all heatmaps be reported
  └── Multiple testing → Instrument and Time heatmaps as robustness tests

Metric-Formulas
  └── Underpins all other metric notes with definitions

Heatmap-Playbook-Diagnostics
  ├── Master reference → links to all 5 heatmap-specific notes
  ├── Rejection criteria → gates before live deployment
  └── Execution quality → Heatmap-Slippage + Execution-Metrics

Heatmap-Parameter ──→ Overfit-Detection-Metrics (PBO, DSR)
Heatmap-Time-Regime ──→ Risk-Metrics (regime-dependent risk)
Heatmap-Slippage ──→ Execution-Metrics (slippage diagnostics)
Heatmap-Instrument ──→ Risk-Metrics (concentration checks)
Heatmap-Trade-Failure ──→ Performance-Metrics (trade-level expectancy)
```

## Decision Flow: Strategy Promotion Gate

1. Compute all [[Performance-Metrics]] pre-cost and after-cost.
2. Run [[Overfit-Detection-Metrics]] (PSR, DSR, PBO, OOS decay).
3. Generate all heatmaps per [[Heatmap-Playbook-Diagnostics]]:
   - [[Heatmap-Parameter]] — is there a robust plateau?
   - [[Heatmap-Time-Regime]] — does it work across regimes?
   - [[Heatmap-Slippage]] — does it survive 2x costs?
   - [[Heatmap-Instrument]] — is PnL broad or concentrated?
   - [[Heatmap-Trade-Failure]] — which trade archetypes lose?
4. Apply rejection criteria from [[Heatmap-Playbook-Diagnostics]].
5. If all gates pass → deploy with limits from [[Risk-Metrics]] dynamic controls.

## Anti-Cookie-Cutter Insights

- The **single most dangerous practice** is reporting pre-cost Sharpe without acknowledging it's an inflated upper bound.
- Heatmaps are **diagnostic rejection tools**, not optimization surfaces. Using them to pick the single best cell defeats their purpose.
- **Every manual "try and discard" is a trial** — the overfit detection framework only works if you count everything.
- A strategy with **modest Sharpe (0.8-1.2) but robust across all heatmaps** is far more deployable than a Sharpe 2.5 strategy that breaks under 1.5x slippage.
