# Current Strategy Factory State

## System Status
- Feature factory: ACTIVE, 16 phases complete (Phase 2 → 12.5)
- Validation gates: ESCALATING, enforced
- Production migration: BLOCKED
- Live trading: BLOCKED

## Track 1: Trend Extension Reversal
- Status: REJECTED_FILTER / VALID_NEGATIVE_RESULT
- Reason rejected: D10-D1 spread failed on 76-stock universe (-0.19%). Survived as 
  hit-rate filter in MR contexts only, but Phase 8 retail-constrained showed 
  structural MR ALL FILTERS REJECTED. Phase 9 Backtrader random-pruning D8_D10 FAILED.
- Graveyard file: alpha_graveyard/trend_extension_reversal_filter.md
- Forbidden rescue rules: DO NOT retune thresholds, reseed, mine D6-D10 variants, 
  stop-hunt, or label-shop. Archived permanently.

## Track 2: Residual Reversion (Active)
- Status: CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED
- Current classification: CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED
- What passed: Strategy-conditioned random pruning (250 perms). 
  mean_reversion/GOOD (R²>=0.20) and structural_mr/GOOD both BEATS_STRATEGY_RANDOM 
  and BEATS_PORTFOLIO_RANDOM. ALL variants (no fit filter): BORDERLINE.
- What remains blocked: Event context incomplete. No earnings calendar. No surprise 
  data. No fundamental repricing detection. FMP_API_KEY missing.
- Why event context is needed: Residual reversion signals can trigger into earnings 
  or other fundamental events. The filter is only valid if it avoids event-period trades.

## FMP Event Overlay
- Status: SANDBOX_ONLY / BLOCKED_FMP_API_KEY_MISSING
- Why blocked: FMP_API_KEY not set in environment
- Allowed use: Event-risk blocker, metadata context, sector/industry tagging
- Blocked use: Alpha signal, trade trigger, production dependency, production migration

## Next Safe Step
1. Watchdog recovery [DONE this session]
2. GitHub-safe checkpoint [IN PROGRESS this session]
3. Set FMP_API_KEY externally if using FMP
4. Run FMP Phase 13.5 dry run and coverage audit
5. Only then test residual event overlay

## Critical Rules
- trend_extension_reversal is REJECTED — do not rescue
- residual_z <= -2.0 + GOOD/ACCEPTABLE R² is event-blocked
- FMP is sandbox-only
- production migration is BLOCKED
- live trading is BLOCKED
