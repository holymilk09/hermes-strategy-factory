# Hypothesis: momentum_continuation_ret5d_ma50_v1 (PREREGISTERED)

Date: 2026-10-05 | Status: PLANNED / EXPLORATORY — forward observation only
Evidence label for everything so far: EXPLORATORY (in-sample reclassification), not validation.

## Why this exists

The matched-window audit (`AUDIT_MATCHED_WINDOW_2026-10-05.md`) found no consistent lift for the frozen relative-strength continuation filter. Gate-level split suggested the `ret_5d > 0` gate carried what value existed (its rejections averaged −3.31%), while `ret_20d_rank ≥ 0.85` did not separate (its rejections averaged +0.83%).

This hypothesis tests the simpler rule on its own. It is a **new** hypothesis with a new ID. It does not modify, rename, or revive the frozen lineage `relative_strength_continuation_phase28a_weak_pass`, whose thresholds, observations, and outcomes stay untouched.

## Rule (frozen at registration)

Select a symbol on a signal date if, on a complete daily series:
- `ret_5d > 0` (close vs close 5 trading bars earlier), AND
- `close > ma50` (50-bar simple moving average including the signal bar).

No rank gates. No other filters. Universe: the 78-symbol list in `tools/momentum_ret5d_ma50_scanner.py` (the observed Strategy Factory universe). Benchmarks SPY/QQQ are never selected.

## Data conventions (frozen)

- One price source per calculation; series-consistent split-adjusted closes (see audit § split finding: never mix ledger pre-split prices with current Yahoo prices).
- Completeness guard: a missing expected session in the 60 bars before the signal makes that symbol/date INSUFFICIENT_DATA — no available-bar shifting, no sliding windows. (This guard exists because the July 2026 accepted cohort's ledger `ret_5d` values were computed on a gapped cache — e.g. MU ledger ret_5d +15.23% vs true +/−1.55% recomputed; ARQQ +73.90% vs +0.73%. Outcomes were price-correct; the *features* were not true 5-day returns. This hypothesis must not repeat that.)
- Outcome: 10 completed trading bars after signal, signal excluded. Raw return in percentage points. Cost-adj (−0.15pp) and delay-adj (−0.05pp) are reporting-only.
- Resolution preserves resolved rows: a resolver run never recomputes a RESOLVED row.

## Exploratory in-sample result (not validation)

Reclassifying the already-observed pool (13 accepted + 159 ghosts, features recomputed clean):
- New-rule selected — n=90, mean +1.8947%, median +1.2298%, hit 54.4%
- New-rule rejected — n=82, mean −2.1915%, median −0.2749%, hit 48.8%
- July 1 only: selected n=33 mean −0.9992% vs rejected n=45 mean −3.2793%
- May 27 broad scan: selected −1.4193% vs rejected −1.0888% (no lift that date)

Read: modest, inconsistent in-sample separation. That justifies a forward test, not a claim.

## Forward test protocol

- Run `tools/momentum_ret5d_ma50_scanner.py scan --log-rejected <rejected.csv>` on fresh data (weekly cadence is sufficient; daily is acceptable), then `resolve` both ledgers after 10 bars, then `summary` on each.
- Accumulate until: **≥30 resolved selected observations across ≥3 distinct signal dates**, or 6 months elapse, whichever comes first.
- Success bar (all must hold): mean excess vs SPY > 0, hit rate ≥ 55%, and selected mean > same-date rejected mean (rejected cohort is logged with `--log-rejected`).
- Kill bar (any): mean excess vs SPY < −2pp at n≥30, or hit rate < 45% at n≥30, or a data-completeness failure is found in >10% of scans.
- If neither bar is hit at the sample target, the hypothesis is inconclusive and gets one explicit extension decision from Matt — no silent continuation.

Tooling verified 2026-10-05 (offline, cache mode): scan as-of 2026-07-01 selected n=33, resolved mean −0.9992%; rejected cohort n=45, mean −3.2793% — both exactly match the independent reclassification script. The completeness guard correctly refuses the original gapped cache (ARQQ/ASML/etc. skipped: 2026-05-27→06-26 gap). Re-scans are idempotent.

## Hard boundaries

- Research only. No broker, no orders, no shadow execution, no production. `sent_to_broker` is always False.
- This hypothesis never writes to the frozen lineage ledgers, the ghost ledger, or any recovered bundle file.
- Any change to the rule above after registration is a new hypothesis (v2), with the change logged here before it is run.

## Decision log

- 2026-10-05 — Registered by Muse on Matt's instruction to proceed with the recommended build. Old lineage downgraded to watch-only in the operator handoff (no further promotion work; its record stays as resolved).
