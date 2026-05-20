# Options Trading Strategies — Encyclopedia

**Family**: Options trading strategies
**Source**: Batch 3 — Strategy Encyclopedia specification
**Core Rule**: Options have fundamentally different failure modes than equity strategies.

---

## Why Options Need Their Own Strategy Cards

Options strategies fail for reasons normal equities don't:
- **Bid/ask spread decay** — multi-leg entry costs often destroy edge before trade begins
- **Assignment risk** — early exercise on shorts is non-deterministic and creates unplanned inventory
- **IV regime mismatch** — high IV strategies need vol to come down; selling during low IV is structurally negative EV
- **Multi-leg fill risk** — legging into positions at different prices changes the intended risk profile
- **Margin behavior** — buying options has defined risk but selling options has theoretically unlimited margin requirements
- **Gamma behavior near expiry** — delta hedging creates whipsaw losses in choppy regimes
- **Term structure surprises** — calendar/diagonal spreads depend on futures curve shape, not just spot price

**Rule**: Every options card must account for Greeks, margin, IV sensitivity, and liquidity requirements.

---

## Strategy Cards (Categorized by Greek Profile)

### Directional Options (Delta-Dominated)

#### OPT-001: Long Call
- **Edge Source**: Trend + volatility (implicit positive vega)
- **Greeks**: +Delta, +Gamma, +Vega, -Theta
- **Max Profit**: Unlimited (theoretical)
- **Max Loss**: Premium paid (finite)
- **Margin**: None beyond premium
- **IV Sensitivity**: High — needs IV expansion or stable low IV on entry
- **Theta Behavior**: Decay accelerates in final 30 days
- **Best Regime**: Strong directional move with IV expansion
- **Worst Regime**: Chop, low volatility, IV crush post-event
- **Professional Equivalent**: Leveraged equity position with defined risk; equivalent to futures + long put
- **Failure Mode**: Paying for optionality that time decay erodes before directional move materializes
- **Required Data**: Options chain, IV term structure, earnings/event calendar, underlying OHLCV

#### OPT-002: Long Put
- **Edge Source**: Trend (down) + volatility
- **Greeks**: -Delta, +Gamma, +Vega, -Theta
- **Professional Equivalent**: Protective equity position or bearish speculation with defined risk
- **Failure Mode**: Same as long call — theta decay is the silent killer
- **Required Data**: Options chain, IV term structure, underlying OHLCV

#### OPT-003: Covered Call
- **Edge Source**: Volatility (short vol premium) + structural
- **Greeks**: +Delta (underlying) -Delta (short call), -Vega, +Theta
- **Max Profit**: Limited to strike premium above cost basis
- **Max Loss**: Underlying decline minus premium received
- **Assignment Risk**: High at expiry if ITM; early exercise possible around dividends
- **IV Sensitivity**: Positive — benefits from selling premium when IV is elevated
- **Best Regime**: Flat to slightly bullish with declining volatility
- **Worst Regime**: Sharp rallies (opportunity cost) or sharp declines (full equity downside)
- **Professional Equivalent**: Equity overlay / volatility monetization; equivalent to long stock + short call = synthetic short put
- **Failure Mode**: Selling capped upside for small premium during sustained bull markets; or holding through drawdowns where premium doesn't cover losses
- **Required Data**: Options chain, dividend calendar, IV rank, underlying positioning

#### OPT-004: Cash Secured Put
- **Edge Source**: Volatility (short vol) + structural (insurance buyer needs)
- **Greeks**: -Delta, +Vega, +Theta
- **Professional Equivalent**: Short put = same payoff as covered call (put-call parity)
- **Failure Mode**: Forced to buy stock at strike when intrinsic value drops below cost basis; margin locked in cash
- **Required Data**: Options chain, IV rank, underlying fundamentals

### Vertical Spreads (Defined Risk)

#### OPT-005: Bull Call Spread (Debit Spread)
- **Edge Source**: Directional + mean reversion of vol
- **Greeks**: +Net Delta, -/+/Net Vega (depends on strikes), +/- Theta
- **Max Profit**: Difference between strikes minus debit paid
- **Max Loss**: Debit paid
- **IV Sensitivity**: Lower than naked options — partially hedged against vol changes
- **Best Regime**: Moderate bullish move, stable or declining IV
- **Professional Equivalent**: Defined-risk directional trade; cost reduction vs naked long call
- **Failure Mode**: Stock moves sideways — still expires worthless; overpaying for volatility premium in the long leg

#### OPT-006: Bear Put Spread (Debit Spread)
- Mirror of bull call spread for downside. Same structural considerations.

#### OPT-007: Bull Put Spread (Credit Spread)
- **Edge Source**: Volatility (short vol) + directional
- **Greeks**: +Net Delta, -Net Vega, +Theta
- **Professional Equivalent**: Similar payoff to bull call spread with different capital structure; credit received as initial positive cash
- **Failure Mode**: Gap below short put strike causes max loss instantly; stop-loss difficult during overnight gaps
- **Required Data**: Options chain, IV rank, support/resistance levels, earnings calendar

#### OPT-008: Bear Call Spread (Iron Condor Wing)
- Mirror of bull put spread for upside.

### Multi-Leg Neutral Strategies (Gamma-Dominated)

#### OPT-009: Iron Condor
- **Edge Source**: Volatility (short vol), range-bound regime
- **Greeks**: Net Delta ≈ 0, -Vega, +Theta, -Gamma
- **Max Profit**: Total premium received
- **Max Loss**: Width of wing - total credit
- **Margin**: Width of one spread
- **IV Sensitivity**: High — IV crush dramatically increases value
- **Best Regime**: Range-bound with elevated IV that declines
- **Worst Regime**: Breakout (either direction) with rising IV
- **Professional Equivalent**: Selling insurance on both sides of a range; equivalent to short strangle + protective wings
- **Failure Mode**: Breakthrough one or both wings during trending regime; IV expansion widens all strike prices; assignment risk on short legs
- **Required Data**: Options chain, IV rank/percentile, volatility surface, earnings calendar, ATR, support/resistance

#### OPT-010: Iron Butterfly
- Like iron condor but with centered strikes (sell ATM call+put, buy OTM wings). Tighter risk/reward ratio, higher profit potential, narrower range.

#### OPT-011: Short Straddle
- **Edge Source**: Volatility (short vol)
- **Greeks**: Net Delta ≈ 0, -Vega, +Theta, -Gamma (large magnitude)
- **Max Loss**: Unlimited (both directions)
- **Professional Equivalent**: Pure short volatility; selling optionality across all regimes
- **Failure Mode**: Any significant directional move causes unlimited losses; margin requirements can force liquidation; assignment unpredictable
- **Required Data**: Options chain, IV rank, underlying realized vol vs implied vol, earnings/calendar events

#### OPT-012: Long Straddle
- **Edge Source**: Volatility expansion (long vol) + directional uncertainty
- **Greeks**: +Vega, -Theta, +/- Gamma
- **Max Loss**: Premium paid
- **Professional Equivalent**: Pure long volatility; buying optionality
- **Failure Mode**: IV crush post-event, slow movement where theta decay outpaces vol expansion
- **Best Regime**: Pre-earnings or pre-announcement with low IV and expectation of high IV after

#### OPT-013: Short Strangle
- Like short straddle but with OTM strikes. Lower probability of moneyness, wider profit range, slightly less premium.

#### OPT-014: Long Strangle
- Like long straddle but with OTM strikes. Cheaper entry, wider break-even points.

### Calendar and Cross-Horizon Strategies

#### OPT-015: Calendar Spread
- **Edge Source**: Volatility term structure (selling near-term vol, buying deferred vol)
- **Greeks**: Variable Delta by setup, +Vega (long deferred vol), net theta depends on structure
- **Professional Equivalent**: Term structure arbitrage — capturing time decay gradient between horizons
- **Failure Mode**: IV crush on near-term leg destroys value; IV spike on long leg increases cost basis; wrong term structure slope

#### OPT-016: Diagonal Spread
- Calendar spread + strikes at different levels. Adds directional component to term structure bet. More complex management, wider risk profile.

### Ratio and Asymmetric Strategies

#### OPT-017: Ratio Spread
- Buy X options at one strike, sell 2X+ options at another. Creates defined risk on one side, undefined on the other.

#### OPT-018: Backspread
- Buy more options than sold, typically at different strikes. Long vol with negative cost structure.

### Specialized Strategies

#### OPT-019: Risk Reversal (Collar Alternative)
- **Edge Source**: Directional + volatility surface skew
- **Greeks**: +Delta, Vega ≈ neutral, Theta ≈ neutral
- **Professional Equivalent**: Equity position + vol surface play; equivalent to synthetic forward with skew overlay
- **Failure Mode**: Skew moves against direction; IV differential narrows

#### OPT-020: Synthetic Long/Short Stock
- **Edge Source**: Structural (arbitrage between synthetic and actual equity)
- **Greeks**: Delta ≈ ±1.0, Gamma ≈ 0, Vega ≈ 0
- **Professional Equivalent**: Equity position synthetically replicated for arbitrage or leverage reasons
- **Failure Mode**: Bid/ask spread on synthetic leg destroys theoretical edge; margin inefficiency

### Active Management Strategies

#### OPT-021: Delta Hedging
- **Edge Source**: Volatility (realizing implied vs realized vol differential)
- **Professional Equivalent**: Volatility arbitrage; realizing the difference between implied premium and actual movement
- **Failure Mode**: Transaction costs from frequent rebalancing destroy edge; large gaps between rebalancing points; path dependency makes P&L non-linear
- **Required Data**: Options chain, underlying tick/minute data, IV surface, hedging costs

#### OPT-022: Gamma Scalping
- **Edge Source**: Volatility (realized vs implied) + gamma
- **Greeks**: Delta ≈ 0 (hedged), +Gamma, +Vega (long straddle/strangle)
- **Professional Equivalent**: Systematic volatility extraction — trading the curvature of options
- **Failure Mode**: Theta decay faster than gamma scalping profits; transaction costs from frequent hedge adjustments; wrong vol regime (need high realized, low implied)
- **Required Data**: Options chain, underlying tick data, IV surface, transaction cost analysis

#### OPT-023: Volatility Risk Premium Harvesting
- **Edge Source**: Volatility (IV consistently overprices RV over long horizons)
- **Professional Equivalent**: Systematic short vol; harvesting the variance risk premium that institutions pay for hedging
- **Failure Mode**: Tail risk events cause extreme losses far exceeding typical premium; margin calls during crises when VRP temporarily inverts; survivorship illusion from many small wins masking one catastrophic loss
- **Required Data**: Historical IV, RV, options chain, VIX, realized volatility calculations

#### OPT-024: Earnings IV Crush
- **Edge Source**: Volatility (IV systematically overprices pre-earnings moves)
- **Greeks**: -Vega, +Theta (short premium strategies)
- **Professional Equivalent**: Event-driven vol selling; exploiting the gap between pre-event uncertainty and post-event reality
- **Failure Mode**: Earnings moves that exceed IV price-in assumption; gap risk; directional surprise overwhelms vol premium captured

### Relative Value Strategies

#### OPT-025: Dispersion Trade
- **Edge Source**: Correlation (implied index vol > weighted individual vol due to correlation premium)
- **Professional Equivalent**: Correlation arbitrage — short index vol, long constituent vol
- **Failure Mode**: Correlation regime shift during market stress (correlations converge to 1); index vol doesn't collapse as expected
- **Required Data**: Index and constituent options chains, implied correlations

#### OPT-026: Skew Trade
- **Edge Source**: Volatility surface shape (put skew mispriced relative to call vol)
- **Professional Equivalent**: Volatility surface arb across strike space
- **Failure Mode**: Tail event causes skew to widen dramatically; short skew leg experiences large losses

#### OPT-027: Term Structure Trade
- **Edge Source**: Volatility term structure (front vs back month mispricing)
- **Professional Equivalent**: Term structure arbitrage
- **Failure Mode**: Curve shape surprise during stress; contango/inversion transitions

#### OPT-028: VIX ETP Strategy
- **Edge Source**: Volatility decay (VIX futures roll yield in contango)
- **Professional Equivalent**: Systematic short vol product creation
- **Failure Mode**: Volatility spike causes catastrophic losses (VXX-style); timing the exit is critical
- **Required Data**: VIX futures curve, VIX ETP pricing, contango/backwardation signals

---

## Options-Specific Failure Summary

| Failure Mode | Mechanism | Mitigation |
|---|---|---|
| Bid/ask spread decay | Multi-leg entry costs eat edge | Only enter when spread < 10% of option premium |
| Assignment risk | Counterparty exercises early | Avoid short options near dividend dates; have stock/buyback plan |
| IV regime mismatch | Selling vol in low IV = structural -EV | Only sell vol when IV rank > 50th percentile |
| Multi-leg fill risk | Legs filled at different prices | Use combo orders; simulate legged entry/exit |
| Margin amplification | Short options require significant margin | Size positions for worst-case margin, not expected |
| Theta decay | Time value erodes long premium | Avoid buying options with < 45 DTE unless specific event catalyst |
| Gamma whipsaw | Delta hedges create losses in chop | Reduce rehedging frequency in low-vol regimes |
| Liquidity gap | Wide spreads make adjustment expensive | Only trade options with > 100 open interest and tight spreads |

---

*Cross-linked: [[Schema-and-Taxonomy]], [[Validation-Framework]], [[Failure-Mode-Catalog]], [[Professional-Equivalent-Map]], [[Feature-Engineering-Catalog]]*
