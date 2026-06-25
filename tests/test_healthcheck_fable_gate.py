"""Phase 6L — Fable Gate Healthcheck Hardening Tests
Source-only regression tests. No data, no venv required.
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Allow importing the healthcheck script
_SCRIPTS_DIR = str(Path(__file__).resolve().parents[1] / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)


# ─── Test A: run_command preserves existing environment ──────────

def test_run_command_preserves_path():
    """run_command must inherit PATH/HOME from the parent process."""
    from run_feature_factory_healthcheck import run_command

    rc, stdout = run_command(["printenv", "PATH"], "test-path")
    assert rc == 0, f"printenv PATH failed: {stdout}"
    assert stdout.strip(), "PATH was empty — env was wiped"


def test_run_command_preserves_home():
    """run_command must preserve HOME from the parent process."""
    from run_feature_factory_healthcheck import run_command

    rc, stdout = run_command(["printenv", "HOME"], "test-home")
    assert rc == 0, f"printenv HOME failed: {stdout}"
    assert stdout.strip(), "HOME was empty — env was wiped"


def test_run_command_sets_pythonpath():
    """run_command must set PYTHONPATH to the project root."""
    from run_feature_factory_healthcheck import run_command, ROOT

    rc, stdout = run_command(
        ["python3", "-c", "import os; print(os.environ.get('PYTHONPATH', 'UNSET'))"],
        "test-pythonpath",
    )
    assert rc == 0, f"python3 -c failed: {stdout}"
    assert str(ROOT) in stdout, f"PYTHONPATH missing ROOT: {stdout.strip()}"


# ─── Test B: all_pass fails when ledger_parse_ok is False ────────

@pytest.fixture
def _mock_ledger_rows():
    """Valid observation rows for the observation ledger path."""
    return [
        {
            "observation_id": "6e506d15369deef3ea4d82ec",
            "symbol": "AMD",
            "outcome_status": "PENDING",
            "sent_to_broker": "false",
            "broker_order_id": "",
            "signal_date": "2026-05-01",
            "signal_close": "116.12",
        },
        {
            "observation_id": "d17b6c30f3bd58a0746592a5",
            "symbol": "ARM",
            "outcome_status": "PENDING",
            "sent_to_broker": "false",
            "broker_order_id": "",
            "signal_date": "2026-05-01",
            "signal_close": "126.88",
        },
        {
            "observation_id": "1eaba1549790ef85879bd98a",
            "symbol": "CRWD",
            "outcome_status": "PENDING",
            "sent_to_broker": "false",
            "broker_order_id": "",
            "signal_date": "2026-05-01",
            "signal_close": "380.60",
        },
        {
            "observation_id": "17fd3fa4ae84027e82b8b2fd",
            "symbol": "DDOG",
            "outcome_status": "PENDING",
            "sent_to_broker": "false",
            "broker_order_id": "",
            "signal_date": "2026-05-01",
            "signal_close": "111.60",
        },
        {
            "observation_id": "6c2f1eb80f83da084c393fb0",
            "symbol": "MRVL",
            "outcome_status": "PENDING",
            "sent_to_broker": "false",
            "broker_order_id": "",
            "signal_date": "2026-05-01",
            "signal_close": "55.00",
        },
        {
            "observation_id": "e9e478ad4f2034c2ad27d6e4",
            "symbol": "SEDG",
            "outcome_status": "PENDING",
            "sent_to_broker": "false",
            "broker_order_id": "",
            "signal_date": "2026-05-01",
            "signal_close": "14.83",
        },
        {
            "observation_id": "f6fda996fae00a3e35ed61c6",
            "symbol": "MRVL",
            "outcome_status": "PENDING",
            "sent_to_broker": "false",
            "broker_order_id": "",
            "signal_date": "2026-05-01",
            "signal_close": "58.00",
        },
    ]


def test_healthcheck_fails_when_ledger_parse_fails(_mock_ledger_rows):
    """When check_ledgers() returns FAIL for all ledgers, the final
    healthcheck decision must be HEALTHCHECK_FAIL_FIX_REQUIRED."""
    from run_feature_factory_healthcheck import main, ROOT, BACKUP_DIR

    fail_ledgers = {
        "data/paper_observation/relative_strength_continuation_observation_ledger.csv": ("FAIL", 0),
        "data/paper_observation/relative_strength_continuation_outcome_ledger.csv": ("FAIL", 0),
        "reports/strategy_factory/hypothesis_registry.csv": ("FAIL", 0),
    }

    def _fake_check_backup():
        return "backups/test.tar.gz", 2_000_000

    def _fake_run_command(cmd_parts, description):
        return 0, "OK"

    with (
        patch("run_feature_factory_healthcheck.check_ledgers", return_value=fail_ledgers),
        patch("run_feature_factory_healthcheck.check_backup", side_effect=_fake_check_backup),
        patch("run_feature_factory_healthcheck.run_command", side_effect=_fake_run_command),
        patch("run_feature_factory_healthcheck.parse_ledger", side_effect=lambda path: _mock_ledger_rows),
    ):
        from io import StringIO

        capture = StringIO()
        sys.stdout = capture
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__

        output = capture.getvalue()
        assert (
            "Decision: HEALTHCHECK_FAIL_FIX_REQUIRED" in output
        ), f"Expected FAIL_FIX_REQUIRED but got:\n{output}"