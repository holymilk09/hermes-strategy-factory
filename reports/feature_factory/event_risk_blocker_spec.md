# Event Risk Blocker Specification

Purpose: Prevent residual reversion from fading real repricing events.
Why: residual_z <= -2.0 can be temporary dislocation OR correct repricing.
Without event context, Hermes cannot distinguish them.

## Blocked Event Types
- Earnings (within 5d before, day of, 2d after)
- Guidance cuts, major downgrades
- Fraud, accounting issues, dilution, offerings
- M&A news, trading halts
- Sector/macro shocks
- Abnormal gaps with news

## Fallback (no event API)
- Use price/volume proxy flags
- Block large gap downs (>5%)
- Block abnormal volume spikes (>3x avg)
- Block extreme single-day moves (>2.5x vol)
- Mark all results EVENT_CONTEXT_INCOMPLETE

## What's Missing
- No earnings calendar API
- No fundamental data
- No news feed
- No event detection beyond price/volume
