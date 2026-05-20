---
title: Pattern Validation Rules
pillar: 18
---

# Validation & Data Snooping Guards

## Problem
Pattern mining creates thousands of candidate rules. Overfitting is the main risk.

## Required Controls
1. White's Reality Check (2000) — corrects p-values for data snooping
2. Deflated Sharpe Ratio (Bailey/López de Prado 2015) — adjusts for trial multiplicity
3. Three-way split: discovery → validation → final test
4. Walk-forward validation on out-of-sample data
5. Bootstrap confidence intervals
6. Multiple testing adjustment (Bonferroni, Holm-Bonferroni, BHY)

## Alpha Graveyard
Log EVERY failed test:
pattern_id, tested_dates, universe, result, why_failed
Never hide failed patterns. Decay tracking is essential.

## AI/ML Validation
AI output is a SIGNAL CANDIDATE, not a trade. Required validation:
- naive baseline (buy-and-hold)
- linear baseline (simple regression)
- random signal baseline
- turnover-matched baseline
- walk-forward validation
- leakage audit
- transaction-cost stress
- model drift monitoring
