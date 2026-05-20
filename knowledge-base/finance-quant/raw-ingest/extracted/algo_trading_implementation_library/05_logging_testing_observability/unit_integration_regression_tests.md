# Unit, Integration, and Regression Tests

## Unit test priorities

1. Feature calculation.
2. Signal generation.
3. Sizing.
4. Risk veto.
5. Fill model.
6. Ledger reconciliation.
7. Metrics formulas.

## Integration test: no-op strategy

Expected result:

- No orders.
- No fills.
- Equity unchanged.
- Logs written.
- Metric report generated.

## Integration test: deterministic toy strategy

Expected result:

- Known order count.
- Known fill count.
- Known cash/position/PnL.
- Known metrics.

## Regression test

Store a golden run output. If output changes, require a review note explaining why.
