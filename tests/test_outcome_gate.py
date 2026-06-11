from pathlib import Path

import pandas as pd
import pytest

from src.research.meta.outcome_gate import (
    PHASE28A_EXPECTED_MEAN,
    PHASE28A_EXPECTED_HIT,
    OutcomeGateResult,
    classify_outcome_gate,
    compute_outcome_metrics,
    determine_next_action,
    read_outcome_ledger,
    run_outcome_gate,
)


def test_read_outcome_ledger_empty(tmp_path: Path):
    df = read_outcome_ledger(tmp_path / "nonexistent.csv")
    assert df.empty


def test_read_outcome_ledger_with_data(tmp_path: Path):
    path = tmp_path / "ledger.csv"
    pd.DataFrame(
        {
            "outcome_status": ["PENDING", "PENDING"],
            "outcome_return": [None, None],
            "sent_to_broker": [False, False],
        }
    ).to_csv(path, index=False)

    df = read_outcome_ledger(path)
    assert not df.empty
    assert len(df) == 2


def test_compute_outcome_metrics_all_pending():
    ledger = pd.DataFrame(
        {
            "outcome_status": ["PENDING", "PENDING"],
            "outcome_return": [None, None],
            "sent_to_broker": [False, False],
        }
    )

    metrics = compute_outcome_metrics(ledger)

    assert metrics["total"] == 2
    assert metrics["pending"] == 2
    assert metrics["resolved"] == 0
    assert metrics["mean_return"] is None


def test_compute_outcome_metrics_partial():
    ledger = pd.DataFrame(
        {
            "outcome_status": ["RESOLVED", "PENDING"],
            "outcome_return": [0.04, None],
            "sent_to_broker": [False, False],
        }
    )

    metrics = compute_outcome_metrics(ledger)

    assert metrics["total"] == 2
    assert metrics["resolved"] == 1
    assert metrics["pending"] == 1
    assert metrics["mean_return"] == 0.04
    assert metrics["hit_rate"] == 1.0


def test_compute_outcome_metrics_all_resolved():
    ledger = pd.DataFrame(
        {
            "outcome_status": ["RESOLVED", "RESOLVED", "RESOLVED"],
            "outcome_return": [0.05, -0.01, 0.03],
            "sent_to_broker": [False, False, False],
        }
    )

    metrics = compute_outcome_metrics(ledger)

    assert metrics["total"] == 3
    assert metrics["resolved"] == 3
    assert metrics["pending"] == 0
    assert metrics["mean_return"] == pytest.approx(0.02333, rel=1e-3)
    assert metrics["hit_rate"] == pytest.approx(2 / 3)


def test_classify_outcome_gate_pending():
    metrics = {"pending": 3, "resolved": 0, "mean_return": None, "hit_rate": None}
    assert classify_outcome_gate(metrics) == "OUTCOME_GATE_PENDING"


def test_classify_outcome_gate_confirmed():
    metrics = {"pending": 0, "resolved": 6, "mean_return": 0.025, "hit_rate": 0.55}
    assert classify_outcome_gate(metrics) == "FORWARD_OBSERVATION_CONFIRMED_EARLY"


def test_classify_outcome_gate_mixed():
    metrics = {"pending": 0, "resolved": 6, "mean_return": 0.01, "hit_rate": 0.50}
    assert classify_outcome_gate(metrics) == "FORWARD_OBSERVATION_MIXED"


def test_classify_outcome_gate_weak():
    metrics = {"pending": 0, "resolved": 6, "mean_return": -0.01, "hit_rate": 0.30}
    assert classify_outcome_gate(metrics) == "FORWARD_OBSERVATION_WEAK"


def test_determine_next_action():
    assert determine_next_action("OUTCOME_GATE_PENDING") == "WAIT_FOR_OUTCOMES"
    assert determine_next_action("FORWARD_OBSERVATION_CONFIRMED_EARLY") == "PAPER_SHADOW_DESIGN_REVIEW_ONLY"
    assert determine_next_action("FORWARD_OBSERVATION_MIXED") == "CONTINUE_FORWARD_OBSERVATION"
    assert determine_next_action("FORWARD_OBSERVATION_WEAK") == "CONTINUE_FORWARD_OBSERVATION"


def test_run_outcome_gate(tmp_path):
    lineage = "relative_strength_continuation"

    obs_dir = tmp_path / "data" / "paper_observation"
    obs_dir.mkdir(parents=True)

    # Write outcome ledger with all PENDING
    pd.DataFrame(
        {
            "outcome_status": ["PENDING"] * 6,
            "outcome_return": [None] * 6,
            "sent_to_broker": [False] * 6,
        }
    ).to_csv(obs_dir / f"{lineage}_outcome_ledger.csv", index=False)

    # Write observation ledger with all PENDING
    pd.DataFrame(
        {
            "outcome_status": ["PENDING"] * 6,
            "sent_to_broker": [False] * 6,
            "observation_id": [str(i) for i in range(6)],
            "signal_timestamp": ["2026-05-20"] * 6,
            "symbol": ["A"] * 6,
        }
    ).to_csv(obs_dir / f"{lineage}_observation_ledger.csv", index=False)

    result = run_outcome_gate(tmp_path, lineage=lineage)

    assert result.classification == "OUTCOME_GATE_PENDING"
    assert result.next_action == "WAIT_FOR_OUTCOMES"
    assert result.total == 6
    assert result.pending == 6
    assert result.resolved == 0


def test_run_outcome_gate_resolved(tmp_path):
    lineage = "relative_strength_continuation"

    obs_dir = tmp_path / "data" / "paper_observation"
    obs_dir.mkdir(parents=True)

    pd.DataFrame(
        {
            "outcome_status": ["RESOLVED"] * 6,
            "outcome_return": [0.04, 0.02, 0.01, -0.01, 0.03, 0.05],
            "sent_to_broker": [False] * 6,
        }
    ).to_csv(obs_dir / f"{lineage}_outcome_ledger.csv", index=False)

    pd.DataFrame(
        {
            "outcome_status": ["RESOLVED"] * 6,
            "sent_to_broker": [False] * 6,
            "observation_id": [str(i) for i in range(6)],
            "signal_timestamp": ["2026-05-20"] * 6,
            "symbol": ["A"] * 6,
        }
    ).to_csv(obs_dir / f"{lineage}_observation_ledger.csv", index=False)

    result = run_outcome_gate(tmp_path, lineage=lineage)

    assert result.classification == "FORWARD_OBSERVATION_CONFIRMED_EARLY"
    assert result.next_action == "PAPER_SHADOW_DESIGN_REVIEW_ONLY"
    assert result.total == 6
    assert result.resolved == 6
    assert result.mean_return == pytest.approx(0.02333, rel=1e-3)
    assert result.hit_rate == pytest.approx(5 / 6)
