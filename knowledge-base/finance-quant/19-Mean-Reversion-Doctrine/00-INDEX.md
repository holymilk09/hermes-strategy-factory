# Pillar 19 — Non-Cookie-Cutter Mean Reversion Doctrine

**Purpose**: Complete operational doctrine for mean reversion as a family of dislocation trades — NOT indicator-based entries.

**Core Thesis**: Mean reversion is not "RSI low, buy." It is: temporary dislocation + correct fair-value anchor + volatility-normalized stretch + exhaustion/reclaim confirmation + regime filter + cost-aware execution + time stop + post-trade diagnostics.

## Notes

| # | Note | Focus |
|---|------|-------|
| 01 | [[01-Edge-Sources-And-Fair-Value-Anchors]] | WHY price should revert + WHAT "mean" actually means |
| 02 | [[02-Deviation-Scoring]] | Vol-normalized stretch measures (z-score, ATR, residual) |
| 03 | [[03-Regime-Filter]] | When MR works vs dies — regime permission system |
| 04 | [[04-Exhaustion-And-Reclaim]] | Confirmation signals — don't buy the falling knife |
| 05 | [[05-Two-Stage-Entry-Template]] | Stage 1 (detect dislocation) → Stage 2 (confirm reclaim) |
| 06 | [[06-Strategy-Variants]] | 6 types: trend-pullback, range-edge, VWAP, pairs, factor-residual, event |
| 07 | [[07-Best-Combos]] | 5 proven non-cookie-cutter combinations |
| 08 | [[08-Filters-And-No-Trade-Logic]] | 8 filter framework + trade blocking rules |
| 09 | [[09-Time-Stops-And-Sizing]] | Time stops by strategy type + signal-quality sizing |
| 10 | [[10-Failure-Modes]] | 11 failure types with meanings |
| 11 | [[11-Heatmap-Diagnostics]] | Required diagnostic heatmaps for MR systems |
| 12 | [[12-Strategy-Template-Config]] | Full YAML strategy template |
| 13 | [[13-Hermes-Operational-Rules]] | Memory rules Hermes uses when reasoning about MR |

## Cross-Links
- [[18-Pattern-Situational-Alpha/00-doctrine/PATTERN_ALPHA_RULES]] — pattern validation applies to MR setups
- [[08-Market-Microstructure/01-Order-Flow-Microstructure-Synthesis]] — order flow exhaustion signals
- [[05-Risk-Portfolio-Execution/Heatmap-Playbook-Diagnostics]] — heatmap framework extends here
- [[16-Strategy-Encyclopedia/Professional-Quant-Strategies]] — MR strategies cataloged there
- [[06-Data-Infrastructure/regime-detection-features]] — regime features feed MR filter
- [[17-Arbitrage-Framework/6-PCA-ETF-Residual-Stat-Arb]] — factor-residual MR variant

## Academic References
- Avramov, Chordia, Goyal — reversals tied to illiquidity, transaction costs can erase edge
- Avellaneda & Lee — PCA/ETF residual stat-arb (residual reversion, not raw price)
- Lo & MacKinlay — rejected random walk for weekly returns, but predictability is conditional
- Cont, Kukanov, Stoikov — order-flow imbalance predicts short-horizon price changes
- Gatev, Goetzmann, Rouwenhorst — pairs trading positive returns, relative-value framework

*This pillar is the doctrinal foundation for any mean reversion strategy we build.*
