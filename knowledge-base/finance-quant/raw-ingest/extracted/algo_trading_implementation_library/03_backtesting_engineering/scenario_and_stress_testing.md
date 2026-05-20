# Scenario and Stress Testing

## Scenario buckets

- High volatility
- Low liquidity
- Rate shock
- Gap open
- Earnings/event shock
- Market crash
- Trend reversal
- Range-bound chop
- API outage
- Broker reject/cancel storm

## Stress knobs

- Double slippage
- Double spread
- Reduce fill rate
- Increase latency
- Delay market data
- Force partial fills
- Remove top winning trades
- Increase borrow/funding cost
- Liquidity cap by participation rate

## Output

Every strategy review should include a stress table. If a strategy only works in the most optimistic execution model, reject it.
