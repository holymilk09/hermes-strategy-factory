# Regime Filter — When Mean Reversion Works vs Dies

## Rule
**Mean reversion is disabled when the market is REPRICING, not merely stretched.**

## Good Regimes (MR Allowed)
- Range-bound market
- Low-to-medium volatility
- Liquid market
- Stable macro backdrop
- Sector dispersion without panic
- Temporary liquidity shock
- Trend intact but pullback stretched

## Bad Regimes (MR Blocked)
- Crash
- Major news repricing
- Earnings disaster
- Credit/liquidity stress
- Strong one-way trend
- Breakdown from long distribution
- Volatility expansion with no reclaim

## Academic Backing
Lo & MacKinlay rejected the random-walk model for weekly returns, but predictability is conditional, unstable, and strategy-dependent. Mean reversion is NOT a universal property — it is regime-dependent.

## Why Our Q1 2025 OOS Failed
SPY dropped ~10% from peak. Our SMA200 regime filter didn't trigger because SPY was still above it. The selloff was too fast — by the time the filter triggered, the damage was done.

**The problem**: SMA200 is a trend-following filter. It doesn't detect REPRICING. We need:
1. Volatility expansion detection (ATR spike, VIX regime)
2. Breadth collapse (advance/decline, % above 50 MA)
3. Credit stress indicators
4. Volume-at-price distribution shifts

## Upgrade Path
Replace binary SMA200 filter with multi-factor regime score:
- VIX level + VIX term structure
- SPY distance from 20/50/200 MA (not just above/below)
- Market breadth
- ATR expansion rate
- Recent drawdown magnitude

## Cross-Links
- [[06-Data-Infrastructure/regime-detection-features]] — regime feature engineering
- [[08-Filters-And-No-Trade-Logic]] — regime filter is one of 8 required filters
- [[05-Risk-Portfolio-Execution/Heatmap-Time-Regime]] — PnL by regime heatmap
