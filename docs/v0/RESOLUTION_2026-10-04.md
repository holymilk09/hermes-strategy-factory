# Strategy Factory — July Cohort Resolution Report
Date: 2026-10-04 | Operator: Muse | Evidence standard: preserve the original experiment, verify the data, make missing evidence visible.

## Result (CODE VERIFIED)
The 6 pending relative-strength continuation observations (signal 2026-07-01) are resolved to the 10th true trading bar, **2026-07-16** (2026-07-03 was a market holiday; bars: Jul 2, 6, 7, 8, 9, 10, 13, 14, 15, 16).

- Arqit (ARQQ) — 28.85 → 16.53 — raw **-42.7036%** — cost-adj -42.8536% — delay-adj -42.7536%
- ASML Holding (ASML) — 1843.04 → 1784.87 — raw **-3.1562%** — cost-adj -3.3062% — delay-adj -3.2062%
- Eli Lilly (LLY) — 1191.74 → 1169.17 — raw **-1.8939%** — cost-adj -2.0439% — delay-adj -1.9439%
- Micron (MU) — 1032.28 → 853.20 — raw **-17.3480%** — cost-adj -17.4980% — delay-adj -17.3980%
- Snowflake (SNOW) — 261.19 → 270.02 — raw **+3.3807%** — cost-adj +3.2307% — delay-adj +3.3307%
- UnitedHealth (UNH) — 426.54 → 423.38 — raw **-0.7408%** — cost-adj -0.8908% — delay-adj -0.7908%

Cost-adjusted = raw − 0.15pp; delay-adjusted = raw − 0.05pp (flat audit deductions, NOT a delayed-entry simulation — HISTORICAL rule from ChatGPT QC record).

Benchmarks, same window (raw closes, 2026-07-01 → 2026-07-16): SPY (SPY) +0.6651%, Nasdaq-100 (QQQ) −2.6518%. July cohort vs SPY: only SNOW positive. vs QQQ: SNOW, LLY, UNH above benchmark despite negative/flat raw for LLY/UNH.

## Updated record
- July cohort: n=6, mean **−10.4103%**, winners 1/6
- Full record: **13 resolved / 0 pending**, mean **+11.4930%**, hit rate **61.54%** (8/13)
- Prior 7 resolved (May 20 cohort mean +32.5039%, plus MRVL Jun 5 +16.8482%) unchanged — their ledger rows are byte-identical to the recovered original (preservation tripwire passed, diff shows exactly 6 lines changed).

## How the data was verified (CODE VERIFIED)
1. Preflight hashes: observation 37f6b338…, outcome b1f02f9c…, ghost d55510a5… — all matched anchors before work.
2. Original VPS cache is unusable for resolution: 2026-07-02 missing and 2026-07-11→08-26 gap in all 8 files; only 9 bars after signal; the resolver picks the 10th *available* bar and would have silently landed ~2026-09-01.
3. Repair source: Yahoo Finance history (auto_adjust=False) — the cache's own source family. Every overlapping close (2026-06-29→07-10 and 08-27→09-01, 13–14 dates per symbol) matched the cache by **0.00000%** for ARQQ, ASML, LLY, MU, SNOW, UNH, SPY, QQQ. Prices are raw closes (cache `close` column; resolver `load_ohlcv` uses raw close, dividends/splits ignored — consistent with the 7 prior resolutions, which recompute exactly from raw closes).
4. Session list from repaired data: Jul 2, 6, 7, 8, 9, 10, 13, 14, 15, 16 = 10 bars. Jul 16 closes above are from that repaired, cross-checked series.
5. New ledger: `relative_strength_continuation_outcome_ledger_RESOLVED_2026-10-04.csv`, sha256 9320d53cad242a2c155ef356289d8d77cc5b9b627b635db32bb89a9fcd2dddd7. All 13 outcome_returns recompute exactly from outcome_close/signal_close. Broker fields empty for all rows; IDs unique (13). Originals untouched — new file lives alongside, not in place of, the recovered ledger.
6. Code-path tests at 1f1a238 (clean worktree, pytest 9.1.1 / pandas 3.0.6): core files test_relative_strength_observation.py + test_relative_strength_continuation.py + test_maturity_watchdog.py = **11 passed**. Full source-only suite: 394 passed, 11 failed, 88 deselected, plus 1 collection error — failures classified as environment-only (hardcoded /opt/data/.venv/bin/python paths, Alpaca calendar network calls, and tests/test_price_volume_capitulation_v2.py importing a script absent from the clean tree at 1f1a238; the VPS had untracked scripts). Retained historical result (OPERATOR REPORTED, Jul 9): 409 passed / 88 deselected source-only, 497 full. Clean-tree count differs — do not treat retained counts as reproduced.

## QC reconciliation with ChatGPT record (2026-10-04)
- Confirmed and applied: 13 approved = manifest, not success; weak_pass = lineage acceptance; 10 completed future bars, signal bar excluded; elapsed time ≠ maturity; cost/delay flat deductions; per-observation values kept separate from cohort aggregates (July mean is reported as a cohort aggregate and never substituted into a single-name block); wrong-cohort reports rejected by identity; no manual in-place ledger edits — resolution is a new file with row-level diff.
- GAPs in ChatGPT record closed by code/data here: raw (not adjusted) close convention; outcome_timestamp = cache bar timestamp (04:00 UTC); ledger stores raw return/close only (cost/delay are audit/reporting calculations); missing-session policy — a missing expected session blocks resolution until real bars are backfilled, available-bar substitution is forbidden (we backfilled real Jul 2, we did not skip it).
- Still GAP, not resolved by this work: hypothesis_registry.csv contents (7 rows — file still on VPS at reports/strategy_factory/hypothesis_registry.csv); ghost multi-horizon progression after MATURE at ≥5 bars; resolver preservation contract in src (our guarded script is the workaround, not a fix to src/paper/relative_strength_observation.py).

## Interpretation limits
- This is 13 forward observations, not a validated strategy. July cohort (1/6, −10.41% mean) materially weakens the May/June picture; maturity ≠ edge; candidate mean returns ≠ portfolio returns (overlap/concurrency not accounted); no production, live, broker, or shadow authorization follows from this. Production/live/broker/shadow remain BLOCKED.
- Next QC step if pursued: re-run the audit with labeled return conventions and matched windows (handoff §9.8 step 6), and decide explicitly whether the July cohort changes the lineage assessment — that is Matt's call, not an automatic promotion or kill.

Files: resolve_pending_guarded.py, build_repaired_cache.py, cache_repaired/ (8 repaired caches), this report — in hidden_files/resolution-2026-10-04/. Originals in hidden_files/recovery-2026-10-03/ unchanged (hashes re-verified after work).
