# Deviation Scoring — How Stretched Is It?

## Rule
A good system does NOT say "price is down a lot."
It says: "deviation is extreme relative to current volatility, liquidity, and regime."

## Useful Deviation Measures

```python
z_score = (price - fair_value) / rolling_std

atr_deviation = (price - anchor) / ATR

residual_z = residual_return / residual_volatility

vwap_deviation = (price - VWAP) / intraday_sigma

pair_spread_z = (spread - spread_mean) / spread_std

vol_z = (implied_vol - realized_vol_forecast) / vol_spread_std
```

## Bad vs Better Example

**Bad**: Buy because RSI < 30.

**Better**: Buy only if:
- `residual_z < -2.0`
- Price below VWAP by > 2 intraday sigmas
- Selling volume is capitulation-level
- Price reclaims prior low or VWAP
- Market regime is NOT crash/trend-down

## Key Insight
RSI is a rank-based oscillator — it tells you where price is relative to its own recent range. It does NOT normalize for:
- Current volatility regime
- Sector/factor movement
- Liquidity conditions
- Whether the move is structural or temporary

A z-score of -2.5 in a low-vol regime is very different from -2.5 in a high-vol regime. RSI cannot distinguish these.

## Cross-Links
- [[01-Edge-Sources-And-Fair-Value-Anchors]] — anchors feed deviation calculation
- [[03-Regime-Filter]] — regime determines whether deviation thresholds are valid
- [[06-Data-Infrastructure/regime-detection-features]] — vol regime features
- [[11-Heatmap-Diagnostics]] — PnL by deviation bucket is a required diagnostic
