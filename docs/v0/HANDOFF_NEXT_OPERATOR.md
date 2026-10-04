# Strategy Factory — Handoff for the Next Operator (start here)

Last updated: 2026-10-04 by Muse. Branch: `v0-research-intel`.
Canonical research branch: `trust-calibration-working` @ `1f1a238eb8c17f2340699ed6d6a30017fe3eeb13` — do not treat `main` as latest.

If you are a new LLM/operator picking this up: you do NOT need Hermes or the VPS. Everything required was recovered, hash-verified, and is held by Matt / Muse locally. Ask Matt for the recovery bundle files and verify them against the hashes in §2 before doing anything. Do not reconstruct ledger rows from chat history. Do not run the VPS resolver.

The QC reference (`QC_CONTINUITY_2026-10-04.md`) is standing guidance for consistency, not scripture: if code-verified evidence or a better method contradicts it, follow the better evidence and log the deviation there (§9).

## 1. Current canonical state (2026-10-04)

- Relative-strength continuation: **13 observations, 13 resolved, 0 pending.**
  Cohorts: 2026-05-20 ×6, 2026-06-05 ×1 (MRVL), 2026-07-01 ×6 (ARQQ, ASML, LLY, MU, SNOW, UNH).
  Full record: mean **+11.4930%**, hit rate **61.54%** (8/13) at the 10-bar horizon.
  July cohort alone: mean **−10.4103%**, 1/6 winners. Maturity ≠ edge; this is a forward observation record, not a validated strategy, not portfolio returns.
- Original residual mean-reversion: frozen, `CONTROLLED_RESEARCH_CANDIDATE_EVENT_BLOCKED`, standalone_alpha: false. Separate lineage — never merge the two.
- Ghost ledger: 159 rows (141 PENDING / 18 MATURE). Multi-horizon progression after MATURE is a known open defect — do not assume 10/20/30-bar ghost outcomes are populated by a 5-bar MATURE stamp.
- Production / live / broker / shadow: **BLOCKED** on all tracks. No authorization in this repo changes that.
- Edge Sheet: packaging exists ($5/mo founding concept); paid launch blocked. Do not make performance claims.

## 2. Recovered data bundle (held locally, NOT in git — by design)

Ledgers and caches are not committed to git. Verify any copy you receive:

- observation ledger — sha256 `37f6b3388538a93bf156aa7e75e7b4dd2281be7aca285b81fe2a1575da928281` (13 rows)
- outcome ledger (pre-resolution, 7/6) — `b1f02f9cfd23f7c919e4d8cd62647b2c46478bf72733ea63c6b00ec5de8d62a9`
- outcome ledger (resolved 2026-10-04, 13/0) — `9320d53cad242a2c155ef356289d8d77cc5b9b627b635db32bb89a9fcd2dddd7`
- ghost ledger — `d55510a51f37fc41c58f62e91268642915c48b1bd75419a612b55bf2a21e8d58` (159 rows)
- OHLCV cache (8 files, `<SYM>_1D.csv`): ARQQ `993972f0…`, ASML `b785e648…`, LLY `8783dc06…`, MU `5140b789…`, SNOW `fe27205f…`, UNH `e807eb3b…`, SPY `77695613…`, QQQ `28272842…` (full hashes in RECOVERY_2026-10-04.md)
- Encrypted backups (ciphertext only; keys are NOT in git, NOT in chat — Matt holds key custody off-VPS): phase6m `fbaa3ba7…`, phase7c `867f6e92…`, phase7d `f5aec2bd…`

If a hash does not match, STOP. Do not "fix" the file. Report the mismatch.

## 3. Before you write anything (QC gate)

Read, in order: this file → `QC_CONTINUITY_2026-10-04.md` → `HANDOFF_DIGEST.md` → `RECONCILIATION.md` → `RESOLUTION_2026-10-04.md`.

Then, for any ledger-affecting work:
1. Establish branch, HEAD, cohort identity, expected counts. Wrong cohort/path/HEAD = stop.
2. Hash all ledgers before work. Hash again after any read-only work — read-only must not mutate.
3. Never edit a ledger in place. Produce a new file, row-level diff against the original, and a preservation check: previously resolved rows byte-identical.
4. Do not run `scripts/update_relative_strength_observation_outcomes.py` / `src/paper/relative_strength_observation.py:resolve_observation_outcomes` on a live ledger: it rebuilds from the observation ledger (all PENDING there) and picks the 10th *available* bar — on a gapped cache it silently shifts the economic window. Use a guarded, cohort-specific procedure (example: `tools/resolve_pending_guarded.py` in this folder).
5. Maturity = 10 completed future bars after the signal, signal bar excluded, settled closes only. Elapsed time is not maturity. A missing expected session blocks resolution until real bars are backfilled — never skip the session and slide the window.
6. Prices are raw closes (cache `close` column). Cost-adjusted = raw − 0.15pp, delay-adjusted = raw − 0.05pp, audit/reporting only — flat deductions, not a delay simulation, and not ledger fields.
7. Keep per-observation values separate from cohort aggregates. The second-MRVL error was exactly that confusion.
8. Run the core tests and report exact counts (see RESOLUTION_2026-10-04.md for the 2026-10-04 local run and why clean-tree counts differ from the retained VPS counts). "All tests pass" without scope and counts is not evidence.
9. Evidence labels on everything: IMPLEMENTED—CODE VERIFIED / IMPLEMENTED—OPERATOR REPORTED / PLANNED / BLOCKED / HISTORICAL / RECONSTRUCTED-UNCONFIRMED. No bare "done/working."
10. No commits/pushes of ledger CSVs, cache CSVs, candidate-artifact CSVs, or encrypted backups. Docs and scripts only.

## 4. Traps (learned the hard way — do not repeat)

- Merging residual mean-reversion with relative-strength continuation.
- Reading `phase28a_weak_pass` as a per-stock confidence score (it is lineage acceptance).
- Confusing the two MRVL observations (2026-05-20: +69.40%; 2026-06-05: +16.85%).
- Accepting a plausible report about the wrong cohort (the rejected CONFIRM/CONTRADICT table: GOOGL/META/NVDA/TSLA/AMD/AAPL is not the approved cohort).
- Modifying valid ledgers to satisfy a stale manifest/test expectation. Repair the expectation.
- Interpreting filter lift (accepted vs ghost) as proof of filter efficacy — cohorts/windows were unmatched; descriptive only.
- Resurrecting the trend-extension filter — it failed the final random-pruning gate and is in the graveyard.
- Assuming sector/residual labels are honest when sector ETF inputs are stale, or that a rank threshold means the same thing in a collapsed universe.
- Return units: normalize before aggregating (fractions vs percentage points caused the −6.66pp → +23.30pp correction).

## 5. Open gaps (visible, not hidden)

- `hypothesis_registry.csv` (7 rows) contents — file still only on VPS at `reports/strategy_factory/hypothesis_registry.csv`; do not reconstruct rows.
- Ghost multi-horizon progression after MATURE (≥5 bars).
- Resolver preservation contract in `src/paper/relative_strength_observation.py` — the guarded script is a workaround, not a src fix. A src fix needs its own preflight + regression test and Matt's approval (frozen scope).
- Full test suite on a clean tree does not reproduce retained VPS counts (missing untracked scripts on VPS; environment-hardcoded paths). Documented, not repaired.
- FMP event blocker still needs an FMP API key (not in git/chat).
- Decision pending Matt: whether the July cohort result changes the lineage assessment, and whether to re-run the audit with matched windows (handoff §9.8 step 6).

## 6. Standing principle

> Preserve the original experiment, verify the data and comparison being used, make missing evidence visible, and never let a favorable label substitute for a reproducible result.
