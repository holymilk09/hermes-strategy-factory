#!/usr/bin/env python3
"""
Ledger preservation verifier — Strategy Factory forward ledgers (P0, 2026-10-14).

Compares a BEFORE snapshot of a forward ledger with the AFTER file produced by a
scan/resolve run and enforces the QC preservation contract:

  - AFTER is a valid CSV with the frozen FIELDS header, observation_ids unique.
  - No observation_id present in BEFORE is lost in AFTER.
  - Rows already RESOLVED in BEFORE are byte-identical in AFTER (all fields).
  - A PENDING row may only stay identical or transition to RESOLVED, and a
    resolved transition must have ALL outcome fields populated (outcome_date,
    outcome_close, outcome_return_pp, spy_return_pp, excess_vs_spy_pp) and must
    not alter any non-outcome field (signal data, hypothesis, sent_to_broker).
  - New rows in AFTER are allowed only with --allow-new-rows (scan runs); a
    resolve-only run must not add rows.

Usage:
  verify_ledger_preservation.py BEFORE.csv AFTER.csv [--allow-new-rows]

Exit code 0 = PASS, 1 = FAIL (details printed). Research only; reads only.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys

# Frozen ledger column order — must match momentum_ret5d_ma50_scanner.FIELDS.
FIELDS = ["observation_id", "hypothesis", "signal_date", "symbol", "signal_close",
          "ret_5d", "close", "ma50", "close_above_ma50", "outcome_date",
          "outcome_close", "outcome_return_pp", "outcome_status", "spy_return_pp",
          "excess_vs_spy_pp", "created_at", "sent_to_broker"]

OUTCOME_FIELDS = ["outcome_date", "outcome_close", "outcome_return_pp",
                  "outcome_status", "spy_return_pp", "excess_vs_spy_pp"]


def load(path: pathlib.Path) -> tuple[list[str] | None, list[dict]]:
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("before", type=pathlib.Path)
    ap.add_argument("after", type=pathlib.Path)
    ap.add_argument("--allow-new-rows", action="store_true",
                    help="permit observation_ids in AFTER that are not in BEFORE (scan runs)")
    args = ap.parse_args()

    errors: list[str] = []
    b_fields, before = load(args.before)
    a_fields, after = load(args.after)
    if a_fields != FIELDS:
        errors.append(f"AFTER header mismatch: {a_fields}")
    if b_fields != FIELDS:
        errors.append(f"BEFORE header mismatch: {b_fields}")

    b_by_id = {r["observation_id"]: r for r in before}
    a_by_id = {r["observation_id"]: r for r in after}
    if len(a_by_id) != len(after):
        errors.append(f"AFTER has duplicate observation_ids ({len(after) - len(a_by_id)} dupes)")
    if len(b_by_id) != len(before):
        errors.append("BEFORE has duplicate observation_ids")

    lost = set(b_by_id) - set(a_by_id)
    if lost:
        errors.append(f"{len(lost)} observation_id(s) lost, e.g. {sorted(lost)[:3]}")
    new = set(a_by_id) - set(b_by_id)
    if new and not args.allow_new_rows:
        errors.append(f"{len(new)} new observation_id(s) appeared in a run that must not add rows")

    n_preserved = n_transitioned = n_unchanged = 0
    for oid, brow in b_by_id.items():
        arow = a_by_id.get(oid)
        if arow is None:
            continue
        if brow["outcome_status"] == "RESOLVED":
            if arow != brow:
                diff = [k for k in FIELDS if arow.get(k) != brow.get(k)]
                errors.append(f"RESOLVED row {oid} ({brow['symbol']} {brow['signal_date']}) "
                              f"was modified in fields {diff} — preservation violated")
            else:
                n_preserved += 1
        elif arow["outcome_status"] == "RESOLVED":
            for k in FIELDS:
                if k not in OUTCOME_FIELDS and arow.get(k) != brow.get(k):
                    errors.append(f"row {oid} changed non-outcome field {k} during resolution")
            for k in OUTCOME_FIELDS:
                if k != "outcome_status" and not arow.get(k):
                    errors.append(f"row {oid} resolved with empty {k} — incomplete resolution")
            n_transitioned += 1
        else:
            if arow != brow:
                diff = [k for k in FIELDS if arow.get(k) != brow.get(k)]
                errors.append(f"PENDING row {oid} mutated in fields {diff} without resolving")
            else:
                n_unchanged += 1

    if errors:
        print(f"FAIL: {args.after} vs {args.before}")
        for e in errors[:20]:
            print(f"  - {e}")
        return 1
    print(f"PASS: {args.after.name}: {len(after)} rows "
          f"({n_preserved} resolved preserved, {n_transitioned} newly resolved, "
          f"{n_unchanged} pending unchanged, {len(new)} new rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
