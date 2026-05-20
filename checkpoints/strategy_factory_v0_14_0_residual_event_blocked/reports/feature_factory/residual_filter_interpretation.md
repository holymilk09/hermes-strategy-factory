# Residual Reversion Filter — Interpretation

Classification: FILTER_ONLY_CANDIDATE / EVENT_CONTEXT_INCOMPLETE

## What It Is

Residual reversion means a stock moved too far relative to its sector ETF benchmark,
and that idiosyncratic dislocation may revert if it was temporary rather than real repricing.

## Current Finding

residual_z <= -2.0 is a FILTER-ONLY candidate. It is NOT standalone alpha.

Standalone:
- Z_NEG_2_0 @ 20d: n=338, mean=+2.49%, hit=57.1%
- Random baseline: BORDERLINE (actual 2.49% vs p95 6.04%)
- Conclusion: Does not decisively beat random selection as standalone

Strategy-conditioned:
- mean_reversion + Z_NEG_2_0: +0.72% over BASE (196 events)
- structural_mr + Z_NEG_2_0: +2.05% over BASE (71 events)
- Conclusion: Improves MR setup quality but sample is small

Extreme:
- Z_NEG_2_5 @ 20d: n=51, mean=+5.24%, hit=80.4%
- Conclusion: SAMPLE_BLOCKED / WATCHLIST_ONLY

## Permitted Uses

- Mean-reversion setup conditioner
- Structural MR entry filter
- Dislocation detector
- Avoid-fading-real-repricing warning (with event context)

## Forbidden Uses

- Standalone buy signal
- Automatic short signal
- Live trading trigger
- Threshold mining (no -1.75, -2.25, -2.75 testing)
- Replacement for stop/exit/risk logic

## Missing

- EVENT_CONTEXT_INCOMPLETE: cannot distinguish temporary dislocation from real repricing
- Needs earnings/fundamental/event data before promotion
