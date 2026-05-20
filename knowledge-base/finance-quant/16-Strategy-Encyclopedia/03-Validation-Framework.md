# Validation Framework

> Every strategy must pass through a validation pipeline before live deployment. This defines the 14 required test types, strategy-test matrix, and minimum baselines that all strategies — especially ML strategies — must beat.

---

## Core Principle

**Validation is not optional.** A strategy without validation is a gambling system with a story attached. The validation framework separates hypotheses that survive contact with reality from those that don't.

### What Validation Does NOT Prove
- It does not prove future profitability
- It does not guarantee the edge hasn't decayed
- It does not eliminate tail risk
- It only eliminates strategies that fail basic reality checks

### What Validation Does Prove
- The strategy survives transaction costs
- The strategy beats naive approaches
- The strategy is not the product of data mining or overfitting (with high probability)
- The strategy has a defined failure mode boundary

---

## 14 Required Validation Tests

### Test 1: Naive Baseline (BUY-AND-HOLD)
**What**: Compare strategy returns to simple buy-and-hold of the same asset(s) over the same period.
**Pass criteria**: Risk-adjusted return (Sharpe or Sortino) must exceed buy-and-hold. Raw return alone is insufficient — drawdown matters.
**Why**: If you can't beat holding, you should be holding. This eliminates strategies that are worse than passive.

### Test 2: Linear Baseline (Simple Model)
**What**: Compare against a single-factor linear model (e.g., linear regression of returns on one feature).
**Pass criteria**: Strategy must significantly outperform the best single-factor linear prediction.
**Why**: If a single linear feature beats your complex strategy, your complexity is worthless.

### Test 3: Random Signal Baseline
**What**: Generate random entry/exit signals with the same signal frequency as the strategy. Run 10,000+ iterations.
**Pass criteria**: Strategy must be above 95th percentile of random distribution.
**Why**: Eliminates strategies that succeed due to luck or favorable randomness.

### Test 4: Turnover-Matched Random Baseline
**What**: Generate random signals with the SAME turnover (trade frequency) as the strategy.
**Pass criteria**: Strategy must be above 95th percentile of turnover-matched random.
**Why**: A critical ML gate. High-turnover strategies have more opportunities to get lucky. This accounts for turnover.

### Test 5: In-Sample / Out-of-Sample Split
**What**: Train on IS period, test on OOS period. Standard 70/30 or 60/40 temporal split.
**Pass criteria**: OOS performance must remain within 50% of IS performance for Sharpe. Degradation beyond 50% suggests overfitting.
**Why**: The most basic test of generalization.

### Test 6: Walk-Forward Analysis
**What**: Rolling window: train on N periods, test on next M. Slide forward and repeat.
**Pass criteria**: Average OOS Sharpe across all windows must exceed baseline. Consistency across windows required.
**Why**: Tests robustness to changing market conditions over time.

### Test 7: Cross-Validation (Time-Series Aware)
**What**: K-fold cross-validation with TIME-SERIES folds (not random shuffling). Each fold preserves temporal ordering.
**Pass criteria**: Performance consistent across folds. No single fold should dominate results.
**Why**: Standard CV shuffles time, creating look-ahead. Time-series CV preserves causality.

### Test 8: Monte Carlo / Randomization Test
**What**: Shuffle returns or signals 10,000+ times, recompute strategy metrics each time.
**Pass criteria**: Actual strategy Sharpe must be in top 5% of shuffled distribution.
**Why**: Tests whether results could arise from lucky timing alone.

### Test 9: Parameter Stability / Sensitivity Analysis
**What**: Perturb each parameter ±10-20% and re-run. Map performance surface.
**Pass criteria**: Performance should not collapse with small parameter changes. Flat plateau > sharp peak.
**Why**: Single-parameter peak performance is curve-fitting. Robust strategies perform well across parameter neighborhoods.

### Test 10: Transaction Cost Analysis
**What**: Apply realistic commission, slippage, and spread to every trade. Test with 2x, 3x estimated costs.
**Pass criteria**: Strategy must remain positive with 2x estimated costs.
**Why**: Many strategies exist only in frictionless backtests.

### Test 11: Maximum Drawdown Stress
**What**: Measure worst historical drawdown and its duration. Apply as hard constraint.
**Pass criteria**: Max drawdown must be within trader's risk tolerance. Duration must be survivable.
**Why**: A strategy with 5 Sharpe and 80% drawdown is untradeable by nearly all real investors.

### Test 12: Regime Segmentation Test
**What**: Split data by regime (trending, mean-reverting, high-vol, low-vol, bull, bear). Test strategy in each regime.
**Pass criteria**: Document which regimes the strategy works in and which it fails in. No strategy works in all regimes.
**Why**: Understanding regime dependency prevents surprise losses when conditions change.

### Test 13: Out-of-Sample Asset Test
**What**: Apply the same strategy logic to different, unseen assets (same instrument class or different).
**Pass criteria**: Performance should not completely collapse. Some degradation expected.
**Why**: If the strategy only works on one ticker, it's a ticker-specific coincidence, not a strategy.

### Test 14: Live Paper Trading (Forward Test)
**What**: Run strategy in real-time with paper trading for minimum 3-6 months before going live.
**Pass criteria**: Paper trading performance within 20% of backtest Sharpe.
**Why**: Backtests miss: execution friction, latency, data feed issues, slippage reality, psychological factors.

---

## Strategy-Test Matrix

| Test | Basic (1-3) | Intermediate (4-6) | Professional (7-10) |
|---|---|---|---|
| 1. Naive Baseline | **Required** | **Required** | **Required** |
| 2. Linear Baseline | Optional | **Required** | **Required** |
| 3. Random Signal | Optional | **Required** | **Required** |
| 4. Turnover-Matched | — | Optional | **Required** |
| 5. IS/OOS Split | **Required** | **Required** | **Required** |
| 6. Walk-Forward | Optional | **Required** | **Required** |
| 7. Cross-Validation | — | Optional | **Required** |
| 8. Monte Carlo | — | Optional | **Required** |
| 9. Parameter Sensitivity | — | **Required** | **Required** |
| 10. Transaction Cost | **Required** | **Required** | **Required** |
| 11. Max Drawdown | **Required** | **Required** | **Required** |
| 12. Regime Segmentation | Optional | **Required** | **Required** |
| 13. OOS Asset Test | — | Optional | **Required** |
| 14. Paper Trading | Optional | Optional | **Required** |

### ML-Specific Tests (Level 5+)
| Test | ML Level 5 | ML Level 9 |
|---|---|---|
| 4-Baseline Minimum | **Required** | **Required** |
| k-Fold + TS Split | **Required** | **Required** |
| Feature Importance | **Required** | **Required** |
| Leakage Tests | **Required** | **Required** |
| Drift Detection | Optional | **Required** |
| Online Performance | Optional | **Required** |
| Adversarial Validation | Optional | **Required** |
| Permutation Importance | Optional | **Required** |

---

## Minimum Baselines (The 4-Barrier Rule)

**No ML strategy passes without beating ALL four baselines:**

### Baseline 1: Naive (Buy-and-Hold)
- Simple: long the asset for entire period
- Multi-asset: equal-weight buy-and-hold
- Pass: Strategy Sharpe > Naive Sharpe

### Baseline 2: Linear (Single-Factor Model)
- OLS regression: return ~ feature (single most predictive feature)
- Cross-sectional: factor tilt (long top decile, short bottom)
- Pass: Strategy Sharpe > Linear Sharpe

### Baseline 3: Random Signal
- Random entry/exit with same signal frequency
- 10,000+ iterations
- Pass: Strategy Sharpe > 95th percentile of random

### Baseline 4: Turnover-Matched Random
- Random signal preserving strategy's exact turnover rate
- Same number of trades, same holding period distribution
- Pass: Strategy Sharpe > 95th percentile of turnover-matched random

### Why All Four?
Each baseline eliminates a different type of false positive:
1. **Naive** → Eliminates "worse than passive"
2. **Linear** → Eliminates "complexity overfit"
3. **Random** → Eliminates "lucky timing"
4. **Turnover-Matched Random** → Eliminates "high-frequency luck"

### The Hurdle Bar
If a complex ML strategy barely beats random signals, it has no edge. It is noise-fitting with a statistical wiggle room.

---

## Validation Failure Decision Tree

```
Does strategy beat naive baseline?
├── NO → DEPRECATED or revisit hypothesis
└── YES → Does it beat linear baseline?
    ├── NO → Feature is insufficient; simplify
    └── YES → Does it beat random signal?
        ├── NO → Likely overfit; regularize or reduce parameters
        └── YES → Does it beat turnover-matched random?
            ├── NO → High-turnover luck; reduce frequency or improve signal quality
            └── YES → PASS → Proceed to paper trading
```

---

## Anti-Cookie-Cutter Insight

**The most insidious validation failure is passing one test but failing another.** A strategy might beat naive baseline (test 1) but fail random test (test 3), meaning it's not worse than buy-and-hold but it's no better than luck. Another might pass random but fail turnover-matched random, meaning it's only working because it trades frequently enough to stumble into good luck. Pass ALL baselines or pass NONE.

---

## Cross-References
- [[Schema and Taxonomy]] — Strategy card field 15: validation_tests[]
- [[Failure Mode Catalog]] — Overfitting, look-ahead, regime failure modes
- [[Feature Engineering Catalog]] — Leakage tests for feature pipelines
- [[Master Index]] — Full encyclopedia overview
- [[Professional Equivalent Map]] — How professionals validate (institutional pipeline)
