from __future__ import annotations

import csv
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.paper.maturity_watchdog import find_symbol_ohlcv_path

# ──────────────────────────────────────────────
# Ghost Ledger — append-only record of rejected / filtered-out setups
# ──────────────────────────────────────────────

GHOST_LEDGER_DIR = Path("data/trust_calibration")
GHOST_LEDGER_PATH = GHOST_LEDGER_DIR / "ghost_ledger.csv"

GHOST_FIELDS = [
    "ghost_id",
    "source_observation_id",
    "symbol",
    "strategy_id",
    "setup_type",
    "signal_date",
    "rejection_reason",
    "failed_gate",
    "score_if_available",
    "price_at_signal",
    "market_weather",
    "published_status",
    "reason_not_published",
    "outcome_5d",
    "outcome_10d",
    "outcome_20d",
    "outcome_30d",
    "max_favorable_move",
    "max_adverse_move",
    "setup_broke",
    "data_status",
    "created_at",
]


@dataclass(frozen=True)
class GhostRecord:
    ghost_id: str
    source_observation_id: str
    symbol: str
    strategy_id: str
    setup_type: str
    signal_date: str
    rejection_reason: str
    failed_gate: str
    score_if_available: str
    price_at_signal: float
    market_weather: str
    published_status: str = "GHOST_ONLY"
    reason_not_published: str = ""
    outcome_5d: str = ""
    outcome_10d: str = ""
    outcome_20d: str = ""
    outcome_30d: str = ""
    max_favorable_move: str = ""
    max_adverse_move: str = ""
    setup_broke: str = ""
    data_status: str = "PENDING"
    created_at: str = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _dict_from_record(r: GhostRecord) -> dict[str, str]:
    return {f.name: str(getattr(r, f.name)) for f in fields(r)}


def load_ghost_ledger(path: Path = GHOST_LEDGER_PATH) -> list[dict[str, str]]:
    """Load existing ghost ledger. Returns empty list if missing."""
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def _read_existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    existing: set[str] = set()
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing.add(row.get("ghost_id", "").strip())
    return existing


def append_ghost_records(
    records: list[GhostRecord],
    path: Path = GHOST_LEDGER_PATH,
) -> int:
    """Append one or more ghost records to the ledger. Idempotent by ghost_id."""
    _ensure_dir(path)
    existing_ids = _read_existing_ids(path)
    new_records = [r for r in records if r.ghost_id not in existing_ids]
    if not new_records:
        return 0

    write_header = not path.exists()
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=GHOST_FIELDS)
        if write_header:
            writer.writeheader()
        for r in new_records:
            row = _dict_from_record(r)
            if not row["created_at"]:
                row["created_at"] = _now_iso()
            writer.writerow(row)
    return len(new_records)


def build_ghost_record(
    *,
    ghost_id: str,
    source_observation_id: str,
    symbol: str,
    strategy_id: str,
    setup_type: str,
    signal_date: str,
    rejection_reason: str,
    failed_gate: str,
    score_if_available: str = "",
    price_at_signal: float = 0.0,
    market_weather: str = "",
) -> GhostRecord:
    """Factory to create a ghost record with defaults."""
    return GhostRecord(
        ghost_id=ghost_id,
        source_observation_id=source_observation_id,
        symbol=symbol,
        strategy_id=strategy_id,
        setup_type=setup_type,
        signal_date=signal_date,
        rejection_reason=rejection_reason,
        failed_gate=failed_gate,
        score_if_available=score_if_available,
        price_at_signal=price_at_signal,
        market_weather=market_weather,
        published_status="GHOST_ONLY",
        reason_not_published=f"Rejected by {failed_gate}: {rejection_reason}",
        data_status="PENDING",
        created_at=_now_iso(),
    )


def resolve_ghost_outcomes(
    root: Path,
    ghost_path: Path = GHOST_LEDGER_PATH,
    ohlcv_dir: Path = Path("data/cache/ohlcv_1d"),
    dry_run: bool = False,
) -> int:
    """Compute outcome fields for PENDING ghost records where sufficient bars exist.

    Reuses checkpoint_result logic from maturity_scoreboard.

    Updates ONLY ghost ledger outcome/status fields. Never touches the
    observation or outcome ledgers, never creates observations, never adds
    or removes ghost rows.

    Status transitions:
      PENDING → MATURE            when >= 5 forward bars exist
      PENDING → INSUFFICIENT_DATA when resolution is impossible
                                  (missing symbol data, bad signal date,
                                  missing signal price)
      PENDING stays PENDING       when < 5 forward bars so far

    When ``dry_run`` is True, computes and returns the number of records
    that WOULD be updated without writing anything.
    Returns number of records updated (or would-be updated in dry-run).
    """
    from src.reporting.maturity_scoreboard import checkpoint_result, load_ohlcv_rows

    records = load_ghost_ledger(ghost_path)
    if not records:
        return 0

    updated = 0
    for rec in records:
        if rec.get("data_status", "").upper() in ("MATURE", "INSUFFICIENT_DATA"):
            continue

        signal_date = rec.get("signal_date", "")
        if not signal_date:
            rec["data_status"] = "INSUFFICIENT_DATA"
            updated += 1
            continue

        try:
            signal_dt = datetime.fromisoformat(signal_date.replace("Z", "+00:00"))
        except Exception:
            rec["data_status"] = "INSUFFICIENT_DATA"
            updated += 1
            continue

        symbol = rec.get("symbol", "").upper()
        ohlcv = find_symbol_ohlcv_path(root, symbol)
        if ohlcv is None:
            rec["data_status"] = "INSUFFICIENT_DATA"
            updated += 1
            continue

        rows = load_ohlcv_rows(ohlcv)
        if not rows:
            rec["data_status"] = "INSUFFICIENT_DATA"
            updated += 1
            continue

        # Find signal date in OHLCV
        try:
            price_raw = rec.get("price_at_signal", "0")
            initial_price = float(price_raw) if price_raw else 0.0
        except Exception:
            initial_price = 0.0

        if initial_price == 0.0:
            rec["data_status"] = "INSUFFICIENT_DATA"
            updated += 1
            continue

        future_rows = [r for r in rows if r["dt"] > signal_dt]
        days_elapsed = len(future_rows)

        if days_elapsed < 5:
            rec["data_status"] = "PENDING"
            continue

        r5 = checkpoint_result(initial_price, future_rows, 5)
        r10 = checkpoint_result(initial_price, future_rows, 10) if days_elapsed >= 10 else None
        r20 = checkpoint_result(initial_price, future_rows, 20) if days_elapsed >= 20 else None
        r30 = checkpoint_result(initial_price, future_rows, 30) if days_elapsed >= 30 else None

        max_fav = 0.0
        max_adv = 0.0
        for r in future_rows:
            ret = (r["close"] / initial_price - 1.0) * 100.0
            if ret > max_fav:
                max_fav = ret
            if ret < max_adv:
                max_adv = ret

        # setup_broke
        try:
            break_level = initial_price * 0.96
        except Exception:
            break_level = initial_price * 0.96
        setup_broke_any = any(
            (r.get("low") is not None and float(r["low"]) <= break_level)
            for r in future_rows
        )

        rec["outcome_5d"] = r5 or ""
        rec["outcome_10d"] = r10 or ""
        rec["outcome_20d"] = r20 or ""
        rec["outcome_30d"] = r30 or ""
        rec["max_favorable_move"] = f"{max_fav:.2f}%"
        rec["max_adverse_move"] = f"{max_adv:.2f}%"
        rec["setup_broke"] = "YES" if setup_broke_any else "NO"
        rec["data_status"] = "MATURE" if days_elapsed >= 5 else "PENDING"
        updated += 1

    # Rewrite entire ledger with updated rows.
    # Dry-run never writes; zero updates never rewrites (no-op safety).
    if dry_run or updated == 0:
        return updated

    _ensure_dir(ghost_path)
    with ghost_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=GHOST_FIELDS)
        writer.writeheader()
        for rec in records:
            # Ensure all fields present
            row = {f: rec.get(f, "") for f in GHOST_FIELDS}
            writer.writerow(row)

    return updated


def ghost_summary(ghost_path: Path = GHOST_LEDGER_PATH) -> dict[str, Any]:
    """Return aggregate summary of ghost ledger records."""
    records = load_ghost_ledger(ghost_path)
    total = len(records)
    if total == 0:
        return {"total_ghost_records": 0}

    matured = sum(1 for r in records if r.get("data_status", "").upper() == "MATURE")
    pending = sum(1 for r in records if r.get("data_status", "").upper() == "PENDING")
    insufficient = sum(1 for r in records if r.get("data_status", "").upper() == "INSUFFICIENT_DATA")

    # Group by rejection reason
    reasons: dict[str, list[str]] = {}
    for r in records:
        reason = r.get("rejection_reason", "UNKNOWN")
        if reason not in reasons:
            reasons[reason] = []
        reasons[reason].append(r.get("ghost_id", ""))

    # Top winners/losers among matured ghosts
    top_winners: list[dict[str, str]] = []
    top_losers: list[dict[str, str]] = []
    for r in records:
        if r.get("data_status", "").upper() != "MATURE":
            continue
        o20 = r.get("outcome_20d", "")
        if not o20:
            o10 = r.get("outcome_10d", "")
            if not o10:
                continue
            o20 = o10
        try:
            val = float(o20.replace("%", "").replace("+", ""))
        except Exception:
            continue
        entry = {"ghost_id": r.get("ghost_id", ""), "symbol": r.get("symbol", ""), "return_20d": o20}
        if val > 0:
            top_winners.append(entry)
        elif val < 0:
            top_losers.append(entry)

    top_winners.sort(key=lambda x: float(x["return_20d"].replace("%", "").replace("+", "")), reverse=True)
    top_losers.sort(key=lambda x: float(x["return_20d"].replace("%", "").replace("+", "")))

    # Check for unexpected winners
    unexpected_winners: list[dict[str, str]] = []
    for r in records:
        if r.get("data_status", "").upper() != "MATURE":
            continue
        o10 = r.get("outcome_10d", "")
        if not o10:
            continue
        try:
            val = float(o10.replace("%", "").replace("+", ""))
        except Exception:
            continue
        if val > 5.0:
            unexpected_winners.append({
                "ghost_id": r.get("ghost_id", ""),
                "symbol": r.get("symbol", ""),
                "rejection_reason": r.get("rejection_reason", ""),
                "return_10d": o10,
            })

    expected_losers: list[dict[str, str]] = []
    for r in records:
        if r.get("data_status", "").upper() != "MATURE":
            continue
        o10 = r.get("outcome_10d", "")
        if not o10:
            continue
        try:
            val = float(o10.replace("%", "").replace("+", ""))
        except Exception:
            continue
        if val < -5.0:
            expected_losers.append({
                "ghost_id": r.get("ghost_id", ""),
                "symbol": r.get("symbol", ""),
                "rejection_reason": r.get("rejection_reason", ""),
                "return_10d": o10,
            })

    return {
        "total_ghost_records": total,
        "matured_ghost_records": matured,
        "pending_ghost_records": pending,
        "insufficient_data_ghosts": insufficient,
        "rejection_reasons": {k: len(v) for k, v in reasons.items()},
        "top_ghost_winners": top_winners[:10],
        "top_ghost_losers": top_losers[:10],
        "unexpected_winners_count": len(unexpected_winners),
        "expected_losers_count": len(expected_losers),
        "rejection_reasons_with_unexpected_winners": list(
            set(e["rejection_reason"] for e in unexpected_winners)
        ),
    }


# ──────────────────────────────────────────────
# Observation pipeline rejection recording
# ──────────────────────────────────────────────

import hashlib
from typing import Callable

import pandas as pd


def _ghost_id_for_rejection(symbol: str, signal_date: str, setup_type: str, failed_gate: str, rejection_reason: str) -> str:
    """Deterministic ghost ID from rejection metadata. Not a random UUID."""
    raw = f"{symbol}|{signal_date}|{setup_type}|{failed_gate}|{rejection_reason}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _resolve_first_failed_gate(
    row: dict[str, Any],
    gates: list[tuple[str, Callable[[Any], bool], str, str]],
) -> tuple[str, str, str] | None:
    """Check gates in priority order. Returns (failed_gate_name, rejection_reason, score_str) or None if all pass."""
    for col_name, check_fn, gate_name, reason in gates:
        val = row.get(col_name)
        if val is None:
            # Column missing — can't determine
            continue
        try:
            fval = float(val)
        except (ValueError, TypeError):
            fval = float(bool(val))
        if not check_fn(fval):
            return gate_name, reason, str(val)
    return None


def record_observation_rejections(
    universe_df: pd.DataFrame,
    root: Path,
    strategy_id: str,
    setup_type: str,
    gates: list[tuple[str, Callable[[Any], bool], str, str]],
    ghost_path: Path = GHOST_LEDGER_PATH,
) -> int:
    """Append GhostRecord rows for non-selected symbols at the latest universe timestamp.

    This is a pure side-effect function. It does NOT modify the universe DataFrame,
    does NOT change which rows are selected, and does NOT affect observation generation.

    Parameters:
        universe_df: DataFrame with 'selected' column and per-timestamp signal data.
        root: Project root for GhostRecord creation.
        strategy_id: e.g. 'relative_strength_continuation'.
        setup_type: e.g. 'swing'.
        gates: Priority-ordered list of (column_name, pass_check_fn, gate_name, rejection_reason).
        ghost_path: Path to ghost ledger CSV.

    Returns:
        Number of new ghost records appended.
    """
    if universe_df.empty or "selected" not in universe_df.columns:
        return 0

    df = universe_df.copy()
    ts_col = None
    for c in ["timestamp", "signal_timestamp", "date", "datetime", "time"]:
        if c in df.columns:
            ts_col = c
            break
    if ts_col is None:
        return 0

    # Find latest timestamp
    try:
        ts = pd.to_datetime(df[ts_col], utc=True, errors="coerce")
        latest_ts = ts.max()
        if pd.isna(latest_ts):
            return 0
    except Exception:
        return 0

    latest = df[ts == latest_ts].copy()
    non_selected = latest[~latest["selected"].astype(bool)]

    if non_selected.empty:
        return 0

    records: list[GhostRecord] = []
    signal_date_str = str(latest_ts)

    for _, row in non_selected.iterrows():
        symbol = str(row.get("symbol", "")).upper()
        if not symbol:
            continue

        close_val = row.get("close")
        try:
            price = float(close_val) if close_val is not None else 0.0
        except (ValueError, TypeError):
            price = 0.0

        gate_result = _resolve_first_failed_gate(dict(row), gates)
        if gate_result is None:
            # Shouldn't happen since row is non-selected, but handle gracefully
            failed_gate = "unknown_gate"
            rejection_reason = "unknown_rejection"
            score_str = ""
        else:
            failed_gate, rejection_reason, score_str = gate_result

        ghost_id = _ghost_id_for_rejection(
            symbol, signal_date_str, setup_type, failed_gate, rejection_reason
        )

        record = build_ghost_record(
            ghost_id=ghost_id,
            source_observation_id="",
            symbol=symbol,
            strategy_id=strategy_id,
            setup_type=setup_type,
            signal_date=signal_date_str,
            rejection_reason=rejection_reason,
            failed_gate=failed_gate,
            score_if_available=score_str,
            price_at_signal=price,
            market_weather="",
        )
        records.append(record)

    return append_ghost_records(records, path=ghost_path)