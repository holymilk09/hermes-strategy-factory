# Review and Learn Loop

The systematic review cadence, questions, and backlog structure that closes the learning cycle for every trading strategy.

## Review Cadence

| Trigger | Review Type | Output |
|---|---|---|
| Every backtest run | Automatic metric pack | Metrics report |
| Every serious experiment | Written review | Experiment review note |
| Every epoch | Promotion/rejection note | Epoch review (committees even if solo) |
| Every paper-trading week | Live-vs-backtest delta report | Delta analysis |
| Every live-trading day | Operational incident review | Incident log entry |

## Core Review Questions

For every review, answer:

1. **What changed from the previous run?** (data, config, code, environment)
2. **Did the code/data/config change?** If yes, what and why.
3. **What weak point got better?** Use [[Strategy-Weak-Point-Detection]] scores.
4. **What weak point got worse?** Regressions must be flagged immediately.
5. **Did improvement come from real edge or looser assumptions?** Cost model, fill model, look-ahead.
6. **Is the result robust to costs?** Test 2x/3x slippage and commission.
7. **Is the result robust to nearby parameters?** Parameter heatmap check.
8. **Does it survive OOS?** Walk-forward test result.
9. **What is the next falsification test?** Every review ends with the next test to run.

## Learning Backlog Labels

| Label | When to Use |
|---|---|
| `strategy_edge` | Genuine signal/alpha insight discovered |
| `data_quality` | Data issue affecting results |
| `execution` | Fill, slippage, order routing issues |
| `risk` | Sizing, position limits, drawdown control |
| `code_bug` | Software defect |
| `overfit_risk` | Strategy may be overfit; needs more OOS or DSR/PBO |
| `ops_failure` | Operational failure (API, infrastructure, deployment) |
| `market_regime` | Strategy performance dependent on regime |

## Implications

- **Reviews compound**: each review makes the next epoch smarter. Skipping reviews = stagnation.
- **Solo operators must still write promotion/rejection notes**: "committees even if solo" means you must formally decide and document.
- **Live-vs-backtest delta is the most valuable review**: it catches the gap between simulation assumptions and reality.

## Failure Modes

- **Review fatigue**: treating reviews as checkboxes rather than genuine analysis.
- **Blameless reviews that miss bugs**: being too lenient and not flagging data or code issues.
- **Promotion without documentation**: deploying without a written review note.
- **No next falsification test**: the review ends without defining the next experiment, breaking the epoch loop.
- **Ignoring label tracking**: without backlog labels, you can't identify systemic issues (e.g., repeated `execution` tags mean the execution layer needs a rewrite).

## Cross-Links

- [[Epoch-Learning-Retraining]] — the epoch-driven learning cycle this loop feeds
- [[Strategy-Weak-Point-Detection]] — weak-point scoring informs review questions 3-4
- [[Trading-System-Build-Doctrine]] — Phase 6 review and iteration
- [[Logging-Audit-Monitoring]] — review_log stream stores review decisions
- [[Logging-Audit-Monitoring]] — individual trade reviews feed the broader review loop
