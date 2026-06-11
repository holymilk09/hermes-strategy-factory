from pathlib import Path

import pandas as pd

from src.research.meta.hypothesis_registry import (
    LINEAGE_DEFINITIONS,
    build_hypothesis_registry,
    grade_from_classification,
    hypothesis_registry_to_dict,
    parse_value_field,
    status_from_classification,
)
from src.research.meta.observation_status import (
    OBSERVATION_SYSTEMS,
    build_observation_overlay,
    next_action_for_system,
    next_action_short,
    read_observation_status,
)


def test_parse_value_field():
    text = "final_classification: TRUE_WALK_FORWARD_WEAK_PASS\ndecision: Some decision\n"

    assert parse_value_field(text, "final_classification") == "TRUE_WALK_FORWARD_WEAK_PASS"
    assert parse_value_field(text, "decision") == "Some decision"


def test_grade_from_classification():
    assert grade_from_classification("TRUE_WALK_FORWARD_WEAK_PASS") == "B"
    assert grade_from_classification("TRUE_WALK_FORWARD_FAIL") == "F"
    assert grade_from_classification("REGIME_HOLDOUT_PASS_RESEARCH_ONLY") == "C+"
    assert grade_from_classification("TRUE_WALK_FORWARD_INCONCLUSIVE") == "D"


def test_status_from_classification():
    assert status_from_classification("TRUE_WALK_FORWARD_WEAK_PASS") == "Active observation"
    assert status_from_classification("TRUE_WALK_FORWARD_FAIL") == "Archived"
    assert status_from_classification("TRUE_WALK_FORWARD_INCONCLUSIVE") == "Archived low-power"


def test_build_hypothesis_registry(tmp_path: Path):
    # Create minimal decision files
    decision_dir = tmp_path / "reports" / "strategy_factory"
    decision_dir.mkdir(parents=True)

    (decision_dir / "relative_strength_continuation_decision.md").write_text(
        "final_classification: TRUE_WALK_FORWARD_WEAK_PASS\n"
        "decision: Some weak pass decision.\n"
    )
    (decision_dir / "sector_residual_mr_decision.md").write_text(
        "final_classification: TRUE_WALK_FORWARD_FAIL\n"
        "decision: Failed.\n"
    )

    graveyard = tmp_path / "filter_graveyard"
    graveyard.mkdir()
    (graveyard / "sector_residual_mr.md").write_text("archived")

    records = build_hypothesis_registry(tmp_path)

    # Should have entries from LINEAGE_DEFINITIONS that match existing files
    rs = [r for r in records if r.lineage == "relative_strength_continuation"]
    sr = [r for r in records if r.lineage == "sector_residual_mr"]

    assert len(rs) == 1
    assert rs[0].classification == "TRUE_WALK_FORWARD_WEAK_PASS"
    assert rs[0].grade == "B"

    assert len(sr) == 1
    assert sr[0].classification == "TRUE_WALK_FORWARD_FAIL"
    assert sr[0].grade == "F"
    assert sr[0].status == "Archived"


def test_read_observation_status(tmp_path: Path):
    obs_path = tmp_path / "obs.csv"
    out_path = tmp_path / "out.csv"

    obs = pd.DataFrame(
        {
            "observation_id": ["a", "b"],
            "signal_timestamp": ["2026-05-20", "2026-05-20"],
            "outcome_status": ["PENDING", "PENDING"],
            "sent_to_broker": [False, False],
        }
    )
    obs.to_csv(obs_path, index=False)

    out = pd.DataFrame(
        {
            "observation_id": ["a", "b"],
            "outcome_status": ["RESOLVED", "PENDING"],
            "outcome_return": [0.02, None],
        }
    )
    out.to_csv(out_path, index=False)

    status = read_observation_status(obs_path, out_path)

    assert status["observations_total"] == 2
    assert status["outcomes_total"] == 2
    assert status["outcomes_resolved"] == 1
    assert status["outcomes_pending"] == 1
    assert status["outcome_mean"] == 0.02


def test_next_action_for_system(tmp_path: Path):
    from src.research.meta.observation_status import ObservationSystemStatus

    mock = ObservationSystemStatus(
        name="test",
        observation_ledger_path="obs.csv",
        outcome_ledger_path="out.csv",
        cycle_log_path=None,
        observations_total=6,
        observations_pending=6,
        outcomes_total=6,
        outcomes_resolved=0,
        outcomes_pending=6,
        outcome_mean=None,
        outcome_hit_rate=None,
        latest_signal_ts="2026-05-20",
        sender_to_broker_any=False,
        cycle_status="OBSERVATION_CYCLE_ACTIVE_PENDING",
        cycle_events=1,
    )

    assert next_action_for_system(mock, "B") == "wait_for_outcome_resolution"
    assert next_action_short(mock, "B") == "Wait until 6 outcome(s) mature (~Jun 4)"


def test_hypothesis_registry_to_dict():
    from src.research.meta.hypothesis_registry import HypothesisRecord

    records = [
        HypothesisRecord(
            lineage="test",
            phase="1A",
            family="test_family",
            thesis="Test thesis",
            fixed_rule="test > 0",
            classification="TRUE_WALK_FORWARD_PASS",
            decision="Pass.",
            grade="B",
            status="Active observation",
            decision_source="test.md",
        )
    ]

    dicts = hypothesis_registry_to_dict(records)
    assert len(dicts) == 1
    assert dicts[0]["lineage"] == "test"
    assert dicts[0]["grade"] == "B"
