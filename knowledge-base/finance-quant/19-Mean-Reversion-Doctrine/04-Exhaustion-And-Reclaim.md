# Exhaustion Confirmation — Don't Buy the Falling Knife

## Rule
**Stretch creates interest. Exhaustion/reclaim creates the trigger.**

## Useful Confirmation Signals

| Signal | Meaning |
|---|---|
| Undercut and reclaim | Sellers pushed below a level but failed to hold it |
| Close back inside prior range | Breakdown/breakout failed |
| VWAP reclaim | Intraday control shifted back |
| Volume climax then fade | Forced selling/buying may be exhausted |
| Lower low but less downside volume | Selling pressure weakening |
| Order-flow imbalance flips | Aggressive selling/buying no longer dominates |
| Spread normalizes | Liquidity stress easing |
| No continuation after stop sweep | Liquidity grab failed |

## Academic Backing
Cont, Kukanov, Stoikov: short-horizon price changes are strongly related to order-flow imbalance at best bid/ask, with impact related to market depth.

## Why This Matters
Our current engine enters on RSI(2) < 10 + consecutive lower closes. That's ONLY measuring stretch. We have ZERO exhaustion confirmation.

We are literally buying the falling knife and hoping it stops falling.

## What We Need to Add
At minimum, one of:
1. **Close reclaim**: price closes back above prior day's low after undercutting it
2. **Volume exhaustion**: today's selling volume < yesterday's (on a down day)
3. **Range reclaim**: price closes in upper half of day's range after gap down
4. **Higher low formation**: intraday higher low after the initial flush

## Cross-Links
- [[05-Two-Stage-Entry-Template]] — exhaustion is Stage 2
- [[08-Market-Microstructure/01-Order-Flow-Microstructure-Synthesis]] — order flow for exhaustion detection
- [[01-Edge-Sources-And-Fair-Value-Anchors]] — edge source defines what should exhaust
