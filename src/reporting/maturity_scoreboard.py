from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScoreboardRow:
    ticker: str
    signal_date: str
    observation_id: str
    initial_main_view: str
    initial_score: str
    initial_price: float
    price_area_that_matters: str
    setup_break_level: float
    current_price: float | None
    days_elapsed: int
    maturity_status: str
    result_5_day: str | None
    result_10_day: str | None
    result_20_day: str | None
    result_summary: str
    plain_english_result: str


def _to_dt(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def load_ohlcv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open() as f:
        rows = list(csv.DictReader(f))
    out: list[dict[str, Any]] = []
    for r in rows:
        date_raw = r.get("date") or r.get("timestamp") or r.get("datetime") or r.get("time")
        if not date_raw:
            continue
        try:
            dt = _to_dt(date_raw)
        except Exception:
            continue
        try:
            close = float(r.get("close") or "nan")
        except Exception:
            close = float("nan")
        low_val = r.get("low")
        try:
            low = float(low_val) if low_val not in (None, "") else close
        except Exception:
            low = close
        out.append({"dt": dt, "close": close, "low": low})
    out.sort(key=lambda x: x["dt"])
    return out


def checkpoint_result(initial_price: float, future_rows: list[dict[str, Any]], checkpoint: int) -> str | None:
    if len(future_rows) < checkpoint:
        return None
    px = future_rows[checkpoint - 1]["close"]
    ret = (px / initial_price - 1.0) * 100.0
    sign = "+" if ret >= 0 else ""
    return f"{sign}{ret:.2f}%"


def classify_maturity(days_elapsed: int, data_missing: bool, setup_broke: bool) -> str:
    if data_missing:
        return "Insufficient Data"
    if setup_broke:
        return "Setup Broke"
    if days_elapsed >= 20:
        return "20-Day Mature"
    if days_elapsed >= 10:
        return "10-Day Mature"
    if days_elapsed >= 5:
        return "5-Day Mature"
    return "Still Maturing"


def build_scoreboard_row(
    *,
    observation: dict[str, str],
    card: Any,
    ohlcv_rows: list[dict[str, Any]],
) -> ScoreboardRow:
    signal_date_raw = observation.get("signal_timestamp", "")
    signal_dt = _to_dt(signal_date_raw)

    future_rows = [r for r in ohlcv_rows if r["dt"] > signal_dt]
    days_elapsed = len(future_rows)

    initial_price = float(observation.get("signal_close") or 0.0)
    try:
        setup_break_level = float(card.setup_breaks_below)
    except Exception:
        setup_break_level = initial_price * 0.96

    current_price = future_rows[-1]["close"] if future_rows else (ohlcv_rows[-1]["close"] if ohlcv_rows else None)

    setup_broke = any((r.get("low") is not None and float(r["low"]) <= setup_break_level) for r in future_rows)

    data_missing = len(ohlcv_rows) == 0
    maturity_status = classify_maturity(days_elapsed, data_missing, setup_broke)

    r5 = checkpoint_result(initial_price, future_rows, 5)
    r10 = checkpoint_result(initial_price, future_rows, 10)
    r20 = checkpoint_result(initial_price, future_rows, 20)

    if days_elapsed < 5:
        r5 = None
    if days_elapsed < 10:
        r10 = None
    if days_elapsed < 20:
        r20 = None

    if data_missing:
        summary = "Insufficient Data"
        plain = "Price history is missing, so maturity and checkpoint results cannot be computed."
    elif setup_broke:
        summary = "Setup Broke"
        plain = "Price moved below the setup-break level before full maturity."
    elif days_elapsed < 5:
        summary = "Still Maturing"
        plain = "Fewer than 5 trading days have passed, so checkpoint results are not ready."
    else:
        summary = maturity_status
        parts = []
        if r5 is not None:
            parts.append(f"5-day {r5}")
        if r10 is not None:
            parts.append(f"10-day {r10}")
        if r20 is not None:
            parts.append(f"20-day {r20}")
        plain = "Checkpoint results available: " + ", ".join(parts) if parts else "Not enough proof yet."

    return ScoreboardRow(
        ticker=observation.get("symbol", ""),
        signal_date=signal_date_raw,
        observation_id=observation.get("observation_id", ""),
        initial_main_view=card.main_view,
        initial_score=card.score,
        initial_price=initial_price,
        price_area_that_matters=card.price_area_that_matters,
        setup_break_level=setup_break_level,
        current_price=current_price,
        days_elapsed=days_elapsed,
        maturity_status=maturity_status,
        result_5_day=r5,
        result_10_day=r10,
        result_20_day=r20,
        result_summary=summary,
        plain_english_result=plain,
    )
