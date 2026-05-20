# Module Contracts

## Data contract

Input:

- Vendor payload
- Requested symbol
- Requested timeframe
- Calendar

Output:

- Normalized `MarketEvent`
- Validated timestamp
- Data quality flags
- Vendor/source ID

## Signal contract

Input:

- Point-in-time feature snapshot
- Strategy config
- Current position state

Output:

- Symbol
- Direction
- Score
- Horizon
- Confidence
- Reason codes

## Portfolio contract

Input:

- Signals
- Capital
- Current holdings
- Risk budget

Output:

- Target position or target weight
- Sizing reason
- Constraints applied

## Risk contract

Input:

- Target portfolio
- Current portfolio
- Risk limits
- Market state

Output:

- Approved target
- Clipped target
- Vetoed target
- Veto reason

## Execution contract

Input:

- Approved target delta
- Market liquidity state
- Broker constraints

Output:

- Order instruction
- Order type
- Quantity
- Limit price if any
- Time-in-force
- Client order ID

## Review contract

Input:

- Backtest/live run
- Metrics
- Trade ledger
- Logs
- Heatmaps

Output:

- Promotion/reject/hold decision
- Weak-point list
- Required next experiments
