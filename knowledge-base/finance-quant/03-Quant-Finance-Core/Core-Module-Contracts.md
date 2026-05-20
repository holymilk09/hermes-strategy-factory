# Core Module Contracts

**Source**: `algo_trading_implementation_library/00_core_bot_structure/module_contracts.md` + `trading_system_component_map.csv`

---

## Core Concept

Each component in the [[Trading-System-Component-Architecture]] communicates through a **structured contract** defining its exact inputs, outputs, and validation guarantees. This contract-based design enables independent testing, composition, and replacement of modules.

### Data Contract
- **Input**: Vendor payload, requested symbol, requested timeframe, calendar
- **Output**: Normalized `MarketEvent`, validated timestamp, data quality flags, vendor/source ID

### Signal Contract
- **Input**: Point-in-time feature snapshot, strategy config, current position state
- **Output**: Symbol, direction, score, horizon, confidence, reason codes

### Portfolio Contract
- **Input**: Signals, capital, current holdings, risk budget
- **Output**: Target position or target weight, sizing reason, constraints applied

### Risk Contract
- **Input**: Target portfolio, current portfolio, risk limits, market state
- **Output**: Approved target, clipped target, or vetoed target with veto reason

### Execution Contract
- **Input**: Approved target delta, market liquidity state, broker constraints
- **Output**: Order instruction, order type, quantity, limit price (if any), time-in-force, client order ID

### Review Contract
- **Input**: Backtest/live run artifacts, metrics, trade ledger, logs, heatmaps
- **Output**: Promotion/hold/reject decision, weak-point list, required next experiments

---

## Implications for Trading Systems

- **Boundary enforcement**: Contracts prevent hidden dependencies. A signal engine cannot silently read global position state; it receives position state as an explicit input parameter.
- **Reason codes as audit trail**: The signal and portfolio contracts require reason codes and sizing reasons. This enables the [[Event-Loop-and-State-Machine|Review & Learning]] layer to reconstruct why a decision was made.
- **Risk as a pure function**: The risk contract maps target + current state → approved/clipped/vetoed. No side effects, no order submission. This makes the risk engine trivially testable with known fixtures.
- **Review as a decision gate, not a dashboard**: The review contract outputs explicit promotion/rejection decisions. It is an operational component, not a passive monitoring tool.
- **Vendor source tracking**: The data contract carries vendor/source ID, enabling the review layer to detect vendor-specific quality issues across strategies.

---

## Potential Failure Modes and Critiques

- **Contract drift**: If a module's implementation diverges from its documented contract (e.g., signal engine adds a new output field), downstream consumers may silently use or ignore it. Strict schema validation at each boundary is required.
- **Missing error paths**: Contracts define the happy path. The [[Failure-Mode-Taxonomy|Data-Failure]] section shows that error conditions (missing bars, time zone mismatch) are common. Contracts must include error/fallback outputs, not just success outputs.
- **Temporal coupling**: The signal contract requires a point-in-time feature snapshot. If the feature layer delivers a snapshot with mixed timestamps (some from future bars, per [[Failure-Mode-Taxonomy|Look-Ahead-Leakage]]), the signal contract cannot detect the violation — it only sees the data it receives.
- **Risk veto without feedback**: The risk contract returns a vetoed target but does not provide alternative suggestions. The execution engine receives nothing, but the signal engine does not learn its signals were rejected. This creates a silent feedback loop gap.
- **Execution contract lacks priority field**: When multiple orders compete for limited liquidity, the execution contract has no priority or ordering field. The system may submit equivalent-signal orders in arbitrary sequence.
- **Review contract input bloat**: The review contract takes metrics + ledger + logs + heatmaps. As the system scales, this input set grows without limit, potentially making review runs intractable without a sampling/rollup strategy.

---

**Related**: [[Trading-System-Component-Architecture]] · [[Event-Loop-and-State-Machine]] · [[Failure-Mode-Taxonomy]]
