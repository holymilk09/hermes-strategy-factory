# Strategy Factory — Matched-Window Audit: Accepted vs Ghost

Date: 2026-10-05 | Operator: Muse
Question: under identical horizon and return conventions, did the relative-strength continuation filter select better 10-bar outcomes than the names it rejected (ghosts)?

Prior comparison (HISTORICAL, rejected as evidence): accepted mean 30.27pp vs rejected-ghost mean 6.97pp, "lift +23.30pp." That compared unmatched cohorts/windows and, at the time, only the 7 pre-July accepted outcomes. This audit replaces it.

## Method (pre-registered)

- Horizon: 10 completed trading bars after signal, signal bar excluded — same for accepted and ghost.
- Return: outcome_close / signal_close − 1, in percentage points, computed **entirely within one fetched series** (Yahoo Close, `auto_adjust=False`). Cost/delay flat deductions (−0.15pp / −0.05pp) shift both groups equally and do not change any difference; raw returns are reported.
- Data: Yahoo Finance daily closes for all 77 ghost symbols + accepted symbols + SPY/QQQ, fetched 2026-10-05.
- **Split-adjustment finding (important):** Yahoo retroactively split-adjusts historical Close. CRWD split 4:1 on 2026-07-02 (ledger signal 650.11 vs current Yahoo signal close 162.53) and HON had a 0.9535 factor on 2026-06-29. Mixing a ledger (pre-split) signal price with a current Yahoo outcome price creates false returns (a CRWD −72% artifact appeared in the first audit pass and was caught by replication). All returns here use Yahoo signal and outcome closes from the same series.
- Replication before analysis (CODE VERIFIED):
  - All 18 ghost MATURE `outcome_10d` values recompute within 0.005pp of the ghost ledger.
  - All 13 accepted outcomes recompute within 0.01pp of the resolved outcome ledger.
  - Ledger hashes verified before work and unchanged after; no ledger was modified. Audit rows: `audit_rows.csv` (172 rows).

## Results

### Primary: same signal date (true matched window)

**2026-07-01 — the largest matched sample**
- Accepted (ARQQ, ASML, LLY, MU, SNOW, UNH) — n=6, mean **−10.4103%**, median −2.5250%, hit rate 1/6, excess vs SPY −11.0754pp
- Ghost (72 rejected, same date) — n=72, mean **−1.6400%**, median +1.4397%, hit rate 41/72 (56.9%), excess vs SPY −2.3051pp
- **Accepted − ghost = −8.7703pp.** On the only date with a large matched ghost pool, the filter's selections underperformed its rejections.

**2026-06-05 — tiny, descriptive only**
- Accepted — n=1 (MRVL), **+16.8482%**
- Ghost — n=5, mean **+4.6985%**, median +0.6587%
- Difference +12.1497pp on n=1 vs n=5. Not evidence by itself.

Average of the two same-date differences: **+1.6897pp** — effectively no consistent filter lift once date is matched.

### Secondary: pooled, matched horizon only (NOT date-matched — do not quote as lift)

- Accepted — n=13, mean **+11.4930%**, median +10.6105%, hit rate 8/13 (61.5%), excess vs SPY +10.1285pp
- Ghost — n=159, mean **−0.9974%**, median +0.2560%, hit rate 81/159 (50.9%), excess vs SPY +0.0747pp
- Ghost ledger-MATURE subset only — n=18, mean +6.9664% (replicates the historical +6.97%)

The pooled gap (+12.4904pp) is date-confounded: the accepted pool is concentrated in the strong May 20 window, while 136 of 159 ghosts come from May 27 and July 1 broad scans. Sensitivity: accepted excluding the May 20 cohort (June+July, n=7) mean **−6.5162%**. Accepted excluding the single May MRVL +69.40% observation (n=12) mean +6.6679%.

### Quasi-matched: same six symbols, two trading days apart

May 20 accepted vs May 22 ghost, same symbols (AMD, ARM, CRWD, DDOG, MRVL, SEDG), overlapping windows:
- Accepted mean +32.5039% vs ghost (same names, 2 days later) mean +11.9586%
- Every one of the six names did better from the May 20 entry than from May 22. This is consistent with entry timing / a strong momentum window, not proof the filter separated winners from losers — the rejected entries were the *same stocks*.

### By failed gate (ghost pooled, 10-bar recomputed)

- Rejected for `ret_5d_positive` (recent return negative) — n=66, mean **−3.3139%**, hit rate 42.4%. This gate's rejections did perform poorly; the gate looks useful.
- Rejected for `ret_20d_rank` (20d momentum too weak) — n=71, mean **+0.8258%**, median +1.1332%, hit rate 54.9%. These rejections performed fine; the gate did not separate losers.
- Rejected for `close_above_ma50` — n=17, mean +0.2227%, hit rate 64.7%. Small n.
- Rejected for `ret_60d_rank` — n=5, mean −0.4592%. Inconclusive.

July detail supporting the gate split: the July ghosts rejected on `ret_5d_positive` include MRVL −30.78%, ARM −22.36%, AMD −7.38%, SEDG −6.54% — the gate avoided real losers that day — while the accepted July names still lost to the broad rejected pool, driven by ARQQ −42.7036% (excess vs SPY −43.37pp) and MU −17.3480% (−18.01pp).

## Interpretation

- Under matched date + horizon, there is **no consistent filter lift**. The earlier +23.30pp figure does not survive matched-window comparison and should not be used.
- What the record supports: a very strong May 20 entry window (same names did worse 2 days later), a useful-looking `ret_5d > 0` gate, a non-separating `ret_20d_rank ≥ 0.85` gate, and a July accepted cohort that underperformed same-day rejections by 8.77pp.
- What it does not support: a validated edge, a promotion/kill decision on statistics alone, or any production conclusion. n=13 accepted, overlapping names across dates (observations are not independent), two usable matched dates only, and means are outlier-sensitive (MRVL).
- Production / live / broker / shadow remain **BLOCKED**.

## Recommendation to operator (Matt's decision)

Options, in order of evidence support:
1. **Downgrade the lineage to watch-only and keep collecting forward observations** — the filter as a whole has not shown matched-window lift; the `ret_5d` gate may carry whatever value exists.
2. Split the hypothesis: test `ret_5d > 0` (plus price > ma50) without the rank gates as a new, explicitly separate hypothesis — do not silently edit the frozen lineage.
3. Kill the lineage outright — defensible on July, but May's window and the `ret_5d` gate result argue the signal is regime-dependent rather than uniformly absent.

No option is taken automatically. Thresholds, lineage identity, and resolved outcomes stay frozen until Matt decides.

Files: `matched_window_audit.py`, `audit_rows.csv`, `audit_run.log`, `raw_yf/` (78 fetched series) in `hidden_files/audit-2026-10-05/`. Original ledgers unchanged (hashes re-verified after work).
