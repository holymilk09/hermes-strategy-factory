# Review and Learn Loop

## Review cadence

- Every backtest run: automatic metric pack.
- Every serious experiment: written review.
- Every epoch: promotion/rejection committee note, even if solo.
- Every paper-trading week: live-vs-backtest delta report.
- Every live-trading day: operational incident review.

## Review questions

1. What changed from the previous run?
2. Did the code/data/config change?
3. What weak point got better?
4. What weak point got worse?
5. Did improvement come from real edge or looser assumptions?
6. Is the result robust to costs?
7. Is the result robust to nearby parameters?
8. Does it survive OOS?
9. What is the next falsification test?

## Learning backlog labels

- `strategy_edge`
- `data_quality`
- `execution`
- `risk`
- `code_bug`
- `overfit_risk`
- `ops_failure`
- `market_regime`
