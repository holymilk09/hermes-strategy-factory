from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def build_shadow_monitor_event(
    status: str,
    classification: str,
    freshness: dict[str, Any],
    orders_written: int,
    notes: str,
) -> pd.DataFrame:
    row = {
        "event_time": pd.Timestamp.utcnow().isoformat(),
        "status": status,
        "classification": classification,
        "freshness_pass": freshness.get("pass"),
        "freshness_reason": freshness.get("reason"),
        "latest_candidate_ts": freshness.get("latest_candidate_ts"),
        "latest_selected_ts": freshness.get("latest_selected_ts"),
        "candidate_age_days": freshness.get("candidate_age_days"),
        "selected_age_days": freshness.get("selected_age_days"),
        "orders_written": orders_written,
        "notes": notes,
    }

    return pd.DataFrame([row])


def append_shadow_monitor_event(event: pd.DataFrame, output_path: Path) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        existing = pd.read_csv(output_path)
        combined = pd.concat([existing, event], axis=0, ignore_index=True)
    else:
        combined = event.copy()

    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    combined.to_csv(tmp, index=False)
    tmp.replace(output_path)

    return {
        "output_path": str(output_path),
        "events_written": int(len(event)),
        "total_events": int(len(combined)),
    }


def classify_shadow_ops(
    freshness: dict[str, Any],
    orders_written: int,
) -> str:
    if not freshness.get("pass"):
        return "SHADOW_READY_BUT_STALE_SOURCE"

    if orders_written == 0:
        return "SHADOW_READY_NO_SIGNALS"

    return "SHADOW_OBSERVATION_ACTIVE"
