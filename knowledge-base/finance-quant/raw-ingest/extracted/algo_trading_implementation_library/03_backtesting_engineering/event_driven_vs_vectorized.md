# Event-Driven vs Vectorized Backtesting

| Type | Best use | Weakness |
|---|---|---|
| Vectorized | Fast signal exploration and parameter sweeps | Easy to create impossible fills and leakage |
| Event-driven | Realistic execution, order state, live parity | Slower and more code |
| Hybrid | Research with vectorized screening, final validation event-driven | Requires discipline not to promote vector-only results |

## Recommended workflow

1. Explore with vectorized tools.
2. Reject weak signals quickly.
3. Promote only candidates that pass event-driven simulation.
4. Re-run with realistic costs, slippage, and risk limits.
5. Use paper trading before live capital.
