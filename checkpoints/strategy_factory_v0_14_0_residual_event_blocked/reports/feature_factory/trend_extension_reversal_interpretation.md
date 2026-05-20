# Trend-Extension Reversal — Signal Interpretation

Status: PRELIMINARY_SIGNAL_CANDIDATE / PRELIMINARY_AVOID_CHASING_FILTER

## What It Actually Says

Technical extension (strong MACD, SMA momentum, overextended price) predicts **short-to-medium-term underperformance**. Less-extended or compressed names outperform most-extended names over a 20-day horizon.

```
D1  most extended:  -0.57% / hit 46.1%
D10 least extended: +1.29% / hit 56.9%
Spread D10-D1:       +1.86%
```

## Signal Type

**Threshold filter — NOT a linear ranking factor.**

- D1-D3: avoid/chasing risk zone — do not enter longs here
- D4-D8: neutral/noisy — ignore for signal purposes
- D9-D10: potential long-candidate / pullback / compression zone

The relationship is not monotonic. D2-D8 show no clean gradient. Only the extremes matter.

## Pooled IC (30-symbol audit)

| Label | IC |
|---|---|
| forward_return_20d | +0.110 |
| excess_vs_spy_20d | +0.053 |
| log_forward_return_20d | +0.110 |
| triple_barrier | +0.039 |

Modest, not large. The original Phase 4 per-symbol IC (-0.38) was inflated by averaging and non-generalizable.

## Permitted Uses

- Long-entry filter (avoid D1-D3)
- Take-profit warning
- Avoid-chasing filter
- Pullback timing filter
- Compression confirmation
- Mean-reversion entry conditioner
- Qullamaggie pullback/compression filter

## Forbidden Uses

- Automatic short signal (extended names can keep squeezing)
- Standalone long/short alpha
- Live trading signal
- Any claim of profitability or trade readiness

## Working Hypothesis

This signal pairs naturally with:
- Qullamaggie watchlist (leader + compression > leader + extension)
- Mean-reversion reclaim
- Momentum swing after pullback
- Factor-residual mean-reversion

Next test: strategy-conditioned validation — does this signal improve existing strategy setups?
