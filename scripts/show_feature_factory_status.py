#!/usr/bin/env python3
"""Phase 30H — Feature Factory Operator Dashboard (~/status)"""
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/opt/data")
SNAPSHOT = BASE / "reports/strategy_factory/feature_factory_state_snapshot.json"
OHLCV_DIR = BASE / "data/cache/ohlcv_1d"
BACKUP_DIR = BASE / "backups"
OBS_LEDGER = BASE / "data/paper_observation/relative_strength_continuation_observation_ledger.csv"
OUTCOME_LEDGER = BASE / "data/paper_observation/relative_strength_continuation_outcome_ledger.csv"

# Research phase grade mapping (manual, from latest Phase 28A)
LINEAGE_GRADE = {
    "relative_strength_continuation": "B",
    "sector_residual_mr": "C",
    "price_volume_capitulation": "D",
    "canonical_residual": "D",
    "regime_conditioned_capitulation_v2": "C",
    "volatility_regime": "C",
    "factor_residual_mr": "D",
}


def load_snapshot():
    if SNAPSHOT.exists():
        with open(SNAPSHOT) as f:
            return json.load(f)
    return None


def get_backup_info():
    backups = sorted(BACKUP_DIR.glob("feature_factory_state_*.tar.gz"), reverse=True)
    if not backups:
        return None, None
    latest = backups[0]
    size_mb = os.path.getsize(latest) / (1024 * 1024)
    if size_mb >= 1000:
        size_str = f"{size_mb / 1024:.0f}G"
    elif size_mb >= 1:
        size_str = f"{int(size_mb)}M"
    else:
        size_str = f"{size_mb:.0f}K"
    # Return relative to backups/ for cleaner display
    rel_path = str(latest.relative_to(BASE))
    return rel_path, size_str


def get_bars_elapsed(signal_ts_str, symbols, ohlcv_dir):
    """Compute how many trading bars elapsed since signal for each symbol."""
    from datetime import datetime, timezone
    import csv

    if not signal_ts_str:
        return {}

    try:
        signal_dt = datetime.fromisoformat(signal_ts_str.replace("Z", "+00:00"))
    except Exception:
        return {}

    result = {}
    for sym in symbols:
        for fname in [f"{sym}_1D.csv", f"{sym}.csv"]:
            path = ohlcv_dir / fname
            if path.exists():
                try:
                    with open(path) as f:
                        reader = csv.reader(f)
                        header = next(reader)
                    # find date column
                    date_col_idx = None
                    for i, c in enumerate(header):
                        if c.strip().lower() in ("date", "timestamp", "time", "datetime"):
                            date_col_idx = i
                            break
                    if date_col_idx is None:
                        date_col_idx = 0

                    dates = []
                    with open(path) as f:
                        next(f)  # skip header
                        for row in csv.reader(f):
                            if row and len(row) > date_col_idx:
                                try:
                                    dt = datetime.fromisoformat(row[date_col_idx].strip().replace("Z", "+00:00"))
                                    dates.append(dt)
                                except Exception:
                                    pass
                    # Count dates after signal
                    after = [d for d in dates if d > signal_dt]
                    result[sym] = len(after)
                except Exception:
                    result[sym] = 0
                break
        else:
            result[sym] = 0
    return result


def main():
    import pandas as pd  # lazy import for OHLCV only

    snap = load_snapshot()
    if snap is None:
        print("=== FEATURE FACTORY STATUS ===")
        print()
        print("NO STATE SNAPSHOT FOUND")
        print(f"Expected: {SNAPSHOT}")
        return

    lineage = snap.get("active_lineage", "unknown")
    grade = LINEAGE_GRADE.get(lineage, "?")
    pending = snap.get("pending", 0)
    resolved = snap.get("resolved", 0)
    symbols = snap.get("symbols", [])
    maturity = snap.get("maturity_classification", "UNKNOWN")
    mature_count = snap.get("mature_count", 0)
    bars_remaining = snap.get("bars_remaining_per_symbol", {})
    leakage = snap.get("broker_leakage", False)
    next_action = snap.get("next_allowed_action", "UNKNOWN")
    signal_ts = snap.get("latest_signal_timestamp", "")

    # Compute bars elapsed dynamically from OHLCV
    bars_elapsed = get_bars_elapsed(signal_ts, symbols, OHLCV_DIR)
    outcome_window = 10  # from Phase 28B spec

    # Latest OHLCV date
    latest_ohlcv = None
    try:
        all_dates = []
        for sym in symbols:
            for fname in [f"{sym}_1D.csv", f"{sym}.csv"]:
                path = OHLCV_DIR / fname
                if path.exists():
                    df = pd.read_csv(path, parse_dates=[0])
                    all_dates.append(df.iloc[-1, 0])
                    break
        if all_dates:
            latest_ohlcv = max(all_dates)
            if hasattr(latest_ohlcv, 'strftime'):
                latest_ohlcv = latest_ohlcv.strftime("%Y-%m-%d")
    except Exception:
        pass

    # Compute bars remaining
    bars_remaining_display = {}
    for sym in symbols:
        elapsed = bars_elapsed.get(sym, 0)
        remaining = max(0, outcome_window - elapsed)
        bars_remaining_display[sym] = f"{elapsed}/{outcome_window}"

    # Backup info
    backup_path, backup_size = get_backup_info()

    print("=== FEATURE FACTORY STATUS ===")
    print()
    print(f"Active lineage: {lineage}")
    print(f"Grade: {grade}")
    print(f"State: {maturity}")
    print()

    print(f"Observations:")
    print(f"  pending={pending}")
    print(f"  resolved={resolved}")
    print(f"  symbols={', '.join(symbols)}")
    print()

    print("Maturity:")
    for sym in symbols:
        display = bars_remaining_display.get(sym, "?/10")
        print(f"  {sym} {display} bars")
    print()

    print(f"Next action:")
    print(f"  {next_action}")
    print()

    print(f"Data:")
    if latest_ohlcv:
        print(f"  latest OHLCV: {latest_ohlcv}")
    else:
        print(f"  latest OHLCV: N/A")
    print()

    print(f"Backup:")
    if backup_path:
        print(f"  latest={backup_path}")
        print(f"  size={backup_size}")
    else:
        print(f"  no backups found")
    print()

    print(f"Broker leakage:")
    print(f"  detected={leakage}")
    print()

    print("Hard blocks:")
    print(f"  Production: {'BLOCKED' if snap.get('production_hard_block') else 'OPEN'}")
    print(f"  Live: {'BLOCKED' if snap.get('live_hard_block') else 'OPEN'}")
    print(f"  Broker: {'DISABLED' if snap.get('broker_execution_disabled') else 'ENABLED'}")
    print(f"  Shadow: {'DISABLED' if snap.get('shadow_disabled') else 'ENABLED'}")


if __name__ == "__main__":
    main()