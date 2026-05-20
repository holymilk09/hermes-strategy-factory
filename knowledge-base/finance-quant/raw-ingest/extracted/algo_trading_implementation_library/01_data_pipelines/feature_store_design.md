# Feature Store Design

## Feature registry fields

| Field | Meaning |
|---|---|
| `feature_name` | Stable identifier. |
| `version` | Increment when formula or input changes. |
| `source_data_version` | Dataset version used. |
| `timestamp_policy` | Event time, release time, vendor time. |
| `lookback_window` | Data window used. |
| `lag_policy` | Minimum delay before feature is usable. |
| `null_policy` | Handling for missing values. |
| `winsorization` | Outlier rule if used. |
| `owner` | Strategy/system owner. |

## Feature classes

- Price features
- Volatility features
- Volume/liquidity features
- Cross-asset features
- Macro features
- Fundamental features
- Options features
- Order-book features
- Regime labels
- Model outputs

## Point-in-time rule

A feature is legal only if all inputs were observable at or before the decision timestamp, including vendor delays and publication lags.
