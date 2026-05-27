# Strategy Factory — Output Contracts

Updated: 2026-05-27

## Setup Card — Canonical Fields

Each Setup Card is a retail-facing output. All fields are required unless marked optional.

| Field | Type | Description |
|---|---|---|
| `symbol` | string | Ticker symbol |
| `main_view` | string | One of allowed labels (see below) |
| `time_range` | string | "Swing Setup: 5–30 trading days" (MVP) |
| `model_score` | float (optional) | Normalized score from strategy engine, if available |
| `price_area_that_matters` | string | Key price zone in plain English |
| `setup_breaks_below` | string | Level where the bullish case is invalidated |
| `setup_breaks_above` | string | Level where the bearish case is invalidated |
| `why_it_looks_strong_or_weak` | string | Narrative rationale, plain English |
| `main_risk` | string | Key risk to the setup |
| `what_changed` | string | What changed since last card (or "New setup") |
| `maturity_status` | string | PENDING / MATURE / RESOLVED |
| `plain_english` | string | One-sentence summary for non-technical readers |
| `disclaimer` | string | Research-only disclaimer |

## Allowed Labels (`main_view`)

| Label | Meaning |
|---|---|
| Bullish Swing Setup | All 5 gates passed, bullish bias |
| Bearish Swing Setup | All 5 gates passed, bearish bias |
| Waiting for Stronger Proof | Momentum present but confirmation needed |
| Waiting for Pullback | Trend positive but price too stretched for entry |
| Waiting for Breakout Confirmation | Tight consolidation, needs volume expansion |
| No Edge | No reliable rating — gates inconclusive |
| Weakening | Setup deteriorating, previous edge fading |
| Too Stretched | Price extended beyond normal range |
| High Risk Setup | Setup exists but volatility or other risk elevated |
| No Reliable Rating Yet | Insufficient data for a rating |

## Banned Words (retail output)

Never use in customer-facing output: Buy, Sell, Buy now, Sell now, Watch, Not Covered, Constructive, Poor regime fit, Neutral, Alpha, Beta, Factor exposure, Regime fit, Signal decay, Weak confirmation, Overweight, Underweight, Accumulate, Reduce.

## 5-Gate Setup Machine (internal)

Each Setup Card is produced by passing through 5 gates in sequence:

1. **Market Weather** — Is the broad market (SPY) in a trending or range-bound regime?
2. **Strength** — Does the symbol show relative strength (20d rank ≥ 0.85, 60d rank ≥ 0.70)?
3. **Proof** — Is the price above its 50-day moving average?
4. **Price Zone** — Is the setup near a support/resistance level that matters?
5. **Break Level** — Is there a clear level where the setup is invalidated?

Only symbols that pass gates 1–3 are candidates. Gates 4–5 determine the price context and invalidation level.

## Retail Wording — Phase Mapping

The `retail_wording.py` module maps internal outcome status + returns to the allowed labels:

- Positive return within window → `Bullish Swing Setup` or `Bearish Swing Setup`
- No significant move → `No Edge` or `Too Stretched`
- Negative return → `Setup Broke` or `Weakening`
- Still maturing → `Waiting for Stronger Proof` or `No Reliable Rating Yet`

## Scoreboard — Canonical Fields

| Field | Type | Description |
|---|---|---|
| ticker | string | Symbol |
| signal_date | date | When the setup was identified |
| observation_id | string | Unique ledger ID |
| initial_main_view | string | Label at signal time |
| initial_score | float (optional) | Score at signal time |
| initial_price | float | Price at signal time |
| current_price | float (optional) | Latest available price |
| days_elapsed | int | Calendar days since signal |
| maturity_status | string | PENDING / MATURE / RESOLVED |
| result_5_day | string (optional) | Hit/miss outcome at 5 bars |
| result_10_day | string (optional) | Hit/miss outcome at 10 bars |
| result_20_day | string (optional) | Hit/miss outcome at 20 bars |
| result_summary | string | "Hit", "Miss", "Partial", or "Pending" |
| plain_english_result | string | Narrative outcome description |

## Edge Sheet Required Sections

- Market Weather
- Top Bullish Swing Setups
- Waiting-for-Proof Setups
- No Edge / Weakening Names
- Hype Trap Radar
- Popular Ticker Pulse
- Price Areas That Matter
- Setup-Break Levels
- What Changed This Week
- Friday Scoreboard
- Reject Ledger

## Product Tier Constraints

- **$5 tier:** One-to-many distribution only. Read from cached JSON outputs. No per-user fresh compute.
- **Watchlist Lite:** Pre-selected ticker pool, same cached outputs.
- **Pro:** Wider ticker pool, same engine, same read-only contract.