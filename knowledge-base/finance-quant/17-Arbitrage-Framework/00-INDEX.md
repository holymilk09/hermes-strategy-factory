# 17. Arbitrage Framework — Index

**Pillar**: Arbitrage & Relative Value Strategies  
**Scope**: Pure arbitrage, statistical arbitrage, and relative-value convergence trades across equities, ETFs, indices, and futures.

---

## Strategy Catalog

### Statistical Arbitrage
| # | Note | Description |
|---|------|-------------|
| 5 | [[5-US-Equity-Pairs-Trading]] | Cointegration-based equity pair mean reversion |
| 6 | [[6-PCA-ETF-Residual-Stat-Arb]] | PCA factor decomposition → residual mean reversion trading |

### ETF/Index Arbitrage
| # | Note | Description |
|---|------|-------------|
| 7 | [[7-ETF-Index-Arbitrage]] | ETF NAV vs. market price premium/discount exploitation |
| 8 | [[8-Index-Futures-Cash-And-Carry]] | Futures vs. spot index cost-of-carry arbitrage |

---

## Cross-Pillar Links
- [[Execution-Cost-Management]] — Transaction cost modeling for all multi-leg arb strategies
- [[Regime-Detection-Markets]] — When arbitrage relationships break down
- [[Risk-Parity-Factor-Neutral]] — Portfolio construction across multiple arb strategies
- [[Kelly-Criterion-Position-Sizing]] — Optimal position sizing for low-volatility arb signals
- [[Borrow-Cost-Lending-Constraints]] — Shorting feasibility and economics

## Notes on Vault Structure
- Notes 1-4 exist elsewhere in the vault or are pure arbitrage types (triangular, covered interest, locational).
- Notes 5-8 are the statistical and equity-focused arb strategies detailed in the Batch 5 research pack.
