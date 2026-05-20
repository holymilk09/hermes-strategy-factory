# Execution Metrics

## Order-level metrics

- Submission latency
- Acknowledgment latency
- Fill latency
- Fill rate
- Partial fill rate
- Cancel rate
- Reject rate
- Average slippage
- Median slippage
- Tail slippage
- Effective spread paid
- Implementation shortfall
- Market impact proxy

## Strategy-level execution diagnostics

| Problem | Detection |
|---|---|
| Strategy profitable only with ideal fills | compare ideal fills vs spread/slippage/impact fills |
| Slippage worse in high-volatility regimes | heatmap slippage by realized volatility bucket |
| Excess rejects | reject rate by broker/order type/symbol |
| Limit orders not filling | fill rate by distance from mid and time-in-force |
| Live/paper mismatch | compare paper fill model to actual live fills |
