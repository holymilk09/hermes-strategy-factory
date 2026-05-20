# Strategy Contract

## Required strategy fields

- Strategy ID
- Hypothesis
- Universe
- Horizon
- Feature inputs
- Signal rule
- Entry rule
- Exit rule
- Sizing rule
- Risk constraints
- Cost assumptions
- Falsification rule

## Required strategy methods

```python
prepare_features(market_data) -> FeatureFrame
generate_signal(features, state, config) -> list[Signal]
build_targets(signals, portfolio_state, config) -> list[Target]
```

The strategy must not submit broker orders directly.
