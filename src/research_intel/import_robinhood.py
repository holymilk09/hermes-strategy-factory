"""Import saved Robinhood `get_equity_historicals` JSON responses into the local cache.

Usage:
  python -m src.research_intel.import_robinhood --settled-through 2026-10-07 \
      --cache cache/research_intel/ohlcv  response1.json [response2.json ...]

Prints a per-symbol import report (bars, first/last date, sha256 of the written file)
so every import is auditable. Refuses to change already-cached settled closes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date

from .data import CacheStore, parse_robinhood_historicals


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--settled-through", required=True, type=date.fromisoformat)
    ap.add_argument("--cache", default="cache/research_intel/ohlcv_v2")
    ap.add_argument("--raw", nargs="*", default=[],
                    help="saved responses fetched with adjustment_type=none, for the "
                         "corporate-action audit (strongly recommended)")
    a = ap.parse_args(argv)
    store = CacheStore(a.cache)
    report = []
    for fp in a.files:
        with open(fp) as f:
            payload = json.load(f)
        for s in parse_robinhood_historicals(payload, settled_through=a.settled_through):
            if not s.dates:
                report.append({"symbol": s.symbol, "bars": 0, "status": "EMPTY — not written"})
                continue
            p = store.write(s)
            report.append({
                "symbol": s.symbol, "bars": len(s.dates),
                "first": s.dates[0].isoformat(), "last": s.dates[-1].isoformat(),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            })
    if a.raw:
        from .data_quality import adjustment_audit
        raws = {}
        for fp in a.raw:
            with open(fp) as f:
                for s in parse_robinhood_historicals(json.load(f), settled_through=a.settled_through):
                    raws[s.symbol] = s
        q = {}
        for row in report:
            sym = row["symbol"]
            if sym in raws and row.get("bars"):
                au = adjustment_audit(store.raw_series(sym), raws[sym])
                row["adjustment_audit"] = au.status
                if au.quarantine:
                    q[sym] = {"dates": list(au.quarantine), "reason": "INVALID corporate-action "
                              "adjustment step(s): " + ", ".join(f"{x.date} factor {x.factor}"
                                                                for x in au.steps if x.kind == "INVALID")}
                    row["quarantined_sessions"] = len(au.quarantine)
        if q:
            store.write_quarantine(q)
    json.dump(report, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
