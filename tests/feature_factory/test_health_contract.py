from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HEALTHCHECK = ROOT / "scripts" / "run_feature_factory_healthcheck.py"


def _summary_fail_lines(stdout: str) -> list[str]:
    """Return the FAIL lines from the healthcheck summary block."""
    lines = []
    in_summary = False
    for line in stdout.splitlines():
        if "=== HEALTHCHECK SUMMARY ===" in line:
            in_summary = True
            continue
        if in_summary:
            if line.strip().startswith("Decision:"):
                break
            if line.strip().lower().startswith("fail"):
                lines.append(line.strip().lower())
    return lines


@pytest.mark.requires_data
@pytest.mark.requires_venv
def test_feature_factory_health_contract_remains_blocked_and_waiting():
    result = subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(HEALTHCHECK)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(ROOT)},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout.lower()

    # Phase 7C: the healthcheck now enforces a fail-closed universe freshness
    # floor (>= 50 fresh symbols). When current OHLCV data is stale, a FAIL
    # decision is CORRECT — but only the universe floor may be the cause.
    # Any other failing check is a real contract violation.
    if "decision: healthcheck_pass_continue_waiting" not in out:
        fails = _summary_fail_lines(result.stdout)
        assert fails, "FAIL decision but no failing summary lines found"
        assert all("universe freshness floor" in f for f in fails), (
            f"Healthcheck failed for reasons other than the universe "
            f"freshness floor: {fails}"
        )
        assert "decision: healthcheck_fail_fix_required" in out

    assert "production: blocked" in out
    assert "live: blocked" in out
    assert "broker: blocked" in out
    assert "shadow: blocked" in out
