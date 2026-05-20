# Multi-Timeframe Features

Multi-timeframe features combine signals from different bar frequencies to create more robust entries, better risk sizing, and improved execution logic.

## Key Concepts

**Useful Combinations:**

| Higher Timeframe | Lower Timeframe | Use |
|---|---|---|
| Daily trend | Intraday pullback | Trend-aligned entries |
| Weekly trend | Daily breakout | Longer-horizon confirmation |
| Hourly volatility | 5-minute execution | Order timing and risk |
| Daily liquidity | Intraday order size | Capacity and fill logic |

**Critical labeling rule:** Every feature must be labeled as one of:
- `closed_bar` — the bar is complete and finalized
- `partial_bar` — the bar is still forming; value will change
- `live_estimate` — a real-time approximation of a closed-bar statistic

## Implications

- **Higher-timeframe context + lower-timeframe precision** is a proven pattern: weekly trend filter + daily entry beats daily-only
- Multi-timeframe features smooth noise without lagging excessively — the lower timeframe catches the entry, the higher provides the filter
- Execution benefits directly from multi-timeframe data: knowing hourly volatility helps size 5-minute orders without overpaying
- The labeling convention (`closed_bar`, `partial_bar`, `live_estimate`) creates auditability — reviewers can instantly see what was available at decision time

## Failure Modes

- **Future bar leakage**: the #1 failure — a lower-timeframe decision uses a higher-timeframe bar that appears closed but still has unprocessed ticks
- **Implicit interpolation**: treating a daily feature as constant throughout the day when it actually requires the day's close
- **Timezone/datetime mismatches**: daily bars close at different times across asset classes (futures vs equities vs crypto)
- **Overlapping windows**: resampling 5-min to hourly creates windows that bleed across hour boundaries
- **Partial bar confusion**: a `partial_bar` hourly vol reading at :30 past the hour looks real but will change by :59

## Cross-Links

- [[Regime Detection Features]] — regime classification on higher timeframe applied as filter on lower
- [[Feature Leakage Prevention]] — partial_bar vs closed_bar labeling prevents the most common look-ahead errors
- [[cross-asset-feature-engineering]] — cross-asset data must be aligned across timeframes before joining
- [[Build Doctrine]] — Phase 1 requires all feature timestamps to be point-in-time before strategy logic
