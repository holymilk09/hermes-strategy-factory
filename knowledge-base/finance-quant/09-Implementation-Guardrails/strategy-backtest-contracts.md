# Strategy and Backtest Contracts

**Source**: `algo_trading_implementation_library/09_agentic_coding_workflows/{strategy_contract, backtest_contract}`

> Mandatory contracts that every strategy and backtest must conform to — the interface agreements between strategy developers and the execution/backtest engine.

---

## Key Concepts

### Strategy Contract — Required Fields

Every strategy must define these 12 fields explicitly (no defaults assumed):

| Field | What It Means |
|---|---|
| **Strategy ID** | Unique identifier for the strategy module |
| **Hypothesis** | The testable trading idea — what edge is being captured and why |
| **Universe** | Which assets, markets, or instruments the strategy trades |
| **Horizon** | Holding period in bars/time — defines the strategy's temporal scale |
| **Feature inputs** | What data the strategy consumes (price, volume, alt-data, etc.) |
| **Signal rule** | How raw features are transformed into trade signals |
| **Entry rule** | Conditions under which positions are opened |
| **Exit rule** | Conditions under which positions are closed |
| **Sizing rule** | How position size is determined (fixed, vol-target, Kelly, etc.) |
| **Risk constraints** | Maximum drawdown, position limits, sector exposure caps |
| **Cost assumptions** | Commission, slippage, bid-ask spread assumptions |
| **Falsification rule** | Pre-defined criteria under which the hypothesis is rejected |

### Strategy Contract — Required Methods

```python
prepare_features(market_data) -> FeatureFrame
generate_signal(features, state, config) -> list[Signal]
build_targets(signals, portfolio_state, config) -> list[Target]
```

**Critical constraint**: Strategy modules must NOT submit broker orders directly. They produce signals/targets; the execution engine converts them to orders.

### Backtest Contract — Required Inputs

| Input | Purpose |
|---|---|
| Strategy ID | Links run to strategy definition |
| Config file | YAML/JSON with parameters |
| Data version | Immutable data snapshot reference |
| Start/end date | Backtest window |
| Universe rule | Asset filter at runtime |
| Cost model | Commission + spread assumptions |
| Slippage model | Price impact formula |
| Fill model | How orders become fills |
| Risk limits | Portfolio-level constraints |
| Random seed | For reproducibility of stochastic elements |

### Backtest Contract — Required Outputs

Every run must produce **all** of:
- Run manifest (JSON with hashes, versions, timestamps)
- Equity curve
- Order ledger
- Fill ledger
- Trade ledger
- Position ledger
- Metric pack
- Data quality report
- Review report

### Core Invariant

> **Same inputs must produce same outputs.**

This is non-negotiable. If changing the random seed or code hash changes results, it means either the seed wasn't captured or the code wasn't versioned.

---

## Implications for Trading Systems

- **Decoupled design**: The strategy contract separates "trading logic" from "execution logic." Strategies cannot bypass risk controls by submitting orders directly.
- **Complete auditability**: The 12 required fields form a self-documenting strategy definition. Anyone can read a strategy's README and understand exactly what it does.
- **Falsification-first**: The falsification rule forces researchers to define failure conditions upfront, combating confirmation bias.
- **Ledger-level transparency**: Separate order, fill, trade, and position ledgers allow debugging at every stage of the trade lifecycle.

---

## Failure Modes

| Failure | Consequence | Prevention |
|---|---|---|
| Strategy submits orders directly | Bypasses risk engine, execution model | Contract method restriction |
| Missing falsification rule | Strategy "zombifies" — runs forever despite being disproven | 12-field validation checklist |
| No random seed captured | Stochastic backtests unreproducible | Run manifest includes seed |
| Partial output artifacts | Cannot diagnose discrepancies between runs | Output checklist in backtest contract |
| No data version in manifest | Results contaminated by future data silently | Data version required in manifest |
| Changing config after seeing results | P-hacking through parameter tweaking | Config hash captured in manifest |
| No cost model specified | Over-optimistic results that vanish in live trading | Cost model mandatory in backtest inputs |

---

## Cross-Links

- [[AI Coding Guardrails]] — the rules that protect these contracts from silent modification
- [[strategy-templates-standards]] — the concrete template implementations
- [[Agentic Workflow Patterns]] — how to implement strategies using these contracts
- [[Run Manifest Structure]] — the JSON schema that tracks every backtest
- [[Data Pipeline Architecture]] — how data flows into the backtest inputs
- [[Schema Catalog]] — data schemas for the required output artifacts
