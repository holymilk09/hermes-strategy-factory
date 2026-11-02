# Verdict: momentum_continuation_ret5d_ma50_v1 — FAILED (killed)

Date: 2026-11-02 | Decision by: Matt (option B: kill v1, preregister a
regime-gated successor) | Evidence label: IMPLEMENTED—CODE VERIFIED
(ledger statistics recomputed from the forward ledgers; cross-source
audit 2026-10-18 reproduced all resolutions from Massive within 0.0007pp)

## Final record

- 81 resolved selected across 4 signal dates (2026-10-02 / 06 / 09 / 16);
  231 resolved rejected. Preregistered sample target (≥30 across ≥3 dates)
  met 2026-10-24 and exceeded.
- Selected: mean −4.81%, median −3.81%, hit 34/81 (42%), mean excess vs
  SPY −3.38pp.
- Same-date rejected: mean −1.15%, hit 48%, excess +0.21pp. The rule
  anti-selected: its rejections outperformed its selections.

## Bars (from the preregistration, unchanged)

- Success (all required): excess > 0 — FAIL (−3.38pp); hit ≥ 55% — FAIL
  (42%); selected mean > rejected mean — FAIL (−4.81% vs −1.15%).
- Kill (any one): excess < −2pp at n≥30 — TRIPPED; hit < 45% at n≥30 —
  TRIPPED.
- Test integrity: 0 blocked, 0 duplicates, preservation verifier PASS on
  every run. The test was valid; the hypothesis failed it.

## Cohort progression (context, not a rescue)

Oct 2: −13.10pp excess · Oct 6: −6.32pp · Oct 9: +1.90pp · Oct 16: +2.88pp.
Cohorts improved monotonically. Post-hoc regime checks run 2026-11-02
against the four cohorts found NO separating variable among the natural
candidates: SPY vs MA50 gate was ON for both catastrophic cohorts and OFF
for the best one; SPY vs MA200 was ON throughout; SPY 10-day realized vol
and the cohorts' own median ret_5d did not separate good from bad cohorts
either. The improvement is recorded as unexplained — possibly noise — and
was NOT used to design the successor's gate after the fact.

## Closure terms

- v1 scanning stops 2026-11-02. Remaining pending rows (51 selected /
  105 rejected, signal dates Oct 23 and Oct 30) resolve under the guarded
  path for the record; no new v1 signal dates are added.
- Ledgers are frozen evidence. They are never edited, merged, or reused
  as the successor's sample.
- The successor is a NEW hypothesis with its own preregistration, ledgers,
  and forward clock. Its gate is chosen a priori and its in-sample
  behaviour on the v1 window is disclosed in its preregistration.
- Production / live / broker / shadow remain BLOCKED, unchanged.
