# LEAN Backtesting Gotchas

Common pitfalls and failure modes when using QuantConnect/LEAN for backtesting and live trading.

## Core Gotchas

### 1. Research Notebook Data Access vs Backtest Data Access

**Problem:** Research notebooks (QuantBook) can access data differently from backtests. Notebooks can load full historical datasets at once, but algorithms only see data at the simulated time moment.

**Implication:** A signal that looks good in a notebook may use future knowledge when deployed in the algorithm. Always respect algorithm time — in the backtest engine, your strategy only knows what happened up to the current bar.

**Mitigation:** Test the same signal in both notebook AND backtest. Compare results. If the notebook results are significantly better, you likely have look-ahead bias.

### 2. Local Data Setup Requirements

**Problem:** Local backtests require correct local data setup or cloud data provider configuration. Missing, misformatted, or incomplete data produces silent errors.

**Implication:** A backtest with no errors can still be wrong if data is missing for certain dates or symbols. This is worse than a crash because it produces false confidence.

**Mitigation:** Always verify data completeness: check date ranges, symbol coverage, and data point counts before trusting backtest results. [[Data-Quality-Checks]]

### 3. Algorithm Framework Module Misuse

**Problem:** LEAN's Algorithm Framework modules are powerful, but misuse can obscure where decisions are made. When alpha, portfolio construction, risk, and execution modules interact in unexpected ways, debugging becomes extremely difficult.

**Implication:** The whole point of the framework is modularity and clarity. If you're not sure which module produced an order, you're using the framework wrong.

**Mitigation:** Follow the mapping in [[LEAN-Algorithm-Framework-Mapping]]. Keep modules focused on their single responsibility. Log decisions at module boundaries.

### 4. Options/Futures Complexity

**Problem:** Options and futures require extra care around chains, expiries, roll logic, and contract selection.

**Implication:** A strategy that works on equity bars may produce completely different results on options due to chain selection, expiry timing, and roll mechanics.

**Mitigation:** Explicitly test chain selection logic. Document roll decisions. Validate expiry handling. Never assume "the first contract" is the right one.

### 5. Model Transfer and Versioning

**Problem:** Object Store/model transfer should be versioned like any model artifact. A model trained on different data version or with different parameters will produce different results.

**Implication:** If you upgrade a model without versioning the old one, you can't rollback. More importantly, you can't reproduce backtests that used the old model.

**Mitigation:** Treat ML models like code: version control, hash inputs, log the model version in every backtest manifest.

### 6. Backtest Statistics Illusion

**Problem:** Backtest statistics (Sharpe ratio, max drawdown, total returns) are not a substitute for custom weak-point diagnostics.

**Implication:** A strategy with Sharpe 2.0 can still fail catastrophically in a specific regime, on a specific asset, or with a specific parameter. Standard statistics are averages that hide worst-case scenarios.

**Mitigation:** Add [[Heatmap-Playbook-Diagnostics]] for custom diagnostics. Check per-regime performance, per-asset performance, and parameter sensitivity. [[Overfit-Detection-Metrics]]

## Anti-Cookie-Cutter Insight

The deepest gotcha in LEAN is that its greatest strength — the Algorithm Framework's modularity — is also its greatest weakness. Clean separation of concerns means errors can propagate silently across module boundaries. An alpha model that produces valid signals, a portfolio model that sizes positions correctly, and an execution model that places orders properly can together produce a disastrous outcome because no single module sees the full picture. The framework prevents spaghetti code but can create systemic blind spots if module-level validation is not performed independently.

## Cross-Links

- [[LEAN-Reference]] — LEAN platform index
- [[LEAN-Local-Backtesting]] — local backtesting workflow
- [[LEAN-Live-Trading-Ops]] — live trading checklist
- [[LEAN-Research-Environment]] — when and how to use notebooks
- [[LEAN-Algorithm-Framework-Mapping]] — module discipline
- [[Feature-Leakage-Prevention]] — look-ahead bias and data leakage patterns
- [[Overfit-Detection-Metrics]] — detect when backtest results are noise
- [[Data-Quality-Checks]] — validate local data before trusting results
- [[Heatmap-Playbook-Diagnostics]] — custom diagnostics beyond standard statistics
- [[VectorBT-Reference]] — vectorbt's overfitting warning applies to LEAN too
