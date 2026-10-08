# Validation results — research-intel products

Branch `claude/v0-build` · Run 2026-10-08 by Claude (Anthropic) against the plan frozen in
`VALIDATION_PLAN.md` (committed `c1e9e2b` before any run). Scripts: `docs/claude-v0/validation/`.
Raw outputs (gitignored, derived from licensed data): `cache/research_intel/validation/`.

**Status after validation: VALIDATED WITH CHANGES — two features removed, one decision
open for Matt, Phase 5 (dogfood) not started.**

## Data

Robinhood daily split-adjusted closes, 34 symbols, 633 sessions, 2024-04-01 -> 2026-10-07.
Raw (unadjusted) closes fetched separately for the corporate-action audit. Earnings calendar
for 2024-04-01 -> 2026-10-17 in 30 contiguous 31-day windows (18 saved to disk, 12 returned
inline; universe-symbol events from the inline 12 transcribed by hand, marked as such).

## Phase 1 — data integrity: PASS (after one fix)

- 1a 34/34 last cached close == official 2026-10-07 close.
- 1b **Found a data error.** HON's adjusted series scales history *up* by an irregular
  0.953987 (2025-10-30..2026-06-12), then shows a 200.00 print and a fake +35% day on
  2026-06-16. Fix: `data_quality.adjustment_audit` + cache quarantine (159 HON sessions now
  behave as missing). Legitimate actions pass: NVDA 10:1, AVGO 10:1, GE spin (1.2404), XLK 2:1.
- 1c 633 SPY sessions, no weekends or holidays, no internal gaps in any symbol.
- 1d 2,511 overlapping closes identical across separate fetches.
- 1e 51 daily moves > 15%: 17 own-earnings reactions, 19 market-wide (QQQ/SMH >= 5%),
  1 peer earnings, 1 new listing (SKHY), 1 data error (HON, now quarantined), 12 news-driven.
  The three largest 2026 news moves were corroborated by news search (MRVL 2026-06-02 AI
  rally; ON 2026-06-26 Synaptics deal; MU 2026-05-26 best month since 1987).

## Phase 2 — engine correctness: PASS

- 2a No look-ahead: 200/200 random cases identical on a cache truncated at the as-of date.
- 2b Independent numpy recomputation: max beta diff 3.6e-15, max corr diff 7.8e-16 (190 compared,
  10 correctly INSUFFICIENT on both sides).
- 2c Brief and weekly map byte-identical across reruns. (Re-run after the Phase 3 changes: still PASS.)

## Phase 3 — product claims, out of sample (2025-07-01..2026-10-07, 320 sessions)

- **3a "implied by its beta": PASS.** Implied move beats a zero forecast for 26/27 stocks;
  pooled corr 0.57 (n 8,440). IS: 24/27, 0.70. Weakest: MRK, ABBV, LLY, UNH (defensives).
  Change: brief now says the market is a weak yardstick when fit r2 < 0.10.
- **3b "moves most with" (linked peers): FAIL.** Only 56.8% of linked pairs stayed >= 0.40
  corr over the next 60 sessions (gate 70%). IS 62.9%. **Removed** from brief and weekly map.
- **3c alerts: rate FAIL (narrowly), meaning PASS.** Rate 3.17% of stock-days (band 0.5–3.0%;
  IS 3.29%). The day after an alert is 1.38x as abnormal as other days (95% CI 1.22–1.54).
  Per plan, the threshold was NOT recalibrated: **decision for Matt** (see below).
- **3d "its result may move X too" (peer earnings): FAIL.** Ratio 1.15 (CI 1.03–1.27), gate
  1.20. IS 1.07 (CI 0.96–1.19). **Removed.**
- **3e "treat B as a weaker guide" (decoupling): PASS.** Decoupled pairs' next-60-session
  corr 0.32 vs healthy 0.48 (diff −0.155, n 687 / 1,617). IS diff −0.132. Kept.
- **3f divergence (descriptive):** n 222; gap narrowed within 5 sessions 55% of the time.
  No directional guidance added (that would be a new registered hypothesis).
- **3g earnings labelling:** 22% of OOS alerts are own-earnings reactions. Bug found: second-
  session post-earnings moves were called "unexplained". Fixed (follow-through label; 4.9%
  of alerts). Spot-checked unlabelled alerts include known news days (GOOGL 2025-09-03
  antitrust ruling, AMD 2025-07-15 export news, ARM 2025-09-10 Oracle AI-capex day).

## Phase 4 — replayed output audit: PASS

20 consecutive briefs (2026-09-10..2026-10-07), 160 items, 320 guidance lines. Every number
in the text traced to the brief's JSON (checker verified with a tampered-number negative
control); zero buy/sell language; longest item block 6 lines. Review by eye fixed two
polish issues ("-0.0%" rendering; book vs item window wording). Limitation: replays use an
earnings calendar fetched 2026-10-08, later than the replay dates (shown in each brief).

## Open decisions for Matt

1. **Alert rate 3.17% vs registered band 3.0%.** Options: (a) accept and widen the band to
   ~3.5% with this result logged as a deviation; (b) register a new threshold (e.g. |z| >= 3.0)
   and re-run 3c on it. Alerts are meaningful either way (3c second part passed).
2. **Phase 5 dogfood** needs your Robinhood account number (the positions tool requires it
   from you). Nothing connects or ships until you grade 10 live sessions.

## What changed in the product because of validation

- Added: corporate-action audit + quarantine; earnings follow-through label; low-fit caveat.
- Removed: "moves most with" peer lists (brief + weekly), peer-earnings read-through line,
  "group label isn't telling you much" line (depended on the removed link claim).
- Kept: implied move, move alerts, decoupling/divergence flags, own-earnings labelling,
  portfolio context, research record.
