# Crypto Funding/Basis Arbitrage (ARB-FUNDING-004)

> **Difficulty**: 6/10 — Statistical / structural / carry
> **Status**: research_only
> **Retail Feasibility**: ⬤⬤⬤ Medium (5/10) — Accessible via standard exchange APIs, but requires significant capital and careful risk management

---

## Source

- **Source**: Arbitrage Strategy Research Pack (Batch 5, 2026-05-17)
- **Core Principle**: "Arbitrage detection is not trade approval."
- **Key Insight**: The real edge is knowing whether the spread is executable, hedgeable, cost-adjusted, capacity-positive, and not a data illusion.
- **Category**: Relative Value / Carry Arbitrage — Funding Rate + Basis Convergence

---

## Key Concepts

### Core Mechanism

Two closely related sub-strategies:

**A) Funding Rate Arbitrage (Cash-and-Carry on Perpetuals)**:
Perpetual futures contracts use a funding rate mechanism to tether the perp price to the underlying spot price. When funding rate is positive (longs pay shorts), go long spot and short perp to collect funding payments. Delta-neutral position captures the funding yield.

**B) Basis (Calendar Spread) Arbitrage**:
When futures contracts on the same asset but different expirations trade at different implied forward prices, go long the cheap dated contract and short the expensive one. At convergence (expiration), the spread must collapse to zero (plus/minus any basis adjustment).

### Edge Source

- **Carry**: Funding rate is a payment stream — a structural yield for holding the offsetting leg
- **Statistical**: Mean-reversion of funding rates around equilibrium (zero); historical distribution is empirically skewed positive in bull markets
- **Structural**: Futures basis converges to zero at expiration by contract design; the convergence is mechanical, not speculative
- **Behavioral**: Retail traders pay premiums for leveraged long exposure via perps; their willingness to pay above-spot creates the positive funding rate that arbs harvest

### Specific Formulas

**A) Funding Rate Arb — Daily Yield**:

Perp funding rate is typically paid every 8 hours (3x/day):
```
Funding_Payment = Position_Size × Funding_Rate_Per_Interval
```

**Annualized Funding Yield**:
```
Y_annual = Funding_Rate_8h × 3 × 365.25
```

If 8h funding rate = 0.01% (0.0001):
```
Y_annual = 0.0001 × 3 × 365.25 = 10.96%
```

**Net Yield (after costs)**:
```
Y_net = Y_annual - trading_fees × 2 × turnover - borrow_cost - opportunity_cost
```

Where:
- trading_fees × 2 = open + close costs
- turnover = frequency of rebalancing (e.g., close and re-open positions when funding changes)
- borrow_cost = interest if using margin for the spot leg
- opportunity_cost = yield forgone on capital (e.g., stablecoin staking yield)

**B) Basis Arb — Profit Calculation**:

```
Basis = Futures_Price - Spot_Price
```

or for calendar spread:
```
Basis_spread = Futures_T2 - Futures_T1   (T2 > T1)
```

**Theoretical Futures Price**:
```
F_theory = S × (1 + r × (T - t)/365.25) - dividends/carry_income
```

Where r = risk-free rate, T = expiry, t = current time.

**Actual vs Theoretical**:
```
Basis_deviation = F_actual - F_theory
```

If Basis_deviation > transaction_costs, arb exists:
- Go short futures, long spot → profit = basis at expiry

**Profit at Expiry (Cash-and-Carry)**:
```
Profit = (F_entry - S_entry) - (trading_fees + funding_during_hold + borrow_cost)
```

**C) Funding Rate Statistical Model**:

Empirical distribution of funding rates is positively skewed. Model as truncated distribution:
```
P(F > 0) >> P(F < 0)   in bull markets
P(F < 0) >> P(F > 0)   in bear markets
```

Expected funding over holding period H:
```
E[F_H] = μ_funding × H + σ_funding × √H × z_α
```

Where z_α accounts for the probability of funding regime change.

**Position Sizing (Kelly-Adjusted)**:
```
f_kelly = (μ_funding × (1 - fee_d)) / σ²_funding
```

But since funding arb is (nearly) delta-neutral:
```
Size ≈ min(capital_available / 2, max_position_per_exchange, liquidity_limit)
```

---

## Implications

- **Most "retail-friendly" arb strategy**: Requires no colocation, no smart contract deployment, no multi-exchange setup (can often be done on one exchange that offers both spot and perps, e.g., Binance)
- **Capital intensive but passive**: Once opened, the position collects funding yield without continuous active management. Main risk is funding rate regime change.
- **Counterparty risk is still CEX risk**: If Binance/Bybit goes down during your position, you lose both legs (correlated loss, not hedged). This is the single largest unpriced risk.
- **Funding rate regime changes matter**: A sustained negative funding period turns the yield negative. The strategy requires monitoring and potential re-entry when funding flips back positive.
- **Basis arb on dated futures is lower-risk than perpetual funding**: Dated futures converge mechanically at expiry. Perpetual funding rates can stay negative indefinitely.
- **Tax complexity**: Each funding payment is a taxable event in many jurisdictions; high-frequency funding collection creates accounting burden.
- **Capacity scales well**: Unlike triangular arb, this is not latency-competitive. Large positions are feasible as long as exchange liquidity supports them.

---

## Failure Modes

1. **Funding Rate Regime Flip**: Funding goes deeply negative for extended period (bear market short-squeeze). Negative funding erodes and may exceed yield captured earlier
2. **Exchange Insolvency (Correlated Counterparty Risk)**: Both legs are on the same exchange → both are frozen simultaneously. The "hedge" provides no protection against platform risk
3. **Liquidation Pin Risk**: If perp leg moves against you faster than you can add margin, the short perp gets liquidated, leaving naked long spot exposure
4. **Basis Widening Before Convergence**: Calendar spreads can widen further before converging; short-term MTM losses may trigger margin calls before convergence occurs
5. **Spot-Futures Decoupling**: In extreme market stress, perpetuals can trade far from spot (e.g., -2% or +2% basis). Mark price algorithms may lag
6. **Exchange Fee Changes**: Fee schedule changes mid-position can destroy the profitability calculus
7. **Liquidity Crunch**: Unable to close one leg without significant slippage during market stress, breaking the delta-neutral assumption
8. **Borrow Cost Surprise**: If using margin for the spot leg, funding rate on borrowed capital may rise and exceed the perp funding yield
9. **Smart Contract / Exchange Bug**: Perp engine malfunction, incorrect funding rate calculation
10. **Regulatory Action**: Country-level ban on perps forces exchange to close positions at unfavorable prices

**Mitigations**: Use multiple exchanges to diversify counterparty risk; set strict position limits per venue; monitor funding rate regime changes daily; use limit orders for entry/exit; maintain 20-30% extra margin above minimum; consider dated futures over perps for lower risk (mechanical convergence); track cumulative funding yield vs. mark-to-market losses.

---

## Cross-links

- [[ARB-TRI-001]] — Crypto Triangular Arbitrage
- [[ARB-CROSS-002]] — Crypto Cross-Exchange Arbitrage
- [[ARB-CYCLIC-003]] — DEX/AMM Cyclic Arbitrage
- [[Basic-Intermediate-Strategies]] — Carry strategies section
- [[11-Kelly-Adaptive-Markets]] — Position sizing and adaptive approaches
- [[05-Failure-Mode-Catalog]] — Failure mode taxonomy
- [[16-Strategy-Encyclopedia/07-Master-Index]] — Strategy schema and validation pipeline

---

*Follow SOP: Every strategy is a hypothesis, not a money printer. Edge is not found — it is validated.*
