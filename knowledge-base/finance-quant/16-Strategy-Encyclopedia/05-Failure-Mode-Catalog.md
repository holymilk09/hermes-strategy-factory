# Failure Mode Catalog

> Comprehensive catalog of 11 failure types that destroy strategy performance. Each failure type includes mechanism, detection methods, and mitigations. Every strategy card must list applicable failure modes in field 16 of the [[Schema and Taxonomy]] card schema.

---

## Core Principle

**Failure modes are not exceptions — they are features of market participation.** Every strategy will encounter conditions where it fails. The question is not "Will this strategy fail?" but "How will this strategy fail, and am I prepared to survive it?"

---

## Failure 1: Overfitting (Curve-Fitting)

**Mechanism**: Parameters or rules are optimized to fit historical noise rather than signal. The strategy appears profitable in backtest because it memorized the past, not because it captured a persistent pattern.

**Symptoms**:
- IS performance >> OOS performance (>2x difference in Sharpe)
- Complex rules with many parameters
- Performance degrades sharply with small parameter changes
- Works on one asset/market only

**Detection**:
- [[Validation Framework]] Tests 5, 6, 7, 9 (IS/OOS split, walk-forward, cross-validation, parameter sensitivity)
- Parameter stability testing
- Deflated Sharpe Ratio (DSR) calculation
- Combinatorial Purged Cross-Validation (CPCV)

**Mitigation**:
- Limit parameters (Occam's razor)
- Use out-of-sample testing
- Apply regularization (in ML models)
- Require parameter neighborhood stability
- Use economic/theoretical justification for each parameter

**Professional View**: Overfitting is the #1 destroyer of retail strategies. In professional quant, it is called "data snooping bias" and is addressed through strict protocols: pre-registration of hypotheses, out-of-sample reserves, and multiple testing corrections.

---

## Failure 2: Look-Ahead Bias (Future Leakage)

**Mechanism**: Strategy uses data that would not have been available at the time of the signal. This includes: using closing price for entry decision during the day, using future data in indicators, point-in-time data not accounting for restatement.

**Symptoms**:
- Backtest works flawlessly, forward test doesn't
- Indicators "repaint" (change past values)
- Entry decisions based on data released after entry time

**Detection**:
- Point-in-time data reconstruction
- Replay-based backtesting (event-driven simulation)
- Indicator audit: check if value at time t uses data from t+1 or later
- Repaint tests: freeze values at each bar, verify no recalculation

**Mitigation**:
- Use event-driven backtesting engine
- Reconstruct databases with point-in-time data
- Audit all indicators for lookahead
- Lag fundamental data by announcement date
- Test with frozen indicator values

**Professional View**: Look-ahead is considered a critical error in professional quant. It is not a "small issue" — it completely invalidates results. Institutional backtesters use dedicated PIT databases and replay engines.

---

## Failure 3: Survivorship Bias

**Mechanism**: Backtest includes only currently-existing assets, ignoring those that were delisted, went bankrupt, or merged. The historical universe is cleaner than it actually was.

**Symptoms**:
- Strategy performs well on current S&P 500 list
- Using "current index constituents" for historical backtest
- No consideration of delisted stocks

**Detection**:
- Use universe with delisted companies included
- Test on historically-accurate universe (point-in-time index lists)
- Compare performance using current vs historical universe

**Mitigation**:
- Use delisting-adjusted databases
- Test on historical universes as they existed at each point in time
- Include bankruptcy/delisting as trading outcome

**Professional View**: Survivorship bias is well-known in academia but still common in retail backtests. The magnitude can be 2-5% annual return bias depending on the universe.

---

## Failure 4: Regime Change (Structural Break)

**Mechanism**: Market dynamics change fundamentally, rendering the strategy's historical edge invalid. The statistical relationship that held in one regime does not hold in another.

**Symptoms**:
- Strategy works for years then suddenly fails
- Performance clustered in specific periods
- Different Sharpe in bull vs bear, high vol vs low vol

**Detection**:
- [[Validation Framework]] Test 12 (Regime Segmentation)
- Rolling performance analysis (Sharpe over trailing windows)
- Structural break tests (Chow test, CUSUM)
- Regime detection (HMM, volatility clustering)

**Mitigation**:
- Build regime detection into the strategy
- Design strategies that adapt or deactivate in wrong regimes
- Use multiple uncorrelated strategies covering different regimes
- Accept that regime change is inevitable; monitor continuously
- Set performance decay triggers for de-activation

**Professional View**: No strategy works in all regimes. Professional systems either (a) are regime-agnostic through diversification or (b) explicitly detect and adapt to regime. Retail traders who claim "my strategy works always" have never tested across regimes.

---

## Failure 5: Transaction Cost Underestimation

**Mechanism**: Backtest uses unrealistically low or zero transaction costs. Real costs include: commission, bid-ask spread, slippage, market impact (for large orders), and timing costs.

**Symptoms**:
- Strategy with high turnover appears very profitable
- Backtest with zero costs shows great returns
- Live trading shows poor performance due to costs

**Detection**:
- [[Validation Framework]] Test 10 (Transaction Cost Analysis)
- Cost analysis at 1x, 2x, 3x estimated costs
- Compare turnover to profitability
- Analyze average trade cost as percentage of average trade profit

**Mitigation**:
- Use realistic cost estimates (commission + 0.5-1 spread + slippage)
- Test performance doubling the estimated costs
- Reduce strategy turnover
- Use limit orders instead of market orders
- Optimize entry timing for lowest-cost execution

**Professional View**: In professional quant, transaction cost modeling is its own specialty. Many strategies that look good in zero-cost backtests are immediately discarded when realistic costs are applied. Market impact (for large orders) is often the most underappreciated cost.

---

## Failure 6: Data Mining / Multiple Testing Bias

**Mechanism**: Testing N strategies or parameter combinations and selecting the best one without adjusting for the number of tests. With enough tests, something will look significant by chance alone.

**Symptoms**:
- "I tested 100 parameter combinations and found the best one"
- Strategy discovered through exhaustive search
- p-value < 0.05 but no adjustment for multiple tests

**Detection**:
- Deflated Sharpe Ratio (DSR)
- Benjamini-Hochberg false discovery rate correction
- White's Reality Check
- Hansen's Superior Predictive Ability test
- Count total number of tests performed

**Mitigation**:
- Pre-register hypotheses before testing
- Apply multiple testing correction
- Use Deflated Sharpe Ratio with number of trials
- Hold out a final test set not used in any optimization
- Report total number of tests attempted

**Professional View**: The number of "dead" strategies that never make it to production far exceeds the number of "live" strategies in professional quant. Multiple testing is rigorously controlled.

---

## Failure 7: Liquidity Risk

**Mechanism**: Strategy assumes it can enter/exit positions at quoted prices, but actual liquidity is insufficient. This includes: thin order books, wide spreads during stress, inability to exit large positions, gap risk.

**Symptoms**:
- Slippage increases during stress
- Backtest fills at mid price but live fills are worse
- Large positions cannot be exited
- Gaps through stop levels

**Detection**:
- Analyze order book depth at trade sizes
- Test fill prices at bid/ask instead of mid
- Simulate large-size trades vs order book
- Analyze gap frequency and gap size
- Test during low-liquidity periods (overnight, holidays)

**Mitigation**:
- Limit position size to fraction of average daily volume (<1-5%)
- Use limit orders with patience
- Avoid holding positions through low-liquidity periods
- Set realistic slippage assumptions
- Test worst-case fill assumptions

**Professional View**: Liquidity is asymmetric — you can enter easily in calm markets but cannot exit easily in stressed markets. Professional funds track their "day-to-liquidate" for each position.

---

## Failure 8: Over-Leverage / Position Sizing Failure

**Mechanism**: Strategy uses excessive leverage or incorrect position sizing, causing ruin before the edge has time to manifest. Even a positive-expectancy strategy will go to zero with too-large bets.

**Symptoms**:
- Large drawdowns that never recover
- Margin calls
- Kelly fraction > 1 (implying infinite leverage)
- Fixed dollar position sizing without volatility adjustment

**Detection**:
- Full Kelly test: if full Kelly > 1, leverage is excessive
- Half-Kelly vs full-Kelly simulation
- Drawdown analysis at various position sizes
- Monte Carlo position sizing tests

**Mitigation**:
- Use fractional Kelly (typically 0.25-0.5 of full Kelly)
- Volatility-adjusted position sizing (ATR, realized vol)
- Set hard maximum position limits
- Portfolio-level risk limits
- Circuit breakers on drawdown

**Professional View**: The most common cause of blow-ups is not bad strategy — it is bad sizing. Professionals use conservative position sizing (often fractional Kelly or risk-budgeting) because capital preservation comes before capital growth.

---

## Failure 9: Correlation Breakdown (Diversification Failure)

**Mechanism**: Strategies or positions thought to be uncorrelated become highly correlated during stress. Diversification benefits disappear exactly when needed most.

**Symptoms**:
- Multiple strategies losing simultaneously
- Correlations that were 0.2 become 0.8 during stress
- "Diversified" portfolio moves as one

**Detection**:
- Stress-test correlation matrix (2008, March 2020)
- Rolling correlation analysis
- Tail dependence analysis (copulas)
- PCA on strategy returns

**Mitigation**:
- Use strategies with different edge sources (not just different indicators)
- Test correlation during stress periods, not just calm periods
- Size positions assuming higher correlation during stress
- Implement portfolio-level risk limits with circuit breakers
- Include crisis alpha strategies

**Professional View**: "In a crisis, all correlations go to 1." This is not a quote — it is a mathematical reality. Diversification works in normal times and fails in stress. Professional risk management assumes this and builds in safety factors.

---

## Failure 10: Model Risk / Specification Error

**Mechanism**: The mathematical model underlying the strategy is misspecified. Wrong distributional assumptions, omitted variables, or incorrect functional forms lead to poor out-of-sample performance.

**Symptoms**:
- Model assumes normal distributions but returns are fat-tailed
- Linear model used for non-linear relationships
- Omitted regime variable
- Features change predictive power over time

**Detection**:
- Residual analysis (normality, autocorrelation tests)
- Out-of-sample forecast accuracy
- Feature drift detection
- Model comparison (does a different specification work better?)

**Mitigation**:
- Test distributional assumptions
- Use non-linear models if relationships are non-linear
- Include regime/state variables
- Regularly re-validate and update models
- Ensemble multiple model specifications
- Maintain model risk documentation

**Professional View**: "All models are wrong, but some are useful." Professionals know their models are approximations and build in robustness through model averaging, stress testing, and continuous monitoring.

---

## Failure 11: Implementation / Operational Risk

**Mechanism**: The strategy concept is sound but implementation errors cause losses. This includes: code bugs, data feed errors, exchange API changes, timezone errors, order routing errors, connectivity failures.

**Symptoms**:
- Backtest and live code produce different signals
- Data feed gaps or errors
- Orders filled incorrectly
- System crashes during trading hours
- Wrong timestamps in order records

**Detection**:
- Unit tests for all signal functions
- Signal comparison: backtest vs live code on same data
- Dry run / paper trading before going live
- Data quality monitoring (gaps, outliers, zero volume)
- Automated reconciliation

**Mitigation**:
- Automated testing pipeline
- Redundant systems and data feeds
- Circuit breakers and kill switches
- Manual override capability
- Logging and audit trail for every action
- Start with small capital and scale up gradually

**Professional View**: Operational risk is responsible for more trading losses than strategy risk in many funds. A bad signal loses money gradually; a bug can lose all capital in minutes.

---

## Failure Mode Quick Reference

| Failure | When It Manifests | Worst-Case | Detection Priority |
|---|---|---|---|
| Overfitting | OOS testing | Complete strategy invalidation | HIGH |
| Look-Ahead Bias | Initial backtest | Complete strategy invalidation | CRITICAL |
| Survivorship Bias | Universe selection | 2-5% annual return bias | HIGH |
| Regime Change | Live trading after stable period | Sudden strategy failure | HIGH |
| Transaction Cost Underestimation | Live execution | Strategy turns unprofitable | HIGH |
| Data Mining | Strategy discovery | False discovery of edge | HIGH |
| Liquidity Risk | Stress / large positions | Unable to exit, amplified losses | MEDIUM |
| Over-Leverage | Consecutive losses | Account blow-up | CRITICAL |
| Correlation Breakdown | Crisis events | Diversification fails exactly when needed | MEDIUM |
| Model Risk | Ongoing | Gradual degradation | MEDIUM |
| Implementation Risk | Initial deployment | Catastrophic bug | CRITICAL |

---

## Anti-Cookie-Cutter Insight

The most dangerous failure mode is **the one you don't know about**. A single critical failure (look-ahead, blow-up through over-leverage, operational bug) can destroy a career. The failure mode catalog is not about being pessimistic — it is about being prepared. Every strategy card must list applicable failure modes. If you cannot name how your strategy will fail, you don't understand your strategy.

---

## Cross-References
- [[Schema and Taxonomy]] — Strategy card field 16: failure_modes[]
- [[Validation Framework]] — Tests designed to detect specific failure modes
- [[Feature Engineering Catalog]] — Leakage failure in feature pipelines
- [[Professional Equivalent Map]] — How professionals handle failure modes
- [[Master Index]] — Full encyclopedia overview
