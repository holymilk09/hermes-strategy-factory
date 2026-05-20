# Framework Selection Matrix

| Framework | Best use | Weakness | Solo-founder fit |
|---|---|---|---|
| QuantConnect / LEAN | Serious multi-asset research/backtesting/live trading | Platform conventions and data costs | High |
| NautilusTrader | Production-grade event-driven architecture and live execution | Heavier engineering | Medium-high if execution-focused |
| vectorbt | Fast vectorized research and large parameter sweeps | Easy to overfit and assume impossible fills | High for exploration only |
| Backtrader | Learning, simple Python strategies, reusable indicators/analyzers | Older ecosystem, weaker production path | Medium |
| Zipline Reloaded | Event-driven equity research lineage | Legacy constraints | Medium |
| Custom engine | Full control | Massive bug surface | Low until you know exactly why |

## Recommendation

Use a hybrid:

1. vectorbt or pandas for early exploration.
2. LEAN for serious event-driven validation.
3. NautilusTrader later if execution/live architecture becomes the core edge.
