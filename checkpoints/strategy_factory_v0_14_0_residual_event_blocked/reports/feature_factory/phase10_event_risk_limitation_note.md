# Event Risk Limitation — Residual Reversion

Status: EVENT_CONTEXT_INCOMPLETE

Residual reversion assumes that price dislocation relative to a benchmark (SPY, sector ETF) 
is temporary and will revert. This assumption fails when the price move is caused by:

- Earnings announcements
- Guidance changes
- Analyst upgrades/downgrades
- Fraud or accounting issues
- Sector-wide shocks
- Macro/rate events
- M&A activity
- Real fundamental repricing

Current Hermes data has NO earnings calendar, fundamental data, or event detection.
Therefore, residual reversion signals CANNOT distinguish temporary dislocation from 
real repricing events.

Implication: Residual filters must be marked EVENT_CONTEXT_INCOMPLETE until 
an event/fundamental data source is integrated. No residual strategy can claim 
full validation without this control.

Do not integrate new APIs in this phase.
