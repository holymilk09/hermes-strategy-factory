#!/usr/bin/env python3
"""Phase 30J — Data Refresh Status Panel
Shows OHLCV freshness for observation symbols without performing any refresh.
"""
import csv
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path("/opt/data")
OHLCV_DIR = BASE / "data/cache/ohlcv_1d"
SNAPSHOT = BASE / "reports/strategy_factory/feature_factory_state_snapshot.json"
OBS_LEDGER = BASE / "data/paper_observation/relative_strength_continuation_observation_ledger.csv"

# US Market holidays (simplified — major only)
# 2026 observed holidays: Jan 1, Jan 19, Feb 16, Apr 3(Good Fri), May 25, Jun 19, Jul 3, Sep 7, Nov 26, Dec 25
MARKET_HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03",
    "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
    "2026-11-26", "2026-12-25",
}


def is_trading_day(dt):
    """Returns True if dt is a weekday and not a major US holiday."""
    if dt.weekday() >= 5:  # Sat=5, Sun=6
        return False
    return dt.strftime("%Y-%m-%d") not in MARKET_HOLIDAYS_2026


def next_trading_day(from_dt):
    """Find next trading day after from_dt."""
    d = from_dt + timedelta(days=1)
    while not is_trading_day(d):
        d += timedelta(days=1)
    return d


def get_symbol_ohlcv_info(sym):
    """Get latest date for a symbol from OHLCV cache."""
    for fname in [f"{sym}_1D.csv", f"{sym}.csv"]:
        path = OHLCV_DIR / fname
        if not path.exists():
            continue
        try:
            with open(path) as f:
                header = next(f).strip().lower().split(",")
            # Find date column
            date_idx = 0
            for i, c in enumerate(header):
                if c in ("date", "timestamp", "time", "datetime"):
                    date_idx = i
                    break
            # Read last line
            with open(path) as f:
                lines = f.readlines()
            if len(lines) < 2:
                return None, 0, None

            last_line = lines[-1].strip()
            parts = last_line.split(",")
            if date_idx >= len(parts):
                return None, 0, None

            date_str = parts[date_idx].strip()
            try:
                last_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except Exception:
                return None, 0, None

            # Count total rows
            total_rows = len(lines)  # minus header? we can just use len(lines)
            return last_date, total_rows, date_str
        except Exception:
            return None, 0, None
    return None, 0, None


def main():
    # Load snapshot
    if SNAPSHOT.exists():
        with open(SNAPSHOT) as f:
            snap = json.load(f)
    else:
        print("=== DATA REFRESH STATUS ===")
        print()
        print("NO STATE SNAPSHOT — cannot determine observation symbols")
        sys.exit(1)

    symbols = snap.get("symbols", [])
    signal_ts_str = snap.get("latest_signal_timestamp", "")
    try:
        signal_dt = datetime.fromisoformat(signal_ts_str.replace("Z", "+00:00"))
    except Exception:
        signal_dt = None

    outcome_window = 10

    print("=== DATA REFRESH STATUS ===")
    print()

    # Section 1: per-symbol OHLCV status
    print("OHLCV by symbol:")
    print(f"  {'Symbol':<8} {'Last Date':<22} {'Rows':<6} {'Bars>AftSig':<12} {'Status'}")
    print(f"  {'-'*56}")

    all_latest = []
    missing = []
    stale = []
    for sym in symbols:
        last_date, total_rows, date_str = get_symbol_ohlcv_info(sym)
        if last_date is None:
            print(f"  {sym:<8} {'NO DATA':<22} {'--':<6} {'--':<12} MISSING")
            missing.append(sym)
            continue

        all_latest.append(last_date)

        # Bars after signal
        if signal_dt:
            # Count all dates in CSV that are > signal_dt
            path = OHLCV_DIR / f"{sym}_1D.csv"
            if not path.exists():
                path = OHLCV_DIR / f"{sym}.csv"
            bars_after = 0
            if path.exists():
                try:
                    with open(path) as f:
                        next(f)  # header
                        for row in csv.reader(f):
                            if not row:
                                continue
                            try:
                                d = datetime.fromisoformat(row[0].strip().replace("Z", "+00:00"))
                                if d > signal_dt:
                                    bars_after += 1
                            except Exception:
                                pass
                except Exception:
                    pass
            bars_str = f"{bars_after}/{outcome_window}"
        else:
            bars_str = "--"

        # Staleness check
        now = datetime.now(timezone.utc)
        days_since = (now - last_date).days
        if days_since > 4:
            status = f"STALE ({days_since}d)"
            stale.append(sym)
        elif days_since > 0:
            status = f"fresh ({days_since}d ago)"
        else:
            status = "fresh (today)"

        print(f"  {sym:<8} {date_str[:22]:<22} {total_rows:<6} {bars_str:<12} {status}")

    print()

    # Section 2: aggregate
    if all_latest:
        latest_all = max(all_latest)
        earliest_all = min(all_latest)
        now = datetime.now(timezone.utc)
        print(f"Latest across all:  {latest_all.strftime('%Y-%m-%d %H:%M')} UTC")
        print(f"Earliest across all: {earliest_all.strftime('%Y-%m-%d %H:%M')} UTC")

        # Next expected market day
        next_day = next_trading_day(latest_all)
        print(f"Next market day:     {next_day.strftime('%Y-%m-%d')} "
              f"({'today' if next_day.date() == now.date() else next_day.strftime('%A')})")
        print()

    # Section 3: problems
    print("Issues:")
    issues = []
    if missing:
        issues.append(f"  missing symbols: {', '.join(missing)}")
    if stale:
        issues.append(f"  stale symbols (>4d): {', '.join(stale)}")
    if not missing and not stale:
        issues.append("  no issues detected")

    # Signal-relative check
    if signal_dt and all_latest:
        latest_all = max(all_latest)
        if latest_all < signal_dt:
            issues.append(f"  WARNING: OHLCV data ({latest_all.date()}) is OLDER than signal ({signal_dt.date()})")
        elif latest_all.date() == signal_dt.date():
            issues.append(f"  note: latest data equals signal date — no forward bars available yet")

    for i in issues:
        print(f"  {i}")
    print()

    # Section 4: market calendar note
    print("Market calendar:")
    print(f"  Holidays 2026: {', '.join(sorted(MARKET_HOLIDAYS_2026))}")
    print(f"  Last Friday:   2026-05-22 (weekend, May 23-24)")
    next_monday = next_trading_day(datetime(2026, 5, 22))
    print(f"  Next session:  {next_monday.strftime('%Y-%m-%d')} (Monday)")


if __name__ == "__main__":
    main()