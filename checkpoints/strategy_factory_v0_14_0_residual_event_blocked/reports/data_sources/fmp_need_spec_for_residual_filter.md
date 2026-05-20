# FMP Fields Needed for Residual Filter Event Context

## Required Fields

| Field | Use | Blocks |
|---|---|---|
| earnings_date | Date of next/last earnings | Block residual_z entries 5d before earnings |
| earnings_time | BMO/AMC timing | Adjust pre-earnings block window |
| eps_surprise | EPS actual vs estimate | >20% surprise = real repricing, block fade |
| revenue_surprise | Revenue actual vs estimate | Large surprise = block |
| guidance_flag | Guidance raised/lowered | Guidance cut = block all residual entries for 10d |
| analyst_rating_change | Upgrade/downgrade date | Downgrade = block residual entries for 5d |
| sector | Sector classification | Improve sector-ETF residual mapping |
| industry | Industry classification | Sub-sector residual grouping |
| market_cap | Market capitalization | Liquidity segmentation |
| index_membership | SP500/NDX/RUT | Liquidity proxy |
| financial_update_date | Last 10-K/10-Q date | Flag stale fundamentals |

## Block Logic

If residual_z <= -2.0 AND any block condition:
- earnings within 5d: SKIP trade
- guidance cut: SKIP trade for 10d
- major downgrade: SKIP trade for 5d
- EPS surprise > 20%: SKIP trade (real repricing)
- Default: CAUTION_NOT_BLOCK (flag but allow)

## Status
SPEC_DEFINED — do not integrate FMP in Phase 11.5.
Evaluation and integration plan in Phase 12.
