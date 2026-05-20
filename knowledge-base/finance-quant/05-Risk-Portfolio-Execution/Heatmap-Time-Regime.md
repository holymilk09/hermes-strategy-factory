# Heatmap Time and Regime Playbook

Source: 06_heatmaps_diagnostics/time_regime_heatmaps.md, 06_heatmaps_diagnostics/heatmap_playbook.md

## Key Concepts

A strategy that works only in one time period or regime may be a regime artifact rather than a real edge. Time and regime heatmaps expose whether performance is stable across market conditions.

### Regime Dimensions

- Volatility bucket (low / medium / high)
- Trend/chop bucket
- Liquidity bucket
- Spread bucket
- Macro event vs non-event
- Earnings vs non-earnings
- Bull/bear/sideways market

### Time Dimensions

- Month
- Quarter
- Day of week
- Hour/session
- Before/after scheduled news

### Interpretation Rule

A strategy can be good even if it only works in one regime, BUT only if the regime filter is measurable before the trade. If the good regime can only be labeled after the fact, it is not deployable.

### Heatmap Construction

- X-axis: volatility bucket or trend bucket
- Y-axis: month/quarter or regime
- Cell: after-cost return, PnL per trade, or hit rate

### Rejection Criteria

From the diagnostic playbook, reject strategies where:
- A signal whose IC vanishes outside one regime (without a pre-trade filter)
- Performance is concentrated in one month or quarter
- The strategy only works during macro events that cannot be predicted

## Implications

1. **Regime-aware strategies need regime prediction** - If your edge exists only in trending markets, you must have a measurable, pre-trade trend indicator.
2. **Seasonality analysis is critical** - Monthly or day-of-week heatmaps expose calendar anomalies that may be data artifacts rather than real edges.
3. **Hour/session analysis matters for intraday** - Strategies that work only during the first 30 minutes may be capturing opening auction noise.
4. **Regime buckets must be computed from lagged data** - Using current volatility to classify the current period creates look-ahead bias. Use lagged or rolling measures.

## Failure Modes / Misinterpretations

- **Post-hoc regime labeling**: Labeling a regime using full-period statistics means the regime labels leak future information. Always use point-in-time regime calculation.
- **Regime bucket boundaries**: Arbitrary bucket cutoffs (e.g., 20th/80th percentile) can create artificial regime boundaries. Test sensitivity.
- **Regime switching frequency**: Some regimes change frequently (hourly volatility) while others change slowly (market cycle). Match your regime window to strategy holding period.
- **Over-segmentation**: Too many regime dimensions creates cells with too few observations to draw statistical conclusions.
- **Confounding time and regime**: A strategy that works only in Q4 may appear to have a seasonal edge, but Q4 may also coincide with low-volatility regimes.

## Cross-Links

- [[Heatmap-Parameter]] for parameter stability across regimes
- [[Heatmap-Instrument]] for regime effects across different symbols
- [[Overfit-Detection-Metrics]] for OOS decay validation
- [[Risk-Metrics]] for regime-dependent risk behavior
