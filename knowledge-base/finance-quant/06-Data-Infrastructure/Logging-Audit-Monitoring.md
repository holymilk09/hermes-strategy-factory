# Logging, Audit & Monitoring

Synthesized from raw ingestion corpus: `logging_contract.md`, `audit_lineage.md`, `monitoring_alerting.md`, `testing_strategy.md`, `unit_integration_regression_tests.md`, `post_trade_review.md`, and `weak_point_review_board.md`.

---

## Key Concepts

### Required Log Streams (Logging Contract)

Every production trading system must maintain these 11 log streams:

| Stream | Contents |
|---|---|
| `run_log` | Run start/end, config, data versions, environment |
| `data_log` | Source, timestamp, quality flags, gaps, anomalies |
| `feature_log` | Feature version, calculation timestamp, nulls/drift |
| `signal_log` | Signal score, reason codes, horizon, confidence |
| `risk_log` | Approved/clipped/vetoed targets and reasons |
| `order_log` | Submitted/cancelled/rejected/acknowledged orders |
| `fill_log` | Fills, fees, slippage, venue |
| `position_log` | Holdings, cash, exposure, leverage |
| `metric_log` | Periodic performance/risk/execution metrics |
| `incident_log` | System failures, data errors, broker/API issues |
| `review_log` | Human/agent review decisions |

**Minimum event fields**: `run_id`, `timestamp`, `event_type`, `component`, `severity`, `payload`, `hash_prev` (for audit chain).

**Golden rule**: Logs are part of the trading system. If a trade was not logged, it is not explainable.

### Audit and Lineage

**Lineage chain** (hash-linked):
```
raw_data_hash -> normalized_data_hash -> feature_hash -> signal_hash -> order_hash -> fill_hash -> metric_hash -> review_hash
```

**Run manifest fields** (per execution):
- Run ID, Strategy ID, Code commit
- Config hash, Data version/hash, Feature version/hash
- Model version/hash
- Start/end time, Random seed
- Environment, Broker/paper/live mode
- Risk limits, Metric pack version

**Tamper detection**: Hash each artifact and store the hash in the run manifest. A full hash chain is optional at MVP level but becomes essential as complexity grows.

### Monitoring and Alerting

**Critical alerts** (immediate action required):
- Missing heartbeat
- Broker disconnected
- Data stale
- Position mismatch
- Open order mismatch
- Max daily loss breached

**Warning/Critical alerts**:
- Slippage above threshold
- Reject rate spike
- Feature drift breach
- Metric degradation

**Required dashboards**:
- Current equity, current positions
- Gross/net exposure
- Orders/fills state
- Realized/unrealized PnL
- Data latency, broker health
- Strategy-level PnL
- Slippage by symbol
- Risk-limit status

### Testing Strategy

**8-layer testing pyramid:**

| Layer | Purpose |
|---|---|
| Unit | Indicators, features, signals, sizing, risk rules |
| Contract | Validate schemas and module I/O |
| Integration | Data → signal → target → order → fill → ledger |
| Regression | Known strategy output must not change unexpectedly |
| Simulation | Broker reject, partial fill, stale data, API outage |
| Statistical | Backtest metrics and validation logic |
| Smoke | Start bot, no-op strategy, logs, report |
| Paper/Live | Compare paper assumptions to real broker behavior |

**Unit test priorities:**
1. Feature calculation
2. Signal generation
3. Sizing
4. Risk veto
5. Fill model
6. Ledger reconciliation
7. Metrics formulas

**Golden run regression**: Store a known-good run output. If output changes without intentional code change, require a review note explaining why.

**Smoke test: No-op strategy**
Expected: no orders, no fills, equity unchanged, logs written, metric report generated.

**Integration test: Deterministic toy strategy**
Expected: known order count, fill count, cash/position/PnL, metrics.

### Post-Trade Review

**Review fields per trade:**
- Trade ID, Strategy ID
- Entry signal reason, Exit reason
- Expected vs actual holding period
- Entry/exit slippage
- MAE (Maximum Adverse Excursion), MFE (Maximum Favorable Excursion)
- Realized PnL, Regime bucket
- Mistake category

**Mistake categories:**
- Good process / bad outcome
- Bad signal
- Bad sizing
- Bad risk rule
- Bad execution
- Bad data
- Code bug
- Manual override
- Unknown

### Weak-Point Review Board

Use an issue-tracking board for strategy/system weaknesses:

| Field | Description |
|---|---|
| ID | Unique weak point identifier |
| Weak point | Description of the issue |
| Evidence | Data/heatmap/review showing the problem |
| Severity | high / medium / low |
| Owner | Who fixes it |
| Next experiment | What test addresses it |
| Status | open / in_progress / resolved / wont_fix |

---

## Implications for Real Trading Systems

- **Logging is not optional**: it's the difference between a system you can debug and a black box losing money.
- **The audit chain enables post-mortem**: when a trade went wrong, you can trace exactly which data, features, and signals drove it.
- **Alerts are triage, not diagnosis**: an alert tells you something is wrong. The logs tell you what.
- **Golden-run regression is your safety net**: silent regressions (e.g., library upgrade changing a rounding behavior) are caught before they hit live.
- **Post-trade review turns losses into learning**: categorizing mistakes reveals systemic issues (e.g., "bad execution" appearing repeatedly means the execution layer needs work).
- **The weak-point board prioritizes your R&D**: don't guess what to fix — score it and attack the highest-value weakness.

---

## Potential Failure Modes

- **Log gaps**: if any of the 11 streams has a gap, incidents become unexplainable.
- **Alert fatigue**: too many warnings cause critical alerts to be ignored. Severity discipline is essential.
- **Unhashed artifacts**: without hashes, you can't detect whether data or code changed between runs.
- **Missing run manifests**: without manifests, you can't reproduce or audit a run.
- **No golden run**: regression tests don't exist, so silent bugs go undetected.
- **Skip the smoke test**: deploying without verifying the no-op strategy means you can't distinguish system bugs from strategy issues.
- **Post-trade review skipped after winning trades**: good outcomes with bad process are missed, and the bad process compounds.
- **Weak-point board ignored**: issues listed but never prioritized or acted on.
- **No incident log**: recurring production failures without tracking means the system degrades silently.
- **Review_log not written**: human/agent decisions are lost, so the learning loop is broken.

---

## Cross-Links

- [[Trading-System-Build-Doctrine]] — Phase 5 production deployment uses all logging, audit, and monitoring controls
- [[Logging-Audit-Monitoring]] — the full logging contract from the raw corpus
- [[Logging-Audit-Monitoring]] — the lineage chain and run manifest
- [[Logging-Audit-Monitoring]] — alert types and dashboard requirements
- [[Logging-Audit-Monitoring]] — 8-layer testing pyramid
- [[Logging-Audit-Monitoring]] — trade review fields and mistake categories
- [[Strategy-Weak-Point-Detection]] — weak-point categories and the review board
- [[Epoch-Learning-Retraining]] — epoch reviews feed the review_log stream
- [[Data-Quality-Checks]] — quality reports are part of the data_log stream
- [[Data-Pipeline-Architecture]] — versioning and hashing of data artifacts
- [[Feature-Store-Design]] — feature hashing in the audit chain
- [[Schema-Catalog]] — schemas that contract tests validate
