# Validation results — research-intel products

Branch `claude/v0-build` · Plan frozen in `VALIDATION_PLAN.md` (`c1e9e2b`, before any run);
Amendment A registered `a5fe616` (2026-10-09) before the re-run. Scripts:
`docs/claude-v0/validation/`. Raw outputs (gitignored, licensed data): `cache/research_intel/validation/`.

**Status: GATES PASSED with changes (repo rule: the word "validated" is not used as a claim).
Independently reviewed. Two features removed. Flag threshold is now a profile setting.
Phase 5 (live dogfood on Matt's book) not started.**

## How this was checked

1. Phases 1–4 run 2026-10-08 against the frozen plan.
2. An independent reviewer (separate agent, had not seen the build) audited code and
   validation on 2026-10-09: 14 findings, 11 confirmed by reproduction. All confirmed
   findings fixed or reported below; each fix has a regression test.
3. Amendment A registered, then phases 1–4 re-run on the fixed code. Numbers below are the re-run.
4. First unseen session (2026-10-08) scored after it settled.

## Data

Robinhood daily split-adjusted closes, 34 symbols, 633 sessions, 2024-04-01..2026-10-07, plus
raw (unadjusted) closes for the corporate-action audit. Earnings calendar 2024-04-01..2026-10-17
in 30 contiguous windows (18 saved to disk; universe events from 12 inline windows transcribed).

## Phase 1 — data integrity: PASS (after two fixes)

- 1a 34/34 last close == official 2026-10-07 close. 1d 2,511 refetched closes identical.
- 1b HON's adjusted series is invalid 2025-10-30..2026-06-18 (irregular 0.954 upward adjustment,
  200.00 print, fake +35% day). Caught by the new adjusted-vs-raw audit and quarantined.
- **Review finding (fixed):** HON's late-June 2026 Aerospace spin left abnormal prints in *both*
  series (repeated closes 06-24, 06-26; ±10% days on flat markets) that the audit can't see.
  Added a sourced `corporate_actions.yaml`; HON quarantined through 2026-07-07 (170 sessions).
- 1c 633 sessions, no weekends or holidays; the only gaps are HON's listed quarantine.
- 1e 50 daily moves > 15%: 17 own earnings, 19 market-wide, 1 peer earnings, 1 new listing,
  12 news-driven (largest 2026 cases corroborated by news search). No data errors remain.

## Phase 2 — engine correctness: PASS

No look-ahead 200/200; numpy recomputation max beta diff 3.6e-15; byte-identical reruns.
(Limitation from review: 2a uses the full-history quarantine, so it cannot detect
quarantine look-ahead.)

## Phase 3 — product claims, out of sample (2025-07-01..2026-10-07)

- **3a as originally run: PASS, but not evidence.** The review showed the "implied move" uses
  the same-day index move, so it is a decomposition, not a forecast; a no-estimation model
  (beta = 1 to SPY) also passed. The product text now says "given that day's index move".
- **3a-v2 (Amendment A): PASS.** Engine beats naive beta=1 on 23/27 stocks (85%), pooled error
  19.9% lower (gate 70% and 10%). IS: 21/27, 18.3%. Losers OOS: GE, JPM, META, MSFT.
- **3b linked peers: FAIL** (56.8% persist vs 70% gate; IS 62.9%). Removed.
- **3c alerts:** rate 3.17% (IS 3.29%) is above the 3.0% band, but that band was set after
  seeing in-sample-period data, so per Amendment A the rate is INFORMATIVE only. Meaning: the
  day after an alert is 1.37x as abnormal (CI 1.20–1.56; reviewer's date-block bootstrap
  1.22–1.54). Kept.
- **3d peer earnings read-through: FAIL as registered (1.15).** The review found the baseline
  wrongly kept own-earnings days. Corrected: OOS 1.21 (CI 1.10–1.35) but IS 1.14 (fails), so
  it doesn't replicate. Stays removed; a candidate for a separately registered forward test.
- **3e decoupling: PASS** (next-60-session corr 0.32 vs 0.48 healthy). Review caveat: the
  validated content is "a recent 20-day correlation predicts the next 60 days"; the flag adds
  little beyond it, and decouplings cluster on 26 dates (regime events). The PASS holds under
  date- and pair-clustered bootstraps.
- **3f divergence:** descriptive; gap narrowed within 5 sessions 55% of the time. No guidance added.
- **3g:** 22% of OOS alerts are own-earnings reactions; second-session follow-through bug fixed.

## Phase 4 — replayed output audit: PASS (re-run after a fix)

**Review finding (fixed):** replays hid earnings that had reported by the fetch date (MU
2026-09-30 never shown). Re-run: MU's warning appears in 11 of the 20 replays. 160 items and
332 guidance lines; every number traces to the brief's JSON (the checker caught one more
hardcoded number, now in the JSON); no buy/sell language; at most 6 lines per item.

## Other review findings fixed

- "Nothing unusual" headline shown when nothing could be judged (weekend, empty profile).
- Weekly map still emitted link/unlink lines after 3b failed.
- Zero-variance (stale) baseline reported a +40% move as "in line with the market".
- Brief crashed on a hypothesis ledger with no resolved rows.
- One corrupt symbol file crashed the whole brief.
- CLI defaulted to the old cache; raw tracebacks on bad input; accepted a Sunday as_of.
- PRODUCT.md quoted stale, overclaiming numbers.

## Forward test (unseen data)

2026-10-08: Robinhood's historical endpoint still returned this session as an interpolated
placeholder the next morning; the official close came from the quotes endpoint (new strict
parser). Brief built cleanly. Engine mean error 0.88pp vs naive 1.74pp (21/28 closer). No
alerts. One session is a smoke test; the log accumulates in `forward_log.jsonl`.

## Amendment B — new analytics (registered `f63cbdb` before running; run 2026-10-09)

- **B1 attribution: PASS.** Two-factor (market + orthogonalised sector ETF) residual MSE is
  lower than market-only for 24/24 names with a cached sector ETF; pooled reduction 23.6%
  (gate 5% and 60%). Largest gains: MU (17.4 → 8.8), LLY (5.4 → 2.9), JPM (1.4 → 0.8).
- **B2 VaR coverage: PASS.** Equal-weight MU/NVDA/LLY/JPM/AAPL/MSFT, rolling 250-session
  historical VaR from the prior session: 10 exceptions in 320 sessions at 95% (3.1%, band
  2.5–8%; Kupiec LR 2.72, not rejected at 5%); 2 at 99% (0.6%).
- **B3 scoreboard: PASS.** 186 random OOS rows recomputed with pandas, zero mismatches.
- Phase 2 (no look-ahead, determinism) re-run including attribution, scoreboard, risk panel
  and the full report: PASS, 200/200.

## Open decisions for Matt

1. **Flag threshold.** Now a profile setting `flag_z` (default 2.5 ≈ 3% of stock-days). The
   registered band question is logged in the plan; nothing was retuned.
2. **Phase 5:** 10 live sessions on your real book (needs your Robinhood account number).
