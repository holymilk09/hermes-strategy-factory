# Risk & Statistical Modeling — Research Synthesis

**Group**: M — Risk, Probability, Statistical Modeling for Trading
**Source**: `raw-ingest/quant_research_library/M_risk_probability_statistical_modeling/`
**Updated**: 2026-05-17

---

## Summary

Group M contains the statistical hygiene layer for everything else. It covers: the empirical stylized facts of asset returns (fat tails, vol clustering, non-normality), multiple testing corrections for factor research, backtest-overfitting defenses (DSR, PBO), and comprehensive risk modeling frameworks (EVT, copulas, CVaR). The core thesis: **financial data breaks almost every classical statistical assumption, and any system that ignores this will blow up**. Every strategy development pipeline must integrate these controls before deployment.

---

## Key Papers

### Tier 1 — Non-negotiable foundations

| Paper | Authors | Year | Access | Role |
|---|---|---|---|---|
| *Empirical Properties of Asset Returns: Stylized Facts and Statistical Issues* | Rama Cont | 2001 | FREE_LANDING | Foundational survey: fat tails, volatility clustering, gain/loss asymmetry, aggregate-to-normal, absence of autocorrelation in returns but strong autocorrelation in vol/abs returns/volume. The "checklist" for any model that assumes normality or stationarity. |
| *The Deflated Sharpe Ratio* | Bailey & López de Prado | 2014 | FREE_LANDING | Adjusts Sharpe ratio inference for selection bias, non-normality, and multiple trials. Provides a realistic hurdle: if you tried 100 strategies and picked the best, your reported Sharpe is almost certainly overestimated. JPM. |
| *The Probability of Backtest Overfitting* | Bailey, Borwein, López de Prado & Zhu | 2014 | FREE_LANDING | Introduces CSCV (Combinatorially-Symmetric Cross-Validation) and PBO metric. Quantifies: "given your backtest search process, how likely is the best result just luck?" JCF. |
| *Multiple Testing and Cross-Section of Expected Returns* | Harvey, Liu, Zhu | 2016 | PAYWALLED | Shows that the "factor zoo" (300+ published factors) is massively inflated by publication bias and multiple testing. Proposes elevated t-stat thresholds. RFS. |
| *Quantitative Risk Management (Book)* | McNeil, Frey, Embrechts | 2015 | BOOK_SAMPLE | The definitive risk modeling textbook. Covers EVT, copulas, CVaR, credit risk, operational risk. The theoretical foundation for understanding tail risk beyond normal approximations. Princeton UP. |

### Tier 2 — Applied ML & Trading Discipline

| Paper | Authors | Year | Access | Role |
|---|---|---|---|---|
| *Advances in Financial Machine Learning* | López de Prado | 2018 | BOOK_SAMPLE | The practical playbook for financial ML: triple-barrier labeling, purged cross-validation, embargoing, bet sizing, feature importance (MDI, MDA, SFI). Not a stats book per se, but operationalizes statistical hygiene for ML pipelines. |
| *Determining Optimal Trading Rules without Backtesting* | Carr, López de Prado | 2014 | FREE_DIRECT_PDF | Derives trading rules from optimal stopping/control theory rather than brute-force backtest search. Conceptually clean alternative to the search-mine-optimize cycle. arXiv:1408.1159. |
| *Machine Learning for Asset Managers* | López de Prado | 2020 | BOOK_SAMPLE | Shorter, portfolio-focused companion to AFML. Covers fractional differentiation, clustering for diversified bets, hierarchical risk parity. Cambridge UP. |

### Tier 3 — Contemporary Validation

| Paper | Authors | Year | Access | Role |
|---|---|---|---|---|
| *Revisiting the Stylized Facts of Financial Time Series* | Ratliff-Crain et al. | 2023 | FREE_DIRECT_PDF | Modern audit: do Cont's 2001 facts still hold with modern electronic markets and higher-frequency data? Mostly yes, with some microstructure-induced shifts. arXiv:2311.07738. |

---

## Core Theses

1. **Returns Are Not Gaussian** — Cont (2001), confirmed by Ratliff-Crain (2023): returns have power-law tails, volatility clusters, vol-of-vol exists, and absolute returns are autocorrelated. Any model assuming normality is fundamentally mis-specified. This is the single most important fact in quantitative finance.

2. **Multiple Testing Destroys Naive Inference** — Harvey/Liu/Zhu show that with 300+ published factors, many are published at t-stats of 2-3 that would disappear under proper multiple-testing corrections. The effective hurdle is ~3.0+ (or ~6.0 for the entire literature accounting for unpublished tests). DSR and PBO provide the machinery for this correction in practice.

3. **Backtest Overfitting Is the Dominant Failure Mode** — López de Prado's PBO work shows that searching many strategy variants and selecting the best produces strategies that have zero out-of-sample edge, and the probability of this happening can be quantified. CSCV provides the diagnostic tool.

4. **Tail Risk Requires Specialized Modeling** — McNeil/Frey/Embrechts establish that EVT (Extreme Value Theory), copulas (for dependence beyond correlation), and CVaR (expected shortfall) are necessary tools when P/L distributions have heavy tails. Standard VaR using normal approximations understates tail risk by orders of magnitude.

5. **Labeling and Validation in ML Must Be Financial** — López de Prado's AFML shows that standard ML cross-validation fails for financial data because labels overlap in time, creating information leakage. Purged K-fold with embargo periods is mandatory. Triple-barrier labeling captures both profit targets and stop-loss events.

6. **Analytical Rules > Backtest Mining** — Carr/López de Prado's paper offers a principled alternative: derive trading rules from optimal control/stopping theory rather than searching the strategy space. This sidesteps the multiple-testing problem at its root.

---

## Implications for Trading Systems

- **Minimum Sharpe hurdle**: When reporting a backtest Sharpe, deflate it using DSR formula. If you tested N strategies with return correlation ρ, the deflated Sharpe accounts for selection bias. If DSR-adjusted Sharpe < Sharpe threshold (e.g., 1.5), reject.

- **PBO screening**: Before deploying any strategy, run CSCV/PBO analysis. If PBO > 5%, the strategy is likely overfit and should be shelved or simplified.

- **Fat-tail position sizing**: Size positions using CVaR, not standard deviation. If returns have power-law tails, σ is not a coherent risk measure — it's misleading. Use EVT-based tail estimation for sizing.

- **Purged cross-validation for ML**: Never use standard K-fold CV on time series data. Use López de Prado's purged CV with embargo to prevent information leakage across train/test splits.

- **Elevated significance thresholds**: For factor research, use t-stat thresholds of 3.0+ minimum (Harvey/Liu/Zhu). For exploratory signals, use even higher thresholds or Bayesian frameworks.

- **Analytical rule design first**: Before backtest mining, derive the theoretically optimal rule form (e.g., optimal threshold, rebalancing frequency) and then calibrate parameters within that restricted space. This dramatically reduces the multiple-testing burden.

- **Tail hedging**: Given fat-tail reality (Cont), portfolios should incorporate tail protection (options, stop-losses, regime switches) as a structural component, not an afterthought.

---

## Failure Modes

| Failure Mode | Mechanism | Mitigation |
|---|---|---|
| **Gaussian fantasy** — using normal VaR, normal P/L models, normal confidence intervals on fat-tailed data. | Underestimates tail risk by factors of 10-100. | Use EVT, CVaR, or empirical quantile estimation. Cont (2001) is the checklist. |
| **Selection bias illusion** — testing 50 strategies and reporting the best one's Sharpe as if it were a single-test result. | Sharpe is inflated. Real out-of-sample performance is much worse. | Apply DSR. Track total number of trials, not just the winner. |
| **Information leakage in CV** — training on data that overlaps with test labels due to holding periods. | Apparent accuracy is fake; strategy fails live. | Purged CV + embargo. AFML Chapter 7. |
| **Factor zoo navigation** — picking factors from published literature without multiple-testing adjustment. | Most published factors don't survive out-of-sample. | Harvey/Liu/Zhu thresholds. Use only factors with economic grounding + strong out-of-sample evidence. |
| **Correlation breakdown** — diversification that relies on historical correlations fails in crisis regimes. | Copulas and EVT show dependence structures are regime-dependent. | Model conditional correlation; use copulas for tail dependence; stress-test regime shifts. |
| **Backtest mining without PBO** — iterating on strategy parameters until the Sharpe "looks good." | Each iteration compounds overfitting. PBO quantifies this. | CSCV/PBO analysis at every iteration. Pre-commit to parameter ranges before backtesting. |
| **Ignoring Cont's facts** — building a model without checking whether it reproduces basic empirical properties. | Model generates unrealistic P/L distributions. | Checklist: fat tails? vol clustering? leverage effect? If model assumes away any of these, question its realism. |

---

## Cross-Links

- [[ML-Asset-Pricing-Synthesis]] — multiple testing controls for ML factor models; uncertainty-aware predictions for sizing
- [[Options-Volatility-Synthesis]] — model risk in vol models; fat-tail awareness for options pricing; vol-of-vol modeling requires Copula/EVT treatment
- [[Research-Library-Synthesis]] — Lineage 3 (Statistical Hygiene) — the prerequisite for all other lineages
- [[Overfit-Detection-Metrics]] — DSR, PBO, CSCV implementation details
- [[Trading-System-Build-Doctrine]] — strategy development pipeline with statistical guards at every stage
- [[Risk-Portfolio-Execution]] — tail risk sizing, CVaR-based portfolio construction, EVT risk measures
- [[Data-Quality-Checks]] — data anomalies that interact with multiple testing (survivorship bias, look-ahead)

---

## Access Status Note

- **Free landing page**: Cont (2001) via ResearchGate; Bailey/López de Prado papers (DSR, PBO) via SSRN — all legally accessible.
- **Direct PDF**: Carr/López de Prado (2014), Ratliff-Crain (2023) — available on arXiv.
- **Paywalled**: Harvey/Liu/Zhu (RFS) — author preprint may exist on Duke/HBS servers.
- **Books**: McNeil/Frey/Embrechts (Princeton), López de Prado AFML (Wiley), López de Prado ML for Asset Managers (Cambridge) — library access or purchase. AFML and the risk management textbook are the highest-ROI purchases.
