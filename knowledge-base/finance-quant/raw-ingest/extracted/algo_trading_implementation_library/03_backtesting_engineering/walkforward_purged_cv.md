# Walk-Forward and Purged Cross-Validation

## Walk-forward structure

```text
train window -> validation window -> test window -> advance -> repeat
```

Use this for strategies that need periodic retraining or parameter selection.

## Purging and embargo

When labels overlap in time, standard cross-validation leaks information across folds. Purging removes training samples whose label windows overlap validation/test samples. Embargo adds a buffer after validation/test windows before training samples are allowed.

## Promotion rule

A strategy is not promoted because one test passed. It is promoted only if:

- OOS expectancy is positive after costs.
- Drawdown is tolerable.
- Parameter heatmap is stable.
- Worst-regime performance is known.
- Execution assumptions are plausible.
