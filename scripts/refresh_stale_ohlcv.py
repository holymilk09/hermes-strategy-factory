#!/usr/bin/env python3
"""PHASE 6J-DATA-REFRESH — Refresh stale OHLCV from Alpaca bars.

Read-only data operation. Fetches Alpaca bars for stale symbols and
appends to local CSV cache. Timestamps are formatted to match existing
data (YYYY-MM-DD HH:MM:SS+00:00). Column set is read from the existing
CSV to handle varying column counts (SPY/QQQ have extra 'capital gains').

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
ALL_SYMBOLS = list(dict.fromkeys(REQUIRED_SYMBOLS + BENCHMARK_SYMBOLS))

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

    api_key, api_secret = _load_alpaca_creds()
    batch = RefreshBatchResult()

    if not api_key or not api_secret:
        print("ERROR: No Alpaca credentials")
        batch.total_failed = len(ALL_SYMBOLS)
        for sym in ALL_SYMBOLS:
            batch.results.append(
                SymbolRefreshResult(symbol=sym, error="No credentials")
            )
        return batch

    cache_dir = find_ohlcv_cache()
    if cache_dir is None:
        print("ERROR: No cache dir")
        batch.total_failed = len(ALL_SYMBOLS)
        for sym in ALL_SYMBOLS:
            batch.results.append(
                SymbolRefreshResult(symbol=sym, error="No cache dir")
            )
        return batch

    print(f"Cache: {cache_dir}")
    print(f"Target: {TARGET_DATE}")
    print(f"Symbols: {', '.join(ALL_SYMBOLS)}\n")

    for sym in ALL_SYMBOLS:
        r = refresh_symbol(sym, cache_dir, api_key, api_secret)
        batch.results.append(r)
        if r.status == "FETCHED":
            batch.total_fetched += 1
            print(f"  {sym}: FETCHED {r.new_bars} bar(s) → {r.bars_after} rows, latest={r.latest_date}")
        elif r.status == "SKIPPED_CURRENT":
            print(f"  {sym}: CURRENT (already at {r.latest_date})")
        else:
            batch.total_failed += 1
            print(f"  {sym}: FAILED — {r.error}")

    return batch


def main() -> None:
    print("=" * 60)
    print("PHASE 6J-DATA-REFRESH — Refresh Stale OHLCV")
    print("=" * 60)
    print()

    batch = refresh_all_stale()

    print()
    print(f"Fetched: {batch.total_fetched}, Failed: {batch.total_failed}")
    if batch.all_succeeded:
        print("All symbols OK — run freshness check to confirm.")
    else:
        print("Some symbols failed — investigate.")

    print("\nProduction: BLOCKED\nLive: BLOCKED")
    print("Broker execution: DISABLED\nShadow orders: DISABLED")
    sys.exit(0 if batch.total_failed == 0 else 1)


if __name__ == "__main__":
    main()