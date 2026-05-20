# Algorithm Framework Mapping

QuantConnect's Algorithm Framework is the cleanest practical mental model for avoiding strategy spaghetti.

| Serious bot component | LEAN-like module |
|---|---|
| Universe filter | Universe Selection |
| Signal generation | Alpha Model |
| Target sizing | Portfolio Construction Model |
| Risk veto/clipping | Risk Management Model |
| Order placement | Execution Model |
| Portfolio/broker/account state | LEAN engine + brokerage models |

## Recommended solo-founder implementation

Even outside QuantConnect, copy the separation:

```text
universe.py
features.py
alpha.py
portfolio.py
risk.py
execution.py
broker.py
ledger.py
metrics.py
review.py
```

Do not combine alpha, sizing, and execution into one function.
