# Strategy Factory State

## Feature Factory
- 16 Python modules in `feature_factory/`
- Feature registry at `config/feature_registry.yaml` (51K, comprehensive)
- Purged walk-forward CV, leakage audit, redundancy analysis all implemented
- Residual feature engine computes sector-ETF-regressed residuals

## Validation Gates (Escalating)
1. Feature computation + storage (Phase 2-3)
2. Leakage audit (Phase 3)
3. Standalone IC + decile analysis (Phase 4)
4. Full universe confirmation (Phase 4.5)
5. Strategy-conditioned tests (Phase 5)
6. Retail-constrained simulation (Phase 8)
7. Backtrader random-pruning (Phase 9)
8. Strategy-conditioned random pruning (Phase 12-12.5)

## Residual Candidate
- **Signal:** residual_z <= -2.0
- **Required gate:** GOOD/ACCEPTABLE fit (R² >= 0.20) from sector ETF regression
- **Passes:** Strategy-conditioned random pruning (250 perms)
- **Blocked:** Event context — earnings, surprises, fundamental repricing
- **FMP role:** Event-risk blocker only — not alpha

## FMP / Event Blocker
- FMP sandbox exists at `config/fmp_sandbox.yaml`
- FMP event features at `config/fmp_event_features.yaml`
- **Blocked:** FMP_API_KEY missing
- Allowed use: block/warn/tag — never trigger trades

## Production / Live Status
- Production migration: **BLOCKED** on all tracks
- Live trading: **BLOCKED** on all tracks
- Only controlled research backtests allowed
