---
title: Macro Event Patterns
pillar: 18
---

# Macro Event Calendar & Features

## Required Calendar
- FOMC meetings (8/year), Fed speakers
- CPI, PPI, PCE (inflation)
- NFP, GDP, ISM manufacturing/services
- Earnings seasons / individual earnings
- Options expiration (monthly, quarterly)
- Quarter-end / month-end windows
- Treasury auctions
- OPEC meetings
- Major crypto unlocks / ETF rebalances
- Index rebalances

## Event Window Features
- days_to_fomc, days_after_fomc
- is_cpi_day, is_nfp_day, is_ppi_day
- is_opex_week, is_month_end_window
- is_quarter_end_window, is_earnings_week
- pre_event_volatility, post_event_gap
- event_day_range, event_day_volume

## Study Design: Before/During/After
Before event: drift direction, vol compression, volume behavior, IV expansion
During event: range expansion, whipsaw risk, spread widening
After event: continuation, reversal, vol crush, delayed sector response

## Pre-FOMC Drift
Lucca & Moench (2014): equities show abnormal returns specifically in the window BEFORE scheduled FOMC announcements, not after. Model example for event-window precision.

## Rule
Do not make macro-event claims without event-study evidence.
