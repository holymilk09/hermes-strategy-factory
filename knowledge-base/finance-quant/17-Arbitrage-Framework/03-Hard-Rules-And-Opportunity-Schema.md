# Arbitrage Hard Rules, Feasibility, and Opportunity Schema

**Source**: Batch 5 — Arbitrage Strategy Research Pack; synthesized from [[Schema-and-Taxonomy]], [[Professional-Quant-Strategies]], [[Options-Trading-Strategies]], [[ai-coding-guardrails]], [[Options-Volatility-Synthesis]], and research literature.
**Purpose**: The non-negotiable rules, feasibility framework, and standardized opportunity description schema for arbitrage detection and execution in the trading system.
**Core Principle**: "Arbitrage detection is not trade approval."

---

## Feasibility Ranking

Every identified arbitrage opportunity must be scored on a feasibility scale before execution consideration:

| Rank | Feasibility | Criterion | Action |
|------|-------------|-----------|--------|
| **F-1** | Not Feasible | No executable edge exists; theoretical only; data artifact | Discard immediately |
| **F-2** | Feasible But Unprofitable | Tradeable but cost-adjusted expected value ≤ 0 (transaction costs, spread, borrow) | Archive; monitor for regime changes |
| **F-3** | Conditionally Feasible | Edge exists under specific conditions (vol regime, liquidity threshold, time of day) | Monitor and alert when conditions are met |
| **F-4** | Feasible and Profitable | Positive cost-adjusted EV, executable, capacity-positive | Queue for execution with risk controls |
| **F-5** | Feasible and Priority | High EV, low risk, high capacity, strong structural edge | Immediate execution alert |

**Feasibility Score Components**:
1. **Signal strength** — Size of mispricing relative to noise floor
2. **Cost-adjusted EV** — (Gross edge − transaction costs − borrow costs − slippage) per unit of capital
3. **Capacity** — How much capital can be deployed before edge erodes
4. **Execution risk** — Probability that all legs fill at expected prices simultaneously
5. **Hedge quality** — How well the hedge isolates the target edge from other risk factors
6. **Regime dependency** — Stability of edge across market conditions
7. **Regulatory/compliance** — Legal constraints, tax treatment, reporting requirements

---

## Hard Rules for Arbitrage Strategies (Rules 1–20)

### Identification Phase

**Rule 1: Detection ≠ Approval**
An identified opportunity is a candidate, not a trade. Every opportunity must pass through the feasibility ranking and hard rules before execution consideration.

**Rule 2: No Naked Exposure**
Every leg of an arbitrage must be hedged or explicitly accounted for in the P&L attribution. No "I'll monitor it" positions. If a risk factor is not hedged, it must be quantified and accepted.

**Rule 3: Cost-Adjusted Edge Is the Only Edge**
Gross theoretical edge is meaningless. Only edge remaining after all costs (bid/ask, commissions, borrow, financing, slippage, exchange fees) is real.

**Rule 4: Data Provenance Required**
Every arbitrage signal must trace to specific, verifiable data sources. If the edge disappears when data quality degrades (stale quotes, delayed feeds), it was not an edge — it was a data artifact.

**Rule 5: Multi-Leg Atomicity**
All legs of a multi-leg arbitrage must be executable as a single atomic operation (or with defined sequential execution risk). If any leg fails, the entire opportunity is void.

### Execution Phase

**Rule 6: Spread Threshold**
For options/multi-leg strategies, total bid/ask spread across all legs must be < 10% of the theoretical edge. If spread > 10%, the opportunity is F-2 at best.

**Rule 7: No Legging Risk Without Approval**
Legging into a position (filling legs sequentially) introduces directional exposure between legs. Legging is only permitted with explicit risk limits on the exposed interval.

**Rule 8: Real-Time Borrow Cost Tracking**
Any strategy requiring short positions must track real-time borrow costs. If borrow cost exceeds projected edge, the position is automatically reduced.

**Rule 9: Pre-Trade Margin Verification**
Before execution, verify that margin requirements will not force unintended liquidation of other positions. Margin must be verified at worst-case, not expected, outcomes.

**Rule 10: Circuit Breaker Mandatory**
Every arbitrage leg must have a circuit breaker — a predefined condition under which the position is closed regardless of theoretical edge. Circuit breakers are not stop-losses; they are thesis-invalidators.

### Risk Management

**Rule 11: Correlation Audit**
Before adding a new arbitrage position, audit correlation with existing positions. If new position is > 0.7 correlated to existing exposure, it is not diversifying — it is concentrating risk.

**Rule 12: Capacity Discipline**
Deploy only up to the capacity where edge is not eroded by your own trading. Track slippage vs. size to identify the erosion curve.

**Rule 13: Tail Risk Accounting**
Every strategy must have a defined maximum tail loss (worst-case scenario). If the tail loss exceeds the portfolio's risk budget for that strategy class, the position is rejected.

**Rule 14: Regime Monitoring**
Arbitrage edges are regime-dependent. Monitor the conditions under which the edge exists and the conditions under which it disappears or inverts. Alert on regime changes.

**Rule 15: No Model Without Calibration Error Bars**
Any model-based pricing (options, convertibles, derivatives) must include calibration error estimates. If calibration error > edge size, the signal is noise.

### Systems and Process

**Rule 16: Audit Trail for All Decisions**
Every trade decision, parameter change, or threshold adjustment must be documented with timestamp and rationale. No "silent" changes.

**Rule 17: No Overfitting to Historical Arbs**
Historical arb opportunities do not guarantee future edges. Market participants adapt. Every edge has a half-life. Monitor edge decay.

**Rule 18: Latency-Aware Feasibility**
Arb opportunities with expected lifetime < latency to execute are not feasible. Calculate: if (detection latency + execution latency) > opportunity lifetime, discard.

**Rule 19: Counterparty Risk**
In any arbitrage involving a counterparty (OTC derivatives, bilateral agreements), counterparty default risk must be quantified and priced into the edge calculation.

**Rule 20: Review and Deprecation**
Every arb strategy must be reviewed quarterly. If the strategy has not produced positive cost-adjusted returns in the previous quarter (or 90 days of live/forward testing), it must be either recalibrated or deprecated.

---

## Universal Opportunity Schema

Every detected arbitrage opportunity must be expressible in this exact schema. This is the standardized format for describing, evaluating, and routing any arbitrage opportunity through the trading system.

```
OPPORTUNITY_ID:    [Unique identifier, e.g., OPP-2026-0517-001]
OPP_TYPE:          [Category: OPTIONS_ARB | EVENT_ARB | STATISTICAL_ARB | CROSS_EXCHANGE_ARB | STRUCTURAL_ARB]
OPP_FAMILY:        [Specific family, e.g., PUT_CALL_PARITY, MERGER_ARB, DISPERSION, BOX_SPREAD, ADR, VOL_ARB, CONVERTIBLE]
DETECTION_TIME:    [ISO 8601 timestamp of first detection]
MARKET_TIME:       [Market state at detection: PRE_OPEN | OPEN | INTRADAY | POST_CLOSE]

-- PRICING --
GROSS_EDGE_BPS:    [Edge in basis points before costs]
COST_ADJUSTED_BPS: [Edge after all transaction costs, spread, borrow, financing]
EDGE_CONFIDENCE:   [0.0–1.0 based on data quality, recency, and model calibration fit]

-- EXECUTION --
LEGS:              [List of all legs: {instrument, action (BUY/SELL), quantity, expected_price, current_spread_bps}]
TOTAL_SPREAD_BPS:  [Sum of spread costs across all legs]
EST_SLIPPAGE_BPS:  [Expected slippage based on liquidity and order size]
EST_FILL_TIME_MS:  [Expected time to fill all legs]
ATOMICITY:         [ATOMIC (all-or-nothing) | SEQUENTIAL (ordered legging with risk limits)]

-- FEASIBILITY --
FEASIBILITY_RANK:  [F-1 | F-2 | F-3 | F-4 | F-5]
CAPITAL_REQUIRED:  [Capital needed, including margin requirements]
CAPACITY_LIMIT:    [Maximum deployable capital before edge erosion]
Borrow_COST_BPS:   [Cost of shorting (0 if no short required)]
FINANCING_BPS:     [Cost of carry/financing the position]
NET_EV_BPS:        [Final cost-adjusted expected value in basis points]

-- RISK --
MAX_TAIL_LOSS:     [Worst-case loss scenario in dollar terms or bps]
MAX_DRAWDOWN:      [Maximum expected drawdown during trade holding period]
TAIL_PROBABILITY:  [Probability of tail event occurring (0.0–1.0)]
HEDGE_QUALITY:     [How well hedge isolates target edge: PERFECT | HIGH | MODERATE | POOR]
REGIME_DEPENDENCY: [Regime(s) where edge exists, e.g., LOW_VOL | HIGH_VOL | TRENDING | RANGE_BOUND]
CORRELATION_AUDIT: [Correlation of this trade with existing portfolio positions (0.0–1.0)]

-- ALERT AND ACTION --
ALERT_PRIORITY:    [P1:Immediate | P2:High | P3:Monitor | P4:Archive]
ALERT_REASON:      [Why this priority: e.g., "Cost-adjusted EV > 50bps + atomic execution available"]
CIRCUIT_BREAKER:   [Condition that invalidates thesis and closes position, e.g., "Spread widens > 50% of entry"]
EXPIRING_AT:       [Time at which the opportunity expires (if event-driven or time-limited)]
REQUIRED_APPROVAL: [NONE | RISK_REVIEW | MANUAL_CONFIRM | MULTI_SIG]

-- METADATA --
DATA_SOURCES:      [List of data sources used for detection, with quality flags]
MODEL_USED:        [Pricing model, if applicable]
CALIBRATION_ERROR: [Model calibration uncertainty]
PREVIOUS_OCCURRENCES: [Count of similar opportunities detected in trailing period]
DEPRECATED:        [true/false — whether this opportunity type has been deprecated by Rule 20]
```

---

## Alert Priority Schema

Opportunities are routed through a priority-based alert system:

| Priority | Code | Action | Criteria |
|----------|------|--------|----------|
| **P1** | IMMEDIATE | Auto-execute or page trader immediately | Net EV > threshold + atomic execution + F-4/F-5 + low tail risk + no regime conflict |
| **P2** | HIGH | Alert within 5 minutes; manual review required | Net EV positive + conditional feasibility + some execution risk + requires monitoring |
| **P3** | MONITOR | Log and watch; alert if conditions improve | Edge exists but below threshold OR cost-adjusted EV near zero OR regime is suboptimal |
| **P4** | ARCHIVE | Log for research; no active alert | F-1 or F-2; historical reference only; may become actionable if regime changes |

**Alert Escalation Rules**:
- P3 → P2: If cost-adjusted edge increases by > 50% or regime alignment improves
- P2 → P1: If atomicity confirmed AND capacity available AND tail risk within budget
- Any → F-1 (discard): If data quality degrades, counterparty risk emerges, or circuit breakers are hit

**Alert Delivery**:
- P1: Push notification + page + auto-queue for execution
- P2: Push notification + log + dashboard
- P3: Log only + daily summary
- P4: Archive in research database for historical analysis

---

## Anti-Cookie-Cutter Insights

1. **The "Free Money" Paradox**: If an arbitrage opportunity is obvious enough to be detected by a retail trader's screener, it was already arbitraged away 10 milliseconds ago. The edge is in the frictions, not the formula.
2. **Correlation Trap**: During crises, all "diversified" arbitrage positions become correlated — the dispersion trade's index vol leg spikes, merger deals get pulled, market makers widen spreads and accumulate toxic inventory. Arbitrage diversification is an illusion in stress scenarios.
3. **The Half-Life Rule**: Every arbitrage edge decays. The decay rate depends on: (a) how many participants can see the signal, (b) how easily it can be automated, (c) how much capital is chasing it. Edges visible to millions via free screeners decay in days.

---

## Cross-References

- [[01-Options-Strategies]] — Options arbitrage strategy cards
- [[02-Event-Market-Strategies]] — Event-driven and market making strategy cards
- [[Schema-and-Taxonomy]] — 24-field strategy card schema, 10-level difficulty ladder
- [[Professional-Quant-Strategies]] — Professional strategy library
- [[ai-coding-guardrails]] — 10 hard rules for development, protected paths
- [[Options-Volatility-Synthesis]] — Vol surface, stochastic vol, rough vol
- [[Market-Microstructure-LOB-Execution-Synthesis]] — Execution costs, spread, liquidity
- [[Failure-Mode-Catalog]] — 11 failure types
- [[Master-Index]] — Full encyclopedia index
