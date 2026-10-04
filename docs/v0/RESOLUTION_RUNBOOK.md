# Controlled Resolution Runbook — the 6 pending July observations

> **2026-10-04 CORRECTION — this runbook has been executed and is now historical.**
> The July cohort was resolved on 2026-10-04 by Muse locally; see `RESOLUTION_2026-10-04.md` for the executed procedure and results (all 13 resolved, 0 pending).
> Corrections to facts assumed below: pending observation IDs are **hex hashes**, not `RSC-20260701-…`; cache files are named `<SYM>_1D.csv`; the VPS cache has a Jul 11→Aug 26 gap plus a missing Jul 2, so "complete" cache must mean *expected-session* completeness — a missing session blocks resolution until real bars are backfilled (§6 of the QC record; available-bar counting is forbidden).
> Do NOT re-run this runbook against the resolved ledger. For any future cohort, follow the guarded pattern in `tools/resolve_pending_guarded.py` and the QC gate in `HANDOFF_NEXT_OPERATOR.md` §3.

Resolves the pending cohort (ARQQ, ASML, LLY, MU, SNOW, UNH — signal
2026-07-01, IDs `RSC-20260701-007` … `RSC-20260701-012`) **without**
recomputing or altering the 7 already-resolved rows.

Run ONLY after `EXTRACTION_CHECKLIST.md` is complete and ledger hashes verify.
VPS or any machine with the repo at `1f1a238` and the canonical cache.

## Known defect this runbook guards against

`scripts/update_relative_strength_observation_outcomes.py` calls
`resolve_observation_outcomes()`, which recomputes **all** rows from the
current cache — it does not preserve previously resolved rows. A naive rerun
can silently rewrite history (code-verified in `RECONCILIATION.md`). Every
phase below exists to make that failure visible before it becomes permanent.

## Phase 0 — Preflight

```bash
cd ~/hermes-strategy-factory
git rev-parse HEAD          # must be 1f1a238eb8c17f2340699ed6d6a30017fe3eeb13
git status --short          # must be clean
python -c "import pandas, numpy; print('deps ok')"
```

Snapshot before any write:

```bash
TS=$(date +%Y%m%d_%H%M%S)
mkdir -p /tmp/sf-pre-resolve-$TS
cp data/paper_observation/relative_strength_continuation_observation_ledger.csv /tmp/sf-pre-resolve-$TS/
cp data/paper_observation/relative_strength_continuation_outcome_ledger.csv     /tmp/sf-pre-resolve-$TS/
sha256sum data/paper_observation/*.csv | tee /tmp/sf-pre-resolve-$TS/pre_hashes.txt
```

STOP if: wrong commit, dirty tree, or hashes don't match the §6 anchors in
`RECOVERY.md`.

## Phase 1 — Maturity watchdog (read-only)

```bash
python scripts/show_relative_strength_maturity_watchdog.py
```

This writes `reports/strategy_factory/relative_strength_maturity_watchdog.md`
and `.json`. Inspect the per-symbol lines. Required for proceed:

- All six pending symbols show `mature=true`, `future_bars=10`,
  `bars_remaining=0`.
- `ready_for_outcome_update=true`, `all_mature=true`.

STOP if any symbol shows fewer than 10 bars or `mature=false`. "Enough time
has passed" is not maturity — the watchdog's bar count is.

## Phase 2 — Cache window audit (the July 2 question)

For each of ARQQ, ASML, LLY, MU, SNOW, UNH, print the actual trading dates
the resolver will use as the 10 future bars:

```bash
python - <<'EOF'
from pathlib import Path
import pandas as pd
root = Path('.')
for sym in ["ARQQ","ASML","LLY","MU","SNOW","UNH"]:
    p = root/"data"/"cache"/"ohlcv_1d"/f"{sym}.csv"
    df = pd.read_csv(p)
    ts = pd.to_datetime(df.iloc[:,0])
    after = ts[ts > pd.Timestamp("2026-07-01")].dt.date.astype(str).tolist()[:10]
    print(sym, len(after), after)
EOF
```

Decision point — do not skip it:

- If every symbol's 10 dates run **2026-07-02 → 2026-07-16**: window is clean,
  proceed.
- If **2026-07-02 is missing** and the 10th bar is **2026-07-17**: the
  resolver is silently extending the economic window. Two options, chosen
  explicitly and recorded: (a) repair/backfill July 2 first, then restart
  this runbook; or (b) accept July 17 as the 10th *available* bar and record
  that choice in the ops log. What is forbidden is saying nothing and
  letting the shift pass unnoticed.
- If any symbol has fewer than 10 bars: classify that observation
  `INSUFFICIENT_DATA`, resolve the rest, record it. Do not force it.

## Phase 3 — Preservation-guarded resolution

```bash
python scripts/update_relative_strength_observation_outcomes.py
```

It rewrites
`data/paper_observation/relative_strength_continuation_outcome_ledger.csv`
in place and writes
`reports/strategy_factory/relative_strength_forward_observation_outcome_report.md`.

Immediately diff resolved history:

```bash
python - <<'EOF'
from pathlib import Path
import pandas as pd
pre  = pd.read_csv("/tmp/sf-pre-resolve-XXX/relative_strength_continuation_outcome_ledger.csv")
post = pd.read_csv("data/paper_observation/relative_strength_continuation_outcome_ledger.csv")
old_ids = set(pre["observation_id"])
for _, r in pre.iterrows():
    oid = r["observation_id"]
    match = post[post["observation_id"] == oid]
    assert len(match) == 1, f"{oid}: row count changed"
    assert match.iloc[0].equals(r), f"{oid}: RESOLVED ROW REWRITTEN"
new_ids = set(post["observation_id"]) - old_ids
print("resolved rows preserved:", len(old_ids))
print("newly resolved:", sorted(new_ids))
EOF
```

(replace `XXX` with the `$TS` from Phase 0.)

STOP conditions — restore from `/tmp/sf-pre-resolve-$TS/` and report if:

- Any of the 7 previously resolved rows changed in any field
  (`RESOLVED ROW REWRITTEN`).
- More or fewer than 6 new rows appeared.
- A new row's `outcome_date` falls outside the window established in Phase 2.

## Phase 4 — Acceptance

- Outcome ledger: 13 rows, 0 pending.
- Watchdog re-run: `all_mature=true`.
- Record post-run `sha256sum` of both ledgers in the ops log alongside the
  Phase 0 pre-hashes, the Phase 2 window decision, and this runbook's name.
- Ledgers are NOT committed to git (design rule). The ops log entry is the
  durable record.

## Standing boundaries (unchanged)

- Research only. Production / live / broker / shadow: BLOCKED.
- This runbook changes no thresholds, no gate definitions, no ghost-ledger
  semantics, no Edge Sheet packaging.
- The CONFIRM/CONTRADICT table from the noncanonical report is not an input
  here and must not be used to cross-check or overwrite canonical rows.
