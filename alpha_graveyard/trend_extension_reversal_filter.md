# Trend-Extension Reversal Filter — REJECTED

**Classification:** REJECTED_FILTER / VALID_NEGATIVE_RESULT

**Date archived:** 2026-05-18

## What It Was

A filter that used technical extension composite (MACD, SMA slopes, momentum) inverted to identify compressed/less-extended stocks. Hypothesis: least-extended names outperform most-extended names over 20d.

## Escalation Arc (Phases 4-9)

Phase 4: IC=0.38 — flagged suspicious
Phase 4.5: IC corrected to 0.05-0.11, D10-D1=+1.86% on 30 symbols
Phase 5: Full 76-symbol universe — D10-D1=-0.19% — standalone FAILED
Phase 6: Per-trade event analysis — directional improvement
Phase 7: Portfolio simulation — improvement with bugs
Phase 8: Retail constraints — bugs found (D8/D9 count inversion, structural_mr rejection error, duplicate result mapping)
Phase 8.5: Audit corrected bugs — D8_D10 showed PF 1.64 vs BASE 0.82 for structural_mr
Phase 9: Backtrader random pruning — D8_D10 PF (22.81) below random p50 (31.22) — FAILED

## Why It Failed

Under Backtrader simulation with canonical signals and retail portfolio constraints, the D8_D10 filter did not beat random same-count trade selection. If the filter added unique information, it would outperform random pruning. It did not.

## Key Lessons

1. Intermediate validation is not enough. A signal can pass IC, decile, and event tests and still fail random-pruning baseline.
2. Position congestion artifacts can inflate apparent filter performance — the D8_D10 vs D9_D10 count inversion was a position management artifact.
3. Profit factor is unreliable when denominators are small or simulation has numerical issues.
4. Random-pruning baseline is the correct final gate.

## Forbidden Resuscitation

Do not retune this filter with:
- D7-D10, D6-D10 thresholds
- Different random seeds
- Different stop/exit combinations
- Alternate labels
- Changed wording

Unless a new independent hypothesis is defined and tested as a separate research item.
