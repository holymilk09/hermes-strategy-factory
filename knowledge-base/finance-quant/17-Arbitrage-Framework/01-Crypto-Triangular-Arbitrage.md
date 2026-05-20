# Crypto Triangular Arbitrage (ARB-TRI-001)

> **Difficulty**: 7/10 — Microstructure / execution alpha
> **Status**: research_only
> **Retail Feasibility**: ⬤ Low (2/10) — Latency-dominated; retail APIs rarely competitive

---

## Source

- **Source**: Arbitrage Strategy Research Pack (Batch 5, 2026-05-17)
- **Core Principle**: "Arbitrage detection is not trade approval."
- **Key Insight**: The real edge is knowing whether the spread is executable, hedgeable, cost-adjusted, capacity-positive, and not a data illusion.
- **Category**: Pure Arbitrage — Single-Exchange Triangular Loop

---

## Key Concepts

### Core Mechanism

Exploit pricing inefficiencies among three trading pairs on a single exchange to execute a closed-loop trade with (theoretically) zero net position change. The classic loop:

```
USDT → BTC → ETH → USDT
```

Each leg is a market order (or limit if queued advantageously). If the product of exchange rates around the loop exceeds 1.0 (net of fees), riskless profit is possible.

### Edge Source

- **Structural**: Temporary order-book dislocations caused by asymmetric flow across pairs, stale quotes on illiquid legs, or fragmented liquidity between USDT-paired and BTC-paired markets
- **Order Flow**: Large trades on one pair cascade into temporary mispricing on correlated pairs before arbitrageurs converge prices
- **Liquidity**: Bid-ask spread differentials across legs that haven't been arbitraged away yet

### Specific Formulas

**Notation**: Let r(A,B) = price quote from asset A to asset B (how many B you get per 1 A).

**Gross Return (3-leg loop)**:
```
R_gross = r(USDT,BTC) × r(BTC,ETH) × r(ETH,USDT)
```

**Net Return after fees**:
```
R_net = r(USDT,BTC) × (1 - f₁) × r(BTC,ETH) × (1 - f₂) × r(ETH,USDT) × (1 - f₃) - 1
```

Where fᵢ = fee rate (maker/taker) on leg i. For Binance VIP0 maker=0.1%, taker=0.1%.

**Profitability Threshold**:
```
R_net > 0  ⟺  r(USDT,BTC) × r(BTC,ETH) × r(ETH,USDT) > 1 / [(1-f₁)(1-f₂)(1-f₃)]
```

With uniform taker fee f = 0.001:
```
Product of rates > (1 / 0.999)³ ≈ 1.00301  →  need >0.301% gross mispricing
```

**Log-Space Detection (numerical stability)**:
```
log R_gross = log r(USDT,BTC) + log r(BTC,ETH) + log r(ETH,USDT)
Execute if: log R_gross > -Σ log(1 - fᵢ)
```

**Cycle Detection (graph formulation)**:
- Build directed graph where nodes = assets, edges = log exchange rates
- Bellman-Ford or SPFA detects negative-weight cycles (after negating log rates)
- Complexity: O(V × E) where V = number of assets, E = number of trading pairs

**Slippage-Adjusted Model**:
```
r̂(A,B) = mid(A,B) ± half_spread(A,B) + impact(A,B, size)
```

Where impact is modeled via order book depth or a square-root model:
```
impact ≈ σ × √(size / ADV)
```

---

## Implications

- **Latency is the primary competitive dimension**: On centralized exchanges, triangular opportunities close in < 100ms for major pairs, < 10ms for collocated participants
- **Graph-based detection scales**: As the number of assets N grows, possible 3-cycles are C(N,3) and 4-cycles grow combinatorially — automation mandatory
- **Fee tiers matter critically**: A VIP-8 maker fee (0.03%) vs retail taker fee (0.1%) shrinks the profitability threshold from 0.30% to ~0.09%, expanding the universe of executable triangles by 10x+
- **Not truly riskless**: Between leg 1 execution and leg 3 completion, prices move. Execution risk is non-zero even if the snapshot showed profit
- **Capital requirement**: Must hold balances in all three assets (or use margin) to avoid transfer delays; or route through a single-asset entry/exit

---

## Failure Modes

1. **Leg Execution Risk (Asynchrony)**: Leg 1 fills but Leg 2 or 3 slip or don't fill — you're left with an open directional position, not a closed arbitrage
2. **Fee Underestimation**: Using maker fee quote while actually paying taker; withdrawal/transfer fees not modeled; tier miscalculated
3. **Stale Quote / Data Illusion**: WebSocket snapshot is milliseconds old; order book moved; quote exists in feed but not in matching engine
4. **Adverse Selection**: Your arbitrage signal is also visible to faster participants; your order arrives after edge is gone
5. **Withdrawal/Delays**: If moving funds to rebalance, exchange withdrawal queues (especially ETH gas) can delay completion
6. **Exchange Risk**: Funds locked during multi-leg trade; platform freeze during extreme volatility; API rate limits throttling detection
7. **Capacity Decay**: As more bots compete, spreads compress toward fee level; profitable triangles shrink to sub-millipercent

**Mitigations**: Use limit orders with aggressive price placement near top-of-book; model full order book depth, not just mid; colocate API; pre-fund all accounts; implement execution atomicity checks with rollback logic.

---

## Cross-links

- [[ARB-CROSS-002]] — Crypto Cross-Exchange Arbitrage (extends to multiple venues)
- [[ARB-CYCLIC-003]] — DEX/AMM Cyclic Arbitrage (on-chain variant)
- [[ARB-FUNDING-004]] — Funding/Basis Arbitrage (funding rate edge)
- [[08-Market-Microstructure-LOB-Execution-Synthesis]] — Order book dynamics
- [[06-Data-Infrastructure/data-pipeline-architecture]] — WebSocket feed design for sub-100ms reaction
- [[05-Failure-Mode-Catalog]] — Failure mode taxonomy references
- [[16-Strategy-Encyclopedia/07-Master-Index]] — Strategy schema and validation pipeline

---

*Follow SOP: Every strategy is a hypothesis, not a money printer. Edge is not found — it is validated.*
