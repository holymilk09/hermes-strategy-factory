# Trading System Build Doctrine

Comprehensive doctrine for building production trading systems. Synthesizes: build sequence, strategy-to-code playbook, production checklist, architecture map, and source registry concepts from the [[00-Anti-Cookie-Cutter-Insights]] and raw ingestion corpus.

**Version**: 1.0  
**Applies to**: All systematic trading system development  
**Philosophy**: Discipline over speed. Reproducibility over cleverness. Risk control over optimization.

---

## Phase 0: Hypothesis & Research

### What
- Define the edge hypothesis in falsifiable terms before touching code.
- Research existing literature and similar strategies ([[Research-Papers-Index]]).
- Source quality: Tier 1-2 only per [[Source-Quality-Rules]]. Reject blogs and SEO farms.

### Key Concepts
- Every strategy starts with a claim: "X predicts Y because Z." If you can't articulate Z, you're curve-fitting.
- Research existing academic / practitioner work first ([[Papers-Docs-Synthesis]]).
- Frame the hypothesis with:
  - **Independent variable**: What data / signal drives the trade?
  - **Dependent variable**: What outcome are you predicting (return, direction, volatility)?
  - **Mechanism**: Why should this work? (behavioral, structural, informational)
  - **Falsification criterion**: What result would prove it wrong?

### Deliverables
- Written hypothesis document
- Literature review summary
- Falsification criteria (quantitative thresholds)

### Failure Modes
- **Mechanism-free hypotheses**: correlation without causation degrades once discovered.
- **Insufficient literature review**: reinventing dead strategies.
- **Vague falsification**: "it doesn't work" is not a falsification criterion.

### Cross-Links
- [[Papers-Docs-Synthesis#factor-discovery-and-multiple-testing]] — Harvey/Liu/Zhu and López de Prado causality primer
- [[Research-Papers-Index]] — prior art discovery
- [[Feature-Leakage-Prevention]] — hypothesis must account for data timing constraints

---

## Phase 1: Data Acquisition & Pipeline

### What
- Acquire raw, immutable data from vendors.
- Build canonical pipeline: vendor adapter → raw store → schema validator → timestamp normalizer → symbol mapper → corporate-action adjuster → aggregator → quality checker → feature calculator → point-in-time feature store.
- Maintain three separate data paths: historical research, backtest feed, live feed.

### Key Concepts
- **Raw data is immutable**: never overwrite vendor payloads.
- **Normalized data is versioned**: every change gets a new hash.
- **Features are timestamped and point-in-time**: only data observable at decision time is legal.
- **Live/research parity**: same feature calculation code for backtest and live. Only data adapter and execution adapter differ.
- **Dataset naming**: `assetclass_vendor_dataset_adjustment_calendar_start_end_hash`

### Deliverables
- Raw data store with immutable vendor payloads
- Pipeline with quality gates
- Data version tracking
- Point-in-time feature store

### Failure Modes
- **Mixed adjustment policies**: split-adjusted prices mixed with raw prices create phantom returns.
- **Timestamp zone confusion**: treating UTC as local shifts signals into the future.
- **Corporate action gaps**: unapplied splits/dividends create return discontinuities.
- **Survivorship bias**: vendor filters silently removing delisted names.
- **Live research divergence**: using different feature code for backtest vs live is the #1 cause of live trading failures.

### Cross-Links
- [[Data-Pipeline-Architecture]] — full canonical pipeline specification
- [[Data-Quality-Checks]] — quality gate that feeds into the pipeline
- [[Feature-Store-Design]] — feature cataloging and versioning after calculation
- [[Feature-Leakage-Prevention]] — point-in-time rules guard every pipeline stage
- [[Aggregated Data-Tactics]] — how aggregated data flows into the pipeline
- [[Multi-Timeframe-Features]] — cross-timeframe feature labeling (closed_bar vs partial_bar vs live_estimate)
- [[13f-Macro-Altdata-Tactics]] — delayed / alternative data handling

---

## Phase 2: Strategy Coding & Signal Generation

### What
- Implement the strategy as a clean pipeline: data → features → signals → targets → orders → fills → ledger.
- Every component is independently testable.
- Signal generation uses only point-in-time legal features.

### Key Concepts
- **Signal contract**: signals output (timestamp, symbol, score, horizon, confidence, reason_codes).
- **Feature isolation**: each signal uses a documented subset of features.
- **Action space**: discrete (buy/sell/hold) or continuous (position weight).
- **Exit logic**: entry is only half the strategy; stops, profit-taking, and time exits are coded with same rigor as entry.
- **Path-dependent trade management** ([[Papers-Docs-Synthesis#tactical-path-dependent-investing]]): model the full trade trajectory, not just entry signals.

### Deliverables
- Signal generation module with defined contract
- Entry and exit logic
- Sizing and position management
- Unit tests for all components

### Failure Modes
- **Look-ahead in signal generation**: features use future data that wasn't available.
- **Hardcoded parameters**: parameters baked into code instead of config files prevent systematic testing.
- **Monolithic code**: untestable signals with implicit data dependencies.
- **Exit logic as afterthought**: exits determine net profitability more than entries.

### Cross-Links
- [[Schema-Catalog]] — signal schema defines the output contract
- [[Logging-Audit-Monitoring]] — test coverage for signal components
- [[Logging-Audit-Monitoring]] — unit test priorities for indicators, features, signals
- [[Papers-Docs-Synthesis#tactical-path-dependent-investing]] — López de Prado tactical investing

---

## Phase 3: Backtesting & Validation

### What
- Deterministic backtest with fixed data version, calendar, and corporate actions.
- Walk-forward evaluation across multiple epochs.
- Multiple testing correction (DSR, PBO) on all optimization results.

### Key Concepts
- **Deterministic replay**: same input + config = same output. Always.
- **Walk-forward epochs** ([[Walk-Forward-Epoch-Protocol]]):
  1. Define hypothesis and falsification rule
  2. Lock train/validation/test dates
  3. Train/select parameters on train/validation only
  4. Evaluate once on test
  5. Run stress and cost sensitivity
  6. Generate heatmaps
  7. Write review
  8. Decide: promote, reject, or hold
- **Overfitting controls**: DSR for Sharpe correction, PBO for overfitting probability, trial count tracking.
- **Stress testing**: cost sensitivity, parameter neighborhood, regime segmentation.
- **Strategy weak-point detection** ([[Strategy-Weak-Point-Detection]]): score parameter fragility, regime fragility, concentration risk, cost sensitivity.

### Deliverables
- Backtest with deterministic output
- Walk-forward epoch records
- DSR and PBO reports
- Heatmaps (parameter, regime, cost)
- Written review for each epoch

### Golden Rule: Never move test windows after seeing bad results. Never reuse test set until it passes.

### Failure Modes
- **P-hacking via backtest**: trying 100 parameter sets and reporting the best.
- **Test set reuse**: evaluating on the same test set repeatedly until it passes.
- **Insufficient cost modeling**: strategies that profit only under optimistic slippage.
- **Single-regime success**: strategy works only in low-vol uptrend.
- **Trade concentration**: profitability explained by top 5 trades.
- **Ignoring autocorrelation**: Sharpe confidence intervals are too narrow.

### Cross-Links
- [[Walk-Forward-Epoch-Protocol]] — the 8-step protocol
- [[Strategy-Weak-Point-Detection]] — weak-point scoring formula
- [[Papers-Docs-Synthesis#overfitting-and-backtest-rigor]] — DSR and PBO methodology
- [[Papers-Docs-Synthesis#sharpe-estimation]] — confidence intervals
- [[Epoch-Learning-Retraining]] — epoch record schema and learning loop
- [[Review-And-Learn-Loop]] — review questions and backlog labels
- [[Logging-Audit-Monitoring]] — live monitoring validates backtest assumptions
- [[Logging-Audit-Monitoring]] — MAE/MFE analysis validates exits

---

## Phase 4: Simulation & Paper Trading

### What
- Run the strategy in paper mode with real-time data and simulated execution.
- Compare paper results to backtest expectations.
- Validate data feed quality, latency, and broker API behavior.

### Key Concepts
- **Paper trading is the bridge**: it catches bugs that backtests miss and assumptions that simulations oversimplify.
- **Live-vs-backtest delta report**: every week, compare paper PnL to backtest PnL for the same period. Investigate divergences.
- **Smoke test first**: no-op strategy → no orders, no fills, equity unchanged, logs written, metrics generated.
- **Deterministic toy strategy**: known order count, known fill count, known cash/PnL, known metrics.

### Deliverables
- Paper trading run with live-vs-backtest comparison
- Smoke test and toy strategy test results
- Broker API behavior documentation

### Failure Modes
- **Paper trading too short**: 2 weeks of paper trading doesn't cover enough market states.
- **Ignoring fill discrepancies**: paper fills assume perfect execution; real fills don't.
- **Skip the no-op test**: if you can't verify nothing happens, you can't trust something happening.
- **Broker API surprises**: order types, limits, reject codes that backtest didn't model.

### Cross-Links
- [[Logging-Audit-Monitoring]] — smoke and paper/live test layers
- [[Logging-Audit-Monitoring]] — no-op and deterministic toy strategy
- [[Logging-Audit-Monitoring]] — dashboards and alerts for paper trading
- [[Logging-Audit-Monitoring]] — all streams must work in paper mode

---

## Phase 5: Production Deployment

### What
- Deploy with capital, starting small, scaling up as confidence is earned.
- Every aspect of the system is monitored and alerted.
- Audit trail from raw data through to fill is maintained.

### Key Concepts
- **Capital ramp-up**: start with 10-20% of intended capital. Scale up only after N epochs meet expectations.
- **Kill criteria**: predefined conditions under which the strategy is stopped. Not "when I feel bad" — actual rules.
- **Audit chain** ([[Logging-Audit-Monitoring]]): raw_data_hash → normalized_data_hash → feature_hash → signal_hash → order_hash → fill_hash → metric_hash → review_hash.
- **Run manifest** per execution: run ID, strategy ID, code commit, config hash, data version, feature version, model version, start/end time, random seed, environment, broker mode, risk limits, metric pack version.
- **Tamper detection**: hash each artifact. Store hashes in manifest.

### Logging Requirements ([[Logging-Audit-Monitoring]])
All 11 log streams must be operational:
1. `run_log` — run start/end, config, data versions
2. `data_log` — source, timestamp, quality flags, gaps
3. `feature_log` — feature version, nulls/drift
4. `signal_log` — signal score, reason codes, horizon, confidence
5. `risk_log` — approved/clipped/vetoed targets and reasons
6. `order_log` — submitted/cancelled/rejected/acknowledged
7. `fill_log` — fills, fees, slippage, venue
8. `position_log` — holdings, cash, exposure, leverage
9. `metric_log` — periodic performance/risk/execution metrics
10. `incident_log` — system failures, data errors, broker issues
11. `review_log` — human/agent review decisions

Minimum event fields: `run_id`, `timestamp`, `event_type`, `component`, `severity`, `payload`, `hash_prev` (audit chain).

### Testing Requirements
| Test Layer | Purpose |
|---|---|
| Unit | Indicators, features, signals, sizing, risk rules |
| Contract | Schema validation, module I/O |
| Integration | Data → signal → target → order → fill → ledger |
| Regression | Golden run — output must not change without review note |
| Simulation | Broker reject, partial fill, stale data, API outage |
| Statistical | Backtest metrics and validation logic |
| Smoke | Start bot, no-op strategy, logs, report |
| Paper/Live | Compare paper assumptions to real broker behavior |

### Monitoring & Alerting ([[Logging-Audit-Monitoring]])
**Critical alerts** (immediate action):
- Missing heartbeat, broker disconnected, data stale, position mismatch, open order mismatch, max daily loss breached

**Warning/Critical**:
- Slippage above threshold, reject rate spike, feature drift breach, metric degradation

**Dashboard elements**:
- Current equity, positions, gross/net exposure, orders/fills state, realized/unrealized PnL, data latency, broker health, strategy-level PnL, slippage by symbol, risk-limit status

### Deployment Checklist

| Item | Status |
|---|---|
| Hypothesis documented with falsification criterion | ☐ |
| Data pipeline with quality gates, raw immutable | ☐ |
| Feature store with versioning and point-in-time policy | ☐ |
| Signal generation with unit tests | ☐ |
| Walk-forward epochs completed, review notes written | ☐ |
| DSR and PBO calculated for all optimizations | ☐ |
| Strategy weak-point score calculated | ☐ |
| Smoke test passed (no-op strategy) | ☐ |
| Deterministic toy strategy produces known output | ☐ |
| Paper trading: live-vs-backtest delta report for ≥4 weeks | ☐ |
| All 11 logging streams operational | ☐ |
| Audit chain hashing operational | ☐ |
| Run manifest generated for every run | ☐ |
| Kill criteria documented | ☐ |
| Critical alerts configured and tested | ☐ |
| Risk limits enforced (position, daily loss, exposure) | ☐ |
| Golden-run regression test established | ☐ |
| Backup/recovery procedures tested | ☐ |
| Incident response plan documented | ☐ |
| Capital ramp-up plan documented | ☐ |

### Failure Modes
- **No kill criteria**: losing strategies continue indefinitely because there's no rule to stop them.
- **Missing logs**: unlogged trades cannot be explained, audited, or fixed.
- **No golden run**: regressions go undetected until PnL surprises.
- **Skipping paper trading**: going directly from backtest to live is the fastest way to lose money.
- **Alert fatigue**: too many warnings cause critical alerts to be ignored.
- **Risk limits not enforced**: coded but not enforced by the risk engine.

### Cross-Links
- [[Logging-Audit-Monitoring]] — 11 required log streams
- [[Logging-Audit-Monitoring]] — hash chain and run manifest
- [[Logging-Audit-Monitoring]] — alert types and dashboard
- [[Logging-Audit-Monitoring]] — 8-layer testing
- [[Logging-Audit-Monitoring]] — test priorities
- [[Epoch-Learning-Retraining]] — drift controls that trigger retraining or kill
- [[Epoch-Learning-Retraining]] — retraining rules and drift types
- [[Logging-Audit-Monitoring]] — mistake categorization for every trade
- [[Trading-System-Build-Doctrine]] — this document

---

## Phase 6: Review, Learn & Iterate

### What
- Continuous learning from every epoch, trade, and incident.
- Systematic review backlog with labeled weak points.
- Retraining only on schedule or drift trigger — never emotional reaction.

### Key Concepts
- **Review cadence** ([[Review-And-Learn-Loop]]):
  - Every backtest run: automatic metric pack
  - Every serious experiment: written review
  - Every epoch: promotion/rejection note
  - Every paper-trading week: live-vs-backtest delta report
  - Every live-trading day: operational incident review
- **Review questions**: What changed? Did code/data/config change? What weak point got better/worse? Did improvement come from real edge or looser assumptions? Is it robust to costs and nearby parameters? Does it survive OOS? What's the next falsification test?
- **Learning backlog labels**: `strategy_edge`, `data_quality`, `execution`, `risk`, `code_bug`, `overfit_risk`, `ops_failure`, `market_regime`
- **Retraining rules** ([[Epoch-Learning-Retraining]]):
  - Retrain when: schedule triggers, feature drift exceeds threshold, signal IC decays, new regime, new data passes QC
  - Do NOT retrain when: one bad trade, drawdown within expected range, emotional reaction, wanting backtest to look better
- **Model drift types**: feature drift, label drift, concept drift, execution drift, regime drift
- **Drift controls**: Feature PSI/KL/KS tests, rolling signal IC, calibration curves, live-vs-backtest slippage, regime classification heatmap

### Deliverables
- Epoch review notes
- Weak-point review board
- Retraining reports
- Post-trade reviews with mistake categorization
- Updated learning backlog

### Failure Modes
- **Reactive retraining**: retraining after one bad trade or drawdown introduces whipsaw behavior.
- **Review without action**: collecting reviews but not updating the system.
- **Emotional overrides**: manual intervention that bypasses the strategy's risk rules.
- **Undocumented promotions**: promoting to live without write-up of why.

### Cross-Links
- [[Review-And-Learn-Loop]] — review cadence, questions, backlog labels
- [[Epoch-Learning-Retraining]] — retraining rules, drift types, controls
- [[Strategy-Weak-Point-Detection]] — weak-point categories and scoring
- [[Logging-Audit-Monitoring]] — review fields and mistake categories
- [[Logging-Audit-Monitoring]] — dashboards feed daily reviews

---

## Strategy-to-Code Translation Rules

These rules translate any trading idea from paper to production code:

1. **If you can't write the hypothesis, you can't code the strategy.** The hypothesis document is a prerequisite.
2. **Every signal is a function with explicit inputs and outputs.** No implicit data dependencies.
3. **Every exit rule is coded with the same rigor as the entry.** Entry + exit = strategy.
4. **Every parameter is in a config file, not hardcoded.** Enables systematic testing.
5. **Every assumption is encoded as a test.** Look-ahead → test with time-shifted data. Cost sensitivity → test with 2x, 3x costs. Regime dependency → test with regime segmentation.
6. **The code path is the same for research and live.** Same pipeline, same features, same signal logic. Only data source and execution adapter differ.
7. **Logs are part of the system, not an add-on.** An unlogged trade is an unexplainable trade.

---

## Source Quality & Vendor Registry

### Source Ranking (per [[Source-Quality-Rules]])
| Rank | Source Type |
|---|---|
| 1 | Peer-reviewed journal or official publisher |
| 2 | Author personal page / university repository |
| 3 | NBER / SSRN / arXiv working paper |
| 4 | Official framework/vendor documentation |
| 5 | High-quality industry whitepaper |
| Reject | Blogs, SEO farms, piracy mirrors, uncited social posts |

For implementation docs, official vendor documentation outranks tutorials.

### Legal Standards (per [[Legal-Download-Notes]])
- **Included**: Author pages, institutional repositories, public working papers, official documentation
- **Excluded**: Sci-Hub, LibGen, piracy mirrors, CAPTCHA-gated files, broken HTML renamed as PDFs

---

## Anti-Cookie-Cutter Insights

1. **The tactic stack is the real edge**: regime gate → exposure throttle → execution filter. The signal is only the beginning.
2. **Quality gates before everything**: garbage data → garbage features → garbage signals → garbage trades. Check quality first.
3. **Epoch discipline compounds**: every epoch review makes the next epoch smarter. Skipping reviews = stagnation.
4. **The kill switch is the most important code you'll write**: everything else can fail and the kill switch saves you.
5. **Simplicity beats breadth**: 2-3 well-tested features and signals outperform 10 weakly understood ones.
6. **Documentation is not overhead**: it's the difference between a strategy you can manage and one you hope works.
