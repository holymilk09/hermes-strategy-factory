# Best Mean-Reversion Combinations

## Combo 1 — Leader Pullback Reversion
Strong stock + bullish trend + pullback to 10/20 EMA + volume dry-up + reclaim.
**Use case**: Qullamaggie-style continuation. Mean reversion INSIDE trend, not bottom fishing.

## Combo 2 — Liquidity Sweep Reclaim
Prior low swept + volume spike + failed continuation + reclaim + target VWAP/range midpoint.
**Use case**: ICT/SMC concept converted into testable microstructure/reversal logic.

## Combo 3 — Sector-Neutral Residual Snapback
Stock underperforms sector ETF by extreme residual_z + no news + sector stable + stock reclaims level.
**Use case**: Professional equity stat arb.

## Combo 4 — VWAP Deviation with OFI Flip
Intraday price moves 2+ sigmas from VWAP + aggressive selling exhausts + order-flow imbalance flips + target VWAP.
**Use case**: Intraday liquid equities/futures.

## Combo 5 — Pair Spread Reversion
Cointegrated/similar pair spread z-score extreme + no event break + hedge ratio stable + spread starts reverting.
**Use case**: Relative-value long/short.

## Which Combo Fits Us?
- **Combo 3 (Sector-Neutral Residual)** — best fit for daily timeframe, US equities, aligns with Avellaneda & Lee, uses correct fair-value anchor
- **Combo 2 (Liquidity Sweep Reclaim)** — second best, needs intraday data for proper sweep detection
- **Combo 1 (Leader Pullback)** — already tried as Qullamaggie, failed on mega-caps

## Cross-Links
- [[06-Strategy-Variants]] — detailed variant descriptions
- [[05-Two-Stage-Entry-Template]] — entry mechanics for each combo
- [[08-Filters-And-No-Trade-Logic]] — filters apply to all combos
