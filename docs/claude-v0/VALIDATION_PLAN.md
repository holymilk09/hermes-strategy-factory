# Validation plan — research-intel products (PREREGISTERED)

Branch `claude/v0-build` · Registered 2026-10-08 by Claude (Anthropic), BEFORE any of the
runs below. Gates, metrics, thresholds, universe and sample split are frozen at this commit.
Any later change is logged in §7 with its reason, and results under the original gate are
still reported.

Product status at registration: **BUILT — UNDER VALIDATION.** Not finished, not connected.

## 1. Rule

A product claim ships only if its gate passes. A feature whose gate fails is removed from
the brief (not reworded to sound weaker). Descriptive outputs that make no claim (raw
moves, dates) only need Phase 1–2.

## 2. Data and split (frozen)

- Source: Robinhood `get_equity_historicals`, daily, split-adjusted, regular session.
- Range: 2024-04-01 -> 2026-10-07 (settled). In-sample (IS) sessions before 2025-07-01;
  out-of-sample (OOS) 2025-07-01 -> 2026-10-07. Thresholds below were set without looking
  at IS or OOS results; IS exists only to report whether OOS behaviour is stable.
- Universe (34): SPY QQQ SMH XLK XLF XLV · MU NVDA AMD AVGO TSM ASML MRVL QCOM ON ARM SKHY ·
  AAPL MSFT GOOGL META AMZN · JPM GS MS BAC · LLY UNH JNJ ABBV MRK · CAT GE HON.
- Earnings history: Robinhood `get_earnings_results` per stock (trailing 8 quarters).

## 3. Phase 1 — data integrity (all must pass)

- **1a Settled close.** Last cached bar close == official last-session close from
  `get_equity_quotes`, within 0.01%, for every symbol.
- **1b Adjustment consistency.** For each symbol, split-adjusted vs raw (`adjustment_type=none`)
  close ratio is constant except across documented splits; every ratio change lands on one date.
- **1c Calendar.** Every stock has every SPY session in its listed range (no internal gaps),
  or each gap is listed. SPY has no weekend dates and no session on 2025-12-25 / 2026-01-01.
- **1d Re-fetch idempotency.** Overlapping fetches agree exactly (the cache refuses conflicts).
- **1e Extreme moves.** Every |daily return| > 15% is listed and checked: earnings reaction
  (from earnings history), index-wide move, or flagged UNEXPLAINED. Gate: zero data-error
  explanations (e.g. a missing split) remain.

## 4. Phase 2 — engine correctness on real data (all must pass)

- **2a No look-ahead.** For 200 random (symbol, date) pairs in OOS, `move_context`, `beta`,
  `pair_health` computed on a cache truncated at that date equal the full-cache results exactly.
- **2b Independent recomputation.** 60d/120d betas and 120d correlations for 200 random cases
  recomputed with numpy (`polyfit` / `corrcoef`) match within 1e-9.
- **2c Determinism.** Two full brief runs produce byte-identical JSON.

## 5. Phase 3 — out-of-sample validation of product claims (OOS only, gates frozen)

- **3a "Implied by its beta" (beta-implied move).** Next-day implied move = trailing-60d beta
  x benchmark move. Gate: implied beats the naive zero-move forecast on MSE for >= 80% of
  stocks, and pooled corr(implied, actual) >= 0.30. Fail -> remove implied move and alerts.
- **3b "Moves most with" (linked peers).** Pairs linked at date t (120d corr >= 0.50).
  Gate: >= 70% still have corr >= 0.40 over sessions t+1..t+60. Fail -> remove peer lists.
- **3c Alerts are rare and meaningful.** Alert rate (|z| >= 2.5) between 0.5% and 3.0% of
  stock-days. AND alert days have mean |next-day residual| >= 1.2x non-alert days
  (bootstrap 95% CI lower bound > 1.0) — i.e. an alert marks a genuinely abnormal period.
  Fail first part -> recalibrate is NOT allowed silently; report and decide with Matt.
  Fail second part -> alert text drops "unusual"-period framing, keeps the raw residual.
- **3d "Its result may move X too" (peer earnings read-through).** Follower |residual| on
  linked-peer earnings-reaction days vs the follower's other days. Gate: ratio >= 1.20 with
  bootstrap 95% CI lower bound > 1.0. Fail -> remove the peer-earnings line.
- **3e "Treat B as a weaker guide" (decoupling).** Pairs flagged DECOUPLING vs pairs HEALTHY
  at t: mean corr over t+1..t+60. Gate: decoupled minus healthy <= -0.10. Fail -> remove the
  sentence; keep the flag as a descriptive event only.
- **3f Divergence.** Descriptive only: report the next-5/10-session relative move after a
  DIVERGENCE flag. No gate, and no directional guidance is added regardless of the result
  (that would be a new hypothesis needing its own registration).
- **3g Earnings labelling.** For alerts within calendar coverage: share labelled as earnings
  reactions, and spot-check 10 unlabelled alerts by date. Descriptive; any mislabel found
  is a bug to fix.

## 6. Phase 4 — replayed output audit; Phase 5 — dogfood

- **4** Replay the brief for 20 consecutive past sessions on a demo profile. Gate: every
  number quoted in the text equals the JSON field it came from (automated check); zero
  buy/sell language; no item longer than ~8 lines on mobile.
- **5** Dogfood: 10 live sessions on Matt's real book (needs his account number). Gate:
  Matt's judgement. Only after 5 does connection/hosting start.

## 7. Deviation log

- (none at registration)
- 2026-10-08, Phase 1e tooling (not a gate change): the first classifier run used a
  "round-number close" data-error rule and all-cluster peers. Both were wrong (MU's real
  1088.00 close tripped the first; the second linked ARM to NFLX). Replaced with the
  corporate-action quarantine and primary-cluster peers; added NEW_LISTING. Gate unchanged.
- 2026-10-08, product change from a Phase 1 finding: `data_quality.adjustment_audit` +
  cache quarantine. HON's adjusted series is invalid 2025-10-30..2026-06-18 (159 sessions
  quarantined). Phases 2-4 run on the quarantined cache.

## 8. Amendment A — registered 2026-10-09 BEFORE re-running (independent review findings)

An independent reviewer showed gate 3a is too easy: the implied move uses the *same-day*
benchmark return, so it is a decomposition, not a forecast, and a no-estimation model
(beta = 1 to SPY for every stock) also passes 3a. 3a as run is kept and reported, but it
no longer counts as evidence for the beta engine. New gate, frozen here:

- **3a-v2 (engine vs naive).** OOS, same stock-days as 3a. Naive model: beta = 1 to SPY.
  Gate: engine pooled MSE (move − implied) < naive pooled MSE by >= 10%, AND engine MSE <
  naive MSE for >= 70% of stocks. Fail -> the brief stops quoting an "implied" move as a
  calibrated yardstick (it may still show the raw benchmark move) and alerts are re-based on
  the naive residual; this would be re-validated before shipping.
- **3d (bias fix, reporting only).** Own-earnings reaction and follow-through days are
  removed from the baseline as well as the peer set. Both versions reported; the gate and
  the removal decision stand unless the corrected ratio's CI lower bound clears 1.0 AND the
  point estimate clears 1.20 (it would then be re-registered as a new claim, not restored).
- **Phase 4 re-run** after fixing reverse look-ahead in `EventCalendar.upcoming` (events
  reported after the replay date were being hidden) and extending HON's quarantine over the
  2026-06-25..06-30 Aerospace spin window.
- The 3c alert band (0.5–3.0%) was set after seeing a 1.2% rate on Jul–Oct 2026 sessions,
  which lie inside OOS. 3c-rate is therefore downgraded to INFORMATIVE, not a valid gate.
