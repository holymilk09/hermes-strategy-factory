# Live Trading Ops Notes

## Required live-state checks

- Broker connected.
- Market data connected.
- Open orders reconciled.
- Positions reconciled.
- Cash/margin reconciled.
- Risk limits loaded.
- Kill switch tested.
- Heartbeat emitting.

## Paper/live difference checklist

- Paper fills are often too clean.
- Paper may not reproduce partial fills.
- API rate limits still matter.
- Live rejected orders reveal invalid assumptions.
- Slippage must be measured, not guessed.
