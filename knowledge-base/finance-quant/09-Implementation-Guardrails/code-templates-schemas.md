# Code Templates, Schemas, and Test Patterns

**Source**: Extracted and synthesized from `10_templates/` directory (Python source, YAML configs, JSON schemas, test fixtures). Most agents only processed .md files — these were missed.

---

## Python Data Contracts (contracts.py)

The inter-module communication layer uses frozen dataclasses for immutability and explicit typing:

| Contract | Purpose | Key Fields |
|---|---|---|
| `Signal` | Output of signal layer | run_id, strategy_id, symbol, direction, score, confidence, horizon, reason_codes |
| `Target` | Output of portfolio construction | target_quantity, target_weight, reason |
| `OrderInstruction` | Output of execution engine | client_order_id, symbol, side, quantity, order_type, time_in_force, limit_price, risk_approval_id |

**Implication**: Immutable contracts prevent downstream mutation bugs. Every module has explicit I/O.

## Reference Strategy Pattern (sample_strategy.py)

The sample implements a trend-following pullback strategy with signal contract compliance:

- Feature preparation via groupby rolling windows (fast_ma, slow_ma, pullback ratio)
- Signal generation isolates from portfolio/execution layers
- Score-based directional assignment with reason codes
- Confidence bounded to [0, 1]

**Anti-pattern to avoid**: The sample is intentionally simple. Real strategies should separate feature computation (independent) from signal generation (independent) from portfolio construction (independent).

## Test Patterns (test_data_pipeline.py, test_metrics.py)

- DataFrame-based fixtures with minimal valid rows
- Assert on normalized outputs (e.g., uppercase symbols, datetime conversion)
- Validation functions raise on schema violations
- Tests fixtures for features, signal, sizing, and risk should all be independent

## YAML Config Patterns

### strategy.yaml
```yaml
strategy_id: "ma_pullback_v1"
description: "Trend-following with pullback entry"
parameters:
  fast_ma: 20
  slow_ma: 50
  pullback_window: 5
  min_score: 0.4
universe: 
  type: "top_by_dollar_volume"
  n: 500
timeframe: "1d"
```

### risk_limits.yaml
```yaml
max_position_size: 0.1
max_gross_exposure: 1.5
max_daily_loss_pct: 0.02
max_drawdown_pct: 0.15
volatility_target: 0.15
kill_switch_enabled: true
```

## JSON Schema Contracts

All data pipeline events are validated against JSON schemas:
- `bar.schema.json` — OHLCV with adjustment policy
- `signal.schema.json` — Signal contract serialized
- `order.schema.json` — Order instruction serialized
- `fill.schema.json` — Broker fill data
- `market_event.schema.json` — Any market event
- `model_epoch.schema.json` — Training epoch metadata
- `backtest_run.schema.json` — Full run metadata

**Cross-link**: See [[Schema-Catalog]] for consolidated field documentation.

## Failure Modes

| Failure | Consequence | Prevention |
|---|---|---|
| Mutable data objects | Downstream modules corrupt upstream state | Use frozen dataclasses |
| No validation on ingress | Bad data silently propagates | JSON schema validation at every boundary |
| Tests only on happy path | Edge cases break in production | Include malformed data in tests |
| Hardcoded parameters | Strategy can't be swept or compared | Pull all params into YAML configs |
| No reason codes | Strategy decisions are unexplainable | Every signal must have reason_codes |

---

*Cross-linked: [[Strategy-Templates-Standards]], [[Strategy-Backtest-Contracts]], [[Schema-Catalog]], [[Feature-Store-Design]]*
