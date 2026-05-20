# Crypto Cross-Exchange Arbitrage (ARB-CROSS-002)

> **Difficulty**: 7/10 — Microstructure / execution alpha + structural
> **Status**: research_only
> **Retail Feasibility**: ⬤⬤ Low-Medium (3/10) — Requires multi-exchange accounts, fast execution, and withdrawal infrastructure

---

## Source

- **Source**: Arbitrage Strategy Research Pack (Batch 5, 2026-05-17)
- **Core Principle**: "Arbitrage detection is not trade approval."
- **Key Insight**: The real edge is knowing whether the spread is executable, hedgeable, cost-adjusted, capacity-positive, and not a data illusion.
- **Category**: Pure Arbitrage — Cross-Venue Price Convergence

---

## Key Concepts

### Core Mechanism

Buy an asset on Exchange A (where price is lower) and simultaneously sell on Exchange B (where price is higher), capturing the spread after all costs. Two execution modes:

1. **Pre-funded (Long-Short)**: Hold the asset on both exchanges. When mispricing detected, buy on A and sell on B instantly. Capital already deployed; no transfer needed. Eliminates transfer lag but ties up capital.

2. **Transfer-based (Buy-Transfer-Sell)**: Buy on A, transfer to B, sell on B. Capture potentially larger persistent spreads but exposed to:
   - Transfer time risk (block confirmation delays, network congestion)
   - Price movement during transfer
   - Exchange deposit/withdrawal processing queues

### Edge Source

- **Structural**: Fragmented liquidity across venues; no universal order book. CEX venues are siloed. Different customer bases, regional demand, fiat on-ramps, listing timing
- **Liquidity**: Asymmetric depth — thin order books on secondary exchanges move faster on news/events
- **Informational**: Latency differences between exchange data feeds; one venue prices in news faster
- **Carry/Structural**: Regional premiums (Korean Kimchi premium, Japanese Yen premium) driven by capital controls or fiat access frictions

### Specific Formulas

**Gross Spread**:
```
Spread_gross = P_sell - P_buy
```

Where P_sell = best bid on selling exchange, P_buy = best ask on buying exchange.

**Net Spread after fees and slippage**:
```
Spread_net = (P_sell × (1 - f_sell) - slippage_sell) - (P_buy × (1 + f_buy) + slippage_buy) - cost_transfer
```

Where:
- f_sell, f_buy = trading fee rates on each exchange
- slippage = estimated impact of order size on each leg
- cost_transfer = blockchain gas fee + exchange withdrawal fee + any spread on conversion

**Percentage Return on Capital**:
```
r% = Spread_net / P_buy
```

**Capacity-Adjusted Expected Value**:
```
E[profit] = Spread_net × size × fill_probability_A × fill_probability_B
```

Where fill_probability accounts for queue position and order book depth at quoted price.

**Transfer-Time Risk Model** (for buy-transfer-sell mode):
```
σ_transfer = σ_annual × √(t_transfer / 365.25)
```

Where t_transfer = expected transfer time in days (includes block confirm + exchange processing).

Probability of profitable transfer:
```
P(profit) = Φ((Spread_net / P_buy - 0.5 × σ² × t) / (σ × √t))
```

Where Φ = standard normal CDF, σ = per-leg price volatility.

**Regional Premium Index**:
```
Kimchi Premium = (P_Korea / P_Global - 1) × 100%
```

---

## Implications

- **Pre-funded is the only viable mode for HFT**: Transfer-based cross-exchange arb has been competed away for major pairs by collocated institutional firms with sub-second internal transfer arrangements
- **Capital inefficiency**: Pre-funding requires ~2x the capital of the trade size (cash on A, asset on B), creating significant funding costs
- **Withdrawal limits**: Exchanges impose daily limits; even with pre-funding, rebalancing requires withdrawals that may be suspended during stress
- **Regulatory/Counterparty risk**: Funds parked across multiple CEXs multiply exposure to exchange insolvency, hack, or regulatory seizure
- **Stablecoin depeg events create massive but dangerous spreads**: USDC/USDT depegs in 2023 showed 5-20% inter-exchange spreads that were impossible to capture safely
- **API rate limits**: Monitoring 10+ exchanges × 100+ pairs × WebSocket connections = massive infrastructure overhead

---

## Failure Modes

1. **Transfer Risk**: Buy-Transfer-Sell mode — blockchain congestion or exchange processing delay turns profitable spread into loss
2. **Withdrawal Suspension**: Exchange halts withdrawals during crisis; funds trapped on one side
3. **Fee Tier Miscalculation**: Quoted fees don't match actual execution; VIP tiers reset monthly; withdrawal fees not modeled
4. **API Latency Jitter**: Price feed delay causes stale signal; order reaches exchange after move already happened
5. **Funding Cost Drag**: Pre-funding capital earns zero while deployed; opportunity cost may exceed expected arb returns
6. **Counterparty Risk**: Exchange insolvency during the arbitrage window (FTX, MtGox paradigm)
7. **Regulatory Risk**: Cross-border transfers flagged; exchange compliance freezes account mid-trade
8. **Correlated Fill Risk**: Adverse selection — the leg with worse execution tends to be the one that was about to move against you

**Mitigations**: Pre-fund on both exchanges; use limit orders with IOC (Immediate-Or-Cancel); maintain withdrawal whitelists pre-approved; monitor multiple price feeds simultaneously; implement "kill switch" when spreads exceed normal bounds (depeg signal); model full order book depth, not best bid/ask only.

---

## Cross-links

- [[ARB-TRI-001]] — Crypto Triangular Arbitrage (single-exchange variant)
- [[ARB-CYCLIC-003]] — DEX/AMM Cyclic Arbitrage (on-chain variant)
- [[ARB-FUNDING-004]] — Funding/Basis Arbitrage (funding rate edge)
- [[08-Market-Microstructure-LOB-Execution-Synthesis]] — Order book dynamics, cross-venue
- [[06-Data-Infrastructure/data-pipeline-architecture]] — Multi-feed synchronization
- [[05-Failure-Mode-Catalog]] — Failure mode taxonomy
- [[16-Strategy-Encyclopedia/07-Master-Index]] — Strategy schema and validation pipeline

---

*Follow SOP: Every strategy is a hypothesis, not a money printer. Edge is not found — it is validated.*
