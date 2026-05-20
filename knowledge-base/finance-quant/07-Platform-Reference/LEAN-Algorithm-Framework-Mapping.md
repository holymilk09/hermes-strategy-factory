# LEAN Algorithm Framework Mapping

QuantConnect's Algorithm Framework is the cleanest practical mental model for avoiding strategy spaghetti. The framework separates a trading system into discrete, independently testable modules.

## Core Concepts

The framework maps "serious bot components" to LEAN modules:

| Serious Bot Component | LEAN Module | Purpose |
|---|---|---|
| Universe Filter | Universe Selection | Determines which securities the strategy monitors and trades |
| Signal Generation | Alpha Model | Produces directional signals (long/short/flat) with confidence scores |
| Target Sizing | Portfolio Construction Model | Converts signals into position sizes (weights) |
| Risk Veto/Clipping | Risk Management Model | Overrides targets that violate risk rules (concentration, drawdown, etc.) |
| Order Placement | Execution Model | Converts portfolio targets into orders (slicing, scheduling, limit/market) |
| Portfolio/Broker/Account State | LEAN Engine + Brokerage Models | Manages PnL, margin, cash, commissions across brokerages |

## Recommended Solo-Founder Module Structure

Even outside QuantConnect, copy this separation. The recommended file structure:

```
universe.py        # Universe selection/filtering logic
features.py        # Feature computation, data processing
alpha.py           # Signal generation (direction, confidence, horizon)
portfolio.py       # Position sizing, target weights
risk.py            # Risk checks, stop-loss, position limits, drawdown halts
execution.py       # Order placement, slicing, limit/market decisions
broker.py          # Broker connectivity, order state management
ledger.py          # Portfolio tracking, PnL, cash accounting
metrics.py         # Performance measurement
review.py          # Post-trade review, hypothesis tracking, diagnostics
```

**Rule:** Do not combine alpha, sizing, and execution into one function. Each module should be independently testable with its own unit tests.

## Implications

- **Independent testing is possible:** Each module can be tested in isolation. Test alpha.py with mock universe data. Test risk.py with mock target weights. Test execution.py with mock targets.
- **Debugging is tractable:** When something goes wrong, you can identify which module produced the incorrect output instead of searching through monolithic strategy code.
- **Strategy composition is natural:** Swap alpha models while keeping risk and execution fixed. Swap executors while keeping everything else fixed. This enables the hybrid workflow from [[Framework-Comparison-Selection]].
- **Team scaling:** Multiple people can work on different modules simultaneously without conflicts.
- **LEAN's framework maps to [[NautilusTrader-Reference]] architecture:** Alpha → signal, portfolio → position sizing, execution → execution engine, risk → risk model.
- **The `features.py` module** is an addition not in native LEAN — it's where signal computation logic goes before alpha consumes it. This keeps alpha focused on signal logic, not data wrangling.

## Failure Modes

- **Module coupling creeping back in:** The framework separates concerns, but it's tempting to make alpha.py call execution.py "for this one edge case." Resist this — it destroys the modular benefit.
- **Portfolio vs allocation confusion:** The portfolio construction model produces target weights, not absolute quantities. If it outputs quantities, it's conflating portfolio construction with leverage/account logic.
- **Risk model as rubber stamp:** If your risk management model never rejects a target, it's not doing anything. Either add real risk checks or remove it. False safety is worse than no safety.
- **Execution model overcomplication:** For simple strategies, the execution module should just convert targets to market orders. Don't build a TWAP/VWAP slicer before you need one.
- **LEDGER gap:** LEAN handles PnL internally, but custom strategies need their own ledger.py for tracking model-level PnL, attribution, and cash reconciliation. Don't rely on the framework's internal accounting for diagnostics.
- **Review module as afterthought:** The review.py module is where you track which hypotheses were tested, which were confirmed, and which were rejected. Without this, you'll re-run the same failed experiments.

## Anti-Cookie-Cutter Insight

The Algorithm Framework's real power isn't that it separates code into modules — it's that it forces you to think about each component as a contract with inputs and outputs. When alpha outputs a signal, what data structure? What confidence metric? What time horizon? When portfolio sizing receives signals, how does it handle conflicting signals, missing signals, or NaN? Making these contracts explicit prevents the most common strategy bug: assumptions baked into code that become invisible when the code grows complex.

## Cross-Links

- [[LEAN-Reference]] — LEAN platform index
- [[LEAN-Local-Backtesting]] — validate the full module pipeline
- [[LEAN-Live-Trading-Ops]] — production deployment of the full pipeline
- [[LEAN-Backtesting-Gotchas]] — framework misuse patterns
- [[LEAN-Research-Environment]] — how notebook discoveries become modules
- [[Framework-Comparison-Selection]] — framework selection within the hybrid workflow
- [[Trading-System-Component-Architecture]] — broader system design context
- [[Data-Pipeline-Architecture]] — how features.py connects to the data pipeline
- [[Execution-Metrics]] — measure execution module quality
- [[Risk-Metrics]] — what risk metrics the risk module should enforce
- [[NautilusTrader-Reference]] — NautilusTrader's architecture parallels this separation
