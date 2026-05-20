# 5. US Equity Pairs Trading

---

## Key Concepts

### Core Mechanism
Identify two US equities with a historically stable price relationship (cointegrated spread). When the spread diverges beyond a statistical threshold, short the outperforming leg and long the underperforming leg. Profit when the spread mean-reverts to its historical equilibrium.

- **Cointegration over correlation**: Correlation measures co-movement; cointegration guarantees a stationary spread (`Y_t - β·X_t`). Use Engle-Granger (2-step OLS + ADF on residuals) or Johansen (multivariate, multi-pair) tests.
- **Hedge ratio (β)**: Estimated via OLS regression `Y_t = α + β·X_t + ε_t`, or more robustly via Total Least Squols (TLS) or Kalman Filter with time-varying β.
- **Trading signal**: Z-score of spread `z_t = (S_t - μ_S) / σ_S`. Entry typically at |z| > 2σ, exit at |z| < 0.5σ or after a stop-loss breach.
- **Rolling estimation**: Hedge ratio and spread statistics re-estimated on rolling windows (e.g., 60–250 trading days) to account for structural breaks.

### Edge Source
- **Behavioral/flow divergence**: Sector-specific news, index rebalancing, or liquidity shocks push one leg away from its partner.
- **Structural relationships**: Supplier-customer pairs, same-industry competitors, dual-listed companies, or spin-off parent/subsidiary naturally track.
- **Inventory/capacity constraints**: Market makers may temporarily widen spreads during stress; statistical mean reversion provides exploitable edge.
- **Speed + precision**: Faster detection of spread divergence + tighter execution cost management = edge over slower participants.

### Specific Formulas

**Spread construction:**
```
S_t = Y_t - β̂ · X_t
```

**Hedge ratio (OLS/EG):**
```
β̂ = Cov(Y, X) / Var(X)
```

**Spread Z-score:**
```
z_t = (S_t - μ_S) / σ_S
where μ_S, σ_S computed on rolling window
```

**Engle-Granger ADF test on residuals:**
```
Δε_t = γε_(t-1) + Σφ_i·Δε_(t-i) + u_t
H₀: γ = 0 (no cointegration)
H₁: γ < 0 (cointegrated)
```

**Half-life of mean reversion (Ornstein-Uhlenbeck):**
```
dS_t = θ(μ - S_t)dt + σ·dW_t
θ estimated from AR(1): S_t = κ + φ·S_(t-1) + η_t
Half-life = -ln(2) / θ  (smaller = faster mean reversion)
```

**Position sizing (Kelly fraction variant):**
```
f* = (μ_spread / σ²_spread) × SR_target
where SR_target accounts for transaction costs
```

**P&L of a pairs trade:**
```
P&L = N · [(Y_t - Y₀) - β̂ · (X_t - X₀)] - 2 · TC
where TC = total round-trip transaction costs
```

### Implications for Trading Systems
- **Screening pipeline**: Run Johansen on all sector-grouped pairs → filter by half-life < 30 days, ADF p-value < 0.05, average spread volatility > threshold → rank by expected Sharpe.
- **Execution is half the edge**: Slippage on two legs simultaneously is the killer. Use limit orders, avoid market hours opens/closes for entries.
- **Regime awareness**: Pairs break down during earnings, M&A announcements, or sector shocks. Maintain event calendars and automatic unwind triggers.
- **Capacity**: Typically $10M–$100M per strategy depending on universe (S&P 500 pairs vs. small-cap). Edge degrades quickly as more capital competes for same trades.
- **Monitoring dashboard**: Track live spread z-scores, rolling β stability, recent half-life changes, and cumulative P&L vs. benchmark.

## Key Implications
- Pairs that have historically cointegrated can **permanently decouple** (structural breaks). Always size for the possibility the spread never returns.
- Diversify across 20-50+ simultaneous pairs to reduce idiosyncratic risk from any single pair blow-up.
- Transaction costs are incurred on **both legs** — the bar for expected spread profit is higher than single-leg trades.

## Failure Modes
- **Cointegration breakdown**: M&A, bankruptcy, regulatory change, or fundamental shift permanently alters the relationship. Spread goes to infinity, not zero.
- **Regime shift in half-life**: Previously fast-reverting pair becomes trending; stop-losses get repeatedly hit.
- **Liquidity mismatch**: One leg is deeply liquid, the other is thinly traded → slippage on the small-cap leg destroys edge.
- **Shorting constraints**: Borrow cost or unavailability on the short leg turns a theoretical edge into a loss (specials in equity lending can charge 20%+ annualized).
- **Overfitting to lookback**: Optimized entry/exit thresholds that work in-sample fail out-of-sample. The "2-sigma entry, 0.5-sigma exit" heuristic often performs worse after costs.
- **Dividend/Capital action mismatches**: Unadjusted dividends, splits, or spin-offs create artificial spread jumps.
- **Latency/execution risk**: Leg execution fails on one side during fast markets. You're left unhedged on a directional bet.

## Cross-Links
- [[PCA-ETF-Residual-Stat-Arb]] — Multi-leg extension, PCA-based factor hedging
- [[ETF-Index-Arbitrage]] — Similar mean-reversion logic but with institutional constraints
- [[Borrow-Cost-Lending-Constraints]] — Shorting feasibility analysis
- [[Cointegration-Testing-Methods]] — Engle-Granger vs. Johansen deep dive
- [[Ornstein-Uhlenbeck-Mean-Reversion]] — OU process parameter estimation
- [[Execution-Cost-Management]] — Slippage modeling for multi-leg trades
- [[Regime-Detection-Markets]] — Identifying when pairs strategies break down
- [[Kelly-Criterion-Position-Sizing]] — Optimal size for spread trades
