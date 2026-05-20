# Feature Store Design

## Key Concepts

### Feature Registry Schema

Every feature in the store must have these fields:

| Field | Meaning |
|---|---|
| `feature_name` | Stable identifier |
| `version` | Increment when formula or input changes |
| `source_data_version` | Dataset version used |
| `timestamp_policy` | Event time, release time, or vendor time |
| `lookback_window` | Data window used for calculation |
| `lag_policy` | Minimum delay before feature is usable |
| `null_policy` | How missing values are handled |
| `winsorization` | Outlier capping rule if applied |
| `owner` | Strategy or system owner |

### Feature Classes

- **Price features**: returns, moving averages, momentum indicators
- **Volatility features**: realized vol, implied vol, spread metrics
- **Volume/liquidity features**: relative volume, dollar volume, depth
- **Cross-asset features**: SPY, VIX, rates, dollar, commodities signals
- **Macro features**: CPI, PMIs, yield curve, credit spreads
- **Fundamental features**: earnings, ratios, revision metrics
- **Options features**: IV rank, skew, term structure, put/call ratios
- **Order-book features**: imbalance, queue dynamics, microstructure
- **Regime labels**: market state classification outputs
- **Model outputs**: predictions from ML/statistical models

### Point-in-Time Rule

> A feature is legal only if **all inputs were observable at or before the decision timestamp**, including vendor delays and publication lags.

This is the single most important rule. If any component of a feature relies on data that was not available at decision time, the feature is tainted.

### Aggregation Rules for Features

When compressing raw data into features:

1. Record exact source timestamp
2. Record exact release timestamp for macro/fundamental data
3. Never use revised values unless testing revised-data assumptions explicitly
4. Use lag buffers for scraped or delayed sources
5. Compare raw vs aggregated data drift
6. Check if aggregation creates hidden look-ahead

## Implications for Real Trading Systems

- **Feature versioning is auditability**: when a trade goes wrong, you must be able to replay exactly which feature values the bot saw
- **The registry is documentation**: a team member (or future you) can read the registry and understand every feature's provenance in 2 minutes
- **Feature owners prevent orphaned features**: when a strategy is retired, the owner field tells you which features can be safely removed
- **Null policy is strategy-critical**: different strategies handle missing data differently — momentum can skip, stat arb must interpolate, event-driven must reject

## Failure Modes

- **Formula change without version bump**: subtle formula tweaks break reproducibility silently
- **Release time vs event time confusion**: macro data published at 8:30 AM but timestamped at midnight creates look-ahead
- **Revisions used live without realizing**: CPI gets revised monthly; using the final number backtests on information the bot didn't have live
- **Winsorization hiding true extremes**: capping outliers at 3-sigma during training makes the model blind to black-swan magnitudes
- **Feature store without null policy**: missing values silently replaced with 0 creates phantom signals

## Cross-Links

- [[Data Pipeline Architecture]] — features are computed in the pipeline after quality checks
- [[Feature Leakage Prevention]] — the point-in-time rule is the primary anti-leakage mechanism
- [[Schema Catalog]] — the model_epoch schema tracks which feature versions were used per epoch
- [[Aggregated Data Tactics]] — multi-timeframe, cross-asset, and regime features are all classes in this registry
- [[Model Drift Detection]] — feature PSI/KL/KS tests detect when features drift from training distribution
