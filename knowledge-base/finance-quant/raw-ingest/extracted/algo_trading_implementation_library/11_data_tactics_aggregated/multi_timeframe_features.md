# Multi-Timeframe Features

## Useful combinations

| Higher timeframe | Lower timeframe | Use |
|---|---|---|
| Daily trend | Intraday pullback | trend-aligned entries |
| Weekly trend | Daily breakout | longer-horizon confirmation |
| Hourly volatility | 5-minute execution | order timing and risk |
| Daily liquidity | Intraday order size | capacity and fill logic |

## Warning

Never let lower-timeframe decisions use incomplete higher-timeframe bars as if they were closed. Label every feature as `closed_bar`, `partial_bar`, or `live_estimate`.
