# Overfit Detection Metrics

**Source**: `02_quant_metrics_catalog/overfit_detection_metrics.md`, `all_quant_metrics_catalog.csv`

## Key Concepts

Overfit detection is the most critical validation layer in systematic trading. Every backtested strategy is the survivor of a selection process — knowing that process determines whether the edge is real or illusory.

### Required Questions Before Deployment

1. **How many strategy variants were tried?** (multiple testing count)
2. **How correlated are the variants?** (independence of trials)
3. **Did validation/test data influence parameter choice?** (look-ahead contamination)
4. **Does the signal survive transaction costs?** (gross vs net edge)
5. **Does performance survive nearby parameter changes?** (parameter cliff detection)
6. **Does performance survive different calendar windows?** (temporal robustness)
7. **Does performance survive different symbols/markets?** (universality test)

### Core Overfit Detection Metrics

| Metric | Purpose | Key Failure |
|---|---|---|
| **Probabilistic Sharpe Ratio (PSR)** | Estimate probability true Sharpe exceeds a benchmark | Requires distribution moment estimates |
| **Deflated Sharpe Ratio (DSR)** | Correct observed Sharpe for selection bias, multiple tests, non-normality | Requires number/correlation of trials |
| **PBO (Probability of Backtest Overfitting)** | Estimate probability that selected strategy is overfit, from CSCV method | Requires careful combinatorial splits |
| **OOS Decay** | `OOS_metric / IS_metric` — edge decay from in-sample to out-of-sample | Can be noisy for short OOS windows |
| **Parameter Stability Score** | Performance variance across nearby parameter grid; detects cliffs | Requires sensible parameter neighborhood |
| **Bootstrap Confidence Interval** | Estimate uncertainty around returns/Sharpe/drawdown via resampling | Resampling scheme must respect time dependence |
| **Newey-West t-stat** | Adjust significance for autocorrelation/heteroskedasticity | Lag choice matters |
| **Minimum Track Record Length** | Required sample length to reject SR threshold | Depends on assumed SR and moments |
| **Multiple Testing Count** | Number of tried variants or effective trials | Often undercounted in manual research |

### Minimum Viable Anti-Overfit Protocol

1. **Lock test window** — never peek.
2. **Run baseline before optimization** — establish a null reference.
3. **Count every variant** — including manually dismissed ones.
4. **Report parameter heatmap** — see [[Heatmap-Parameter]].
5. **Report OOS performance** — not just IS.
6. **Report after-cost performance** — slippage, fees, impact.
7. **Report worst-regime performance** — edge should exist across conditions, not just favorable ones.

## Implications

1. **PBO is the gold standard for backtest validation** — it uses combinatorial cross-validation (CSCV) to estimate the probability that your "best" strategy is actually noise.
2. **DSR corrects for the hidden reality**: if you tried 50 variants, the best Sharpe is biased upward. DSR deflates it using the trial count and non-centrality of the Sharpe distribution.
3. **Parameter cliffs are death sentences** — if a strategy's performance drops sharply when a parameter changes by 5%, it's overfit to noise, not signal.
4. **OOS decay ratio < 0.5** (performance halved out-of-sample) is a major red flag. The exact threshold depends on strategy type, but severe decay = no edge.
5. **Count every variant honestly** — including "I tried that but didn't like the look of it" decisions. Each is a trial that inflates the effective multiple testing burden.

## Failure Modes / Misinterpretations

- **Undercounting trials**: Manual research is the worst offender. Changing one parameter, rerunning, and "seeing it looks bad" still counts as a trial.
- **PBO requires combinatorically complete splits**: If CSCV splits are too few, PBO underestimates overfit probability.
- **DSR assumes independent trials**: Correlated trials (e.g., slight MA length variations) reduce the effective multiple testing burden, but the correlation matrix is hard to estimate.
- **OOS decay noise for short windows**: A single bad luck period in OOS can make a real edge look overfit. Use bootstrap CI on OOS to distinguish noise from decay.
- **Parameter neighborhood must be sensible**: Testing parameters orders of magnitude apart tells you nothing about local stability.
- **Newey-West lag choice**: Too few lags leaves autocorrelation uncorrected; too many loses power. Use data-driven lag selection.
- **PSR vs DSR**: PSR tells you if Sharpe is significantly above a threshold; DSR tells you if the *observed* Sharpe is inflated by selection. Use both.

## Cross-Links

- [[Performance-Metrics]] for the raw metrics being defended
- [[Heatmap-Parameter]] for visual parameter stability analysis
- [[Heatmap-Time-Regime]] for temporal robustness testing
- [[Metric-Formulas]] for underlying metric definitions
- [[Execution-Metrics]] for after-cost performance reporting
