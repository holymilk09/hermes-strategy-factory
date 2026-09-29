# Strategy Factory Recovery Record — 2026-09-29

How the pre-gateway-collapse research state can be recovered, what conversation
history actually contains, and what remains genuinely missing.

Evidence labels follow the project reporting standard. Everything sourced from
ChatGPT's conversation history below is `IMPLEMENTED — OPERATOR REPORTED`
(conversation history), not code-verified.

## 1. Source

- On 2026-09-29 Matt asked ChatGPT (which holds the full Strategy Factory
  conversation history) a targeted gap questionnaire: the six missing resolved
  outcome values, ghost ledger contents, anything post-July-8, and backup/key
  locations.
- ChatGPT's reply explicitly separated exact retained values from gaps and
  refused to reconstruct missing rows.
- The full reply is preserved in the chat record; this file records the
  recovery-relevant facts, the gap analysis, and the ordered recovery plan.

## 2. Newly recovered: all seven resolved outcome values (COMPLETE)

The 2026-05-20 cohort, exact values from the prior audit discussion:

| Symbol | Signal close | Outcome close | Raw 10d | Cost-adj | Delay-adj | Bench-rel |
|---|---|---|---|---|---|---|
| AMD  | 447.58 | 523.20 | +16.90% | +16.75% | +16.85% | +13.04% |
| ARM  | 256.73 | 393.44 | +53.25% | +53.10% | +53.20% | +49.40% |
| CRWD | 650.11 | 719.09 | +10.61% | +10.46% | +10.56% |  +6.76% |
| DDOG | 212.24 | 243.60 | +14.78% | +14.63% | +14.73% | +10.93% |
| MRVL | 186.80 | 316.43 | +69.40% | +69.25% | +69.35% | +65.54% |
| SEDG |  56.22 |  73.14 | +30.10% | +29.95% | +30.05% | +26.25% |

Audit snapshot benchmarks: SPY +2.14%, QQQ +3.85%.

Second MRVL (2026-06-05 cohort) cross-checked: signal 263.47 → outcome 307.86
on 2026-06-22, +16.85% raw / +16.70% cost-adj / +16.80% delay-adj.

Verification performed 2026-09-29 (Muse):

- Raw returns recompute exactly from signal/outcome closes (spot-checked all six).
- cost-adjusted = raw − 15 bps; delay-adjusted = raw − 5 bps. Consistent with
  the code-verified constants in `RECONCILIATION.md`.
- ChatGPT confirmed "delay-adjusted" here is the flat 5 bps deduction, NOT a
  true next-bar delayed-entry simulation. Matches the code finding.
- No explicit per-observation delay flags (`DELAY_PASS` / `DELAY_FAIL` /
  `DELAY_FRAGILE`) exist in the retained history — only the numeric
  delay-adjusted values.
- An older compacted value for the second MRVL (295.10 / +12% / June 19) was
  explicitly reconciled in history as stale/incorrect. Canonical is
  307.86 / +16.85% / June 22. This increases confidence the surviving values
  were actively error-checked, not just transcribed.

## 3. Ghost ledger: snapshots recovered, rows NOT recovered

ChatGPT does not hold the full 159-row ledger. What it does hold:

- Early snapshot: 12 ghosts (6 relative-strength rejections + 6
  regime-conditioned). Reasons: `20d_momentum_too_weak` ×5,
  `60d_momentum_too_weak` ×1, `pullback_not_deep_enough` ×6. No outcomes
  matured yet.
- A second early report of 12 relative-strength rejections
  (`20d_momentum_too_weak` ×10, `60d_momentum_too_weak` ×2) — different
  scope/run. Preserved as a separate historical snapshot; NOT merged.
- Six-rejection batch (81 → 87 rows), exact rows: AMD, CRWD, DDOG, SEDG →
  `20d_momentum_too_weak`; ARM, MRVL → `recent_negative_return`.
- First 18 matured ghosts: mean 10d return +6.97%; 6 unexpected winners
  > +5% named (ARM +13.01%, MRVL +47.12%, MRVL +28.15%, MRVL +27.12%,
  AMD +18.28%, ARM +18.89%); 4 expected losers < −5% NOT named (gap).
  One AMD ghost at +4.88% explicitly confirmed below the +5% bucket cutoff.
- Final state: 159 total / 141 PENDING / 18 MATURE / 0 INSUFFICIENT_DATA.
  Ghost hash `d55510a5…e8d58` matches the handoff.
- Filter-lift audit (post unit-fix): accepted mean 30.27pp vs ghost mean
  6.97pp → +23.30pp, labeled "Filter Lift Strong". Explicitly descriptive
  only — cohorts not date-matched, entry conventions differed.

**Biggest unrecoverable gap from conversation history: the full 159-row
ghost ledger.** Counts, batches, and some outcomes survive; row-level
identities do not.

## 4. Post-July-8: nothing new canonical

- The CONFIRM/CONTRADICT table was reproduced exactly (GOOGL/META/NVDA/TSLA
  2026-05-15; AMD/AAPL 2026-06-02; July-1 names pending with values ARQQ
  0.0456, ASML 0.0312, LLY 0.0287, MU 0.0378, SNOW 0.0423, UNH 0.0256).
- Its rejection as noncanonical is confirmed: wrong paths (`/opt/data/...`
  instead of `data/cache/ohlcv_1d/`), wrong script
  (`/opt/data/src/maturity_watchdog.py`), wrong universe (GOOGL/META/NVDA/
  TSLA/AMD/AAPL instead of the canonical cohort). Must NOT be used to
  recreate the canonical outcome ledger.
- No confirmed canonical Phase 7F. Canonical recovery target remains
  **13 observations / 7 resolved / 6 pending** (ARQQ, ASML, LLY, MU, SNOW,
  UNH — signal 2026-07-01).
- Phase 30H/30I were earlier work despite numbering, not post-July-8 activity.

## 5. Encrypted backups and keys

Three encrypted backups reported in the private repo
`holymilk09/hermes-strategy-factory-backups`:

- **Phase 6M** (2026-06-29): release `backup-20260629-120855`, encrypted SHA
  `fbaa3ba7…`. Key at `/opt/data/backups/.phase6m_encryption_key`.
  Off-VPS copy: NOT confirmed.
- **Phase 7C** (2026-07-02): draft release ID 348156695, encrypted SHA
  `867f6e92…`. Key derived from `GITHUB_TOKEN`, stored in `.env`, rotated
  via GitHub. Not a durable independent archival key.
- **Phase 7D** (2026-07-08, most relevant): release
  `backup-phase7d-20260708-164414`, 15,584 bytes, encrypted SHA
  `f5aec2bd…` reported matching local. Key at
  `/opt/data/backups/.phase7d_key` (mode 600). Completion report explicitly
  said **VPS-only (no off-VPS copy)**; the follow-up push report did not
  confirm the key-storage step. Off-VPS copy: NOT confirmed.

Access check 2026-09-29: the deploy key used for this work
(`muse-hsf-deploy`, scoped to `holymilk09/hermes-strategy-factory`) returns
"Repository not found" for the backups repo. Pulling the encrypted backups
requires Matt's own access or a key with that repo's scope.

## 6. Recovery anchors (all match the handoff)

- Git: `trust-calibration-working` @ `1f1a238eb8c17f2340699ed6d6a30017fe3eeb13`
- Manifest: 13 total / 7 resolved / 6 pending
- Observation ledger SHA: `37f6b3388538a93bf156aa7e75e7b4dd2281be7aca285b81fe2a1575da928281`
- Outcome ledger SHA: `b1f02f9cfd23f7c919e4d8cd62647b2c46478bf72733ea63c6b00ec5de8d62a9`
- Ghost ledger SHA: `d55510a51f37fc41c58f62e91268642915c48b1bd75419a612b55bf2a21e8d58`
- Phase 7D encrypted backup SHA: `f5aec2bd96974ff2119d520784acc0294a070fc936821f44755d2fca8fc867a1`

## 7. Ordered recovery plan

1. **Gateway back on → extract from disk.** Copy
   `data/paper_observation/relative_strength_continuation_observation_ledger.csv`,
   `..._outcome_ledger.csv`, `data/trust_calibration/ghost_ledger.csv`,
   the OHLCV cache manifest, and any key material under `/opt/data/backups/`.
   Verify each file against the anchors in §6. If hashes match, recovery is
   complete — everything below is moot.
2. **If disk is stale/dead → encrypted backups.** Pull the Phase 7D backup
   from the private repo (needs Matt's access). Key hunt, in order: password
   manager, laptop notes, any `.env` copies off the VPS, GitHub token
   rotation history (7C key derivation). Do NOT assume the key survived
   because the push succeeded.
3. **If keys are gone → reconstruct, labeled honestly.** Observation and
   outcome ledgers can be rebuilt to high fidelity from §2 + the handoff
   (all 13 IDs, symbols, dates, signal closes, and all 7 outcome values are
   now known). Label `RECONSTRUCTED / UNCONFIRMED` — reconstruction will NOT
   reproduce the original SHAs, and must never be presented as the original
   record. The 159-row ghost ledger is an accepted loss; rebuild policy TBD
   (re-running ghost generation recreates *a* ledger, not *the* ledger).
4. **Then resolve the 6 pending** under the controlled procedure (preflight,
   preservation of the 7 resolved, row-level diff) — separate runbook, only
   after the ledger state is canonical again.

## 8. What this changes

- Nothing about the v0 research-intelligence branch: it is built from git +
  the handoff and does not depend on the VPS.
- The six missing outcome values are no longer missing from the *knowledge*
  record — only the original ledger files (and their hashes) still need disk
  recovery.
- The ghost ledger remains the one artifact that conversation history cannot
  restore.
