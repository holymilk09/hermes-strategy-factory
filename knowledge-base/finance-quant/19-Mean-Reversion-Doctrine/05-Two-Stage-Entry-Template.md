# Two-Stage Entry Template

## Rule
**Bad entry**: Buy when price is stretched.
**Better entry**: Stage 1 detect dislocation → Stage 2 wait for reclaim/failed continuation.

## Example Long Setup (Non-Cookie-Cutter)

1. Stock is in a bullish higher-timeframe trend
2. Price pulls sharply below 10 EMA / 20 MA / VWAP
3. Move is > 2 ATR or residual_z < -2
4. Volume spikes into selloff
5. Price undercuts prior low
6. **Price reclaims that low or reclaims VWAP** ← THIS IS THE TRIGGER
7. Enter on reclaim or first higher low
8. Stop below sweep low
9. Target: VWAP / 10 EMA / prior range midpoint / fair-value residual mean

## Compare to Our Current Engine

| Component | Current (Cookie-Cutter) | Doctrine (Non-Cookie-Cutter) |
|---|---|---|
| Edge source | None defined | Liquidity pressure / temporary overreaction |
| Fair value | Raw price RSI | Residual z-score / VWAP deviation |
| Deviation | RSI(2) < 10 | Vol-normalized z < -2.0 |
| Exhaustion | None | Undercut-reclaim / volume climax |
| Entry trigger | RSI threshold cross | Reclaim of swept level |
| Stop | Fixed 3% | Below sweep low (structural) |
| Target | Fixed 2% | VWAP / 20 MA / residual mean |
| Time stop | None | Exit if no reversion within N days |
| Regime | SMA200 (too slow) | Multi-factor regime score |

**Verdict: Our current engine has 2/9 components. This doctrine requires 9/9.**

## Cross-Links
- [[04-Exhaustion-And-Reclaim]] — Stage 2 signals
- [[02-Deviation-Scoring]] — Stage 1 thresholds
- [[12-Strategy-Template-Config]] — full YAML config for this template
