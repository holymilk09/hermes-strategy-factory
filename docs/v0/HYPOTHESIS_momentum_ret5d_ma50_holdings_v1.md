# Hypothesis: momentum_continuation_ret5d_ma50_holdings_v1 (PREREGISTERED)

Date: 2026-10-14 | Status: PLANNED / EXPLORATORY — forward observation only
Approved by Matt: 2026-10-14 (P1 of the Strategy Factory enhancement plan).

## Why this exists

The forward test of `momentum_continuation_ret5d_ma50_v1` scans a frozen
78-symbol universe that contains **none of Matt's uncovered real holdings**
(coverage gap verified 2026-10-14: GME, HOOD, NNE, BE, NVTS, VRT all absent).
That test must not be altered mid-flight — its universe is frozen in its
preregistration, and extending it would make cohorts non-comparable.

This is a **separate, parallel hypothesis** with its own ID, its own ledgers,
and its own counts. It applies the identical rule to the holdings the v1
universe misses, so the portfolio gets forward coverage without contaminating
the v1 verdict. Rows from this track are **never** merged into v1 ledgers,
counts, or verdict math, and vice versa.

Its near-term purpose is portfolio context — which of Matt's uncovered
holdings pass/fail the rule each week, feeding the research-intel layer v0 was
designed to produce. Any verdict on this track is deferred until its sample
target is met (below); with ~7 names, selected counts per date will be small
and a verdict is expected to take months.

## Rule (frozen at registration)

Identical to v1, verbatim:
- `ret_5d > 0` (close vs close 5 trading bars earlier), AND
- `close > ma50` (50-bar simple moving average including the signal bar).

No rank gates. No other filters. Benchmarks SPY/QQQ are never selected.

## Universe (frozen at registration — version 1)

Matt's real holdings (book of record 2026-10-13/14) that the v1 78-symbol
universe does not cover:

- **GME, HOOD, NNE, BE, NVTS, VRT** — the names in the 2026-10-14 coverage gap.
- **VST** — a real-money holding (~101 shares) also absent from the v1
  universe; included for the same reason.

Logged exclusions (deliberate, with reasons — not oversights):
- **SPCX** — position sold (Matt confirmed 2026-10-14); not a current holding.
- **SKHY (1 sh), APLD (~4 sh), ADPT (10 sh)** — stub/dust positions in the
  book of record, below materiality for a forward signal record.
- **MU, AMD** — real holdings already covered by the v1 universe (MU via its
  selected/rejected cohorts); duplicating them here would double-count.

Universe changes require an amendment logged in this document **before** the
first scan that uses the changed list, with the universe version incremented.
Changed lists never apply retroactively to earlier signal dates.

## Data conventions (frozen)

Identical to v1:
- One price source per calculation; series-consistent (split-adjusted) closes.
- Completeness guard: a missing expected session in the 60 bars before the
  signal makes that symbol/date INSUFFICIENT_DATA — no available-bar shifting.
- Outcome: 10 completed trading bars after signal, signal excluded, raw return
  in percentage points. Cost-adj (−0.15pp) / delay-adj (−0.05pp) reporting-only.
- Resolution is guarded (P0, 2026-10-14): SPY-calendar session check plus NYSE
  calendar cross-check; a row never resolves with blank benchmark fields.
- Resolution preserves resolved rows: a resolver run never recomputes a
  RESOLVED row.

## Forward test protocol

- Scanner run with `--track holdings` writes only to this track's ledgers in
  `hidden_files/forward_ret5d_ma50_holdings_v1/` (observations + rejected).
- Cadence: weekly, inside the existing `forward-scan-weekly` cron, after the
  v1 steps. First scan at registration (2026-10-14).
- Sample target: **≥30 resolved selected observations across ≥3 distinct
  signal dates**, or 6 months elapse, whichever comes first — same bars as v1
  if a verdict is evaluated (success: mean excess vs SPY > 0, hit rate ≥ 55%,
  selected mean > same-date rejected mean; kill: mean excess < −2pp or hit
  rate < 45% at n≥30, or data-completeness failure in >10% of scans).
- If the target is not reached in 6 months, the track gets one explicit
  extension decision from Matt — no silent continuation. Given the small
  universe, "inconclusive / context-only" is an expected and acceptable
  outcome; it is not a failure of the track.
- Event-risk caveat: this track is price-only. Names like GME/NNE carry
  binary/event risk and the FMP event blocker is still unbuilt. Any surfacing
  of holdings-track flags in briefs must pass the standing dated-event check
  and carry research-only labeling. A flag is context, never a call to action.

## Hard boundaries

- Research only. No broker, no orders, no shadow execution, no production.
  `sent_to_broker` is always False.
- This hypothesis never writes to the v1 forward ledgers, the frozen lineage
  ledgers, the ghost ledger, or any recovered bundle file.
- Any change to the rule above after registration is a new hypothesis (v2),
  logged here before it is run.

## Decision log

- 2026-10-14 — Registered by Muse on Matt's approval of the enhancement
  plan (P1), following the 2026-10-14 coverage-gap audit.
