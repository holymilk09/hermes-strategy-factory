---
title: Feature Builder Schema
pillar: 18
---

# Numeric Feature Definitions

## Candle Geometry
- body_size_pct: abs(close - open) / (high - low) if high != low else 0
- upper_wick_pct: (high - max(open, close)) / (high - low)
- lower_wick_pct: (min(open, close) - low) / (high - low)
- close_location_value: (close - low) / (high - low)
- range_pct: (high - low) / close
- gap_pct: (open - prev_close) / prev_close

## Trend State
- distance_to_10EMA: (close - EMA10) / close
- distance_to_20MA: (close - SMA20) / close
- distance_to_50MA: (close - SMA50) / close
- distance_to_52w_high: (close - high_52w) / high_52w
- ma_spread_pct: (SMA20 - SMA50) / close
- slope_sma20_5bar, slope_sma50_10bar

## Expansion/Contraction
- N_day_return_pct
- volume_relative_to_20d: vol / sma20(vol)
- ATR_percent: ATR(14) / close
- base_width_pct: (period_high - period_low) / period_low
- range_contraction: today_range < sma5(prev_ranges) * threshold
- volume_dryup: today_vol < sma5(prev_vols) * 0.5

## Pullback / Wave
- pullback_depth_pct: (swing_high - current_low) / swing_high
- days_since_swing_high
- days_since_swing_low
- higher_low_count, lower_high_count
- inside_day_count

## Calendar/Macro
- days_to_fomc, days_after_fomc
- is_cpi_day, is_nfp_day, is_opex_week
- is_month_end_window, is_quarter_end_window
- is_earnings_week, pre_event_volatility
