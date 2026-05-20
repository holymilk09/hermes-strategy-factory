# Build Sequence

## Phase 0 — Spine before strategy

Deliverable: a bot that can ingest data, emit a no-op signal, size zero, submit no orders, log everything, and produce a run report.

Required outputs:

- `run_id`
- `config_hash`
- `data_version`
- `code_version`
- `universe`
- `calendar`
- `metric_pack`
- `review_note`

## Phase 1 — Data pipeline

Build only data loading, normalization, calendars, symbol mapping, corporate actions, aggregation, and quality checks. No strategy logic.

Pass criteria:

- Same input produces same bars.
- Timestamps are normalized.
- Missing bars are flagged.
- Split/dividend adjustments are explicit.
- All feature timestamps are point-in-time.

## Phase 2 — Backtest harness

Build event-driven simulation with fills, fees, slippage, portfolio state, cash, margin, and order state.

Pass criteria:

- Trade ledger reconciles with position ledger.
- Cash ledger reconciles with equity curve.
- Fees and slippage appear in run output.
- Same run ID/config/data gives deterministic result.

## Phase 3 — First strategy

Add one simple baseline strategy. Do not optimize yet.

Pass criteria:

- Signal logic is testable without broker/backtest engine.
- Strategy can be disabled with config.
- Every trade can be explained from signal -> sizing -> risk -> order -> fill.

## Phase 4 — Metrics and diagnostics

Add performance, risk, trade, execution, overfit, and regime metrics.

Pass criteria:

- Each metric has definition and input data.
- Metrics are emitted as machine-readable JSON/CSV.
- The report identifies the weakest 3 failure modes.

## Phase 5 — Epoch learning

Introduce walk-forward epochs, parameter stability, regime review, and strategy decay checks.

Pass criteria:

- Train/validation/test windows are locked before evaluation.
- No strategy is promoted without OOS, cost, and sensitivity checks.
- Parameter heatmaps show no narrow cliff-only edge.

## Phase 6 — Paper/live bridge

Add broker API, paper trading, reconciliation, order state machine, kill switches, monitoring, and post-trade review.

Pass criteria:

- Broker positions reconcile with internal state.
- Duplicate orders are blocked.
- Kill switch works.
- Paper/live deltas are reviewed.
