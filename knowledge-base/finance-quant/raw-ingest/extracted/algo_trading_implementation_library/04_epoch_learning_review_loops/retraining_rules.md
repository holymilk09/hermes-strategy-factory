# Retraining Rules

## Retrain only when

- Predefined schedule triggers.
- Feature drift exceeds threshold.
- Signal IC decays below threshold.
- Strategy enters a known different regime.
- New data passes quality checks.

## Do not retrain when

- One bad trade occurs.
- A live drawdown is within expected historical range.
- You are emotionally reacting to losses.
- You want the latest backtest to look better.

## Required retraining output

- New model version
- Old vs new metric comparison
- Feature drift report
- OOS test report
- Promotion/rejection note
