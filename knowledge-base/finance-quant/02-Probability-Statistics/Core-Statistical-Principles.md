# Probability, Statistics & Inference — Foundational Concepts

**Purpose**: Statistical reasoning foundations for trading system design. This section captures probability theory and inference concepts that underpin strategy validation, risk modeling, and edge discovery.

---

## Core Statistical Principles for Trading

### Bayesian Inference in Markets
- **Concept**: Update priors with new evidence rather than relying on point estimates
- **Application**: Regime detection, position sizing under uncertainty, model averaging
- **Failure Mode**: Uninformative prions mask regime shifts; over-confident prions prevent adaptation
- **Cross-linked**: [[Risk-Metrics]], [[Bayesian-Regime-Model]] (from ML strategies), [[Epoch-Learning-Retraining]]

### Multiple Testing and False Discovery
- **Concept**: Testing N strategies inflates Type I error rate; must correct or use Deflated Sharpe Ratio
- **Key Papers**: Bailey/Lopez de Prado DSR, Harvey/Liu/Zhu cross-section study, Sullivan/Timmermann/White bootstrap
- **Application**: Strategy selection from large candidate pools, factor mining validation
- **Failure Mode**: Naive Sharpe comparison overstates performance; publication bias in factor research
- **Cross-linked**: [[Overfit-Detection-Metrics]], [[DSR-Formula]], [[Metric-Formulas]], [[Risk-Statistical-Modeling-Synthesis]]

### Time Series Properties and Stationarity
- **Concept**: Financial returns exhibit fat tails, volatility clustering, mean reversion at different scales
- **Key Reference**: Cont (2001) stylized facts, Ratliff-Crain et al. (2023) modern validation
- **Application**: Model selection must account for non-stationarity; rolling stats preferred to global statistics
- **Failure Mode**: Assuming normality → underestimating tail risk; assuming stationarity → model breaks in regime shifts
- **Cross-linked**: [[Risk-Statistical-Modeling-Synthesis]], [[Data-Quality-Checks]], [[Feature-Engineering-Catalog]]

### Causal Inference vs Correlation
- **Concept**: Correlation between features and returns does not imply causation; spurious relationships abound
- **Application**: Feature selection should prioritize causal mechanisms (order flow → price impact) over spurious correlations
- **Failure Mode**: Data mining → features that correlate by chance in training data but fail out-of-sample
- **Cross-linked**: [[Feature-Leakage-Prevention]], [[Overfit-Detection-Metrics]], [[Feature-Engineering-Catalog]]

### Information Theory for Finance
- **Concept**: Shannon entropy measures uncertainty; mutual information measures predictive relationship strength
- **Application**: Feature selection (max mutual information with returns), regime uncertainty measurement, portfolio diversification (entropy of returns)
- **Failure Mode**: Estimating entropy/MI from small samples → unreliable measurements
- **Cross-linked**: [[Feature-Engineering-Catalog]], [[Entropy-Concepts]]

---

## Hypothesis Testing for Trading

### The Testing Pipeline
1. **Null hypothesis**: Strategy has no edge (expected return = 0 or benchmark return)
2. **Test statistic**: Sharpe ratio, t-statistic, or other performance measure
3. **P-value under null**: Probability of observing statistic if null is true
4. **Correction**: Adjust for multiple testing (Bonferroni, FDR, DSR)
5. **Decision**: Reject null only if corrected p-value < significance level

### Key Anti-Cookie-Cutter Insight
Standard hypothesis testing assumes independence of tests. In strategy research, this assumption is routinely violated:
- Strategies tested sequentially share data and insights from previous tests
- Parameter sweeps test the same strategy hundreds of times
- Feature selection uses the same data for both selection and evaluation

**Result**: Nominal p-values are meaningless without explicit multiple testing correction.

---

## Minimum Bar for Statistical Claims

| Claim | Required Evidence |
|---|---|
| "Strategy has positive expectancy" | OOS Sharpe > 0 after costs, DSR-adjusted |
| "Feature is predictive" | Mutual information significant, survives purged CV |
| "Strategy beats benchmark" | t-test with regime-stratified returns, multiple testing correction |
| "Model improves predictions" | Beats naive + linear + random baselines with statistical significance |
| "Edge persists" | Live/paper comparison with reconciliation, parameter stability |

---

*Cross-linked: [[Overfit-Detection-Metrics]], [[Risk-Statistical-Modeling-Synthesis]], [[Validation-Framework]], [[Trading-System-Build-Doctrine]], [[Feature-Engineering-Catalog]]*
