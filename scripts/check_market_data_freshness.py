#!/usr/bin/env python3
"""PHASE 6J-CALENDAR — Alpaca Calendar Freshness Check.

Read-only script. Does NOT run observation generation cycle.
Does NOT mutate any ledger or strategy state.

Output states:
  DATA_CURRENT
  DATA_STALE_NEEDS_REFRESH
  CALENDAR_UNAVAILABLE
  PROVIDER_BARS_UNAVAILABLE
  CACHE_PATH_MISMATCH
  LEDGER_INTEGRITY_FAIL
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from src.reporting.market_calendar_freshness import check_data_freshness, assert_no_ledger_mutation


def main() -> None:
    result = check_data_freshness(root=ROOT)

    print("=" * 60)
    print("PHASE 6J-CALENDAR — Alpaca Calendar Freshness Check")
    print("=" * 60)
    print()

    if not result.alpaca_calendar_available:
        print(f"Status: {result.status}")
        if result.error:
            print(f"Error: {result.error}")
        print()
        print("Production: BLOCKED")
        print("Live: BLOCKED")
        print("Broker execution: DISABLED")
        print("Shadow orders: DISABLED")
        sys.exit(0 if result.status == "CALENDAR_UNAVAILABLE" else 1)

    print(f"Status: {result.status}")
    print(f"As of UTC: {result.as_of_utc}")
    print()
    print(f"Alpaca calendar entries: {result.calendar_entries}")
    print(f"Latest completed session: {result.latest_completed_session}")
    print(f"Latest session close (ET): {result.latest_completed_session_close}")
    print()
    print(f"Local OHLCV latest session: {result.local_ohlcv_latest_session}")
    print()

    print("--- Required Symbols ---")
    for sym in ["AMD", "ARM", "CRWD", "DDOG", "MRVL", "SEDG"]:
        ld = result.required_latest.get(sym, "N/A")
        flag = "  <<< STALE" if ld and ld < (result.latest_completed_session or "0") else \
               "  <<< MISSING" if ld is None else ""
        print(f"  {sym}: {ld or 'MISSING'}{flag}")

    print()
    print("--- Benchmark Symbols ---")
    for sym in ["SPY", "QQQ"]:
        ld = result.benchmark_latest.get(sym, "N/A")
        flag = "  <<< STALE" if ld and ld < (result.latest_completed_session or "0") else \
               "  <<< MISSING" if ld is None else ""
        print(f"  {sym}: {ld or 'MISSING'}{flag}")

    print()
    if result.stale_symbols:
        print(f"Stale symbols: {', '.join(result.stale_symbols)}")
    if result.missing_symbols:
        print(f"Missing symbols: {', '.join(result.missing_symbols)}")
    if not result.stale_symbols and not result.missing_symbols:
        print("All symbols current — no stale data detected.")

    print()
    print("Production: BLOCKED")
    print("Live: BLOCKED")
    print("Broker execution: DISABLED")
    print("Shadow orders: DISABLED")


if __name__ == "__main__":
    main()