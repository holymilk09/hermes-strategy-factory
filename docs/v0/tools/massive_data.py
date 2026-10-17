#!/usr/bin/env python3
"""
Massive data layer — Strategy Factory (built 2026-10-17).

Pulls daily bars from Massive (formerly Polygon.io) through the registered
custom.massive connector helper and writes them as plain OHLCV CSVs
(`Date,Open,High,Low,Close,Volume`) that the other Strategy Factory tools
(scanner cache mode, relationship engine) can read unchanged.

Why this exists: Yahoo Finance data is fine for personal research but its
terms restrict commercial redistribution — the MCP build spec requires a
licensed vendor before any paid distribution. Massive is that vendor.
Massive bars here are split- AND dividend-adjusted (`adjusted=true`, set by
the connector helper). That differs from the Yahoo convention used by the
frozen v1 forward test (split-adjusted only), so:

  - v1 forward ledgers keep resolving on Yahoo until the Oct 2026 verdict.
    Switching a live forward test's price source mid-flight would be a
    methodology change; the parity check (see the goal's hidden_files) is
    the evidence base for any post-verdict switch decision by Matt.
  - New builds (relationship engine, future hypotheses) use Massive.

Auth: this tool never sees the API key. It shells to the connector helper
(`~/workspace/custom-connectors/custom.massive/bin/massive.py`), which holds
the credential through the registered connection. Rate limits follow Matt's
plan; calls are sequential with a small delay, and a 429 stops the run
(partial progress is kept and reported) per the connector doc.

Usage:
  massive_data.py pull SYM [SYM ...] --from 2025-10-01 --to 2026-10-16 --out DIR
  massive_data.py pull --universe-file symbols.txt --from ... --to ... --out DIR
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import subprocess
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

HELPER = pathlib.Path.home() / "workspace/custom-connectors/custom.massive/bin/massive.py"
ET = ZoneInfo("America/New_York")
FIELDS = ["Date", "Open", "High", "Low", "Close", "Volume"]


def fetch_aggs(symbol: str, start: str, end: str) -> list[dict]:
    """Daily bars for one symbol via the connector helper. Raises on API errors."""
    proc = subprocess.run(
        [sys.executable, str(HELPER), "aggs", symbol, start, end],
        capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"helper failed for {symbol}: {proc.stderr.strip()[:300]}")
    payload = json.loads(proc.stdout)
    if payload.get("status") not in ("OK", "DELAYED"):
        raise RuntimeError(f"Massive status {payload.get('status')} for {symbol}")
    return payload.get("results") or []


def bar_date(ms_epoch: int) -> str:
    """Session date (America/New_York) for a Massive daily-bar timestamp."""
    return datetime.fromtimestamp(ms_epoch / 1000, tz=ET).date().isoformat()


def write_cache(out_dir: pathlib.Path, symbol: str, bars: list[dict]) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for b in bars:
        rows.append({
            "Date": bar_date(b["t"]),
            "Open": b["o"], "High": b["h"], "Low": b["l"],
            "Close": b["c"], "Volume": b.get("v", ""),
        })
    rows.sort(key=lambda r: r["Date"])
    path = out_dir / f"{symbol}.csv"
    with open(path, "w", newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def cmd_pull(args) -> int:
    symbols = list(args.symbols or [])
    if args.universe_file:
        symbols += [ln.strip().upper() for ln in
                    pathlib.Path(args.universe_file).read_text().splitlines()
                    if ln.strip() and not ln.startswith("#")]
    symbols = sorted(set(symbols))
    if not symbols:
        print("no symbols given", file=sys.stderr)
        return 2
    ok, empty, failed = [], [], []
    for sym in symbols:
        try:
            bars = fetch_aggs(sym, args.from_date, args.to_date)
        except Exception as e:
            msg = str(e)
            if "429" in msg:
                print(f"RATE LIMITED at {sym}; stopping with partial progress "
                      f"({len(ok)} ok, {len(empty)} empty, {len(failed)} failed)")
                failed.append(sym)
                break
            print(f"  FAIL {sym}: {msg}")
            failed.append(sym)
            continue
        if not bars:
            print(f"  EMPTY {sym}: no bars returned")
            empty.append(sym)
            continue
        n = write_cache(args.out, sym, bars)
        print(f"  {sym}: {n} bars {args.from_date}..{args.to_date}")
        ok.append(sym)
        time.sleep(0.25)
    print(f"pull complete: {len(ok)} ok, {len(empty)} empty, {len(failed)} failed "
          f"-> {args.out}")
    if failed:
        print(f"failed: {failed}")
    if empty:
        print(f"empty: {empty}")
    return 0 if not failed else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pull")
    p.add_argument("symbols", nargs="*", help="tickers to pull")
    p.add_argument("--universe-file", type=pathlib.Path, default=None,
                   help="file with one ticker per line")
    p.add_argument("--from", dest="from_date", required=True, help="YYYY-MM-DD")
    p.add_argument("--to", dest="to_date", required=True, help="YYYY-MM-DD")
    p.add_argument("--out", type=pathlib.Path, required=True, help="cache directory")
    args = ap.parse_args()
    return {"pull": cmd_pull}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
