# Feature Leakage Prevention

Synthesized from `feature_leakage_danger_list.md` and leakage patterns identified across the data pipeline, feature store, and aggregated data tactics.

---

## Key Concepts

Feature leakage occurs when a feature uses information that was **not available at the decision timestamp**. Any leakage corrupts training, inflates backtest performance, and guarantees live losses.

### Leakage Danger List

| Danger | How It Happens | Prevention |
|---|---|---|
| **Earnings surprise using final reported data** | Feature uses revised earnings that arrived days after the reporting date | Use actual release timestamp; version data with release times |
| **Macro data using revised values** | CPI/GDP gets revised; feature uses final value instead of first release | Track all revisions; use point-in-time release table |
| **Index constituent membership from future date** | Membership lists change; using current list for past data | Use historical constituent snapshots |
| **Market cap/liquidity screen from future values** | Screen based on market cap computed with future prices | Use lookback-window market cap at decision time |
| **Analyst ratings scraped without timestamp** | Scraped data lacks precise timestamp | Always record scrape timestamp; assume next-bar availability |
| **News sentiment assigned to wrong timestamp** | Article timestamp != publication timestamp != scrape timestamp | Use publication+buffer as feature availability |
| **Options chain using unavailable contracts** | Backtest uses options contracts that expired before the trade date | Options data must be point-in-time snapshot |
| **Adjusted prices changing signal thresholds** | Split adjustment changes historical price levels used as thresholds | Recalculate thresholds using the adjustment policy active at decision time |
| **Resampled bars including future intraday data** | 5-min bar at 10:00 includes data from 10:00:01 to 10:04:59 but signal at 10:00:30 | Label features as `closed_bar`, `partial_bar`, or `live_estimate` |

### The Point-in-Time Rule

> A feature is legal **only if all inputs were observable at or before the decision timestamp**, including vendor delays and publication lags.

This rule guards every stage of the pipeline. If any component relies on data not available at decision time, the feature is tainted.

### Aggregation-Specific Leakage

Aggregated data is especially vulnerable:
- **"Daily" features computed at midnight** using 16:15 data leak 15 minutes into the next day
- **Revised data masquerading as first release**: macro datasets often store only the latest revision
- **Survivorship in alt data coverage**: databases drop delisted stocks, making historical coverage appear better than reality
- **Circular regime features**: regime detectors using the same features as the signal double-count information
- **Regime hindsight bias**: using end-of-period regime labels to label training data when the regime was only clear in retrospect

### Aggregation Safety Rules

1. Record exact source timestamp
2. Record exact release timestamp for macro/fundamental data
3. Never use revised values unless testing revised-data assumptions explicitly
4. Use lag buffers for scraped or delayed sources
5. Compare raw vs aggregated data drift
6. Check if aggregation creates hidden look-ahead

### Multi-Timeframe Labeling

Every multi-timeframe feature must be labeled:
- `closed_bar` — higher-timeframe bar is complete and no future data is included
- `partial_bar` — bar is still forming; feature is live estimate subject to change
- `live_estimate` — feature computed from incomplete data with explicit uncertainty

**Never let lower-timeframe decisions use incomplete higher-timeframe bars as if they were closed.**

---

## Implications for Real Trading Systems

- **Leakage is the #1 cause of false edge**: strategies that look great in backtest and fail live often have undetected leakage.
- **The point-in-time rule is non-negotiable**: every feature must pass this check before entering the feature store.
- **Aggregation is the leakiest stage**: compressing raw data into features creates many subtle timing traps.
- **Cross-vendor timestamp comparison catches leakage**: if two vendors report different timestamps for the same event, investigate.

---

## Potential Failure Modes

- **Vendor timestamp vs release timestamp confusion**: using the vendor's ingest timestamp instead of the actual release timestamp.
- **Corporate action date ambiguity**: split ex-date vs announcement date — the market reacts on announcement, not ex-date.
- **Delayed alt data**: sentiment data scraped hourly may have a 30-60 minute delay from publication; if not buffered, it leaks.
- **Silent vendor data changes**: vendor updates historical data without notification, invalidating past feature values.
- **Feature formula change without re-checking leakage**: adding a new input to a feature calculation may introduce leakage even if the old formula was clean.

---

## Cross-Links

- [[Data-Pipeline-Architecture]] — point-in-time guards every pipeline stage
- [[Feature-Store-Design]] — the point-in-time rule is the primary anti-leakage mechanism; timestamp_policy and lag_policy fields enforce it
- [[Data-Quality-Checks]] — poor-quality data can mask leakage (e.g., timestamp errors)
- [[Aggregated-Data-Tactics]] — aggregation safety rules
- [[Multi-Timeframe-Features]] — closed_bar vs partial_bar vs live_estimate labeling
- [[Research-Papers-Index]] — multiple-testing papers address leakage indirectly via DSR/PBO
- [[Trading-System-Build-Doctrine]] — Phase 1 data pipeline and Phase 2 signal generation enforce leakage checks
