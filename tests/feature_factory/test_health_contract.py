from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEALTHCHECK = ROOT / "scripts" / "run_feature_factory_healthcheck.py"


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
    assert "decision: healthcheck_pass_continue_waiting" in out
    assert "production: blocked" in out
    assert "live: blocked" in out
    assert "broker: blocked" in out
    assert "shadow: blocked" in out
