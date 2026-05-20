# Epoch Learning Model

Epoch learning means the system learns from controlled evaluation periods. It does not mean constantly changing parameters until the backtest looks good.

## Epoch unit

An epoch is a fixed research/review cycle:

```text
hypothesis -> train -> validate -> test -> deploy/paper -> review -> backlog -> next epoch
```

## Epoch record

- Epoch ID
- Hypothesis ID
- Data version
- Feature version
- Train window
- Validation window
- Test window
- Parameters tried
- Winning parameters
- OOS metrics
- Stress metrics
- Promotion decision
- Weak points
- Next actions

## What can learn

- Feature usefulness
- Parameter stability
- Regime dependency
- Cost sensitivity
- Execution weakness
- Code/data bugs
- Strategy decay

## What must not happen

- Moving test windows after bad results.
- Reusing test set until it passes.
- Adding features without logging trials.
- Promoting a model because one metric improved.
