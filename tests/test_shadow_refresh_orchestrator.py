from pathlib import Path

import pandas as pd

from src.paper.refresh_orchestrator import (
    append_refresh_log,
    load_candidate_freshness_snapshot,
    run_command,
)


def test_load_candidate_freshness_snapshot(tmp_path: Path):
    path = tmp_path / "candidate_ledger.csv"

    df = pd.DataFrame(
        {
            "timestamp": ["2026-05-01", "2026-05-02"],
            "symbol": ["AAPL", "MSFT"],
            "selected": [False, True],
        }
    )
    df.to_csv(path, index=False)

    snap = load_candidate_freshness_snapshot(path)

    assert snap["candidate_rows"] == 2
    assert snap["selected_rows"] == 1
    assert snap["rejected_rows"] == 1
    assert snap["latest_selected_ts"] is not None


def test_append_refresh_log(tmp_path: Path):
    path = tmp_path / "refresh_log.csv"

    snapshot = {
        "candidate_rows": 10,
        "selected_rows": 2,
        "rejected_rows": 8,
        "latest_candidate_ts": "2026-05-01T00:00:00+00:00",
        "latest_selected_ts": "2026-05-01T00:00:00+00:00",
    }

    result = append_refresh_log(
        log_path=path,
        status="PASS",
        classification="SHADOW_REFRESH_FRESH",
        snapshot=snapshot,
        notes="ok",
    )

    assert path.exists()
    assert result["total_events"] == 1

    result2 = append_refresh_log(
        log_path=path,
        status="PASS",
        classification="SHADOW_REFRESH_FRESH",
        snapshot=snapshot,
        notes="ok",
    )

    assert result2["total_events"] == 2


def test_run_command_success(tmp_path: Path):
    result = run_command(
        name="echo",
        command=["python3", "-c", "print('ok')"],
        cwd=tmp_path,
        timeout_seconds=10,
    )

    assert result.passed is True
    assert "ok" in result.stdout_tail
