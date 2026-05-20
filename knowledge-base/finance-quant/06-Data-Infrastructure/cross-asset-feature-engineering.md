# Cross-Asset Feature Engineering

Cross-asset features embed macro risk context into per-asset signals. They answer: "What does the broader risk environment say about this trade?"

## Key Concepts

| Asset Class | Features | Primary Use |
|---|---|---|
| Equity Indexes | SPY/QQQ/IWM returns | Risk-on/off gate, relative strength |
| Volatility | VIX, realized vol proxy | Regime detection, volatility targeting, size adjustments |
| Rates | 2Y/10Y yields, yield curve slope | Macro shock detection, sector rotation context |
| Dollar | DXY proxy | FX carry context, EM vs DM flows |
| Commodities | Oil, gold | Inflation proxy, flight-to-safety |
| Credit | HYG/LQD, spread proxies | Credit stress detection, liquidity regime |
| Crypto | BTC/ETH trend, funding rates, open interest | Risk appetite pulse (especially in 24/7 hours) |

**Use cases:**
- **Risk-on/risk-off gates**: block equity longs when credit spreads widen aggressively
- **Sector rotation context**: relative index momentum signals sector leadership shifts
- **Volatility targeting**: scale positions inversely to cross-asset realized vol
- **Event avoidance**: suppress signals during macro event windows detected via vol/credit spikes
- **Macro shock detection**: multi-asset dislocations (rates + credit + equity moving together) indicate structural breaks

## Implications

- Cross-asset features are **regime classifiers**, not alpha generators — they tell you *when* a signal is likely to work, not *what* to trade
- Each feature needs a falsification test: "If I remove VIX from the model, does Sharpe degrade significantly?" without one, you're adding complexity without proving edge
- Cross-asset signals must use **correct timestamps** — a VIX close at 16:15 ET shouldn't leak into a 16:00 decision
- Simpler cross-asset stacks outperform complex ones: 2-3 well-tested features beat 10 weakly understood ones

## Failure Modes

- **Dimensionality creep**: adding every cross-asset feature available without a causal story inflates model complexity and overfit risk
- **Correlation decay**: cross-asset relationships break during regime shifts (e.g., negative stock-bond correlation in 2022)
- **Timestamp misalignment**: different asset classes close at different times; using a "closing" price from an asset that trades past 16:00 creates look-ahead
- **Funding rate misinterpretation** (crypto): high funding ≠ directional signal without volume/OI context
- **Credit spread proxies lag**: HYG/LQD are ETF proxies, not CDS spreads — they embed equity beta alongside credit risk

## Cross-Links

- [[Regime Detection Features]] — cross-asset data is the primary input for regime classification
- [[Multi-Timeframe Features]] — cross-asset data must be aligned across timeframes
- [[Feature Leakage Prevention]] — timestamp alignment is the #1 risk in cross-asset features
- [[regime-detection-features]] — cross-asset risk is rated medium priority
- [[13F Macro Alt-Data Tactics]] — macro data sources and calendar considerations
- [[Build Doctrine]] — Phase 1 requires point-in-time feature timestamps before any strategy logic
- [[Strategy-to-Code Playbook]] — every signal hypothesis must include a regime filter
