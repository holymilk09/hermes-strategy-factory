# Mean Reversion Strategy Variants

Mean reversion is NOT one strategy. It is a family of dislocation trades. Each context demands a different variant.

## A. Trend-Pullback Mean Reversion
**Best for**: Strong leaders
- Stock in strong uptrend
- Pullback reaches 10 EMA / 20 MA
- Range contracts, volume dries up
- Buy reclaim / breakout from tight pullback

**This is NOT "fade strength."** It is: buy temporary weakness inside leadership.

## B. Range-Edge Mean Reversion
**Best for**: Sideways markets
- Price reaches range low
- Volatility spike occurs
- Breakdown fails
- Enter reclaim
- Target range midpoint or upper value area

## C. VWAP Mean Reversion
**Best for**: Intraday
- Price deviates far from VWAP
- Order flow exhausts
- Price reclaims micro level
- Target VWAP or partial VWAP

## D. Pairs Mean Reversion
**Best for**: Related instruments
- A/B spread diverges
- Spread z-score extreme
- Pair relationship stable
- No event explains divergence
- Trade convergence

**Academic backing**: Gatev, Goetzmann, Rouwenhorst found positive self-financing portfolio returns in pairs trading — a relative-value framework, not a simple indicator trade.

## E. Factor-Residual Mean Reversion
**Best for**: Professional stat arb
- Remove market/sector/factor movement
- Trade ONLY idiosyncratic residual overreaction
- This is the Avellaneda & Lee approach

## F. Event Overreaction Mean Reversion
**Best for**: After news/macro
- Initial move is large
- Market overreacts
- Price fails to continue
- Reclaim appears
- Trade partial retracement
- **Hardest part**: distinguish overreaction from correct repricing

## Which Variant Should We Build?
Given our setup (daily bars, Alpaca, ~$30k paper account, US equities):
- **A (Trend-Pullback)** — already partially tested as Qullamaggie. Failed on large caps.
- **B (Range-Edge)** — feasible. Needs range detection + failed breakdown logic.
- **E (Factor-Residual)** — most professional. Needs sector ETF regression. Aligns with user's inelasticity interest.
- **F (Event Overreaction)** — hardest to automate. Future work.

**Recommendation**: Start with E (factor-residual) — it uses the correct anchor (residual, not raw price) and aligns with the Kyle's Lambda microstructure direction.

## Cross-Links
- [[01-Edge-Sources-And-Fair-Value-Anchors]] — each variant maps to different edge sources
- [[07-Best-Combos]] — practical combinations of variants
- [[17-Arbitrage-Framework/6-PCA-ETF-Residual-Stat-Arb]] — implementation reference for variant E
- [[16-Strategy-Encyclopedia/Professional-Quant-Strategies]] — strategy cards for these
