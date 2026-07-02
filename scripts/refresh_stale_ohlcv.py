#!/usr/bin/env python3
"""PHASE 7C-DATA-REPAIR — Refresh the FULL research universe OHLCV from Alpaca bars.

Read-only data operation with respect to ledgers/strategy state. Fetches
Alpaca bars for every symbol in the research universe (discovered from the
OHLCV cache) plus required benchmark and sector ETFs, and appends to the
local CSV cache. Timestamps are formatted to match existing data
(YYYY-MM-DD HH:MM:SS+00:00). Column set is read from the existing CSV to
handle varying column counts (SPY/QQQ have extra 'capital gains').

Phase 7C contract:
  - The relative-strength continuation filter ranks against the BROAD
    research universe. Refreshing only the 6 approved observation symbols
    is INVALID — ret_20d_rank / ret_60d_rank become meaningless.
  - Sector ETFs (SMH, IGV, TAN) are required for drift attribution and
    must be part of the refresh scope.
  - Universe freshness floor: if fewer than MIN_FRESH_UNIVERSE symbols
    have bars at the target session after refresh, this script FAILS
    CLOSED (exit 1). Do not weaken the floor to get a green check.

Does NOT run observation generation cycle.
Does NOT mutate ledgers or strategy state.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# Calendar freshness module — source of truth for latest completed session
from src.reporting.market_calendar_freshness import (
    fetch_alpaca_calendar,
    parse_calendar_entries,
    get_latest_completed_session,
)

ROOT = Path(__file__).resolve().parents[1]
OHLCV_DIRS = ["data/cache/ohlcv_1d", "data/cache/ohlcv", "data/ohlcv_1d"]
ALPACA_DATA_URL = "https://data.alpaca.markets/v2/stocks"

REQUIRED_SYMBOLS = ["AMD", "ARM", "CRWD", "DDOG", "MRVL", "SEDG"]
BENCHMARK_SYMBOLS = ["SPY", "QQQ"]

# Sector ETFs required for drift attribution (Phase 7C):
#   SMH — semiconductors (AMD, MRVL, ARM)
#   IGV — software/cloud (CRWD, DDOG)
#   TAN — solar/clean energy (SEDG)
SECTOR_ETF_SYMBOLS = ["SMH", "IGV", "TAN"]

# Universe freshness floor. If fewer than this many symbols have current
# bars at the target session AFTER refresh, the refresh FAILS CLOSED.
# Do not lower this to get a green check.
MIN_FRESH_UNIVERSE = 50


def resolve_refresh_universe(root: Path) -> list[str]:
    """Resolve the full refresh scope for the research universe.

    Universe source (least-risky derivation, documented in
    docs/strategy_factory/DATA_SCOPE_CONTRACT.md):
      1. Every symbol with a CSV in the OHLCV cache (data/cache/ohlcv_1d/).
         This matches discover_symbol_paths() in
         src/paper/relative_strength_observation.py — the exact discovery
         mechanism the continuation filter uses to build its ranking
         universe (which ranks over all cached non-ETF symbols).
      2. Benchmark ETFs: SPY, QQQ (always included).
      3. Sector ETFs required for drift attribution: SMH, IGV, TAN
         (always included, even if not yet in the cache — a CSV must be
         seeded for a brand-new symbol before bars can be appended;
         missing files are reported as failures, not silently skipped).
      4. The 6 approved observation symbols (defensive union — they are
         already in the cache).

    Returns a sorted, de-duplicated list of symbols.
    """
    symbols: set[str] = set()

    for rel in OHLCV_DIRS:
        cache = root / rel
        if not cache.is_dir():
            continue
        for p in cache.glob("*.csv"):
            sym = p.stem.upper().replace("_1D", "").replace("_1d", "")
            if sym:
                symbols.add(sym)
        break  # first existing cache dir is the canonical one

    symbols.update(REQUIRED_SYMBOLS)
    symbols.update(BENCHMARK_SYMBOLS)
    symbols.update(SECTOR_ETF_SYMBOLS)

    return sorted(symbols)

# TARGET_DATE is resolved dynamically from Alpaca calendar.
# Override via REFRESH_TARGET_DATE env var for testing only.
TARGET_DATE: str | None = None


def _resolve_target_date() -> str:
    """Determine the target date for OHLCV refresh.

    Priority:
    1. REFRESH_TARGET_DATE env var (testing override only)
    2. Alpaca calendar latest completed session (production path)

    Returns the target date as YYYY-MM-DD string.
    Raises SystemExit(1) with CALENDAR_UNAVAILABLE if both fail.
    """
    override = os.environ.get("REFRESH_TARGET_DATE")
    if override:
        return override

    raw = fetch_alpaca_calendar()
    if raw is None:
        print("CALENDAR_UNAVAILABLE — Alpaca calendar returned no data.")
        print("Set REFRESH_TARGET_DATE env var for manual override (testing only).")
        sys.exit(1)

    entries = parse_calendar_entries(raw)
    if not entries:
        print("CALENDAR_UNAVAILABLE — Alpaca calendar returned empty entry list.")
        sys.exit(1)

    latest = get_latest_completed_session(entries)
    if latest is None:
        print("CALENDAR_UNAVAILABLE — Could not determine latest completed session.")
        sys.exit(1)

    return latest.date.isoformat()


@dataclass
class SymbolRefreshResult:
    symbol: str
    status: str = "FAILED"
    bars_before: int = 0
    bars_after: int = 0
    new_bars: int = 0
    latest_date: str | None = None
    error: str | None = None


@dataclass
class RefreshBatchResult:
    results: list[SymbolRefreshResult] = field(default_factory=list)
    total_fetched: int = 0
    total_failed: int = 0

    @property
    def all_succeeded(self) -> bool:
        return self.total_failed == 0


def _load_alpaca_creds() -> tuple[str, str]:
    env = {}
    env_path = ROOT / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env[k.strip()] = v.strip()
    return env.get("ALPACA_API_KEY", ""), env.get("ALPACA_SECRET_KEY", "")


def fetch_alpaca_bars(
    symbol: str, start: str, end: str, api_key: str, api_secret: str
) -> list[dict[str, Any]] | None:
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Accept": "application/json",
    }
    url = (
        f"{ALPACA_DATA_URL}/{symbol}/bars"
        f"?timeframe=1Day&start={start}&end={end}"
        f"&limit=5&adjustment=split"
    )
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode()).get("bars", [])
    except Exception:
        return None


def find_ohlcv_cache() -> Path | None:
    for rel in OHLCV_DIRS:
        candidate = ROOT / rel
        if candidate.is_dir():
            return candidate
    return None


def read_csv_latest_date(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            return None
        time_col = None
        if reader.fieldnames:
            for c in ["timestamp", "date", "datetime", "time"]:
                if c in reader.fieldnames:
                    time_col = c
                    break
        if time_col is None:
            return None
        return max(r[time_col].strip()[:10] for r in rows)
    except Exception:
        return None


def read_csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with open(path) as f:
            return sum(1 for _ in f) - 1
    except Exception:
        return 0


def format_alpaca_timestamp(bar_ts: str) -> str:
    """Convert Alpaca timestamp (2026-05-28T04:00:00Z) to CSV format
    matching existing data (2026-05-28 04:00:00+00:00)."""
    # Strip 'Z', replace 'T' with space, append +00:00
    return bar_ts.replace("T", " ").rstrip("Z") + "+00:00"


def append_bars_to_csv(path: Path, bars: list[dict[str, Any]]) -> int:
    """Append new bars to CSV. Reads existing header to match column set.
    Formats timestamps to match existing data convention.
    Returns count of bars appended."""
    # Read existing CSV to get fieldnames and existing dates
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        existing_dates: set[str] = set()
        for row in reader:
            for c in ["timestamp", "date", "datetime", "time"]:
                if c in row and row[c]:
                    existing_dates.add(row[c].strip()[:10])
                    break

    if not fieldnames:
        return 0

    # Build mapping from Alpaca bar keys to CSV column names
    key_map = {
        "date": "t",
        "open": "o",
        "high": "h",
        "low": "l",
        "close": "c",
        "volume": "v",
    }

    new_rows = []
    for bar in bars:
        ts = bar.get("t", "")[:10]
        if ts in existing_dates:
            continue  # deduplicate

        row = {}
        for csv_col in fieldnames:
            if csv_col in key_map:
                raw = bar.get(key_map[csv_col], "")
                if csv_col == "date":
                    raw = format_alpaca_timestamp(bar.get("t", ""))
                row[csv_col] = raw
            elif csv_col == "dividends":
                row[csv_col] = 0.0
            elif csv_col in ("stock splits", "stock_splits", "capital gains"):
                row[csv_col] = 0.0
            else:
                row[csv_col] = ""
        new_rows.append(row)

    if not new_rows:
        return 0

    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for row in new_rows:
            writer.writerow(row)

    return len(new_rows)


def fetch_alpaca_bars_history(
    symbol: str, start: str, end: str, api_key: str, api_secret: str,
    limit: int = 10000,
) -> list[dict[str, Any]] | None:
    """Fetch a long history of daily bars (used to seed brand-new symbol CSVs)."""
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Accept": "application/json",
    }
    url = (
        f"{ALPACA_DATA_URL}/{symbol}/bars"
        f"?timeframe=1Day&start={start}&end={end}"
        f"&limit={limit}&adjustment=split"
    )
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode()).get("bars", [])
    except Exception:
        return None


SEED_HISTORY_START = "2023-01-03T00:00:00Z"
SEED_CSV_COLUMNS = ["date", "open", "high", "low", "close", "volume",
                    "dividends", "stock splits"]


def seed_symbol_csv(
    symbol: str, cache_dir: Path, api_key: str, api_secret: str,
    target_date: str,
) -> SymbolRefreshResult:
    """Create a new OHLCV CSV for a symbol that has no cache file yet.

    Used for required sector ETFs (e.g. IGV, TAN) that were never part of
    the cache. Fetches full daily history since SEED_HISTORY_START and
    writes a CSV in the standard column layout. Never overwrites an
    existing file.
    """
    result = SymbolRefreshResult(symbol=symbol)
    csv_path = cache_dir / f"{symbol}_1D.csv"
    if csv_path.exists():
        result.error = "seed refused: CSV already exists"
        return result

    td = datetime.strptime(target_date, "%Y-%m-%d")
    fetch_end = (td + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    bars = fetch_alpaca_bars_history(
        symbol, SEED_HISTORY_START, fetch_end, api_key, api_secret
    )
    if not bars:
        result.error = "Alpaca history fetch returned no data"
        return result

    bars = [b for b in bars if b.get("t", "")[:10] <= target_date]
    if not bars:
        result.error = "No bars at/before target date"
        return result

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SEED_CSV_COLUMNS)
        writer.writeheader()
        for b in bars:
            writer.writerow({
                "date": format_alpaca_timestamp(b.get("t", "")),
                "open": b.get("o", ""),
                "high": b.get("h", ""),
                "low": b.get("l", ""),
                "close": b.get("c", ""),
                "volume": b.get("v", ""),
                "dividends": 0.0,
                "stock splits": 0.0,
            })

    result.new_bars = len(bars)
    result.bars_after = read_csv_row_count(csv_path)
    result.latest_date = read_csv_latest_date(csv_path)
    result.status = "SEEDED"
    return result


def refresh_symbol(symbol: str, cache_dir: Path, api_key: str,
                   api_secret: str) -> SymbolRefreshResult:
    result = SymbolRefreshResult(symbol=symbol)

    csv_path = None
    for name in [f"{symbol}.csv", f"{symbol}_1D.csv", f"{symbol}_1d.csv"]:
        p = cache_dir / name
        if p.exists():
            csv_path = p
            break

    if csv_path is None:
        # Required sector ETFs with no cache file are seeded with full history
        if symbol in SECTOR_ETF_SYMBOLS:
            assert TARGET_DATE is not None
            return seed_symbol_csv(symbol, cache_dir, api_key, api_secret, TARGET_DATE)
        result.error = "CSV not found"
        return result

    result.bars_before = read_csv_row_count(csv_path)

    # TARGET_DATE guaranteed to be set by refresh_all_stale before calling this
    assert TARGET_DATE is not None, "TARGET_DATE must be resolved before refresh_symbol"

    # Compute fetch range: 5 days before target + 1 day after (safety margin)
    td = datetime.strptime(TARGET_DATE, "%Y-%m-%d")
    fetch_start = (td - timedelta(days=5)).strftime("%Y-%m-%dT00:00:00Z")
    fetch_end = (td + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")

    bars = fetch_alpaca_bars(
        symbol, fetch_start, fetch_end,
        api_key, api_secret,
    )

    if bars is None:
        result.error = "Alpaca bars API returned no data"
        return result
    if not bars:
        result.error = "Alpaca bars API returned empty list"
        return result

    bars = [b for b in bars if b.get("t", "")[:10] <= TARGET_DATE]
    result.new_bars = append_bars_to_csv(csv_path, bars)
    result.bars_after = read_csv_row_count(csv_path)
    result.latest_date = read_csv_latest_date(csv_path)

    if result.new_bars > 0:
        result.status = "FETCHED"
    elif result.latest_date and TARGET_DATE and result.latest_date >= TARGET_DATE:
        result.status = "SKIPPED_CURRENT"
    else:
        result.error = f"No new bars (latest={result.latest_date}, target={TARGET_DATE})"

    return result


def refresh_all_stale() -> RefreshBatchResult:
    global TARGET_DATE

    # Resolve target date from Alpaca calendar (or env override)
    TARGET_DATE = _resolve_target_date()

    # Resolve full research universe + benchmarks + sector ETFs
    all_symbols = resolve_refresh_universe(ROOT)

    api_key, api_secret = _load_alpaca_creds()
    batch = RefreshBatchResult()

    if not api_key or not api_secret:
        print("ERROR: No Alpaca credentials")
        batch.total_failed = len(all_symbols)
        for sym in all_symbols:
            batch.results.append(
                SymbolRefreshResult(symbol=sym, error="No credentials")
            )
        return batch

    cache_dir = find_ohlcv_cache()
    if cache_dir is None:
        print("ERROR: No cache dir")
        batch.total_failed = len(all_symbols)
        for sym in all_symbols:
            batch.results.append(
                SymbolRefreshResult(symbol=sym, error="No cache dir")
            )
        return batch

    print(f"Cache: {cache_dir}")
    print(f"Target: {TARGET_DATE}")
    print(f"Universe size (discovered + required ETFs): {len(all_symbols)}")
    print(f"Symbols: {', '.join(all_symbols)}\n")

    for sym in all_symbols:
        r = refresh_symbol(sym, cache_dir, api_key, api_secret)
        batch.results.append(r)
        if r.status == "FETCHED":
            batch.total_fetched += 1
            print(f"  {sym}: FETCHED {r.new_bars} bar(s) → {r.bars_after} rows, latest={r.latest_date}")
        elif r.status == "SEEDED":
            batch.total_fetched += 1
            print(f"  {sym}: SEEDED {r.new_bars} bar(s) (new CSV) → {r.bars_after} rows, latest={r.latest_date}")
        elif r.status == "SKIPPED_CURRENT":
            print(f"  {sym}: CURRENT (already at {r.latest_date})")
        else:
            batch.total_failed += 1
            print(f"  {sym}: FAILED — {r.error}")

    return batch


def summarize_freshness(batch: RefreshBatchResult) -> dict[str, Any]:
    """Build a universe-freshness summary from a refresh batch.

    Reports:
      - universe_size: symbols in refresh scope
      - refreshed_count: symbols with newly fetched bars
      - fresh_count: symbols whose latest bar is at/after TARGET_DATE
      - stale_count: symbols still behind TARGET_DATE (or failed)
      - stale_symbols: list of stale/failed symbols
      - sector_etf_freshness: per sector ETF latest date + fresh flag
      - min_fresh_universe: the fail-closed floor
      - floor_pass: fresh_count >= MIN_FRESH_UNIVERSE
    """
    fresh: list[str] = []
    stale: list[str] = []
    for r in batch.results:
        if r.latest_date and TARGET_DATE and r.latest_date >= TARGET_DATE:
            fresh.append(r.symbol)
        else:
            stale.append(r.symbol)

    sector_freshness: dict[str, dict[str, Any]] = {}
    by_symbol = {r.symbol: r for r in batch.results}
    for etf in SECTOR_ETF_SYMBOLS:
        r = by_symbol.get(etf)
        latest = r.latest_date if r else None
        sector_freshness[etf] = {
            "latest_date": latest,
            "fresh": bool(latest and TARGET_DATE and latest >= TARGET_DATE),
            "error": (r.error if r else "not in refresh scope"),
        }

    return {
        "target_date": TARGET_DATE,
        "universe_size": len(batch.results),
        "refreshed_count": batch.total_fetched,
        "fresh_count": len(fresh),
        "stale_count": len(stale),
        "stale_symbols": sorted(stale),
        "sector_etf_freshness": sector_freshness,
        "min_fresh_universe": MIN_FRESH_UNIVERSE,
        "floor_pass": len(fresh) >= MIN_FRESH_UNIVERSE,
    }


def main() -> None:
    print("=" * 60)
    print("PHASE 7C-DATA-REPAIR — Refresh Full Research Universe OHLCV")
    print("=" * 60)
    print()

    batch = refresh_all_stale()
    summary = summarize_freshness(batch)

    print()
    print("── Universe Freshness Report ──")
    print(f"Universe size: {summary['universe_size']}")
    print(f"Refreshed (new bars): {summary['refreshed_count']}")
    print(f"Fresh at latest session ({summary['target_date']}): {summary['fresh_count']}")
    print(f"Stale: {summary['stale_count']}")
    if summary["stale_symbols"]:
        print(f"Stale symbols: {', '.join(summary['stale_symbols'])}")
    print("Sector ETF freshness:")
    for etf, info in summary["sector_etf_freshness"].items():
        status = "FRESH" if info["fresh"] else f"STALE/MISSING ({info['error'] or 'behind target'})"
        print(f"  {etf}: latest={info['latest_date']} — {status}")
    print(f"Universe floor: {summary['fresh_count']}/{summary['min_fresh_universe']} "
          f"{'PASS' if summary['floor_pass'] else 'FAIL (FAIL-CLOSED)'}")

    print()
    print(f"Fetched: {batch.total_fetched}, Failed: {batch.total_failed}")

    print("\nProduction: BLOCKED\nLive: BLOCKED")
    print("Broker execution: DISABLED\nShadow orders: DISABLED")

    if not summary["floor_pass"]:
        print(f"\nUNIVERSE_FLOOR_VIOLATION — fewer than {MIN_FRESH_UNIVERSE} "
              "symbols fresh at target session. Failing closed. "
              "The relative-strength ranks are NOT valid on this cross-section.")
        sys.exit(1)

    sys.exit(0 if batch.total_failed == 0 else 1)


if __name__ == "__main__":
    main()