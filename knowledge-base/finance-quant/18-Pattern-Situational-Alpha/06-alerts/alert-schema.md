---
title: Pattern Alert Schema
pillar: 18
---

# Pattern Alert Output Schema

alert_type: pattern_candidate
pattern_family: e.g. first_pullback_after_momentum_expansion
symbol: XYZ
timeframe: daily
trend_state:
  sma20_above_sma50: bool
  sma20_slope_positive: bool
  sma50_slope_positive: bool
expansion:
  five_day_return_pct: float
  rvol_on_breakout: float
  close_location_value: float
pullback:
  pullback_depth_pct: float
  low_above_sma20: bool
  range_contraction: bool
  volume_dryup: bool
trigger:
  pivot_high: float
  entry_type: breakout_above_pivot
  stop_reference: pullback_low
status: CANDIDATE_ONLY
tradeable_claim_allowed: false
required_review:
  - market_regime
  - liquidity
  - earnings_calendar
  - spread_slippage
  - position_sizing

## Bad Alert Example
"Bullish candle. Buy." — never produce this.
