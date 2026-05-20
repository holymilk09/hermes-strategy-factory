# Mean Reversion Failure Modes

| Failure | Meaning |
|---|---|
| Falling knife | Entered on stretch without confirmation |
| Real repricing | News/fundamentals changed; price SHOULD NOT revert |
| Trend day | MR disabled but bot traded anyway |
| Cost illusion | Edge existed before fees/slippage only |
| Illiquidity trap | Apparent reversal edge in names too expensive to trade |
| Short squeeze | Short MR trade against crowded squeeze |
| Bad anchor | Mean was arbitrary and irrelevant |
| Stale pair | Relationship broke |
| Overfit threshold | Works only at one magic z-score |
| Late entry | Reversion already happened before fill |
| No time stop | Short-term trade became long-term loss |
| Correlation pileup | Multiple positions were same hidden bet |

## Which Failures Hit Our Current Engine?

| Failure | Status | Evidence |
|---|---|---|
| Falling knife | ✅ ACTIVE | No exhaustion confirmation — RSI entry only |
| Real repricing | ✅ ACTIVE | No news/event filter — bought during Q1 2025 selloff |
| Trend day | ⚠️ PARTIAL | SMA200 too slow to catch trend days |
| Cost illusion | ❌ Clear | We model costs |
| Bad anchor | ✅ ACTIVE | RSI = arbitrary rank-based oscillator, not fair value |
| No time stop | ✅ ACTIVE | No time-based exit |
| Correlation pileup | ⚠️ Unknown | Not measuring position correlation |

**4 active failures, 2 partial.** This is fixable but requires a fundamental redesign of the entry logic.

## Cross-Links
- [[08-Filters-And-No-Trade-Logic]] — filters prevent most failure modes
- [[04-Exhaustion-And-Reclaim]] — prevents falling knife
- [[03-Regime-Filter]] — prevents real repricing and trend day
- [[05-Risk-Portfolio-Execution/Heatmap-Trade-Failure]] — failure mode diagnostics
