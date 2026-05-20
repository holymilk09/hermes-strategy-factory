# Regime Detection Features

Regime features aggregate market conditions into discrete buckets that gate whether signals are allowed, sized, or rejected outright.

## Key Concepts

**The Tactic Stack Order:**
1. Primary signal (alpha)
2. Regime gate (allow/block)
3. Exposure throttle (size up/down)
4. Execution filter (order type, max size)
5. Review segmentation (diagnose where it works/fails)

**Regime Feature Map:**

| Regime | Indicator Features | Strategy Implication |
|---|---|---|
| Low vol uptrend | Low realized vol, rising breadth, positive index momentum | Trend/pullback strategies may work |
| High vol downtrend | High realized vol, negative breadth, widening spreads | Reduce size, avoid mean reversion without stops |
| Choppy range | Low trend strength, mean-reverting returns | Mean-reversion possible, trend signals weak |
| Liquidity stress | Wide spreads, low depth, high volatility | Reduce order size, avoid market orders |
| Event regime | Macro/earnings/high news density | Block entries or lower exposure |

**High-value aggregate features:**
- Realized volatility regime
- Market breadth (% of stocks above moving average)
- Dollar volume percentile
- Spread percentile
- Sector momentum
- Cross-asset risk regime
- Options IV rank/skew
- Macro event calendar proximity
- Funding/OI for crypto
- Institutional/crowding probes

## Implications

- Regime gates are the **highest-leverage feature** — a mediocre signal in the right regime outperforms a great signal in the wrong one
- Regime classification must be **forward-looking at decision time**: you classify using only data available *now*, not what the regime "was" by end of week
- Segmentation in review is essential: aggregate backtest metrics hide regime-dependent performance (e.g., strategy only works in low-vol uptrend, fails everywhere else)
- Heatmaps should be built on regime slices, not just parameter slices

## Failure Modes

- **Regime hindsight bias**: using end-of-period regime labels to label training data (the regime was only clear in retrospect)
- **Regime overfitting**: too many regime buckets → each bucket has too few data points for reliable inference
- **Regime lag**: using long lookback windows delays regime transitions, trapping the system in the old regime during a crash
- **Circularity**: if the regime uses the same features as the signal, you're double-counting
- **Regime instability**: boundaries that work in one period fail in another (e.g., fixed VIX thresholds when structural vol levels change)

## Cross-Links

- [[cross-asset-feature-engineering]] — cross-asset returns feed regime classification
- [[Multi-Timeframe Features]] — regime can be detected on higher timeframe and applied to lower
- [[regime-detection-features]] — realized vol, market breadth, spread/liquidity all rated high priority
- [[Feature Leakage Prevention]] — regime features are especially leak-prone due to revised macro data
- [[Aggregated Data Tactics]] — the full tactic stack architecture
- [[Build Doctrine]] — Phase 5 mandates regime review in walk-forward epochs
- [[Production Trading Checklist]] — post-run review must flag weakest regimes
