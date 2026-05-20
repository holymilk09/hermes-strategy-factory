# Edge Sources and Fair-Value Anchors

## Prime Rule
**No edge source = no mean-reversion trade.**

The first component is not an indicator. It is the REASON price should revert.

## Valid Edge Sources

| Edge Source | What It Means |
|---|---|
| Liquidity pressure | Someone needed immediacy and pushed price too far |
| Inventory imbalance | Dealers/MMs adjusted inventory, then price normalizes |
| Panic / capitulation | Sellers became price-insensitive |
| Stop-run / liquidity sweep | Obvious levels swept, then price failed to continue |
| Factor residual dislocation | Stock moved too far vs sector/factor peers |
| Pair/relative-value spread | Two historically related assets diverged abnormally |
| VWAP / institutional execution distortion | Price deviated from session fair value |
| Volatility overshoot | Realized/implied vol spiked beyond normal regime |
| Event overreaction | Market initially mispriced news or macro event |

**Academic backing**: Avramov, Chordia, Goyal document reversals tied to illiquidity — largest effects in high-turnover, low-liquidity stocks. But transaction costs can exceed contrarian profits.

## Fair-Value Anchors

**Rule: Mean reversion should usually be RESIDUAL reversion, not raw price reversion.**

Bad anchors (arbitrary):
- Price is far from 20 MA
- RSI is low
- Stock is down 5%

### Better Anchors by Strategy Type

| Strategy Type | Better Anchor |
|---|---|
| Intraday stock | VWAP, anchored VWAP, prior day value area |
| Trend pullback | 10 EMA / 20 MA / rising 50 MA |
| Pairs trade | Hedge-adjusted spread |
| Stat arb | PCA / ETF / factor residual |
| Sector relative value | Sector ETF-adjusted return |
| Options | Implied vol vs realized vol / peer vol / surface fit |
| Crypto perp basis | Spot/perp basis and funding-normalized fair value |
| Macro event | Pre/post-event expected distribution |

**Academic backing**: Avellaneda & Lee model U.S. equity stat-arb using PCA or sector ETF regressions, trading idiosyncratic residuals as mean-reverting processes.

## Implications for Our System
Our current RSI(2) strategy uses **raw price RSI** — the most cookie-cutter anchor possible. It answers "is price low?" not "is price dislocated from fair value?"

**Upgrade path**: Replace RSI(2) with residual z-score against sector ETF or VWAP deviation.

## Cross-Links
- [[02-Deviation-Scoring]] — how to measure stretch from these anchors
- [[08-Market-Microstructure/01-Order-Flow-Microstructure-Synthesis]] — Kyle's Lambda for liquidity pressure
- [[17-Arbitrage-Framework/6-PCA-ETF-Residual-Stat-Arb]] — factor residual implementation
- [[06-Strategy-Variants]] — each variant uses different anchors
