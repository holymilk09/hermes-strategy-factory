---
title: Pattern & Situational Alpha Rules
created: 2026-05-17
status: active
pillar: 18-Pattern-Situational-Alpha
---

# Pattern Alpha Doctrine

## Prime Directive
No candlestick names, chart pattern labels, seasonal tendencies, day-of-week patterns, macro-event behavior, or time-of-day behavior are proven strategies.

Every visual/situational pattern must be converted into:
1. measurable condition
2. measurable outcome
3. universe + timeframe
4. data source
5. baseline comparison
6. cost/slippage assumptions
7. validation test
8. failure modes
9. status label

## Allowed Status Labels
- IDEA_ONLY
- UNVERIFIED_PATTERN
- RESEARCH_CANDIDATE
- VALIDATION_RUNNING
- BACKTESTED_ONLY
- OOS_TESTED
- PAPER_CANDIDATE
- BLOCKED
- RETIRED

## Forbidden Labels
PROFITABLE, GUARANTEED, VALIDATED, READY_TO_TRADE, RISK_FREE, HIGH_CONFIDENCE_WITHOUT_EVIDENCE

## Visual → Numeric Conversion
Never rely on visual labels alone. Convert every pattern into:
- body_size_pct, upper_wick_pct, lower_wick_pct
- close_location_value, range_pct, gap_pct
- volume_relative_to_20d, realized_volatility, ATR_percent
- distance_to_10EMA/20MA/50MA/52w_high
- pullback_depth_pct, base_width_pct, range_contraction
- volume_dryup, days_since_swing_high/low
- higher_low_count, lower_high_count, inside_day_count
- breakout_level, failed_breakout_count

## Pattern ≠ Strategy
A pattern becomes a strategy only after: entry logic + exit logic + sizing + risk control + execution model + cost model + validation + review gate.

## Event Study Rule
If conditional hit rate does not beat unconditional baseline → mark NO_EDGE.
Hit rate alone is meaningless without baseline, costs, and adverse excursion analysis.

## Data Snooping Guard
Pattern mining creates thousands of candidate rules. Use:
- White's Reality Check
- Deflated Sharpe Ratio (Bailey/López de Prado)
- Separate discovery/validation/final test datasets
- Log EVERY failed test in alpha_graveyard/

## Decay Rule
Every pattern is assumed to decay over time. Recalibrate. Retest. Log failures.
