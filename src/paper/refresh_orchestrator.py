from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class RefreshCommandResult:
    name: str
    command: list[str]
    returncode: int
    stdout_tail: str
    stderr_tail: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0


def run_command(
    name: str,
    command: list[str],
    cwd: Path,
    timeout_seconds: int = 900,
    env: dict[str, str] | None = None,
) -> RefreshCommandResult:
    import os as _os

    run_env = _os.environ.copy() if env is None else env
    run_env.setdefault("PYTHONPATH", f"{cwd}/.local/lib/python3.13/site-packages:{cwd}")

    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        env=run_env,
    )

    stdout_tail = "\n".join(proc.stdout.splitlines()[-80:])
    stderr_tail = "\n".join(proc.stderr.splitlines()[-80:])

    return RefreshCommandResult(
        name=name,
        command=command,
        returncode=proc.returncode,
        stdout_tail=stdout_tail,
        stderr_tail=stderr_tail,
    )


def load_candidate_freshness_snapshot(candidate_ledger: Path) -> dict[str, Any]:
    if not candidate_ledger.exists():
        raise FileNotFoundError(candidate_ledger)

    df = pd.read_csv(candidate_ledger)
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "timestamp" not in df.columns:
        raise ValueError("Candidate ledger missing timestamp")

    if "selected" not in df.columns:
        raise ValueError("Candidate ledger missing selected")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["selected"] = df["selected"].astype(bool)
    df = df.dropna(subset=["timestamp"])

    selected = df[df["selected"]].copy()

    latest_candidate_ts = df["timestamp"].max()
    latest_selected_ts = selected["timestamp"].max() if not selected.empty else None

    return {
        "candidate_rows": int(len(df)),
        "selected_rows": int(df["selected"].sum()),
        "rejected_rows": int((~df["selected"]).sum()),
        "latest_candidate_ts": latest_candidate_ts.isoformat(),
        "latest_selected_ts": latest_selected_ts.isoformat() if latest_selected_ts is not None else None,
    }


def append_refresh_log(
    log_path: Path,
    status: str,
    classification: str,
    snapshot: dict[str, Any],
    notes: str,
) -> dict[str, Any]:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    row = pd.DataFrame(
        [
            {
                "event_time": pd.Timestamp.utcnow().isoformat(),
                "status": status,
                "classification": classification,
                "candidate_rows": snapshot.get("candidate_rows"),
                "selected_rows": snapshot.get("selected_rows"),
                "rejected_rows": snapshot.get("rejected_rows"),
                "latest_candidate_ts": snapshot.get("latest_candidate_ts"),
                "latest_selected_ts": snapshot.get("latest_selected_ts"),
                "notes": notes,
            }
        ]
    )

    if log_path.exists():
        existing = pd.read_csv(log_path)
        combined = pd.concat([existing, row], axis=0, ignore_index=True)
    else:
        combined = row

    tmp = log_path.with_suffix(log_path.suffix + ".tmp")
    combined.to_csv(tmp, index=False)
    tmp.replace(log_path)

    return {
        "output_path": str(log_path),
        "events_written": 1,
        "total_events": int(len(combined)),
    }
