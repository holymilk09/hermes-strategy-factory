# QuantConnect / LEAN Gotchas

- Research notebooks can access data differently from backtests; respect algorithm time.
- Local backtests require correct local data setup or cloud data provider configuration.
- Algorithm Framework modules are powerful, but misuse can obscure where decisions are made.
- Options/futures require extra care around chains, expiries, roll logic, and contract selection.
- Object Store/model transfer should be versioned like any other model artifact.
- Backtest statistics are not a substitute for custom weak-point diagnostics.
