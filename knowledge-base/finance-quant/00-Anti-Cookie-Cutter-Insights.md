# Anti-Cookie-Cutter Insights

**Purpose**: This is the highest-value page in the vault. It captures non-obvious lessons that separate sophisticated systems from standard ones.

## Core Thesis
Most "quant" systems fail not because of bad math, but because they optimize for the wrong objective or ignore second-order effects.

## Insights Collected So Far

### 1. **The Backtest-Forward Test Gap is Usually Structural, Not Statistical**
Many strategies look good in backtests because they implicitly assume liquidity and execution that doesn't exist. The real filter isn't statistical significance — it's whether the strategy can survive realistic market impact and adverse selection.

### 2. **Overfitting is Often a Symptom of Poor Problem Definition**
Fitting too many parameters is bad. Fitting the *wrong* parameters because you asked the wrong question is worse. Example: optimizing Sharpe ratio without modeling capacity or drawdown path dependency.

### 3. **Regimes Are Not Just "Bull/Bear"**
The most predictive regime splits often come from market microstructure or order flow characteristics, not just price direction. Volatility regime + liquidity regime + participant regime combinations are usually more powerful.

### 4. **Information Edge Usually Decays Faster Than Most People Model**
Academic factors published in journals often have half-lives measured in months once widely known. Sustainable edges tend to be either:
- Extremely high-frequency (infrastructure heavy)
- Extremely structural (regulatory, tax, or contract-based)
- Or continuously re-discovered through new data features

### 5. **Risk Management is Often Just a Proxy for Good Edge Definition**
Many "risk management" overlays are bandaids for strategies that never had a true edge to begin with. True edge definition already incorporates risk characteristics.

### 6. **Demand Discovery ≠ Trade Selection** (from Qullamaggie analysis)
Buying the strongest mover without a tightness filter = buying extension. The momentum screener identifies where institutional demand is flowing. Tightness confirms whether selling pressure has been absorbed and price is compressed. They are separate signals that must align. Counter-intuitive: Rank-1 momentum with poor tightness = bad setup. Rank-30 with perfect tightness = excellent setup.

### 7. **Volume Dry-Up is Ambiguous Without Preceding Context**
Low volume means nothing alone. It can signal "selling exhausted" or "nobody cares." Only volume contraction WITHIN a sustained uptrend = supply absorption. Without the uptrend context, low volume = dead stock, not a coiling spring.

### 8. **Fixed Thresholds Are Always Wrong in Wrong Regimes**
A screener calibrated to produce 30 candidates in a bull market will produce 3 in a bear market. The correct response to zero candidates is NOT "lower the thresholds" — it's "no setups exist right now, stand aside." Forcing trades when the system finds nothing is a form of self-delusion.

### 9. **Mean Reversion Is a Family of Dislocation Trades, Not an Indicator** (from MR Doctrine)
RSI < 30 → buy is the most common "quant" strategy and also the weakest. Real mean reversion requires: an identifiable edge source (liquidity pressure, forced selling, stop-run failure), a valid fair-value anchor (residual, not raw price), volatility-normalized deviation, exhaustion confirmation, and regime permission. Our engine had RSI(2) < 10 as the entire logic — scoring 1.5/8 on the filter framework. The best mean-reversion systems are mostly filters, not entries.

### 10. **Stretch Is Not an Entry — Exhaustion Is** (from MR Doctrine)
Buying because price is "far from mean" is buying the falling knife. The entry trigger should be evidence that forced selling/buying has EXHAUSTED: undercut-and-reclaim, volume climax then fade, order-flow imbalance flip, VWAP reclaim. Without this, you're predicting the bottom — not reacting to it.

### 11. **Residual Reversion > Raw Price Reversion** (from Avellaneda & Lee)
Professional stat arb doesn't trade "stock dropped, buy it." It removes market/sector/factor movement and trades only the idiosyncratic residual. If a stock drops 3% but its sector ETF dropped 2.8%, the residual is only -0.2% — no signal. Raw RSI would fire; residual z-score would not. This single distinction separates retail from institutional mean reversion.

### 12. **Time Stops Are Non-Negotiable for Mean Reversion** (from MR Doctrine)
If mean reversion doesn't revert on schedule, the thesis is weakening. A daily pullback trade should resolve in 1-3 days. A pairs trade should decay within its estimated half-life. Without a time stop, a short-term mean reversion trade becomes a long-term baghold — the #1 failure mode for retail MR systems.

---

**How to Add**:
- When you notice a pattern that feels "non-obvious" or "contrarian to standard advice", add it here with supporting reasoning.
- Link relevant notes from other sections.

*This page should feel slightly uncomfortable to read. If it doesn't, it's not sharp enough yet.*
