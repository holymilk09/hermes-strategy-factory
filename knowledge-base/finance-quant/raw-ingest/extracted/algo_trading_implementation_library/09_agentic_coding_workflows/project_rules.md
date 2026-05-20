# Project Rules for Agentic Coding

## Hard rules

1. Do not create new files unless the requested change requires it.
2. Do not refactor protected paths without explicit instruction.
3. Do not change strategy assumptions silently.
4. Do not change data windows silently.
5. Do not change transaction costs silently.
6. Do not modify test windows after seeing results.
7. Every backtest run must produce a run manifest.
8. Every metric formula must be centralized.
9. Every strategy must use the same module contract.
10. Every bug fix must include a regression test.

## Protected paths

```text
src/core/contracts.py
src/core/ledger.py
src/core/risk.py
src/core/metrics.py
configs/
data_versions/
reports/
```
