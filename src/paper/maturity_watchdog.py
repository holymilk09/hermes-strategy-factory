from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_observation_ledger(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    if df.empty:
        return df

    df.columns = [str(c).strip().lower() for c in df.columns]

    if "signal_timestamp" in df.columns:
        df["signal_timestamp"] = pd.to_datetime(
            df["signal_timestamp"], utc=True, errors="coerce"
        )

    if "outcome_window" in df.columns:
        df["outcome_window"] = pd.to_numeric(
            df["outcome_window"], errors="coerce"
        ).fillna(10).astype(int)

    if "sent_to_broker" in df.columns:
        df["sent_to_broker"] = df["sent_to_broker"].astype(bool)

    return df


def find_symbol_ohlcv_path(root: Path, symbol: str) -> Path | None:
    candidates = [
        root / "data" / "cache" / "ohlcv_1d" / f"{symbol}.csv",
        root / "data" / "cache" / "ohlcv_1d" / f"{symbol}_1D.csv",
        root / "data" / "cache" / "ohlcv_1d" / f"{symbol}_1d.csv",
        root / "data" / "cache" / f"{symbol}.csv",
        root / "data" / "cache" / f"{symbol}_1D.csv",
        root / "data" / "cache" / f"{symbol}_1d.csv",
        root / "data" / f"{symbol}.csv",
        root / "data" / f"{symbol}_1D.csv",
        root / "data" / f"{symbol}_1d.csv",
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


def load_ohlcv_timestamps(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]

    time_col = None
    for c in ["timestamp", "date", "datetime", "time"]:
        if c in df.columns:
            time_col = c
            break

    if time_col is None:
        return pd.Series(dtype="datetime64[ns, UTC]")

    ts = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    ts = ts.dropna().sort_values().drop_duplicates()
    return ts.reset_index(drop=True)


def compute_maturity_status(
    root: Path,
    observation_ledger: Path,
) -> dict[str, Any]:
    obs = load_observation_ledger(observation_ledger)

    if obs.empty:
        return {
            "classification": "NO_OBSERVATIONS",
            "observations_total": 0,
            "all_mature": False,
            "ready_for_outcome_update": False,
            "rows": [],
            "sent_to_broker_any": False,
        }

    required = ["symbol", "signal_timestamp", "outcome_window"]
    missing = [c for c in required if c not in obs.columns]

    if missing:
        return {
            "classification": "WATCHDOG_FAIL_MISSING_COLUMNS",
            "missing": missing,
            "observations_total": int(len(obs)),
            "all_mature": False,
            "ready_for_outcome_update": False,
            "rows": [],
            "sent_to_broker_any": False,
        }

    sent_to_broker_any = False
    if "sent_to_broker" in obs.columns:
        sent_to_broker_any = bool(obs["sent_to_broker"].astype(bool).any())

    rows = []

    for _, row in obs.iterrows():
        symbol = str(row["symbol"]).upper()
        signal_ts = pd.Timestamp(row["signal_timestamp"])

        if signal_ts.tzinfo is None:
            signal_ts = signal_ts.tz_localize("UTC")
        else:
            signal_ts = signal_ts.tz_convert("UTC")

        outcome_window = int(row["outcome_window"])

        path = find_symbol_ohlcv_path(root, symbol)

        if path is None:
            rows.append(
                {
                    "symbol": symbol,
                    "signal_timestamp": signal_ts.isoformat(),
                    "ohlcv_found": False,
                    "latest_ohlcv_ts": None,
                    "future_bars": 0,
                    "bars_remaining": outcome_window,
                    "outcome_window": outcome_window,
                    "mature": False,
                    "status": "MISSING_OHLCV",
                }
            )
            continue

        timestamps = load_ohlcv_timestamps(path)
        future = timestamps[timestamps > signal_ts]

        future_bars = int(len(future))
        bars_remaining = max(outcome_window - future_bars, 0)
        mature = future_bars >= outcome_window

        rows.append(
            {
                "symbol": symbol,
                "signal_timestamp": signal_ts.isoformat(),
                "ohlcv_found": True,
                "ohlcv_path": str(path),
                "latest_ohlcv_ts": timestamps.max().isoformat() if not timestamps.empty else None,
                "future_bars": future_bars,
                "bars_remaining": bars_remaining,
                "outcome_window": outcome_window,
                "mature": mature,
                "status": "MATURE" if mature else "PENDING",
            }
        )

    mature_count = sum(1 for r in rows if r["mature"])
    total = len(rows)
    all_mature = mature_count == total and total > 0

    if sent_to_broker_any:
        classification = "WATCHDOG_HARD_FAIL_BROKER_FLAG"
    elif all_mature:
        classification = "OUTCOMES_READY"
    elif mature_count > 0:
        classification = "PARTIALLY_MATURE"
    else:
        classification = "PENDING_MATURITY"

    return {
        "classification": classification,
        "observations_total": total,
        "mature_count": mature_count,
        "pending_count": total - mature_count,
        "all_mature": all_mature,
        "ready_for_outcome_update": all_mature,
        "sent_to_broker_any": sent_to_broker_any,
        "rows": rows,
    }


def write_watchdog_reports(
    result: dict[str, Any],
    markdown_path: Path,
    json_path: Path,
) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(
        json.dumps(result, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )

    lines = []
    lines.append("# Relative Strength Maturity Watchdog")
    lines.append("")
    lines.append(f"classification: {result['classification']}")
    lines.append(f"observations_total: {result.get('observations_total')}")
    lines.append(f"mature_count: {result.get('mature_count')}")
    lines.append(f"pending_count: {result.get('pending_count')}")
    lines.append(f"all_mature: {result.get('all_mature')}")
    lines.append(f"ready_for_outcome_update: {result.get('ready_for_outcome_update')}")
    lines.append(f"sent_to_broker_any: {result.get('sent_to_broker_any')}")
    lines.append("")
    lines.append("## Per Symbol")
    lines.append("")

    for row in result.get("rows", []):
        lines.append(
            f"- {row['symbol']}: future_bars={row['future_bars']} "
            f"bars_remaining={row['bars_remaining']} "
            f"mature={row['mature']} "
            f"latest_ohlcv_ts={row['latest_ohlcv_ts']} "
            f"status={row['status']}"
        )

    lines.append("")
    lines.append("## Next Action")
    lines.append("")

    if result["classification"] == "OUTCOMES_READY":
        lines.append("Run outcome updater and drift report.")
    elif result["classification"] == "PARTIALLY_MATURE":
        lines.append("Do not run final drift classification yet. Continue waiting until all observations mature.")
    elif result["classification"] == "PENDING_MATURITY":
        lines.append("Continue daily observation cycle. Outcomes are not mature.")
    elif result["classification"] == "WATCHDOG_HARD_FAIL_BROKER_FLAG":
        lines.append("Halt and audit broker contamination.")
    else:
        lines.append("No action.")

    lines.append("")
    lines.append("Production: BLOCKED")
    lines.append("Live: BLOCKED")
    lines.append("Broker execution: DISABLED")
    lines.append("Shadow orders: DISABLED")

    markdown_path.write_text("\n".join(lines), encoding="utf-8")
