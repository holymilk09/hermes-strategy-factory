from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ObservationSystemStatus:
    name: str
    observation_ledger_path: str
    outcome_ledger_path: str
    cycle_log_path: str | None
    observations_total: int
    observations_pending: int
    outcomes_total: int
    outcomes_resolved: int
    outcomes_pending: int
    outcome_mean: float | None
    outcome_hit_rate: float | None
    latest_signal_ts: str | None
    sender_to_broker_any: bool
    cycle_status: str | None
    cycle_events: int


OBSERVATION_SYSTEMS: list[dict[str, Any]] = [
    {
        "name": "relative_strength_continuation",
        "observation_ledger": "data/paper_observation/relative_strength_continuation_observation_ledger.csv",
        "outcome_ledger": "data/paper_observation/relative_strength_continuation_outcome_ledger.csv",
        "cycle_log": "data/paper_observation/relative_strength_observation_cycle_log.csv",
    },
    {
        "name": "regime_conditioned_capitulation_v2",
        "observation_ledger": "data/paper_observation/regime_conditioned_capitulation_v2_observation_ledger.csv",
        "outcome_ledger": "data/paper_observation/regime_conditioned_capitulation_v2_outcome_ledger.csv",
        "cycle_log": "data/paper_observation/forward_observation_cycle_log.csv",
    },
]


def read_observation_status(
    observation_ledger: Path,
    outcome_ledger: Path,
) -> dict[str, Any]:
    """Read observation and outcome ledgers to compile current status."""
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
        try:
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
        except Exception:
            pass

    if outcome_ledger.exists():
        try:
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
        except Exception:
            pass

    return status


def read_cycle_log_status(cycle_log: Path) -> dict[str, Any]:
    """Read the latest entry from a cycle log to get current cycle status."""
    result: dict[str, Any] = {
        "cycle_status": None,
        "cycle_events": 0,
    }

    if not cycle_log.exists():
        return result

    try:
        df = pd.read_csv(cycle_log)

        if df.empty:
            return result

        result["cycle_events"] = int(len(df))

        last = df.iloc[-1]
        if "cycle_status" in last:
            result["cycle_status"] = str(last["cycle_status"])
    except Exception:
        pass

    return result


def build_observation_overlay(
    root: Path,
) -> list[ObservationSystemStatus]:
    """Build live observation overlay for all registered observation systems."""
    results: list[ObservationSystemStatus] = []

    for sys_def in OBSERVATION_SYSTEMS:
        name = sys_def["name"]
        obs_path = root / sys_def["observation_ledger"]
        out_path = root / sys_def["outcome_ledger"]

        status = read_observation_status(obs_path, out_path)

        cycle_status = None
        cycle_events = 0
        if sys_def.get("cycle_log"):
            cycle_path = root / sys_def["cycle_log"]
            cycle_info = read_cycle_log_status(cycle_path)
            cycle_status = cycle_info["cycle_status"]
            cycle_events = cycle_info["cycle_events"]

        results.append(
            ObservationSystemStatus(
                name=name,
                observation_ledger_path=str(obs_path),
                outcome_ledger_path=str(out_path),
                cycle_log_path=str(root / sys_def["cycle_log"]) if sys_def.get("cycle_log") else None,
                observations_total=status["observations_total"],
                observations_pending=status["observations_pending"],
                outcomes_total=status["outcomes_total"],
                outcomes_resolved=status["outcomes_resolved"],
                outcomes_pending=status["outcomes_pending"],
                outcome_mean=status["outcome_mean"],
                outcome_hit_rate=status["outcome_hit_rate"],
                latest_signal_ts=status["latest_signal_ts"],
                sender_to_broker_any=status["sent_to_broker_any"],
                cycle_status=cycle_status,
                cycle_events=cycle_events,
            )
        )

    return results


def next_action_for_system(
    status: ObservationSystemStatus,
    hypothesis_grade: str,
) -> str:
    """Determine the next allowed action for an observation system."""
    if status.sender_to_broker_any:
        return "HARD_FAIL_BROKER_FLAG"

    if status.observations_total == 0 and hypothesis_grade == "F":
        return "archived_no_rescue"

    if status.observations_total == 0:
        return "wait_for_signal_generation"

    if status.outcomes_pending > 0 and status.outcomes_resolved == 0:
        return "wait_for_outcome_resolution"

    if status.outcomes_resolved > 0 and status.outcomes_pending > 0:
        return "partial_outcomes_resolved_wait_for_remaining"

    if status.outcomes_resolved > 0 and status.outcomes_pending == 0:
        if hypothesis_grade in ("B", "C+"):
            return "forward_observation_active_review_next_hypothesis"
        return "review_outcomes_before_proceeding"

    return "unknown_state"


def next_action_short(status: ObservationSystemStatus, hypothesis_grade: str) -> str:
    """Short human-readable next action."""
    if status.sender_to_broker_any:
        return "BROKER_FLAG — investigate immediately"

    if status.observations_total == 0 and hypothesis_grade == "F":
        return "Archived — no action"

    if status.observations_total == 0:
        return "No signals yet — wait for market data"

    if status.outcomes_pending > 0 and status.outcomes_resolved == 0:
        return f"Wait until {status.outcomes_pending} outcome(s) mature (~Jun 4)"

    if status.outcomes_resolved > 0 and status.outcomes_pending > 0:
        return f"Partial outcomes ({status.outcomes_resolved} resolved, {status.outcomes_pending} pending)"

    if status.outcomes_resolved > 0 and status.outcomes_pending == 0:
        if hypothesis_grade in ("B", "C+"):
            return "Outcomes complete — evaluate next hypothesis or variant"

        return "Outcomes complete — review before further action"

    return "Unknown state"
