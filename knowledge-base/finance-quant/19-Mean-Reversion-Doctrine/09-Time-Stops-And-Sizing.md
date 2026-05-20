# Time Stops and Position Sizing

## Time Stop Rule
**If mean reversion does not revert on schedule, the thesis is weakening.**

Mean reversion should NOT become a long-term baghold.

### Time Stops by Strategy Type

| Strategy Type | Time Stop |
|---|---|
| Intraday VWAP reversion | Exit by session close |
| Daily pullback reversion | Exit if no reclaim within 1-3 days |
| Pairs / stat arb | Exit if spread doesn't decay within expected half-life |
| Options vol reversion | Exit before event or after vol normalization |

### For Residual / Stat Arb
- Estimate half-life of mean reversion (Ornstein-Uhlenbeck)
- If spread does not start reverting within expected half-life → reduce or exit
- Our daily MR should have a 3-5 day time stop maximum

## Position Sizing

**Do NOT size every mean-reversion trade equally.**

Size based on:
- Distance to stop
- Expected adverse excursion
- Liquidity
- Spread
- Volatility
- Setup score (how many filters passed)
- Regime score
- Correlation with other positions
- News risk
- Borrow risk (for shorts)

### For Long-Only Pullback Trades
```
risk_per_trade = 0.25% to 1.00% of account
stop = below sweep low / base low / reclaim failure level
size = account_risk / stop_distance
```

### For Pairs / Stat Arb
Size by: gross exposure, net exposure, beta neutrality, sector neutrality, spread volatility.

### Averaging Down
Do NOT average down unless the system explicitly has:
- Scale-in levels defined
- Max position defined
- Invalidation point defined
- Portfolio exposure limit defined

## Cross-Links
- [[08-Filters-And-No-Trade-Logic]] — setup score determines sizing
- [[05-Risk-Portfolio-Execution/Risk-Metrics]] — risk per trade formulas
- [[12-Strategy-Template-Config]] — sizing params in config
