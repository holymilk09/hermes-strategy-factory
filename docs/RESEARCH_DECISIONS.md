# Research Decisions

## Trend Extension Reversal — REJECTED
- **Phase 4.5:** 30-symbol audit showed +1.86% D10-D1 spread
- **Phase 5:** 76-symbol full universe showed -0.19% — FAILED
- **Phase 8:** Retail-constrained structural MR all filters REJECTED (-16% to -31%)
- **Phase 9:** Backtrader random-pruning D8_D10 FAILED
- **Verdict:** REJECTED_FILTER / VALID_NEGATIVE_RESULT
- **Action:** Permanently archived in alpha_graveyard. Do not rescue, retune, or reseed.

## Residual Reversion — ACTIVE but EVENT-BLOCKED
- **Phase 11.5:** Residual diagnostic packet — median R²=0.3723, 67/76 usable symbols
- **Phase 12:** Standalone random pruning FAILED. Strategy-conditioned required.
- **Phase 12.5:** Repaired bug — strategy signal filter applied BEFORE residual_z.
  With GOOD/ACCEPTABLE fit: BEATS_STRATEGY_RANDOM and BEATS_PORTFOLIO_RANDOM.
- **Status:** CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED
- **Next:** FMP dry run → event overlay trial → controlled research backtest with event blocking

## FMP Sandbox
- **Phase 13:** FMP client skeleton, cache structure, PIT policy created
- **Phase 13.5:** Blocked — FMP_API_KEY missing
- **Role:** Event-risk blocker only — block/warn/tag, never trigger trades
