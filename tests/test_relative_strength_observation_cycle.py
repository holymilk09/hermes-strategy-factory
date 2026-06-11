from pathlib import Path

import pandas as pd

from src.paper.relative_strength_observation_cycle import (
    CycleCommandResult,
    append_cycle_log,
    classify_cycle,
    read_observation_status,
    run_command,
)


def test_run_command_success(tmp_path: Path):
    result = run_command(
        name="echo",
        command=["/opt/data/.venv/bin/python", "-c", "print('ok')"],
        cwd=tmp_path,
        timeout_seconds=10,
    )

    assert result.passed is True
    assert "ok" in result.stdout_tail


def test_read_observation_status_empty(tmp_path: Path):
    status = read_observation_status(
        observation_ledger=tmp_path / "obs.csv",
        outcome_ledger=tmp_path / "out.csv",
    )

    assert status["observations_total"] == 0
    assert status["outcomes_total"] == 0


def test_read_observation_status_with_rows(tmp_path: Path):
    obs_path = tmp_path / "obs.csv"
    out_path = tmp_path / "out.csv"

    obs = pd.DataFrame(
        {
            "observation_id": ["a"],
            "signal_timestamp": ["2026-05-20"],
            "outcome_status": ["PENDING"],
            "sent_to_broker": [False],
        }
    )
    obs.to_csv(obs_path, index=False)

    out = pd.DataFrame(
        {
            "observation_id": ["a"],
            "outcome_status": ["RESOLVED"],
            "outcome_return": [0.02],
        }
    )
    out.to_csv(out_path, index=False)

    status = read_observation_status(obs_path, out_path)

    assert status["observations_total"] == 1
    assert status["observations_pending"] == 1
    assert status["outcomes_resolved"] == 1
    assert status["outcome_mean"] == 0.02


def test_classify_cycle_ready_no_signals():
    ok = CycleCommandResult("x", ["x"], 0, "", "")
    status = {
        "sent_to_broker_any": False,
        "observations_total": 0,
        "outcomes_pending": 0,
        "outcomes_resolved": 0,
    }

    assert classify_cycle(ok, ok, status) == "OBSERVATION_CYCLE_READY_NO_SIGNALS"


def test_classify_cycle_active_pending():
    ok = CycleCommandResult("x", ["x"], 0, "", "")
    status = {
        "sent_to_broker_any": False,
        "observations_total": 6,
        "outcomes_pending": 6,
        "outcomes_resolved": 0,
    }

    assert classify_cycle(ok, ok, status) == "OBSERVATION_CYCLE_ACTIVE_PENDING"


def test_classify_cycle_active_resolved():
    ok = CycleCommandResult("x", ["x"], 0, "", "")
    status = {
        "sent_to_broker_any": False,
        "observations_total": 6,
        "outcomes_pending": 0,
        "outcomes_resolved": 6,
    }

    assert classify_cycle(ok, ok, status) == "OBSERVATION_CYCLE_ACTIVE_RESOLVED"


def test_append_cycle_log(tmp_path: Path):
    log = tmp_path / "cycle.csv"
    ok = CycleCommandResult("x", ["x"], 0, "", "")
    status = {
        "observations_total": 6,
        "observations_pending": 6,
        "outcomes_total": 6,
        "outcomes_resolved": 0,
        "outcomes_pending": 6,
        "outcome_mean": None,
        "outcome_hit_rate": None,
        "latest_signal_ts": "2026-05-20T04:00:00+00:00",
        "sent_to_broker_any": False,
    }

    result = append_cycle_log(log, "OBSERVATION_CYCLE_ACTIVE_PENDING", ok, ok, status)

    assert log.exists()
    assert result["total_events"] == 1
