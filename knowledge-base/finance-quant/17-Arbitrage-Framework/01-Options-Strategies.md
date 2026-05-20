# Options Arbitrage Strategies

**Source**: Batch 5 — Arbitrage Strategy Research Pack; synthesized from [[Options-Trading-Strategies]], [[Options-Volatility-Synthesis]], [[Schema-and-Taxonomy]], and research literature.
**Family**: Options/Relative Value Arbitrage (Difficulty 8–10)
**Core Rule**: Put-call parity is an identity, not a strategy — the edge comes from the frictions around it.
**Key Insight**: Every options arbitrage is fundamentally a test of whether market microstructure (spreads, fees, borrowing costs, assignment risk) makes the theoretical edge executable.

---

## OPA-001: Put-Call Parity Arbitrage

**Edge source**: structural, statistical
**Asset classes**: Equities, options
**Timeframes**: Intraday, tick

**Core Mechanism**:
Put-call parity states: C − P = S − PV(K) (call minus put equals spot minus present value of strike). Any deviation creates a synthetic mispricing between a protective put (long stock + long put) and a fiduciary call (long call + cash equal to PV(K)).

**Execution Structure**:
- When C − P > S − PV(K): Buy synthetic put (short stock + long call + PV(K) cash), buy actual put → locked profit
- When C − P < S − PV(K): Buy synthetic call (long stock + long put), buy actual call → locked profit
- Close all legs simultaneously at expiry or when parity reverts

**Professional Equivalent**:
- Market makers enforce parity continuously via automated systems
- Edge exists only transiently, captured by high-frequency systems with direct exchange access

**Data needed**: Options chain (real-time), spot price, interest rate curve, dividend schedule
**Failure modes**: 
- Bid-ask spread on multi-leg entry destroys theoretical edge
- Borrow cost on short stock leg may exceed captured spread
- Dividend surprises change the parity equation (S adjusted on ex-date)
- Execution latency — arb window closes in milliseconds
- Assignment risk on short options legs

**Anti-Cookie-Cutter Insight**:
Put-call parity arb is the "free money" that professionals treat as a cost center. Retail traders see a parity violation and think "profit"; market makers see it as an invitation that their auto-hedge already priced in. The real question is never "is it mispriced?" but "who is mispricing it and why?" — if you can't answer that, you're likely the liquidity being provided.

---

## OPA-002: Box Spread Arbitrage

**Edge source**: structural, carry
**Asset classes**: Options
**Timeframes**: Intraday to multi-day

**Core Mechanism**:
A box spread combines a bull call spread and a bear put spread at the same strikes, creating a riskless payoff equal to the strike difference at expiry. The theoretical value is (K₂ − K₁) discounted to present. If the box costs less than this discounted difference, arbitrage exists.

**Entry Structure**:
- Buy call K₁, sell call K₂ (bull call spread)
- Buy put K₂, sell put K₁ (bear put spread)
- Net payoff at expiry = K₂ − K₁ (deterministic)

**When It Works**:
- Early exercise risk on short legs is the dominant concern
- Only viable on European-style options (no early exercise risk) or deep ITM European options
- American-style options have non-deterministic early exercise that can destroy the locked payoff

**Professional Equivalent**:
- Fixed-income desks use box spreads as synthetic financing instruments
- Tax-motivated structuring (though this has regulatory scrutiny)

**Failure modes**:
- **Early exercise destroys the box** — the most critical failure. If a short American option is exercised early, the locked payoff becomes unhedged and exposure explodes
- Multi-leg spread costs compound (4 legs × bid/ask)
- Margin efficiency: brokers may not recognize the riskless nature and require full margin
- Commission erosion on the locked spread may exceed arb profit
- Tax complications in some jurisdictions (IRS scrutiny on box spreads used for tax deferral)

**Implementation**:
- Restrict to European options (index options like SPX)
- Verify that all legs fill at prices consistent with net arbitrage after costs
- Confirm margin treatment before execution
- Monitor for corporate actions (dividends, spin-offs) that affect option terms

---

## OPA-003: Volatility Arbitrage

**Edge source**: volatility, statistical
**Asset classes**: Options, volatility indices
**Timeframes**: 1d, 1w+

**Core Mechanism**:
Volatility arbitrage exploits the difference between a stock's implied volatility (what options prices predict) and its realized volatility (what actually happened). The trade is delta-neutral: long the option side that is cheap on a vol basis, short the option side that is expensive, hedge delta with the underlying.

**Structure Variants**:
- **Long vol arb**: Buy options when IV < RV forecast, delta-hedge to capture realized vol exceeding implied
- **Short vol arb**: Sell options when IV > RV forecast, delta-hedge to keep the excess premium
- **Relative vol arb**: Long vol on one stock, short vol on another with similar fundamentals but divergent IV

**Edge Source Detail**:
The Volatility Risk Premium (VRP) — the systematic tendency of IV to exceed RV — is one of the most persistent premiums across all asset classes (see [[Professional-Quant-Strategies]] S-PR-013). Institutions pay for portfolio insurance, creating structural demand for options that pushes IV above true expected RV.

**Delta-Hedging Requirement**:
The arb is not directional — it requires continuous delta hedging to isolate the vol component. This means:
- Rebalancing hedge as underlying moves (gamma exposure)
- Managing funding costs of the hedge position
- The number and timing of rebalances determines realized P&L

**Professional Equivalent**:
- Variance swap desks hedge away delta to isolate pure vol exposure
- Dispersion trading (see OPA-004) for index vs. constituent vol spreads
- Vol surface relative value trades using SVI parameterization (Gatheral 2006)

**Data needed**: Options chain, IV surface, historical RV, realized vol calculations, underlying tick data
**Failure modes**:
- Transaction costs from frequent delta rebalancing destroy edge
- Large gaps between rebalancing points create unhedged directional exposure
- IV regime shifts: a short vol arb can become a long vol position overnight during a spike
- Model risk: wrong vol model (BS vs. Heston) produces wrong hedge ratios
- Correlation in vol spikes: short vol positions all fail simultaneously during crises

**Anti-Cookie-Cutter Insight**:
Vol arb returns are path-dependent even when direction-neutral. Two identical setups — same IV, same RV, same strike, same delta hedge frequency — can produce materially different P&L because the realized path of the underlying determines how often and at what prices the hedge must be adjusted. This is the only "directional" element in a direction-neutral strategy.

---

## OPA-004: Dispersion Trading

**Edge source**: volatility, statistical
**Asset classes**: Index options + constituent options
**Timeframes**: 1d, 1w+

**Core Mechanism**:
Index implied volatility is typically higher than the weighted average implied volatility of its constituents. This "correlation premium" exists because index vol embeds the assumption that constituents move together. If the actual correlation is lower than what the index vol prices in, the dispersion trade profits.

**Standard Structure**:
- Short index options (e.g., SPX straddle)
- Long constituent options (e.g., individual S&P 500 name straddles), weighted by index membership
- Delta-hedge both legs to isolate the correlation component

**Profit Condition**:
Profit when actual realized correlation < implied correlation (the correlation priced into the index vs. constituents spread). The trade is a bet on correlation mean-reversion.

**Professional Equivalent**:
- Systematic correlation arbitrage at volatility-focused funds
- Relative value volatility trading (vol surface desk → correlation desk)

**Data needed**: Index options chain, all constituent options chains, index weights, IV surfaces, historical correlation matrix
**Failure modes**:
- **Correlation regime shift** — during market stress, correlations converge to 1 (the "correlation trap"), and the index vol spike overwhelms the long constituent vol positions
- Transaction costs on 20+ constituent legs compound dramatically
- Liquidity mismatch: index options are liquid; many individual constituent options are illiquid
- Rebalancing: index weight changes require adjusting constituent positions
- Margin and capital requirements across hundreds of options legs

**Anti-Cookie-Cutter Insight**:
Dispersion trading is a premium-selling strategy disguised as a hedge. You're selling the market's fear of systemic correlation (index vol) and buying the reality of idiosyncratic movement (individual vol). It works beautifully until everyone needs the exit door at once — then correlation spikes and the short index vol leg becomes catastrophic. The edge is real but the tail risk is asymmetric and underestimated by most backtests.

---

## OPA-005: Convertible Bond Arbitrage

**Edge source**: structural, volatility, carry
**Asset classes**: Convertible bonds, options, underlying equity
**Timeframes**: 1d, 1w+

**Core Mechanism**:
Convertible bonds combine a straight bond + embedded call option on the underlying stock. Convertible arb exploits mispricing between the convertible bond and its synthetic components by going long the convertible and short the underlying stock to delta-hedge, capturing the "cheap" embedded option.

**Execution Structure**:
1. Price the convertible using a model (e.g., binomial tree, Monte Carlo) that accounts for the bond floor + call option
2. When the convertible trades below its theoretical value (including the option component):
   - Buy the convertible bond
   - Short the underlying equity (delta-hedge ratio determined by the convertible's delta)
   - Collect the bond's coupon income
3. As stock price moves, adjust the short equity position (re-hedge delta)
4. Profit sources: cheap optionality + coupon income + volatility of the underlying (since you're long gamma through the convertible)

**Edge Components**:
- **Vol arb**: The embedded option is often priced at lower vol than standalone options on the stock
- **Carry**: Coupon income from the bond leg (positive carry if hedge financing cost < coupon)
- **Gamma**: Long gamma through the convertible, capturing realized vol via delta rebalancing

**Professional Equivalent**:
- Convertible arbitrage is one of the oldest hedge fund strategies (classic relative value)
- Requires prime brokerage for repo/borrow rates, convertible positioning
- Often paired with other credit relative value strategies

**Data needed**: Convertible bond pricing and terms (conversion ratio, call provisions, sinking fund), underlying stock price/vol, credit spread data, repo/borrow rates, options chain on underlying
**Failure modes**:
- Credit risk: if the issuer's credit deteriorates, the bond floor collapses (this is not delta-hedgeable)
- Liquidity mismatch: convertible bonds are far less liquid than the underlying stock
- Short stock borrow costs can exceed the coupon income, flipping carry negative
- Call provisions allow the issuer to force conversion, changing the payoff structure
- Market risk: during equity crashes, the hedge ratio changes rapidly and the bond floor may not hold
- Hard-to-borrow stocks (often the most volatile, highest-conviction arb targets) may be unavailable for shorting

**Anti-Cookie-Cutter Insight**:
Convertible arb is not pure volatility arbitrage — it's volatility arbitrage sitting on top of credit risk. When you buy a convertible, you're also buying credit exposure to the issuer. In a stress scenario, you get hit on both sides: the stock crashes (your short hedge doesn't fully offset because the bond floor doesn't hold) and credit spreads widen (the bond declines). This double jeopardy is why convertible arb had spectacular blow-ups in 2008 and 2020.

---

## Cross-References

- [[Professional-Quant-Strategies]] — S-PR-013: Volatility Risk Premium
- [[Options-Trading-Strategies]] — Full options strategy encyclopedia
- [[Options-Volatility-Synthesis]] — Stochastic vol, surface modeling, rough vol
- [[Schema-and-Taxonomy]] — Strategy card schema, difficulty ladder, edge taxonomy
- [[Family-9: Options/Volatility-Arbitrage]] — Options/Vol arb strategy family
- [[Market-Microstructure-LOB-Execution-Synthesis]] — Execution costs, slippage, liquidity
- [[Failure-Mode-Catalog]] — 11 failure types
- [[Master-Index]] — Full encyclopedia index
