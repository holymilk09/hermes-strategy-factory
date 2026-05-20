# Hermes Strategy Factory

**Status: RESEARCH-ONLY — Not production-ready. Not live-trading-ready.**

A multi-phase quantitative strategy research and validation framework built with Hermes Agent.
Validates alpha signals through escalating statistical gates before any strategy migration.

## Current State
- **16 validation phases complete** (Phase 2 → 12.5)
- **Active candidate:** Residual reversion (residual_z <= -2.0 + GOOD/ACCEPTABLE R²)
- **Classification:** CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED
- **Production migration:** BLOCKED
- **Live trading:** BLOCKED

## Core Components
- `feature_factory/` — 16 Python modules for feature computation, validation, and store management
- `reports/feature_factory/` — Phase-by-phase validation reports (Phase 2-12.5)
- `config/` — Strategy configs, feature registry, backtest integration plan
- `alpha_graveyard/` — Permanently rejected signals with forbidden rescue rules
- `knowledge-base/` — Quant doctrine, mean reversion docs, research notes

## Active Research Track
Residual reversion (factor-residual MR, Avellaneda & Lee approach):
- Sector ETF regression computes idiosyncratic residual returns
- Residual_z <= -2.0 flags extreme deviations
- GOOD/ACCEPTABLE fit filter (R² >= 0.20) required — without it, BORDERLINE at best
- Passes strategy-conditioned random pruning (250 perms) for mean_reversion and structural_mr
- **Blocked:** Event context incomplete — needs FMP earnings calendar for event-risk blocking

## Rejected Tracks
- **Trend Extension Reversal:** FAILED standalone decile ranking on 76-stock universe. 
  Backtrader random-pruning FAILED. Permanently archived. Do not rescue.

## Running Health Checks
```bash
# Gateway health
ps aux | grep 'hermes gateway run'

# Watchdog
cat /opt/data/gateway.pid
cat /opt/data/gateway-watchdog.pid

# Checkpoint verification
ls checkpoints/strategy_factory_v0_14_0_residual_event_blocked/
```

## Blocked Actions
See `docs/BLOCKED_ACTIONS.md` for full list.
