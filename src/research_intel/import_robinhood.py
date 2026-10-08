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
    ap.add_argument("--cache", default="cache/research_intel/ohlcv")
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
    json.dump(report, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
