from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class CycleCommandResult:
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
) -> CycleCommandResult:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )

    return CycleCommandResult(
        name=name,
        command=command,
        returncode=proc.returncode,
        stdout_tail="\n".join(proc.stdout.splitlines()[-80:]),
        stderr_tail="\n".join(proc.stderr.splitlines()[-80:]),
    )


def read_observation_status(
    observation_ledger: Path,
    outcome_ledger: Path,
) -> dict[str, Any]:
    status: dict[str, Any] = {
        "observations_total": 0,
        "observations_pending": 0,
        "outcomes_total": 0,
        "outcomes_resolved": 0,
        "outcomes_pending": 0,
        "outcome_mean": None,
        "outcome_hit_rate": None,
        "latest_signal_ts": None,
        "sent_to_broker_any": False,
    }

    if observation_ledger.exists():
        obs = pd.read_csv(observation_ledger)

        if not obs.empty:
            obs.columns = [str(c).strip().lower() for c in obs.columns]

            status["observations_total"] = int(len(obs))

            if "outcome_status" in obs.columns:
                status["observations_pending"] = int(
                    obs["outcome_status"].astype(str).eq("PENDING").sum()
                )

            if "signal_timestamp" in obs.columns:
                ts = pd.to_datetime(obs["signal_timestamp"], utc=True, errors="coerce")
                if ts.notna().any():
                    status["latest_signal_ts"] = ts.max().isoformat()

            if "sent_to_broker" in obs.columns:
                status["sent_to_broker_any"] = bool(
                    obs["sent_to_broker"].astype(bool).any()
                )

    if outcome_ledger.exists():
        out = pd.read_csv(outcome_ledger)

        if not out.empty:
            out.columns = [str(c).strip().lower() for c in out.columns]

            status["outcomes_total"] = int(len(out))

            if "outcome_status" in out.columns:
                resolved = out[out["outcome_status"].astype(str).eq("RESOLVED")].copy()
                status["outcomes_resolved"] = int(len(resolved))
                status["outcomes_pending"] = int(len(out) - len(resolved))

                if "outcome_return" in resolved.columns:
                    r = pd.to_numeric(resolved["outcome_return"], errors="coerce").dropna()
                    if not r.empty:
                        status["outcome_mean"] = float(r.mean())
                        status["outcome_hit_rate"] = float((r > 0).mean())

            if "sent_to_broker" in out.columns:
                status["sent_to_broker_any"] = bool(
                    status["sent_to_broker_any"]
                    or out["sent_to_broker"].astype(bool).any()
                )

    return status


def append_cycle_log(
    log_path: Path,
    cycle_status: str,
    observation_result: CycleCommandResult,
    outcome_result: CycleCommandResult,
    status_snapshot: dict[str, Any],
) -> dict[str, Any]:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    row = pd.DataFrame(
        [
            {
                "event_time": pd.Timestamp.now("UTC").isoformat(),
                "cycle_status": cycle_status,
                "observation_returncode": observation_result.returncode,
                "outcome_returncode": outcome_result.returncode,
                "observations_total": status_snapshot.get("observations_total"),
                "observations_pending": status_snapshot.get("observations_pending"),
                "outcomes_total": status_snapshot.get("outcomes_total"),
                "outcomes_resolved": status_snapshot.get("outcomes_resolved"),
                "outcomes_pending": status_snapshot.get("outcomes_pending"),
                "outcome_mean": status_snapshot.get("outcome_mean"),
                "outcome_hit_rate": status_snapshot.get("outcome_hit_rate"),
                "latest_signal_ts": status_snapshot.get("latest_signal_ts"),
                "sent_to_broker_any": status_snapshot.get("sent_to_broker_any"),
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


def classify_cycle(
    observation_result: CycleCommandResult,
    outcome_result: CycleCommandResult,
    status_snapshot: dict[str, Any],
) -> str:
    if not observation_result.passed or not outcome_result.passed:
        return "OBSERVATION_CYCLE_FAIL"

    if status_snapshot.get("sent_to_broker_any"):
        return "OBSERVATION_CYCLE_HARD_FAIL_BROKER_FLAG"

    if status_snapshot.get("observations_total", 0) == 0:
        return "OBSERVATION_CYCLE_READY_NO_SIGNALS"

    if status_snapshot.get("outcomes_pending", 0) > 0:
        return "OBSERVATION_CYCLE_ACTIVE_PENDING"

    if status_snapshot.get("outcomes_resolved", 0) > 0:
        return "OBSERVATION_CYCLE_ACTIVE_RESOLVED"

    return "OBSERVATION_CYCLE_PASS"
