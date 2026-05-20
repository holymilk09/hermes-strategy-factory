# DEX/AMM Cyclic Arbitrage (ARB-CYCLIC-003)

> **Difficulty**: 8/10 — Microstructure / structural / informational
> **Status**: research_only
> **Retail Feasibility**: ⬤⬤ Low-Medium (3/10) — On-chain but MEV-dominated; requires smart contract deployment and gas optimization

---

## Source

- **Source**: Arbitrage Strategy Research Pack (Batch 5, 2026-05-17)
- **Core Principle**: "Arbitrage detection is not trade approval."
- **Key Insight**: The real edge is knowing whether the spread is executable, hedgeable, cost-adjusted, capacity-positive, and not a data illusion.
- **Category**: Pure Arbitrage — On-Chain AMM Price Convergence

---

## Key Concepts

### Core Mechanism

Exploit price differences between automated market makers (AMMs) on decentralized exchanges. When the spot price of Token X / Token Y differs between Pool A (e.g., Uniswap V3) and Pool B (e.g., Curve), execute a cyclic arbitrage that:

1. Trades Pool A to move its price toward equilibrium
2. Trades Pool B in the opposite direction to capture the spread
3. Returns to the starting asset (or stablecoin) with net profit

Unlike CEX triangular arb, AMM pricing is **deterministic** via the constant product (or other) invariant — the exact price after a given trade size is **knowable in advance**.

**AMM Pricing Model (Constant Product)**:
```
x × y = k    (Uniswap V2)
```

Where x, y = reserves of Token A, Token B; k = invariant constant (pre-trade).

**Output amount for input Δx**:
```
Δy_out = y × Δx / (x + Δx) × (1 - fee_pct)
```

Where fee_pct = protocol fee (typically 0.3% for Uniswap V2, variable for V3).

**Spot price before trade**:
```
P_spot = y / x   (price of A in terms of B)
```

**Effective execution price** (for a trade of size Δx):
```
P_eff = Δy_out / Δx = y / (x + Δx) × (1 - fee_pct)
```

**Optimal Arbitrage Trade Size**:
Given two pools with (x₁, y₁) and (x₂, y₂) and fees f₁, f₂:

The optimal Δx that maximizes profit satisfies:
```
∂(profit) / ∂(Δx) = 0
```

For constant-product pools (no fees for simplicity):
```
Δx_optimal = √(x₁ × x₂ × y₁ × y₂) - x₁   (simplified; exact depends on curve)
```

**Real calculation (iterative)**: Given discrete AMM curves, solve numerically:
```
max_Δx { output_after_cycle(Δx, pool₁, pool₂) - Δx - gas_cost_native }
```

### Edge Source

- **Structural**: AMMs price through mathematical curves that respond deterministically to flow. Divergence between pools is guaranteed when one pool experiences trade flow but the other doesn't. Arb trades are the mechanism that converges prices.
- **Informational**: Mempool visibility — seeing pending trades before they execute allows front-running the convergence
- **Order Flow**: Large DEX trades (whale swaps, liquidations) create temporary mispricing that arbs exploit

### Specific Formulas — Advanced

**Uniswap V3 Concentrated Liquidity**:
Price changes only within active tick ranges. Outside the active range, price doesn't move (no liquidity). This makes V3 pricing **piecewise constant**:

```
For tick i to tick i+1: L is constant
Δx → Δy follows: Δ(1/√P) = Δx / L
```

Where L = concentrated liquidity in the tick range, P = √price.

**MEV Profitability (per block)**:
```
profit_block = max_arb_profit - priority_fee_paid - base_gas × gas_used - gas_price_refund
```

Where priority_fee is the bribe paid to validators to include your transaction first.

**Gas-Optimal Threshold**:
Arb is only executable when:
```
arb_profit > gas_cost × gas_price + priority_fee + protocol_fees
```

On Ethereum L1, a typical swap + arb cycle uses 300,000-600,000 gas. At 50 gwei, gas cost ≈ 0.015-0.03 ETH (~$30-60 at $2000/ETH).

**Flash Loan Arbitrage**:
```
profit = arb_output - flash_loan_amount - flash_loan_fee - gas_cost
```

Where flash_loan_fee ≈ 0.05-0.09% of borrowed amount (Aave: 0.05%, dYdX: 0%).

No capital needed, but must be profitable after 0.05% fee + gas.

**Optimal Priority Fee**:
In a competitive MEV environment, the equilibrium bribe equals the arb profit minus gas:
```
priority_fee_equilibrium = arb_profit - gas_cost - ε
```

Where ε → 0 as number of competing searchers increases.

---

## Implications

- **MEV competition is brutal**: On Ethereum mainnet, the top searchers capture >95% of MEV. Profit is bid away to validators via priority fees. The arb bot makes the profit; the arb *searcher* makes the gas costs.
- **V3 complexity**: Concentrated liquidity makes price curves piecewise discontinuous — simple constant-product formulas fail near tick boundaries
- **Multi-hop paths**: The most profitable arbs often traverse 4-6 pools across multiple protocols (Uniswap → Curve → Balancer → Sushi)
- **Flash swaps**: Some protocols allow atomic execution of arb without upfront capital in a single transaction — if any leg fails, the entire transaction reverts (zero loss, zero gain)
- **MEV-protected RPCs change the game**: Services like Flashbots Private Transactions and MEV-Blocker prevent sandwich attacks but also limit visibility into competitor strategies
- **L2s are the frontier**: Lower gas costs on Arbitrum, Optimism, and Base create arbitrage opportunities where mainnet is competed away

---

## Failure Modes

1. **MEV Competition / Priority Fee Bidding War**: Multiple bots see the same opportunity; only the one paying the highest priority fee wins. Net profit after bribe may be near-zero
2. **Transaction Reorder / Frontrun**: Your transaction is sandwiched or frontrun by a MEV bot with better block-building relationships
3. **Block Reorg Risk** (L2s): Optimistic rollup state reorgs during the confirmation window can invalidate assumed prices
4. **Gas Estimation Error**: Underestimate gas → transaction out-of-gas and reverts, wasting priority fee. Overestimate → lose to cheaper competitor
5. **Slippage on Large Sizes**: The "optimal" trade size assumes infinite depth within tick range — concentrated liquidity may be shallower than expected
6. **Protocol Risk / Smart Contract Bug**: Exploited during arb execution; new AMM deployed with bug in invariant calculation
7. **Impermanent Loss Misestimation**: If providing LP capital as part of strategy, IL during volatile periods can exceed arb gains
8. **Regulatory/Compliance**: Flashbots inclusion doesn't guarantee anonymity; on-chain activity is fully traceable
9. **Oracle Manipulation**: Some arbitrage routes depend on oracles for pricing; oracle manipulation attacks can make the arb appear profitable when it's actually a honeypot

**Mitigations**: Deploy custom smart contracts for atomic multi-hop execution; use Flashbots for private transaction submission; model full tick-depth for V3 pools; maintain gas estimation with buffer; monitor MEV-competitor activity; use L2 venues for lower-competition opportunities.

---

## Cross-links

- [[ARB-TRI-001]] — Crypto Triangular Arbitrage (CEX variant)
- [[ARB-CROSS-002]] — Crypto Cross-Exchange Arbitrage
- [[ARB-FUNDING-004]] — Funding/Basis Arbitrage
- [[08-RL-Deep-Direct-RL-Portfolio-Management]] — MEV optimization via RL (research direction)
- [[06-Data-Infrastructure/data-pipeline-architecture]] — Mempool monitoring infrastructure
- [[05-Failure-Mode-Catalog]] — Failure mode taxonomy
- [[16-Strategy-Encyclopedia/07-Master-Index]] — Strategy schema and validation pipeline

---

*Follow SOP: Every strategy is a hypothesis, not a money printer. Edge is not found — it is validated.*
