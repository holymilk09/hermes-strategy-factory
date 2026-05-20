# Research Environment Workflow

## Use notebooks for

- Hypothesis exploration.
- Feature inspection.
- Distribution analysis.
- Plotting.
- Training ML models.
- Quick sanity checks.

## Do not use notebooks for

- Final strategy implementation.
- Live trading logic.
- Untracked parameter changes.
- Hidden feature transformations.

## Notebook-to-code rule

Every useful notebook result must become a versioned function or module with tests before it can enter the backtest engine.
