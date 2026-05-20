# Production Trading Checklist

## Pre-run

- Config committed and hashed.
- Universe fixed.
- Calendar fixed.
- Data source/version recorded.
- Model version recorded.
- Risk limits loaded.
- Broker account state reconciled.
- Open orders reconciled.
- Market session schedule checked.
- News/event blocklist checked if relevant.

## During run

- Heartbeat alive.
- Data latency below threshold.
- Broker API reachable.
- Position delta within allowed tolerance.
- Order count below max per minute/day.
- Notional exposure under limit.
- Drawdown under stop threshold.
- Slippage under warning threshold.
- No duplicate order IDs.
- All order state transitions valid.

## Post-run

- Fill ledger reconciles with broker fills.
- Cash ledger reconciles with broker cash.
- Equity curve generated.
- Slippage report generated.
- Trade attribution generated.
- Weakest symbols/time windows/regimes flagged.
- Any system incident categorized.
- Review note written before next parameter change.
