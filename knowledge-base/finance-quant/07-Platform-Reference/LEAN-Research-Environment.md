# LEAN Research Environment

The LEAN/QuantConnect research environment (QuantBook) provides notebook-based exploration for hypothesis generation, feature inspection, model training, and sanity checks.

## Core Concepts

- **QuantBook (notebooks):** Jupyter-based research environment connected to LEAN's data infrastructure.
- **Uses for notebooks:**
  - Hypothesis exploration — "does this signal have predictive power?"
  - Feature inspection — examine distributions, correlations, missing data patterns.
  - Distribution analysis — check stationarity, skewness, kurtosis, outlier rates.
  - Plotting — equity curves, signal scatter, correlation matrices.
  - Training ML models — fit models, cross-validate, select hyperparameters.
  - Quick sanity checks — verify data access, test signal computation on a sample.
- **Do NOT use notebooks for:**
  - Final strategy implementation — notebooks are not deployable or reproducible.
  - Live trading logic — notebooks cannot handle live data streaming or order management.
  - Untracked parameter changes — changing parameters in a notebook without versioning destroys reproducibility.
  - Hidden feature transformations — transformations must be explicit and tested.

## The Notebook-to-Code Rule

**Every useful notebook result must become a versioned function or module with tests before it can enter the backtest engine.**

This rule exists because:
1. Notebooks don't enforce testing — you can't be sure a signal works the same way twice.
2. Notebooks hide transformations — inline code makes it difficult to audit what was done.
3. Notebooks don't version parameters — changing a threshold without recording it makes past results irreproducible.
4. Notebooks access data differently from backtests [[LEAN-Backtesting-Gotchas]].

## Implications

- Use notebooks as a sketchpad, not as a production tool. Every insight should be promulgated from notebook → module → test → backtest.
- The research environment is where [[VectorBT-Reference]] fits naturally: use vectorbt or pandas in notebooks for fast hypothesis screening, then extract validated signals into modules.
- Notebook results that look good should be viewed skeptically: the notebook has access to full history, which makes look-ahead bias easy to commit.
- Training ML models in notebooks is fine, but the trained model (artifacts, weights, parameters) must be versioned in the Object Store with the same care as code [[LEAN-Backtesting-Gotchas]].
- Feature transformations discovered in notebooks should be extracted into the [[Schema-Catalog]] so they're formally typed and validated.

## Failure Modes

- **Look-ahead bias via notebook data access:** Notebooks access full historical data at once. It's trivially easy to accidentally use future data. Always test the signal in the backtest engine, and compare results to notebook results — any significant improvement in notebooks usually means look-ahead bias [[Feature-Leakage-Prevention]].
- **Parameter drift in notebooks:** Changing a threshold, lookback window, or filter in a notebook without recording the change makes every prior result suspect. Always version parameter changes.
- **Unreproducible explorations:** Notebooks without cells executed in order produce different outputs each time. This makes it impossible to reproduce research findings. Always run notebooks top-to-bottom and commit executed versions.
- **Feature leakage in transformations:** Hidden transformations (normalization, imputation, lagging) in notebook cells can leak information. Extract to explicit, tested functions.
- **ML model overfitting in research:** Training an ML model in a notebook with full historical access and then deploying it in a time-forward backtest will almost certainly underperform. Time-series cross-validation is mandatory.
- **Dashboard paralysis:** OpenBB and research tools can produce overwhelming amounts of data. Focus exploration on specific hypotheses, not general "let's look at everything."

## Cross-Links

- [[LEAN-Reference]] — LEAN platform index and study order
- [[LEAN-Local-Backtesting]] — next step after notebook exploration
- [[LEAN-Backtesting-Gotchas]] — notebook data access vs backtest data access divergence
- [[LEAN-Algorithm-Framework-Mapping]] — how notebook discoveries become modules
- [[VectorBT-Reference]] — vectorbt fits naturally in the notebook research workflow
- [[Feature-Leakage-Prevention]] — patterns that cause look-ahead bias
- [[Overfit-Detection-Metrics]] — detect when notebook results are noise
- [[Logging-Audit-Monitoring]] — tests required before notebook code enters backtest
