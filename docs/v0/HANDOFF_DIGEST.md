# ChatGPT handoff — digest

**Source:** `chatgpt-handoff-2026-09-29.md` (verbatim, 2026-09-29)
**Verification by Muse (2026-09-29):**
- `trust-calibration-working` exists at `1f1a238eb8c17f2340699ed6d6a30017fe3eeb13` — matches handoff ✓
- `main` @ `c149578` is the older packaging checkpoint — the earlier repo tour
  saw this, NOT the working branch. Corrected below.
- **Full reconciliation complete — see `RECONCILIATION.md`.** Every
  code-checkable handoff claim verified against the working branch (24 checks:
  23 CODE VERIFIED, 1 not-verified — the "16 modules" claim; the repo has 15
  `.py` files). No contradictions found. Extra findings: hardcoded 60-bar ETF
  minimum in `residual.py`; `residual_z = 0.0` (not NaN) on zero residual std;
  Phase 27A uses pandas sample-SD (ddof=1) vs original engine's NumPy ddof=0;
  the outcome resolver writes atomically (tmp+replace) — only the ghost
  resolver's direct mode-"w" write is non-atomic.

## 1. The correction that matters most: two lineages, not one

| | Residual mean-reversion (original) | Relative-strength continuation (later, active) |
|---|---|---|
| Rule | `residual_z <= -2.0` AND `residual_r2 >= 0.20` | `ret_5d > 0`, `close > ma50`, `ret_20d_rank >= 0.85`, `ret_60d_rank >= 0.70` |
| Status | `CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED`, `standalone_alpha: false` | Forward observation, 13 approved / 7 resolved / 6 pending |
| What it is | Strategy-conditioned filter candidate | Recorded observations with 10-bar outcome windows |

Plus the **Edge Sheet product**: packaging complete ($5/mo founding access),
Shopify NOT deployed, paid launch BLOCKED.

**Do not conflate:** hypothesis ≠ observation ≠ outcome ≠ audit label ≠ setup
card ≠ commercial product. A positive result at one level never authorizes the
next.

## 2. Current state (verified branch)

- Working branch: `trust-calibration-working` @ `1f1a238` — manifest 13/7/6
- Resolved (7): AMD, ARM, CRWD, DDOG, MRVL, SEDG (2026-05-20) + MRVL (2026-06-05;
  +16.85% over 2026-06-05→06-22)
- Pending (6): ARQQ, ASML, LLY, MU, SNOW, UNH (all 2026-07-01) — maturity and
  data provenance need verification; NOT "resolved because time passed"
- Frozen: thresholds, scoring, lineage identity, maturity definitions, original
  observations, resolved outcomes, broker/live/shadow, trend-extension graveyard
- Blocked: paid launch & performance claims, legal clearance, hosted DB/API,
  Shopify billing, FMP key

## 3. Evidence labels — adopt for all SF reporting

`IMPLEMENTED — CODE VERIFIED` / `IMPLEMENTED — OPERATOR REPORTED` /
`PLANNED` / `BLOCKED` / `HISTORICAL` / `RECONSTRUCTED / UNCONFIRMED`.
No more bare "done" or "works."

## 4. Key design rationale (why, not just what)

- **Filter must beat "doing less" randomly** — fewer trades look better via
  costs/congestion alone. Hence strategy-conditioned random pruning (Gates 7–8).
- **Strategy conditioning precedes residual filtering** (Phase 12.5 fix) — the
  candidate pool defines the question being tested.
- **Event context is veto-only** — FMP may block/warn/tag, never generate alpha
  or trigger production.
- **Rejected signals stay dead** — trend-extension reversal is in the graveyard;
  no resurrection via re-cutting, seed hunting, or relabeling.
- **Maturity ≠ edge** — signal recorded ≠ horizon complete ≠ positive return ≠
  benchmark outperformance ≠ filter improvement ≠ executable profit ≠ durable edge.
- **Candidate returns ≠ portfolio returns** — overlapping mean forward returns
  are not CAGR; concurrency must be accounted.

## 5. Gotchas most relevant to v0's relationship engine

- **Sector attribution overclaim (§8.12):** stale/missing sector ETF inputs let
  market outperformance wear a sector-independent label. v0 rule: sector data
  fresh or the label is dishonest.
- **Rank universe is part of the strategy (§8.11, §10.5):** a collapsed
  universe (6 names) made the 0.85 rank threshold admit only the top name.
  Universe freshness is a correctness property, not ops hygiene.
- **Timestamps ≠ availability (§10.4):** bar labels (midnight/04:00 UTC) aren't
  availability times. Use session identity + known-at timestamps.
- **Residual arrays aligned by length, not timestamp (§10.6):** missing dates
  can misalign stock vs ETF returns in the original engine.
- **Benchmark identity must travel with the result (§3.6):** a SPY fallback is
  market-only, not a sector residual, even in the same fields.
- **v0 stays read-only on ledgers** (maturity-watchdog rule: reports yes,
  ledger writes no).

## 6. Known code gaps (do not build on these without repair)

- **Outcome resolver preservation gap (§10.2, CODE-VERIFIED):** reruns rebuild
  from the observation ledger and can recompute previously resolved rows.
  Preflight + regression-tested preservation contract required before any write.
- **Ghost five-bar terminal state (§10.7, CODE-VERIFIED):** rows marked MATURE
  at 5 bars never receive 10/20/30-bar outcomes.
- **Return-unit inference by magnitude is unsafe (§10.10):** parse by declared
  schema, not magnitude.
- **"Delay-adjusted" = flat 5bp deduction (§10.11),** not a real delayed-entry sim.
- **Ghost CLI `--write` vs function default `dry_run=False` (§10.8):**
  importing the function is not read-only.
- **Leakage audit is metadata/name checks (§5.5),** not a formal PIT proof.
- **16 modules claimed, 15 files recovered (§5.1)** — flagged, not verified.

## 7. Discarded shortcuts (§10.22)

Do not repeat: "all tests pass ⇒ audit trustworthy" · "7 positives ⇒ strong
evidence of edge" · "fixed bp deduction ⇒ delay-robust" · "research engine 90%
complete." Tests can go green without the defect fixed (§10.15) — require exact
command, commit, and collected/selected/passed/failed/skipped/deselected counts.

## 8. Durable principle

> Preserve the original experiment, verify the data and comparison being used,
> make missing evidence visible, and never let a favorable label substitute for
> a reproducible result.

## 9. Safe next steps (from handoff §9.8, still valid)

1. Reconcile repo ↔ VPS state (branch, commit, ledger hashes)
2. Review resolver preservation before another write
3. Verify July cohort windows; backfill real missing sessions
4. Verify backup + independently stored decryption key
5. Controlled resolution of the 6 pending only, with row-level diff
6. Re-run audit with labeled return conventions and matched windows
7. Fix ghost multi-horizon progression
8. Keep paid launch blocked
