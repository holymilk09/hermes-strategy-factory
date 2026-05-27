# Strategy Factory — Product Roadmap

Product: Strategy Factory Edge Sheet
Slogan: Know the setup before you chase the stock.
Price: $5/month (founding access)
Signature output: Setup Cards
Core mechanism: 5-Gate Setup Machine (Market Weather → Strength → Proof → Price Zone → Break Level)
Signature risk feature: Hype Trap Radar
Accountability feature: Friday Scoreboard

---

## Phase A — Continue Maturity (current)

**Status: ACTIVE**

- Daily after-close updates only
- No feature work
- Wait for 5/10/20-day outcomes to mature (currently 6 pending, 3/10 bars)
- Keep ghost ledger running idempotently
- Keep Friday Scoreboard honest (no fabricated results)

**Gate to next phase:** At least one full outcome window completed across all observations.

---

## Phase B — $5 Founding Access Packaging

**Status: PENDING (gated by Phase A completion)**

- Shopify landing page copy only (no payment integration yet)
- Sample Edge Sheet (curated static example)
- Email template (plain-text + HTML)
- PDF/HTML archive of one sample cycle
- Compliance language review

**Explicitly excluded:**
- Custom ticker selection
- SMS notifications
- AI assistant
- Dashboard
- Real-time data
- Personalized advice

---

## Phase C — Edge Sheet Launch

**Status: PENDING (gated by Phase B)**

- Monday Edge Sheet (weekly swing setup candidates)
- Friday Scoreboard (accountability report)
- Hype Trap Radar (symbols with strong buzz but weak gates)
- Popular Ticker Pulse (coverage of frequently watched names)
- Price Area That Matters (key support/resistance zone in plain English)
- Setup Breaks Below (level where setup is invalidated)
- Research-only disclaimer on every output

---

## Phase D — Watchlist Lite

**Status: PENDING (gated by Phase C → 3 months of production Edge Sheets)**

- Pick up to 5 supported tickers per subscriber
- Read from cached setup cards only (no fresh compute per user)
- No unsupported custom research
- No personalized advice wording
- Still uses same validated engine path

---

## Phase E — Pro Tier

**Status: PENDING (gated by Phase D)**

- More covered tickers (scope TBD)
- Score history (how each setup card's rating changed over time)
- Setup history (when signals triggered, matured, resolved)
- Daily or 3x weekly update cadence
- Still reads from same validated engine (no parallel strategy path)

---

## Phase F — ML-0 Dataset Export

**Status: PENDING (gated by → enough completed outcomes for statistically meaningful analysis)**

- Dataset export from observation/outcome/ghost/trust ledgers
- Research-only, no model training
- No predictions
- No strategy changes
- CSV/Parquet export with schema documentation

---

## Phase G — ML Calibration Overlay

**Status: PENDING (gated by Phase F + ≥100 completed outcomes)**

- Calibration/ranking overlay on existing gates (not replacement)
- Never auto-change strategy rules
- Always human-reviewed before gate modifications
- Rank-order existing gates by predictive power, not create new ones

## Timeframe Rules

- MVP: Swing Setup only (5–30 trading days)
- Do not add short-term (1–5 days), long-term (1–6 months), premarket, or after-hours until explicitly planned with separate horizon_id and maturity tracking
- No options in any phase until explicitly approved