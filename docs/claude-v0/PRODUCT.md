# Strategy Factory research-intel — product (claude/v0-build)

Status 2026-10-08: **products complete, not yet connected** (no MCP server, no hosting,
no billing — those come after the product is accepted). Author: Claude (Anthropic).
Evidence labels per `docs/v0/QC_CONTINUITY_2026-10-04.md`.

## The products (IMPLEMENTED — CODE VERIFIED)

1. **Daily brief** (`brief.py`, M4). For each watched name, in interest order: last-session
   move vs the move its beta implied, which peers it actually co-moves with, earnings for the
   name and its linked peers, and plain-English guidance. A headline lists only what matters
   today, or says explicitly that nothing is unusual.
2. **Move alerts** (`moves.py`, M5). Fire only when a move is unusual *for that name*
   (|residual z| >= 2.5 vs a baseline that excludes the judged day). Alerts that land on an
   earnings reaction are named as such; if the loaded calendar doesn't cover the date, the
   brief says earnings can't be ruled out instead of claiming "unexplained".
3. **Weekly relationship map** (`weekly.py`, M6). Betas, linked pairs, group cohesion, and
   the list of what changed since last week (beta shifts >= 0.30, pairs linking/unlinking,
   groups tightening/loosening, names entering/leaving).
4. **Research record** (`research_record.py`). Cohort summaries for the frozen lineage and the
   preregistered `ret5d+ma50` hypothesis status with its success/kill bars. Reads ledgers
   read-only and hashes them before and after.

Inputs: an interest profile (`interest.py`, M3) — holdings, pins, ticker mentions that decay
(14-day half-life), sector interest that re-ranks but never adds names — and portfolio context
(`portfolio.py`): weights, group exposure, portfolio beta with its coverage.

## How to run

```bash
python -m src.research_intel.import_robinhood --settled-through 2026-10-07 saved_response.json
python -m src.research_intel.cli brief  --profile profile.json \
    --events cal.json:2026-10-08:2026-11-07 --out reports_out/
python -m src.research_intel.cli alerts --profile profile.json
python -m src.research_intel.cli weekly --profile profile.json --previous last_week.json --out reports_out/
python -m src.research_intel.cli record --ledger-frozen F.csv --ledger-hyp S.csv --ledger-hyp-rejected R.csv
```

Example profile: `docs/claude-v0/examples/demo_profile.json` (DEMO, not a real book).

## Honesty rules enforced in code

- Settled closes only; Robinhood `interpolated` gap-fill bars dropped (SKHY had 73).
- Missing session -> INSUFFICIENT_DATA. Short history -> window shrinks, labelled SHORT_HISTORY.
- Every result carries sample size, window and an evidence label.
- Units declared per ledger (fraction vs pp), converted once; implausible values flagged.
- An earnings calendar knows the dates it covers; absence of an event outside them proves nothing.
- No buy/sell language (tested). `sent_to_broker` is False everywhere.

## Verification (2026-10-08, Python 3.13.16, pytest 9.1.1)

- `tests/research_intel`: **62 passed** with the local cache; **58 passed, 4 skipped** without it.
- Alert calibration on real data: 12 alerts in 982 name-days (1.2%) over 60 sessions — the
  rate a 2.5-sigma rule should give. The three largest (MSFT +15.5% 2026-07-30, AAPL -7.4%
  2026-07-31, NVDA +8.7% 2026-08-27) each fall on the session after an after-close report
  (dates verified against Robinhood `get_earnings_results`), and the brief labels them so.
- Pre-existing `tests/reporting tests/feature_factory`: 22 failed / 1 passed, identical on the
  untouched base `2c08108` (missing VPS-only artifacts). No regression.

## Known limits (visible, not hidden)

- Research-record ledgers are not in this environment; the record shows NOT_LOADED until the
  hash-verified bundle is supplied. A canonical-hash check (13 resolved, mean +11.4930%, hit
  61.54%) runs automatically when the 2026-10-04 resolved ledger is loaded.
- The hypothesis "completeness failure > 10% of scans" kill bar needs scan logs; not evaluated.
- Thresholds are HEURISTIC defaults, reported with every result.
- Robinhood is the development data source only; a redistributable feed is required before
  anything is sold. Real-data outputs are therefore NOT committed to this public repo.
