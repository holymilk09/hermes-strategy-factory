# Strategy Template — Non-Cookie-Cutter Mean Reversion

## Full YAML Configuration

```yaml
strategy_id: mr_advanced_001
strategy_name: Liquidity-Exhaustion Reclaim Mean Reversion

edge_source:
  - liquidity_pressure
  - temporary_overreaction
  - failed_breakdown

universe:
  asset_class: US_equities
  filters:
    min_price: 5
    min_avg_dollar_volume_20d: 20000000
    exclude_earnings_window: true
    exclude_halt_news_fraud: true

higher_timeframe_regime:
  allowed:
    - bullish_trend_pullback
    - sideways_range
  blocked:
    - crash_regime
    - confirmed_downtrend
    - fundamental_repricing

fair_value_anchor:
  primary:
    - VWAP
    - anchored_VWAP
    - 20_MA
    - factor_residual_mean
  secondary:
    - prior_range_midpoint
    - sector_adjusted_return

deviation_condition:
  any:
    - residual_z <= -2.0
    - vwap_deviation <= -2.0_intraday_sigma
    - close_distance_from_20MA <= -1.5_ATR
    - one_day_return <= -2.0_rolling_sigma

exhaustion_confirmation:
  required_any:
    - undercut_and_reclaim
    - VWAP_reclaim
    - failed_breakdown
    - order_flow_imbalance_flip
    - volume_climax_then_contraction

entry:
  type: reclaim_trigger
  examples:
    - buy_on_reclaim_of_prior_low
    - buy_on_reclaim_of_VWAP
    - buy_on_break_of_first_higher_low

stop:
  type: structure_based
  level:
    - below_sweep_low
    - below_reclaim_failure_low
    - below_range_low

targets:
  target_1: VWAP_or_range_midpoint
  target_2: 20MA_or_prior_high
  time_stop: exit_if_no_reversion_within_expected_window

risk_controls:
  max_risk_per_trade_pct: 0.5
  max_positions_correlated_cluster: 3
  max_daily_loss_pct: 1.5
  no_trade_if_spread_above_threshold: true
  no_trade_if_data_stale: true

validation_required:
  - baseline_comparison
  - random_signal_baseline
  - regime_breakdown
  - cost_slippage_stress
  - max_adverse_excursion_analysis
  - parameter_stability_heatmap
  - out_of_sample_test
```

## Compare to Our Current Config

Our `strategy_config.yaml` has:
- ✅ Universe filters
- ✅ Cost modeling
- ❌ No edge source definition
- ❌ No fair-value anchor (uses raw RSI)
- ❌ No exhaustion confirmation
- ❌ No time stop
- ❌ No regime scoring (binary SMA200 only)
- ❌ No structural stops (fixed 3%)
- ❌ No validation checklist

## Cross-Links
- [[05-Two-Stage-Entry-Template]] — entry logic this config implements
- [[08-Filters-And-No-Trade-Logic]] — filter stack this config enforces
- [[09-Time-Stops-And-Sizing]] — sizing rules referenced here
