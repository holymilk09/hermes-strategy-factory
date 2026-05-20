# Papers and Docs Synthesis

Synthesized from 18 embedded PDFs + official docs index in the research papers collection. Key concepts, implications, failure modes, and cross-links.

---

## 1. Overfitting & Backtest Rigor (Bailey / López de Prado cluster)

### Key Concepts
- **Deflated Sharpe Ratio (DSR)**: Adjusts observed Sharpe for multiple-testing. The Sharpe you see is inflated when you tried many variations. DSR = SR_observed / √(1 + (N-1)·ρ) where N is number of trials and ρ is average correlation.
- **Probability of Backtest Overfitting (PBO)**: Uses Combinatorially Symmetric Cross-Validation (CSCV) to estimate the probability that a strategy selected as "best" in-sample will underperform OOS.
- **Sharpe Efficient Frontier**: Geometric analysis showing that strategies cluster along a frontier; most apparent outperformers are within the noise band.
- **Statistical overfitting**: Repeated strategy search inflates apparent performance even when individual tests are "correct."

### Implications for Trading Systems
- Every strategy promotion should report DSR, not raw Sharpe.
- Use CSCV/PBO as a gate before paper trading. If PBO > 30%, do not deploy.
- The number of trials matters as much as the result. Track trial counts rigorously.
- Backtest performance is not evidence of edge — it's evidence you found a lucky configuration. Only OOS validates.

### Failure Modes
- **Trial-count ignorance**: "Sharpe 1.5 over 10 years" means nothing without knowing you tried 200 configurations to find it.
- **Correlation underestimation**: DSR assumes you know ρ (trial correlation). If trials are highly correlated, DSR under-penalizes; if independent, it under-penalizes less.
- **PBO misuse**: Running CSCV once and treating the result as gospel; PBO itself has variance.
- **Cherry-picking metrics**: Promoting on max drawdown or win rate when Sharpe fails DSR.

### Cross-Links
- [[Research-Papers-Index]] — 4 papers in this category
- [[Trading-System-Build-Doctrine]] — Phase 3 validation gates
- [[Strategy-Weak-Point-Detection]] — overfit_risk as a backlog label
- [[Feature-Leakage-Prevention]] — leakage is the #1 cause of apparent-but-false backtest edge

---

## 2. Factor Discovery & Multiple Testing (Harvey/Liu/Zhu, López de Prado Causality Primer)

### Key Concepts
- **Multiple testing correction**: With 300+ published factors, the t-stat threshold for "discovery" should be ~3.0, not 1.96.
- **Causal vs correlational alpha**: Most published factors are correlations without causal mechanism. Factor investing requires causal logic or it degrades once discovered.
- **Falsifiability**: Every factor hypothesis must specify what would disprove it.

### Implications for Trading Systems
- Factor research must pass t > 3.0 hurdle or DSR-adjusted threshold.
- Build causal narratives before testing: "Why should this variable predict returns?" If you can't articulate it, it's likely spurious.
- Track a factor hypothesis registry: hypothesis → evidence → decision (reject/hold/accept).

### Failure Modes
- **p-hacking factor mining**: trying 50 features and reporting the 2 that worked.
- **Publication bias**: the literature only shows factors that worked; negative results are never published.
- **Causal story laundering**: writing a plausible story after finding a significant correlation (post-hoc rationalization).

### Cross-Links
- [[Research-Papers-Index]] — 2 papers
- [[Feature-Priority-Matrix]] — features scored on causal plausibility, not just backtest performance
- [[Trading-System-Build-Doctrine]] — hypothesis specification before testing

---

## 3. Sharpe Estimation (Riondato/Two Sigma, CRAN pbo)

### Key Concepts
- Sharpe ratio estimation has confidence intervals; a 1.5 Sharpe on 3 years of daily data has wide bounds.
- Standard error of Sharpe ≈ 1/√(T) for i.i.d. returns. With non-i.i.d. (autocorrelated) returns, SE is larger.
- CRAN `pbo` package provides reference implementation for CSCV-style diagnostics.

### Implications for Trading Systems
- Report Sharpe confidence intervals, not point estimates.
- Require minimum track length for Sharpe estimates: < 2 years of daily data = unreliable.
- Use the pbo package or equivalent for overfitting diagnostics in backtest evaluation pipeline.

### Failure Modes
- **Ignoring autocorrelation**: strategy returns are often autocorrelated (trend-following especially), which inflates Sharpe and narrows confidence intervals falsely.
- **Small-sample Sharpe worship**: treating a 2.0 Sharpe on 6 months as proof of edge.

### Cross-Links
- [[Research-Papers-Index]] — 2 papers/docs
- [[Overfitting-Backtest-Rigor]] — DSR + Sharpe estimation are complementary

---

## 4. Technical Analysis Foundations (Lo et al., Brock et al.)

### Key Concepts
- **Lo et al. (2000)**: Formalized technical pattern recognition with kernel regression. Showed some patterns contain marginal information, but effect sizes are small and transaction-cost sensitive.
- **Brock et al. (1992)**: Moving average and trading range rules have statistical power on historical equity data, but most profitability disappears after cost adjustment and in out-of-sample periods.

### Implications for Trading Systems
- Technical indicators are baselines, not alphas. Use them as features in broader models, not standalone strategies.
- Always test technical signals after cost adjustment and with walk-forward evaluation.
- Pattern recognition requires statistical formalization — eyeballing charts is not a strategy.

### Failure Modes
- **Retail folklore confusion**: head-and-shoulders and support/resistance may feel meaningful but fail statistical tests.
- **Data-mining indicators**: creating custom indicators by combining standard ones until one works.
- **Ignoring regime dependency**: technical rules may work only in specific volatility/trend regimes.

### Cross-Links
- [[Research-Papers-Index]] — 2 papers
- [[Regime-Detection-Features]] — technical signals need regime gating
- [[Multi-Timeframe-Features]] — indicators work differently across timeframes

---

## 5. Market Stylized Facts (Cont, Ratliff-Crain et al.)

### Key Concepts
- **Cont (2001)**: Returns have fat tails, volatility clustering, absence of autocorrelation (except at very short horizons), volume-volatility correlation, asymmetry (leverage effect).
- **Ratliff-Crain et al. (2023)**: Re-tested Cont's facts on modern intraday data. Most facts still hold, but intraday structure is more complex: microstructure noise, opening/closing effects, and cross-asset spillovers are stronger.

### Implications for Trading Systems
- Any model assuming normal returns is mis-specified. Use fat-tailed distributions or nonparametric methods.
- Volatility clustering means GARCH-class models or realized vol estimators are necessary.
- Intraday strategies must model microstructure effects (bid-ask bounce, opening auction, closing imbalance).
- Stylized facts are constraints on what strategies can work, not strategies themselves.

### Failure Modes
- **Normal-distribution assumption**: VaR and risk models assuming Gaussian returns underestimate tail risk.
- **Ignoring asymmetry**: long-only strategies implicitly assume symmetric risk but losses accelerate faster than gains.
- **Treating stylized facts as stationary**: the shape of tails and volatility clustering may change across regimes.

### Cross-Links
- [[Research-Papers-Index]] — 2 papers
- [[Cross-Asset-Feature-Engineering]] — cross-asset spillovers confirmed by modern stylized facts
- [[Data-Quality-Checks]] — extreme return z-scores detect violations of stylized facts in data

---

## 6. Strategy Development Process (Peterson 2015, 2023)

### Key Concepts
- Strategy development is experiment design, not curve-fitting.
- Frame every parameter choice as a hypothesis with a falsification criterion.
- Separate exploration phase (wide search) from confirmation phase (narrow OOS test).
- Document every trial: data version, parameter set, result, decision.

### Implications for Trading Systems
- Use the epoch model: hypothesis → train → validate → test → deploy/paper → review → backlog → next epoch.
- Track an experiment log: every run has a config hash, data version, and result.
- Use golden-run regression tests: if output changes without intentional change, investigate.

### Failure Modes
- **Exploration without confirmation**: searching widely but never doing a clean OOS test.
- **Moving the goalposts**: changing the test window after seeing bad results.
- **Undocumented trials**: without a trial log, you can't correct for multiple testing.

### Cross-Links
- [[Research-Papers-Index]] — 2 papers
- [[Epoch-Learning-Retraining]] — the epoch model operationalizes Peterson's framework
- [[Trading-System-Build-Doctrine]] — Phases 1-3 are Peterson's experiment design applied to trading systems

---

## 7. Deep Reinforcement Learning for Trading (FinRL, Yang et al., Jiang et al.)

### Key Concepts
- **FinRL (Liu et al. 2020)**: Open-source DRL library for trading. Demonstrates that DRL can work in controlled environments but requires careful design of state space, action space, and reward function.
- **Yang et al. (2018)**: Actor-Critic DRL for stock trading. Shows feasibility but results are highly sensitive to training parameters and market regime.
- **Jiang et al. (2017)**: Portfolio-vector memory approach with online stochastic batch learning. Uses portfolio-level reward rather than single-stock reward.

### Implications for Trading Systems
- DRL is an advanced technique; use only after classical approaches are exhausted.
- Reward function design is critical: Sharpe-based rewards encourage risk management; pure return rewards encourage excessive leverage.
- Epoch-based evaluation is essential for DRL: the model can learn training-set-specific behaviors.
- DRL requires strict separation of training, validation, and test to avoid memorization.

### Failure Modes
- **Overfitting to training market**: DRL memorizes specific price paths rather than learning generalizable patterns.
- **Reward hacking**: optimizing for the reward metric in ways that violate the spirit (e.g., exploiting simulation artifacts).
- **Regime dependence**: DRL trained on bull markets fails catastrophically in bear markets.
- **Reproducibility gap**: DRL results vary significantly with random seeds; single-run reports are unreliable.
- **Non-stationarity**: markets are adversarial, not stationary environments; DRL assumes the environment distribution is stable during training.

### Cross-Links
- [[Research-Papers-Index]] — 3 papers
- [[Epoch-Learning-Retraining]] — DRL requires frequent re-evaluation
- [[Epoch-Learning-Retraining]] — concept drift is the main DRL failure mode
- [[Logging-Audit-Monitoring]] — DRL decisions must be explainable for audit

---

## 8. Tactical / Path-Dependent Investing (López de Prado 2015)

### Key Concepts
- Path-dependent strategies (entry/exit timing, profit-taking, stop-loss) require modeling the entire trade trajectory, not just entry signals.
- OU (Ornstein-Uhlenbeck) process as a model for mean-reverting tactical trades.
- Optimal profit-taking and stop-loss depend on the return process, not fixed percentages.

### Implications for Trading Systems
- Entry signals are only the start; exit mechanics determine net profitability.
- Dynamic stops (volatility-based, trailing) outperform fixed stops for most strategies.
- Backtests must model exit logic with same rigor as entry logic.

### Failure Modes
- **Fixed-percentage stops**: arbitrary levels that don't account for asset volatility.
- **Ignoring slippage on exits**: stop-loss orders in volatile markets suffer worst slippage.
- **Profit-taking truncation**: taking profits too early cuts the tail of winning trades.

### Cross-Links
- [[Research-Papers-Index]] — 1 paper
- [[Trading-System-Build-Doctrine]] — Phase 2 includes exit logic
- [[Logging-Audit-Monitoring]] — live alerts catch exit execution failures
- [[Logging-Audit-Monitoring]] — MAE/MFE analysis validates exit design

---

## Official Documentation Summary

### Backtesting & Live Trading Frameworks
- **QuantConnect/LEAN**: Full-featured cloud + local backtesting. Algorithm Framework (Alpha → Portfolio Construction → Execution) is the modular pattern to follow.
- **NautilusTrader**: Event-driven, supports backtesting and live trading on same codebase. Best for HFT and multi-venue.
- **vectorbt**: Vectorized backtesting for fast exploration. Not event-driven; unsuitable for order-level simulation.
- **Backtrader / Zipline**: Legacy Python backtesters; useful for prototyping but lack modern event-driven architecture.

### Data & Broker APIs
- **Databento**: High-quality historical tick/OHLCV data with unified API. Point-in-time support essential.
- **OpenBB**: Open-source data aggregation layer. Good for research, not for live data feeds.
- **Alpaca**: Paper and live trading API for equities/crypto. REST + WebSocket.
- **IBKR TWS API**: Full broker API but complex. Order submission and management require state machine design.
- **CCXT**: Crypto exchange unification layer. Supports 100+ exchanges with consistent API.

### Cross-Links
- [[Official-Docs-Index]] — full URL catalog
- [[Trading-System-Build-Doctrine]] — framework selection guides Phase 1-2 implementation
- [[Data-Pipeline-Architecture]] — vendor adapters for data sources
