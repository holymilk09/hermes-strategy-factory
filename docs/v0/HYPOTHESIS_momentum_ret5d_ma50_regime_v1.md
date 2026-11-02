# Hypothesis: momentum_continuation_ret5d_ma50_regime_v1 (PREREGISTERED)

Date: 2026-11-02 | Status: PREREGISTERED — forward observation only
Evidence label: PLANNED (no forward data yet). Research only; no broker, no
orders, no shadow execution. Production remains BLOCKED on all tracks.

## Why this exists

`momentum_continuation_ret5d_ma50_v1` was forward-tested and **FAILED**:
81 resolved selected, mean excess vs SPY −3.38pp, hit 42%, both kill bars
tripped (see `VERDICT_momentum_ret5d_ma50_v1.md`). Matt's decision
(2026-11-02, option B): kill v1 and preregister a regime-gated successor.
This is that successor — a **new** hypothesis with a new ID, new ledgers,
and a new forward clock. It does not modify, rename, revive, or inherit
data from v1 or from the frozen relative-strength lineage.

## The gate, and the honest disclosure

Gate (frozen): selections are made **only when SPY's close is above SPY's
own 50-bar simple moving average** on the signal date (same complete-series
conventions as the base rule). On gate-OFF dates the scan still runs and
all 78 symbols are logged to the rejected cohort; nothing is selected.

Rationale (a priori): the SPY-above-MA50 trend filter is the standard
index-regime gate in the momentum literature — the claim under test is
that short-horizon momentum continuation only pays when the broad market
is in an uptrend regime, and that v1's unconditional version harvested
reversals in non-uptrend conditions.

**Disclosure — the gate's behaviour on the v1 window is known and is
adverse:** checked 2026-11-02 before registration, the gate was ON for
both of v1's catastrophic cohorts (2026-10-02: SPY 769.64 vs MA50 763.70;
2026-10-06: 779.09 vs 765.22) and OFF for v1's best cohort (2026-10-16:
763.25 vs 768.50, excess +2.88pp). Three other natural candidates were
also checked and also failed to separate v1's cohorts (SPY vs MA200: ON
throughout; SPY 10-day realized vol: 11.0/8.7% bad vs 8.3/10.3% good;
cohort median ret_5d: +3.15/+4.00% bad vs +3.65/+4.53% good). This gate
was chosen anyway, on Matt's explicit instruction, for its a priori
standing — NOT because it explains v1's record. The forward test below
is the arbiter; if the gate merely reproduces v1's failure on gate-ON
dates, the kill bars will say so on fresh data.

## Rule (frozen at registration)

On a signal date, for each symbol in the v1 78-symbol universe
(`DEFAULT_UNIVERSE` in the scanner; benchmarks SPY/QQQ never selected):

- Compute the regime gate from SPY: `spy_close > spy_ma50` (50-bar SMA
  including the signal bar, complete series required).
- Select the symbol if the gate is ON **and** `ret_5d > 0` **and**
  `close > ma50` (the v1 base rule, unchanged).
- If the gate cannot be determined (SPY series missing or incomplete),
  the scan aborts and writes nothing — fail closed, never gate-assumed.

## Data conventions (frozen)

Identical to v1: one price source per calculation (Yahoo via the scanner,
as v1 and the holdings track), series-consistent split-adjusted closes,
the 60-bar completeness guard (missing expected session = INSUFFICIENT_DATA,
no window sliding), outcome = 10 completed bars after signal (signal
excluded), raw returns in percentage points, cost/delay adjustments
reporting-only, resolved rows never recomputed.

## Forward test protocol

- Weekly scans via the Saturday pipeline (`--track regime`), then guarded
  `resolve` on both ledgers after 10 bars, then `summary`.
- Accumulate until: **≥30 resolved selected observations across ≥3 distinct
  gate-ON signal dates**, or 6 months elapse, whichever comes first.
  Gate-OFF dates contribute rejected rows only and do not count toward
  the sample target.
- Success bar (all must hold): mean excess vs SPY > 0, hit rate ≥ 55%,
  selected mean > same-date rejected mean.
- Kill bar (any): mean excess vs SPY < −2pp at n≥30, or hit rate < 45% at
  n≥30, or a data-completeness failure in >10% of scans.
- If neither bar is hit at the sample target: inconclusive — one explicit
  extension decision from Matt, no silent continuation.
- Any change to the rule or the gate after registration is a new
  hypothesis (v2), logged here before it is run.

## Hard boundaries

- Research only. `sent_to_broker` is always False.
- This hypothesis never writes to the v1 ledgers, the holdings ledgers,
  the frozen lineage, or any recovered bundle file. Its ledgers live in
  the goal workspace under `forward_ret5d_ma50_regime_v1/`.

## Decision log

- 2026-11-02 — Registered by Muse on Matt's instruction (option B,
  confirmed after the gate-evidence briefing): kill v1, preregister the
  successor with the SPY > MA50 gate anyway.
