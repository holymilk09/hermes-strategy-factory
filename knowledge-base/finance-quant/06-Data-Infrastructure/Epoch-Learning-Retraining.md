# Epoch Learning & Retraining

Synthesized from raw ingestion corpus: `epoch_learning_model.md`, `retraining_rules.md`, `model_drift_rules.md`, `review_and_learn_loop.md`, `walk_forward_epoch_protocol.md`, and `strategy_weak_point_detection.md`.

---

## Key Concepts

### The Epoch Model

An epoch is a **fixed research/review cycle**, not continuous parameter tweaking:

```
hypothesis -> train -> validate -> test -> deploy/paper -> review -> backlog -> next epoch
```

Each epoch is a complete experiment with a hypothesis, a decision, and a learning artifact. It does NOT mean changing parameters until the backtest looks good.

### Epoch Record Schema

Every epoch must record:
- **Epoch ID** — unique identifier
- **Hypothesis ID** — which hypothesis is being tested
- **Data version** — which data snapshot was used
- **Feature version** — which feature set was used
- **Train / Validation / Test windows** — locked dates
- **Parameters tried** — full trial log
- **Winning parameters** — selected configuration
- **OOS metrics** — out-of-sample performance
- **Stress metrics** — cost sensitivity, regime segmentation, parameter neighborhood
- **Promotion decision** — promote / reject / hold
- **Weak points** — identified fragilities
- **Next actions** — what the next epoch should address

### Walk-Forward Protocol

1. Define hypothesis and falsification rule
2. Lock train/validation/test dates (no peeking)
3. Train or select parameters on train/validation only
4. Evaluate **once** on test
5. Run stress and cost sensitivity
6. Generate heatmaps (parameter, regime)
7. Write review
8. Decide: promote, reject, or hold

### Model Drift Types

| Drift Type | Meaning | Detection |
|---|---|---|
| Feature drift | Input distribution changed | PSI/KL/KS tests on feature distributions |
| Label drift | Outcome distribution changed | Distribution shift in target variables |
| Concept drift | Feature-outcome relationship changed | Rolling signal IC, calibration curves |
| Execution drift | Fill/slippage environment changed | Live-vs-backtest slippage comparison |
| Regime drift | Macro/liquidity/volatility changed | Regime classification heatmap |

### Retraining Rules

**Retrain ONLY when:**
- Predefined schedule triggers (e.g., monthly, quarterly)
- Feature drift exceeds threshold
- Signal IC decays below threshold
- Strategy enters a known different regime
- New data passes quality checks

**Do NOT retrain when:**
- One bad trade occurs
- Live drawdown is within expected historical range
- You are emotionally reacting to losses
- You want the latest backtest to look better

**Required retraining output:**
- New model version
- Old vs new metric comparison
- Feature drift report
- OOS test report
- Promotion or rejection note

### Review and Learn Loop

**Review cadence:**
- Every backtest run → automatic metric pack
- Every serious experiment → written review
- Every epoch → promotion/rejection committee note (even if solo)
- Every paper-trading week → live-vs-backtest delta report
- Every live-trading day → operational incident review

**Review questions:**
1. What changed from the previous run?
2. Did the code/data/config change?
3. What weak point got better?
4. What weak point got worse?
5. Did improvement come from real edge or looser assumptions?
6. Is the result robust to costs?
7. Is the result robust to nearby parameters?
8. Does it survive OOS?
9. What is the next falsification test?

**Learning backlog labels:**
`strategy_edge`, `data_quality`, `execution`, `risk`, `code_bug`, `overfit_risk`, `ops_failure`, `market_regime`

### Strategy Weak-Point Detection

**Weak-point categories and detection:**

| Category | Detection Method |
|---|---|
| Parameter fragility | Heatmap cliff, low neighborhood stability |
| Regime fragility | Poor performance in vol/liquidity/trend buckets |
| Symbol concentration | PnL dominated by few instruments |
| Time concentration | PnL dominated by month/day/session bucket |
| Trade concentration | Top 5 trades explain most profit |
| Cost fragility | Edge disappears after higher slippage/spread |
| Execution fragility | High rejects, partial fills, live/paper slippage gap |
| Data fragility | Quality flags correlate with profits |
| Model drift | Feature distribution or signal IC changes |

**Weak-point score:**
```
weakness_score =
  0.25 * parameter_fragility
+ 0.20 * regime_concentration
+ 0.15 * trade_concentration
+ 0.15 * cost_sensitivity
+ 0.10 * symbol_concentration
+ 0.10 * model_drift
+ 0.05 * data_quality_risk
```
Use as prioritization, not truth.

---

## Implications for Real Trading Systems

- **Epoch discipline compounds**: each reviewed epoch makes the next smarter. Skipping reviews = stagnation.
- **Retraining is a decision, not a reflex**: emotional retraining after losses introduces whipsaw. Use schedule + drift triggers only.
- **Drift detection is early warning**: by the time PnL is bad, it's been bad for weeks. Drift detectors catch degradation before PnL.
- **Weak-point scoring tells you what to fix first**: don't guess — measure and prioritize.
- **The review loop is the system's immune system**: without it, bugs, drift, and overfitting compound silently.

---

## Potential Failure Modes

- **Moving test windows after bad results**: this is cheating. The test window is locked before training.
- **Reusing test set until it passes**: this destroys the test set's out-of-sample property.
- **Adding features without logging trials**: undocumented feature additions are invisible multiple testing.
- **Promoting on a single metric improvement**: improvement in Sharpe with worse drawdown is not improvement.
- **Drift false positives**: too-sensitive drift thresholds trigger unnecessary retraining.
- **Drift false negatives**: too-lenient thresholds allow degraded models to continue.
- **Review without action**: collecting reviews but not acting on weak points = wasted effort.
- **Emotional override**: manual intervention bypassing the epoch protocol.
- **Undocumented promotions**: deploying without a write-up = impossible to audit later.
- **Epoch too short**: 1-2 weeks of data doesn't cover enough market states for valid evaluation.
- **Epoch too long**: 2+ years means you won't detect degradation quickly enough.

---

## Cross-Links

- [[Trading-System-Build-Doctrine]] — Phases 3, 5, 6 operationalize the epoch model
- [[Review-And-Learn-Loop]] — the full review loop from the raw corpus
- [[Strategy-Weak-Point-Detection]] — weak-point categories and scoring formula
- [[Epoch-Learning-Retraining]] — the companion note below (also covers drift controls)
- [[Data-Pipeline-Architecture]] — feature versions tracked per epoch
- [[Feature-Store-Design]] — feature versioning is critical for epoch reproducibility
- [[Papers-Docs-Synthesis#strategy-development-process]] — Peterson's experiment design framework
- [[Papers-Docs-Synthesis#overfitting-and-backtest-rigor]] — DSR and PBO for epoch validation
- [[Logging-Audit-Monitoring]] — epoch review decisions go in the review_log stream
- [[Logging-Audit-Monitoring]] — post-trade data feeds epoch weak-point detection
