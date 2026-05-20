# 8. Index Futures Cash-and-Carry

---

## Key Concepts

### Core Mechanism
Exploit mispricing between an index futures contract and its underlying spot index portfolio by simultaneously buying the cheaper and selling the more expensive, locking in a riskless (or near-riskless) profit after accounting for financing costs.

- **Futures fair value (cost-of-carry):** `F_theoretical = S_0 × exp((r - δ) · T)` where S_0 = spot index level, r = risk-free rate, δ = continuous dividend yield, T = time to expiry.
- **Cash-and-carry (futures overpriced):** Buy the spot basket of index constituents, sell the futures contract. Hold until expiry. Profit = F_market - F_theoretical - costs.
- **Reverse cash-and-carry (futures underpriced):** Sell the spot basket (short), buy the futures contract. Profit = F_theoretical - F_market - costs.
- **Convergence at expiry:** At expiration, futures price equals spot index level. Any deviation at initiation that exceeds total costs is captured risklessly.
- **Basis trading:** The "basis" = F_market - S_0. The trade is essentially a basis convergence trade with deterministic payoff at expiry.

### Edge Source
- **Financing rate differential**: If your actual borrowing/lending rate differs from the rate implied in futures pricing, you capture the spread. Institutions with cheap access to repo rates have structural advantage.
- **Dividend forecasting edge**: Futures pricing uses market-implied dividend yields. If you can forecast index-level dividends more accurately (using individual stock dividend calendars, special dividends), you identify pricing errors.
- **Supply/demand imbalances**: Heavy futures positioning (e.g., pension hedging flows, CTA trend-following) pushes futures away from fair value, creating arbitrage opportunities.
- **Tax and regulatory frictions**: Some participants face constraints (leverage limits, short-sale bans) that prevent them from closing arbitrage. Unconstrained participants capture the edge.
- **Cross-venue latency**: In global index futures (e.g., Eurostoxx, Nikkei, FTSE futures trading in different venues), microsecond advantages in detecting and executing mispricing create edge.

### Specific Formulas

**Fair value (continuous compounding):**
```
F* = S_0 · e^((r - δ) · T)
```

**Fair value (discrete, more precise):**
```
F* = (S_0 - PV_dividends) · (1 + r · T/365)
where PV_dividends = Σ (D_i · e^(-r · t_i)) for each dividend payment
```

**Implied financing rate from observed futures:**
```
r_implied = (1/T) · ln(F_market / (S_0 · e^(-δ · T)))
```

**Implied dividend yield from observed futures:**
```
δ_implied = r - (1/T) · ln(F_market / S_0)
```

**Cash-and-carry profit:**
```
Profit_CC = F_market - S_0 · e^((r_actual - δ_actual) · T) - TC
where TC = all transaction, financing, and carry costs
```

**Reverse cash-and-carry profit:**
```
Profit_RCC = S_0 · e^((r_actual - δ_actual) · T) - F_market - TC
```

**Basis:**
```
Basis = F_market - S_0
Fair basis = S_0 · (e^((r - δ) · T) - 1)
Mispricing = |Basis - Fair basis| / S_0
```

**Annualized excess return from arb:**
```
AR = (|Basis - Fair basis| / S_0) · (365 / days_to_expiry) - cost_rate
```

**Dividend-adjusted futures mispricing (in index points):**
```
Δ = F_market - [(S_0 - D_present_value) · (1 + r · T/365)]
Trade if Δ > (TC_futures + TC_spot + TC_financing) / multiplier
```

**Mark-to-market margin impact:**
```
Daily P&L = (F_t - F_(t-1)) × multiplier × contracts
Initial margin + maintenance margin affect capital efficiency
Margin cost = margin_pct × r_opportunity
```

### Implications for Trading Systems
- **ETF substitution**: Instead of buying all 500 S&P constituents, use the largest/most liquid ETF tracking the index as spot proxy. Reduces execution cost but introduces tracking error risk.
- **Roll arbitrage**: Near-month vs. far-month futures spreads. Trade the roll differential when backwardation/contango deviates from cost-of-carry predictions.
- **Margin efficiency**: Futures require only margin (typically 3-8% of notional), making this capital-efficient. But mark-to-market losses require daily cash infusion.
- **Execution sequencing**: For cash-and-carry, execute the leg that's harder to fill first (usually the spot basket), then the futures. Futures are more liquid.
- **Dividend calendar**: Must model exact dividend amounts, ex-dates, and payment dates for all index constituents. A single special dividend miss can wipe out months of edge.
- **Scalability**: S&P 500 / E-mini futures arb can absorb $100M-$1B+. Niche/EM index futures have lower capacity but wider mispricing.

## Key Implications
- **Not truly riskless**: Dividend uncertainty, margin calls, and financing rate changes during the holding period introduce real risk. The "riskless arbitrage" label is theoretical.
- **Quarterly expiry roll effect**: As futures near expiry, basis must converge. The final week often sees concentrated arb flows that can move prices.
- **Negative rates environment**: When r < 0 or r ≈ 0, the cost-of-carry model flips. Traditional arb relationships need recalibration — this happened in Europe during 2014-2022.
- **Cross-market opportunities**: When index futures trade on multiple exchanges (e.g., Nikkei on OSE, SGX, CME) with slight timing/liquidity differences, cross-venue arb adds another dimension.

## Failure Modes
- **Dividend forecast error**: Index-level dividends miss estimates → the "locked in" profit becomes a loss. Special dividends (M&A-related, one-time) are particularly dangerous.
- **Financing rate spike**: If repo rates spike during the trade (e.g., Sep 2019 repo crisis), the cost of carrying the spot position increases, wiping out expected profit.
- **Margin call cascade**: Adverse mark-to-market moves force additional margin deposits. If capital is constrained, the position must be closed prematurely at a loss.
- **Regime change in cost-of-carry**: Central bank policy shifts, dividend tax changes, or index methodology changes alter the arbitrage equilibrium.
- **Execution slippage on basket**: Buying 500 stocks without moving the spot index upward is nearly impossible in size. Slippage narrows or eliminates the theoretical edge.
- **Early exercise risk (for EFP)**: Exchange for Physical transactions have settlement timing risks.
- **Liquidity evaporation**: During crises, even index futures can experience widened bid-ask spreads. Exit becomes expensive.
- **Dividend tax changes**: If dividend withholding tax rates change (e.g., cross-border investments), after-tax dividend yield differs from the model, creating systematic bias.

## Cross-Links
- [[7-ETF-Index-Arbitrage]] — Similar convergence logic, ETF as spot proxy
- [[Cost-Of-Carry-Futures-Pricing]] — Detailed cost-of-carry model derivation
- [[Dividend-Forecasting-Index-Level]] — Aggregate dividend yield estimation
- [[Basis-Trading-Convergence]] — Basis convergence mechanics and timing
- [[5-US-Equity-Pairs-Trading]] — Spot index ETF vs. futures as a synthetic pair
- [[Repo-Financing-Rates]] — Actual borrow costs vs. model rates
- [[Futures-Roll-Optimization]] — Calendar spread and roll yield
- [[Margin-Capital-Efficiency]] — Capital requirements for arb strategies
- [[Execution-Cost-Management]] — Basket execution, VWAP/TWAP for index constituents
