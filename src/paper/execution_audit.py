from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def build_execution_audit_event(
    event_type: str,
    status: str,
    notes: str,
    metadata: dict[str, Any] | None = None,
) -> pd.DataFrame:
    metadata = metadata or {}

    row = {
        "event_time": pd.Timestamp.utcnow().isoformat(),
        "event_type": event_type,
        "status": status,
        "notes": notes,
        "metadata": str(metadata),
    }

    return pd.DataFrame([row])


def append_execution_audit_event(event: pd.DataFrame, output_path: Path) -> dict[str, Any]:
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
