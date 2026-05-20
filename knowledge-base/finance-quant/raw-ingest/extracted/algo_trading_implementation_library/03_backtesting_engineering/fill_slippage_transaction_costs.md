# Fill, Slippage, and Transaction Costs

## Cost layers

1. Commission
2. Exchange fees
3. Spread cost
4. Slippage
5. Market impact
6. Borrow cost
7. Funding/margin cost
8. Tax/friction if relevant

## Fill model levels

| Level | Model | Use |
|---|---|---|
| L0 | ideal close/open fill | debugging only |
| L1 | spread + commission | first realism pass |
| L2 | volatility/liquidity-based slippage | better backtest validation |
| L3 | volume participation + impact | capacity testing |
| L4 | LOB/queue simulation | microstructure/execution research |

## Rule

A strategy that dies after basic spread/slippage was never a strategy. It was a chart artifact.
