# Architecture Map

```text
raw data -> normalization -> quality checks -> feature store -> signal engine
       -> portfolio construction -> risk engine -> execution engine -> broker/exchange
       -> fills -> position/cash ledger -> metrics -> diagnostics -> review loop
```

## Non-negotiable separations

| Layer | Owns | Must not own |
|---|---|---|
| Data ingestion | Vendor fetch, timestamps, schemas, raw storage | Strategy decisions |
| Feature store | Feature calculation, point-in-time snapshots | Trade execution |
| Signal engine | Directional/relative-value hypotheses | Position sizing, broker orders |
| Portfolio construction | Target weights/position sizes | Market-data fetching |
| Risk engine | Hard limits, vetoes, exposure caps | Alpha generation |
| Execution engine | Order type, timing, routing, retry | Strategy thesis |
| Broker adapter | API translation and state sync | Model training |
| Ledger | Cash, positions, fills, fees, margin | Forward-looking assumptions |
| Metrics engine | Return/risk/trade/execution/ML diagnostics | Altering trades |
| Review loop | Weak-point classification and improvement backlog | Rewriting historical results |

## Principle

The bot should be explainable as a chain of decisions. If a trade cannot be traced from raw data to feature to signal to sizing to risk to order to fill to PnL, the system is not production-ready.
