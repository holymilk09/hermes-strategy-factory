# 6. PCA/ETF Residual Statistical Arbitrage

---

## Key Concepts

### Core Mechanism
Decompose a cross-section of asset returns using Principal Component Analysis (PCA) to extract common factors (market, sector, style). Trade the **residuals** — the portion of returns unexplained by these factors — which should behave like idiosyncratic noise with mean-reversion properties.

- **PCA decomposition**: Returns matrix R (n_assets × t_days) → eigendecompose covariance matrix Σ = VΛV' → principal components PC_k = V_k'R.
- **Factor model**: R_t = α + Σ_k β_k · PC_(k,t) + ε_t. The residual ε_t = R_t - Ŕ_t is the tradeable signal.
- **Factor selection**: Retain top K components explaining 70-95% of variance. First PC ≈ market beta; subsequent PCs ≈ sector/style factors.
- **Residual trading**: Go long assets with negative residuals (underpriced relative to factor model) and short assets with positive residuals (overpriced). Neutralize factor exposure by construction.
- **ETF residuals**: For ETF arbitrage specifically, decompose ETF returns vs. basket returns → residual captures pricing inefficiency between fund and NAV.

### Edge Source
- **Factor model misspecification by slow participants**: Many market participants use simple CAPM or 3-factor Fama-French models. A richer PCA model captures additional risk premia, leaving a "cleaner" residual.
- **Overreaction correction**: Market overreacts to asset-specific news relative to factor context. Residuals revert as prices correct.
- **ETF flow-induced mispricing**: Large ETF creations/redemptions cause temporary NAV divergence. PCA isolates this from broader market moves.
- **Systematic dealer/liquidity provider behavior**: Market makers hedge along PCA-identified risk factors, creating predictable patterns in residual space.
- **Capacity in the residual**: The idiosyncratic component is genuinely low-correlation to market, providing diversification benefits that attract institutional capital flow.

### Specific Formulas

**PCA decomposition:**
```
Σ = Cov(R)  [n × n covariance matrix of returns]
Σ · v_k = λ_k · v_k  [eigenvalue problem]
Sort λ_1 ≥ λ_2 ≥ ... ≥ λ_n
K = min{k : Σ_i=1^k λ_i / Σ_j=1^n λ_j > 0.85}
```

**Factor scores (PC time series):**
```
PC_(k,t) = v_k' · R_t = Σ_i v_(k,i) · R_(i,t)
```

**Residual calculation per asset:**
```
ε_(i,t) = R_(i,t) - α_i - Σ_(k=1)^K β_(i,k) · PC_(k,t)
where β_(i,k) = v_(k,i) · λ_k  (loadings)
```

**Residual z-score signal:**
```
z_(i,t) = ε_(i,t) / σ_(ε,i,rolling)
Long assets where z < -threshold, short where z > +threshold
```

**Dollar-neutral portfolio weights:**
```
w_i = -z_(i,t) / Σ_j |z_(j,t)|  [inverse-vol residual weighting]
Ensures Σ w_i = 0 (dollar neutral) and Σ w_i · β_(i,k) ≈ 0 (factor neutral)
```

**Residual Sharpe ratio:**
```
SR_residual = E[Σ w_i · ε_(i,t)] / Std[Σ w_i · ε_(i,t)]
```

**Cumulative variance explained:**
```
CV(K) = Σ_(k=1)^K λ_k / Σ_(k=1)^n λ_k
Rule of thumb: K=1 → ~60-70% (market), K=3-5 → ~80-90% (market+sectors)
K=10-20 → ~95% for S&P 500
```

### Implications for Trading Systems
- **Rolling PCA vs. full sample**: PCA on full history includes stale factors. Use rolling windows (60-250 days) or exponentially weighted covariance for adaptive factor identification.
- **Rebalancing frequency**: Daily to weekly rebalance balances signal freshness against transaction costs. Intraday PCA requires careful covariance estimation to avoid noise.
- **Factor interpretation**: Top PCs don't always map cleanly to known factors. The 4th-5th components might capture obscure sector rotations or style tilts.
- **Risk management**: Even "factor-neutral" portfolios have exposure to higher-order PCs. Monitor residuals of the residuals.
- **Computational cost**: Full PCA on 3000+ US stocks × daily data is fast (seconds). Real-time intraday updating is also feasible with rank-1 update algorithms.
- **ETF residuals application**: Run PCA on ETF vs. its constituent basket returns → residual signals NAV deviation opportunities.

## Key Implications
- **More components ≠ better**: Including too many PCs risks fitting noise. Cross-validate K using out-of-sample residual Sharpe, not in-sample variance explained.
- **Residual clustering**: After major market events, residuals across many assets become correlated. The "diversification" benefit breaks down exactly when it's most needed.
- **Factor drift**: PCA factors change meaning over time. A sector factor today might be a style factor tomorrow. Continuous monitoring is essential.

## Failure Modes
- **Residual non-stationarity**: Residuals may trend rather than revert if the factor model is incomplete or if there's genuine alpha (not just noise).
- **Factor number misspecification**: Too few K → residual contains factor exposure → directional risk. Too many K → residual is noise → no edge.
- **Covariance estimation error**: Sample covariance matrix is noisy when n_assets approaches t_days. Use shrinkage estimators (Ledoit-Wolf) or factor-based covariance.
- **Turnover overload**: High-frequency PCA residual signals generate excessive turnover. Transaction costs swamp residual alpha.
- **Correlation breakdown in crises**: During market stress, all correlations → 1. PCA factors collapse, residuals blow up in ways the model cannot predict.
- **ETF creation/redemption suspension**: Funds trading at premiums when creation is halted (e.g., international ETFs during foreign market closures). Residual appears tradeable but is structural.
- **Index reconstitution**: When baskets change, historical PCA factors become invalid. The "residual" is actually a regime shift, not a tradeable signal.

## Cross-Links
- [[5-US-Equity-Pairs-Trading]] — Two-asset special case of factor residual trading
- [[ETF-Index-Arbitrage]] — ETF residuals applied to NAV/fund pricing
- [[Factor-Model-Risk-Decomposition]] — Fama-French, Carhart, and custom factor models
- [[Covariance-Matrix-Estimation]] — Ledoit-Wolf shrinkage, sample vs. factor-based
- [[Stat-Arb-Portfolio-Construction]] — Dollar-neutral, factor-neutral portfolio assembly
- [[Regime-Detection-Markets]] — When factor models and residuals break down
- [[Transaction-Cost-Turnover-Analysis]] — Whether residual signal exceeds trading friction
- [[PCA-Eigenvalue-Interpretation]] — Interpreting and naming principal components in finance
