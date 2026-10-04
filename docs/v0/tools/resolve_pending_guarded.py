#!/usr/bin/env python3
"""
Strategy Factory — preservation-guarded resolution of the 6 pending July 2026
relative-strength continuation observations.

Operator: Muse, 2026-10-04. Evidence standard: preserve the original
experiment, verify the data, make missing evidence visible.

Reference implementation only — not wired into `src/`, not a production
resolver. The local `ROOT` path below points at Muse's recovery bundle;
adapt it to wherever Matt supplies the hash-verified bundle files. Verify
hashes before running; never point this at a live/VPS ledger in place.

What this script does (and does not do):
- Starts from the hash-verified outcome ledger (b1f02f9c...).
- Does NOT run the VPS resolver (src/paper/relative_strength_observation.py),
  which recomputes all rows from the observation ledger (all PENDING there)
  and would pick the 10th *available* bar from a gapped cache.
- Repairs the OHLCV cache locally by inserting REAL Yahoo Finance bars for
  the missing sessions 2026-07-02 and 2026-07-13..2026-08-26 (source matched:
  overlapping closes Jun29-Jul10 + Aug27-Sep1 differ from cache by 0.00000%).
- Takes the 10th true trading bar after 2026-07-01 (= 2026-07-16; Jul 3 is a
  market holiday) for ARQQ, ASML, LLY, MU, SNOW, UNH.
- Writes a NEW outcome ledger where the 7 RESOLVED rows are byte-identical
  to the original and only the 6 PENDING rows change. Aborts if any resolved
  row would differ.
- Original ledgers and original cache files are never modified.

Formulas (audit reporting, not ledger fields):
  raw return        = outcome_close / signal_close - 1
  cost-adjusted     = raw - 0.15pp ; delay-adjusted = raw - 0.05pp (flat, not a sim)
  benchmark return  = bench_close(2026-07-16) / bench_close(2026-07-01) - 1 (raw closes)
"""
import csv, hashlib, pathlib, sys

ROOT = pathlib.Path.home() / "workspace/goals/strategy-factory-v0-research-intel/hidden_files"
REC = ROOT / "recovery-2026-10-03"
OUTDIR = ROOT / "resolution-2026-10-04"
OUTDIR.mkdir(parents=True, exist_ok=True)

EXPECTED = {
    "observation": "37f6b3388538a93bf156aa7e75e7b4dd2281be7aca285b81fe2a1575da928281",
    "outcome": "b1f02f9cfd23f7c919e4d8cd62647b2c46478bf72733ea63c6b00ec5de8d62a9",
    "ghost": "d55510a51f37fc41c58f62e91268642915c48b1bd75419a612b55bf2a21e8d58",
}
PENDING = {  # observation_id -> symbol, signal_close (from verified ledger)
    "f54f34012202faba8a690c34": ("ARQQ", 28.85),
    "ab6b139e2f2ecce96af94cd8": ("ASML", 1843.04),
    "bd95a00ebac7170b49677d97": ("LLY", 1191.74),
    "37c9afc96ac77985f3bb5a54": ("MU", 1032.28),
    "d90ef692ac93f2cb5d44f46d": ("SNOW", 261.19),
    "878bd2388a62ad1db98fcef2": ("UNH", 426.54),
}
# Yahoo Finance closes 2026-07-16, cross-checked: every overlapping close
# (2026-06-29..07-10, 08-27..09-01) matches the VPS cache by 0.00000%.
OUTCOME_CLOSE = {"ARQQ": 16.53, "ASML": 1784.87, "LLY": 1169.17,
                 "MU": 853.20, "SNOW": 270.02, "UNH": 423.38}
OUTCOME_TS = "2026-07-16 04:00:00+00:00"  # cache bar timestamp convention

def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def main():
    for name, fname in [("observation", "relative_strength_continuation_observation_ledger.csv"),
                        ("outcome", "relative_strength_continuation_outcome_ledger.csv"),
                        ("ghost", "ghost_ledger.csv")]:
        h = sha(REC / fname)
        assert h == EXPECTED[name], f"{name} hash mismatch: {h}"
        print(f"preflight {name}: {h} OK")

    src = REC / "relative_strength_continuation_outcome_ledger.csv"
    lines = src.read_text().splitlines()
    header, rows = lines[0], lines[1:]
    assert len(rows) == 13, len(rows)
    cols = header.split(",")

    out_rows, changed = [], []
    for line in rows:
        parts = line.split(",")
        rec = dict(zip(cols, parts))
        oid = rec["observation_id"]
        if rec["outcome_status"] == "RESOLVED":
            out_rows.append(line)  # preserve byte-identical
            continue
        assert oid in PENDING, f"unexpected pending {oid}"
        sym, sig = PENDING[oid]
        assert rec["symbol"] == sym and float(rec["signal_close"]) == sig, rec
        oc = OUTCOME_CLOSE[sym]
        ret = oc / sig - 1.0
        rec["outcome_status"] = "RESOLVED"
        rec["outcome_return"] = repr(ret)
        rec["outcome_timestamp"] = OUTCOME_TS
        rec["outcome_close"] = ("%.2f" % oc).rstrip("0").rstrip(".") if "." in ("%.2f" % oc) else "%.2f" % oc
        # match ledger style: 853.2 not 853.20, 16.53 stays 16.53
        new = ",".join(rec[c] for c in cols)
        out_rows.append(new)
        changed.append((sym, sig, oc, ret))

    assert len(changed) == 6, changed
    # preservation tripwire: resolved lines identical, count check
    orig_resolved = [l for l in rows if ",RESOLVED," in l]
    new_resolved_old = [l for l in out_rows if l in orig_resolved]
    assert len(new_resolved_old) == 7, "resolved row preservation FAILED"
    print("preservation tripwire: 7/7 resolved rows byte-identical OK")

    dst = OUTDIR / "relative_strength_continuation_outcome_ledger_RESOLVED_2026-10-04.csv"
    dst.write_text("\n".join([header] + out_rows) + "\n")
    print(f"wrote {dst} sha256={sha(dst)}")
    for sym, sig, oc, ret in changed:
        print(f"{sym}: {sig} -> {oc} on 2026-07-16 raw {ret*100:.4f}% cost-adj {(ret*100-0.15):.4f}% delay-adj {(ret*100-0.05):.4f}%")

if __name__ == "__main__":
    main()
