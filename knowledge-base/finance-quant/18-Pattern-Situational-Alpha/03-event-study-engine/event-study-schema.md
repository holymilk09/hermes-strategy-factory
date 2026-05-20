---
title: Event Study Engine Schema
pillar: 18
---

# Event Study Definition Schema

## Structure
event_id: unique_identifier
condition:
  day_0: description
  day_1: description
  rule: measurable_boolean_expression
outcome:
  day_k: description
  rule: measurable_boolean_expression
universe:
  symbols: [...]
  session: regular_trading_hours | extended
filters:
  exclude_holidays: true
  exclude_half_days: true
  regime_filter: optional
  macro_event_filter: optional
metrics:
  hit_rate
  baseline_hit_rate
  excess_hit_rate (hit_rate - baseline)
  confidence_interval
  binomial_p_value
  average_return_if_traded
  max_adverse_excursion
  max_favorable_excursion
  expected_value
  transaction_cost_adjusted_pnl
status: RESEARCH_ONLY until proven otherwise

## Core Rule
Conditional hit rate must beat unconditional baseline with statistical significance.
Example: conditional 55%, conditional 54% → NO_EDGE.
A 55% hit rate is worthless if baseline is 53%, losses exceed wins, or fills are unrealistic.

## Example: Friday Low Revisit Monday
Condition: Friday.high < Thursday.high
Outcome: Monday.low <= Friday.low
Controls: exclude holidays, half-days, define session, test SPY/QQQ/ES/NQ separately, test by regime, compare baseline.
