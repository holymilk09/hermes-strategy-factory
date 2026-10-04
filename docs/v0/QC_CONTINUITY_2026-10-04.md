# Strategy Factory — QC Continuity Reference

Saved: 2026-10-04
Source: ChatGPT QC continuity record pasted by Matt on 2026-10-04, reconciled by Muse against code at `trust-calibration-working @ 1f1a238eb8c17f2340699ed6d6a30017fe3eeb13` and the recovered ledgers.

## Status of this document

This is a **standing reference for long-term consistency**, not scripture and not clearance.

Use it to avoid repeating old mistakes. If code-verified evidence, a reproduced calculation, or a better method contradicts this reference, follow the better evidence — then record the deviation, the reason, and the evidence in this file's deviation log (and in memory) so the next operator does not re-litigate it.

Evidence labels apply throughout: IMPLEMENTED—CODE VERIFIED / IMPLEMENTED—OPERATOR REPORTED / PLANNED / BLOCKED / HISTORICAL / RECONSTRUCTED-UNCONFIRMED.

ChatGPT's own record is explicitly partial/historical. It is not, by itself, authorization to write to a ledger, promote a strategy, or unblock production.

## 1. Canonical posture

- Three tracks, never conflated:
  1. Original residual mean-reversion — frozen, `CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED`, standalone alpha: false.
  2. Relative-strength continuation — active observation lineage: `ret_5d > 0`, `close > ma50`, `ret_20d_rank >= 0.85`, `ret_60d_rank >= 0.70`.
  3. Edge Sheet — product/packaging layer only.
- Production / live / broker / shadow: **BLOCKED** on all tracks.
- Frozen unless Matt explicitly unfreezes: strategy thresholds, scoring, maturity definitions, original observations, resolved outcomes, lineage identity.
- "13 approved observations" = accepted manifest. It is not 13 wins and not production approval.
- `relative_strength_continuation_phase28a_weak_pass` is lineage acceptance, not a per-stock rating or confidence score.

## 2. Confirmed rules (applied 2026-10-04, code-verified)

- Maturity = 10 completed future bars after the signal; signal bar excluded; settled closes only.
- Elapsed calendar time is not maturity.
- A missing expected session blocks resolution until **real** bars are backfilled. Counting available bars and sliding the window is forbidden.
- Canonical price is the raw `close` column. Dividends/splits are ignored by `load_ohlcv`; prior resolutions recompute exactly from raw closes.
- `outcome_timestamp` = the outcome bar's cache timestamp (`04:00:00+00:00` convention).
- Ledger stores raw return/close only. Cost-adjusted = raw − 0.15pp; delay-adjusted = raw − 0.05pp. These are flat audit/reporting deductions, not a delayed-entry simulation, and not ledger fields.
- Keep per-observation values separate from cohort aggregates. Never substitute a cohort mean into a single-name result.
- Wrong-cohort reports are rejected by identity, not debated on numbers (see §4).
- Return units must be normalized before aggregating (fractions vs percentage points).
- No manual in-place ledger edits. Any resolution is a new file + row-level diff + preservation check that previously resolved rows are byte-identical.
- Read-only work must not mutate inputs: hash before and after.

## 3. Resolver warning (code-verified, do not ignore)

`src/paper/relative_strength_observation.py:resolve_observation_outcomes` at 1f1a238:
- rebuilds outcomes from the **observation ledger** (which still shows all 13 as PENDING; the outcome ledger is authoritative);
- takes bars strictly after the signal, requires ≥10 or stays PENDING;
- picks `iloc[9]` — the 10th *available* bar, with no calendar/session check.

On the recovered VPS cache (2026-07-02 missing; 2026-07-11→2026-08-26 gap; only 9 bars after 2026-07-01), any 1-bar refresh would silently resolve the July cohort to ~September 2026 instead of the true 10th trading bar, 2026-07-16.

**Do not run the VPS resolver or `refresh_stale_ohlcv.py` on a live ledger.** Use a guarded, cohort-specific procedure instead (worked example: `docs/v0/tools/resolve_pending_guarded.py`). Fixing this in `src/` is a separate, Matt-approved task with its own preflight and regression test.

## 4. Error catalogue — do not repeat

- Substituting cohort aggregates for per-observation values (the second-MRVL contamination error).
- Accepting a plausible numeric report about the wrong cohort/identity. Historical example: a CONFIRM/CONTRADICT table about GOOGL/META/NVDA/TSLA/AMD/AAPL was rejected — it was not the approved cohort (May: AMD, ARM, CRWD, DDOG, MRVL, SEDG; Jun: MRVL; Jul: ARQQ, ASML, LLY, MU, SNOW, UNH).
- Confusing the two MRVL observations: 2026-05-20 → +69.40%; 2026-06-05 → +16.85%.
- Treating filter lift (accepted vs ghost) as proof of filter efficacy when cohorts/windows are unmatched. Descriptive only.
- Interpreting a favorable label (`weak_pass`, "approved", "mature") as an edge, a win, or permission to trade.
- Modifying a valid ledger to satisfy a stale manifest or test expectation. Repair the expectation, not the ledger.
- Resurrecting a failed gate/filter because a later narrative sounds good. Failed items stay in the graveyard unless re-tested under a new, explicit hypothesis.
- Magnitude-based return-unit inference. Normalize units explicitly.

## 5. Test evidence

- Retained, OPERATOR REPORTED (2026-07-09, not reproduced locally): source-only 409 passed / 88 deselected; full 497 passed.
- Reproduced locally 2026-10-04 at clean 1f1a238 (pytest 9.1.1 / pandas 3.0.6):
  - Core resolution path (`test_relative_strength_observation`, `test_relative_strength_continuation`, `test_maturity_watchdog`): **11 passed**.
  - Full source-only suite: 394 passed, 11 failed, 88 deselected, 1 collection error. Failures classified environment-only: hardcoded `/opt/data/.venv/bin/python` paths, Alpaca calendar network calls, and `tests/test_price_volume_capitulation_v2.py` importing a script absent from the clean tree (VPS had ~64 untracked scripts).
- Never present retained counts as reproduced. Report scope, command, and counts every time.

## 6. Gaps closed by Muse (2026-10-04, code-verified)

- Raw vs adjusted convention: raw `close` is canonical (see §2).
- Dividends/splits treatment: ignored by `load_ohlcv`; matched by using Yahoo `auto_adjust=False`.
- Endpoint/session list for July 2026: Jul 2, 6, 7, 8, 9, 10, 13, 14, 15, 16 (Jul 3 holiday) → outcome date 2026-07-16.
- Benchmark formula: raw closes, same window — SPY +0.6651%, QQQ −2.6518% (2026-07-01→2026-07-16).
- `outcome_timestamp` convention: outcome bar timestamp.
- Missing-session policy: block until real backfill (see §2).
- Resolver idempotency defect: confirmed, documented, worked around with a guarded script — **not** fixed in `src/`.

## 7. Still open (make missing evidence visible, do not reconstruct)

- `reports/strategy_factory/hypothesis_registry.csv` (7 rows) — still VPS-only; contents unknown here.
- Ghost ledger post-MATURE multi-horizon progression (10/20/30-bar after a 5-bar MATURE stamp).
- Resolver preservation contract in `src/` (see §3).
- Hypothesis registry / audit re-run with matched windows — Matt's decision.
- Whether the July cohort changes the lineage assessment — Matt's decision. The record now stands at 13 resolved / 0 pending, mean +11.4930%, hit rate 61.54% (8/13); July cohort mean −10.4103%, 1/6 winners. Thirteen observations is not a validated edge.

## 8. Operator gate before any ledger-affecting work

1. Confirm branch, HEAD, cohort identity, expected counts. Wrong cohort/path/HEAD = stop.
2. Hash observation, outcome, and ghost ledgers before work.
3. State the exact rule set you will apply (from §2) before touching data.
4. Produce a new file; never edit in place. Row-level diff; previously resolved rows byte-identical.
5. Recompute every return from signal/outcome closes; verify IDs unique; broker fields empty unless a real broker record exists (none does).
6. Re-hash originals after work; they must be unchanged.
7. Run core tests; report exact counts and scope.
8. Label every claim with an evidence label from the header.

## 9. Deviation log

Record here (date, rule/reference section, what was done differently, evidence, Matt approval if applicable) whenever a better method overrides this reference.

- 2026-10-04 — §3 workaround adopted as standard practice for resolutions: guarded cohort script instead of the `src/` resolver, because the resolver is code-verified to shift windows on gapped caches. Evidence: `RESOLUTION_2026-10-04.md`; originals hash-unchanged; 6-line diff only.

## 10. Standing principle

Preserve the original experiment, verify the data and comparison used, make missing evidence visible, never let a favorable label substitute for a reproducible result.
