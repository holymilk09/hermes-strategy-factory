# Filters and No-Trade Logic

## Rule
**The best mean-reversion systems are MOSTLY filters.**

A great MR setup should have at least 4 of these 8 filters:

| # | Filter | Purpose |
|---|--------|---------|
| 1 | Regime filter | Avoid one-way trend/crash regimes |
| 2 | Fair-value anchor | Define what "mean" actually means |
| 3 | Vol-normalized deviation | Avoid arbitrary thresholds |
| 4 | Liquidity exhaustion | Avoid catching knives |
| 5 | Reclaim trigger | Confirms failed continuation |
| 6 | Event/news filter | Avoid fading real repricing |
| 7 | Cost/capacity filter | Prevent fake edge |
| 8 | Time stop | MR should work quickly or be wrong |

## No-Trade Rules

Block the trade if:
- Earnings within next 1-2 days
- Fresh negative guidance
- Fraud/accounting issue
- Major downgrade with real fundamental change
- Stock breaks 50 MA on huge volume
- Market in crash regime
- Spread is wide
- Volume is too low
- Borrow is unavailable (for shorts)
- Trend is accelerating against the setup
- Price has NOT reclaimed any level
- ATR expansion is extreme

## Bad vs Better Filter Stack

**Bad** (cookie-cutter):
- RSI < 30
- Price below lower Bollinger Band

**Better** (non-cookie-cutter):
- residual_z < -2.2
- AND price above rising 50 MA
- AND no earnings/news shock
- AND volume capitulation occurred
- AND price reclaimed prior low
- AND spread normalized
- AND target before stop offers > 1.5R
- AND setup has positive expectancy in this regime

## How Many Filters Does Our Current Engine Have?

| Filter | Current Engine | Status |
|---|---|---|
| Regime | SMA200 binary | ⚠️ Too slow |
| Fair-value anchor | Raw RSI | ❌ Wrong anchor |
| Vol-normalized deviation | None | ❌ Missing |
| Liquidity exhaustion | None | ❌ Missing |
| Reclaim trigger | None | ❌ Missing |
| Event/news filter | None | ❌ Missing |
| Cost/capacity | $0.005 + 10bps | ✅ Present |
| Time stop | None | ❌ Missing |

**Score: 1.5 / 8 filters.** This is why OOS fails.

## Cross-Links
- [[03-Regime-Filter]] — detailed regime rules
- [[04-Exhaustion-And-Reclaim]] — exhaustion confirmation signals
- [[09-Time-Stops-And-Sizing]] — time stop implementation
- [[10-Failure-Modes]] — what happens when filters are missing
