# Broker/API Comparison

| Broker/API | Best use | Weakness |
|---|---|---|
| Interactive Brokers | Broad asset access, serious retail/pro account routing | API complexity, TWS/IB Gateway operational overhead |
| Alpaca | Simple stock/options/crypto API-first workflow | Coverage and routing limitations vs IBKR |
| Coinbase Advanced | Regulated US crypto access | Crypto-only and venue-specific constraints |
| CCXT | Multi-exchange crypto research/execution abstraction | Exchange-specific quirks and uneven feature support |
| Tradier | Options-oriented retail API | Requires careful order/chain handling |

## Order adapter requirements

- Normalize order type support.
- Normalize time-in-force.
- Normalize order status.
- Normalize errors.
- Store broker order ID and client order ID.
- Reconcile open orders on startup.
