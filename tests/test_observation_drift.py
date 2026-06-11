import pandas as pd
import pytest

from src.research.meta.observation_drift import (
    BacktestBenchmark,
    classify_observation_drift,
    compare_to_benchmark,
    next_action_from_classification,
    summarize_observation_state,
    summarize_resolved_outcomes,
)


def test_summarize_observation_state_pending():
    obs = pd.DataFrame(
        {
            "observation_id": ["a", "b"],
            "signal_timestamp": ["2026-05-20", "2026-05-20"],
            "outcome_status": ["PENDING", "PENDING"],
            "sent_to_broker": [False, False],
        }
    )

    out = pd.DataFrame(
        {
            "observation_id": ["a", "b"],
            "outcome_status": ["PENDING", "PENDING"],
        }
    )

    state = summarize_observation_state(obs, out)

    assert state["observations_total"] == 2
    assert state["resolved"] == 0
    assert state["pending"] == 2
    assert state["sent_to_broker_any"] is False


def test_summarize_resolved_outcomes():
    out = pd.DataFrame(
        {
            "outcome_status": ["RESOLVED", "RESOLVED", "PENDING"],
            "outcome_return": [0.02, -0.01, None],
        }
    )

    summary = summarize_resolved_outcomes(out)

    assert summary["resolved_count"] == 2
    assert summary["mean_return"] == 0.005
    assert summary["hit_rate"] == 0.5


def test_classify_pending_low_resolved():
    state = {"sent_to_broker_any": False}
    summary = {"resolved_count": 2, "mean_return": 0.10, "hit_rate": 1.0}

    result = classify_observation_drift(state, summary)

    assert result == "OBSERVATION_DRIFT_PENDING"


def test_classify_confirmed_early():
    state = {"sent_to_broker_any": False}
    summary = {"resolved_count": 6, "mean_return": 0.03, "hit_rate": 0.67}

    result = classify_observation_drift(state, summary)

    assert result == "FORWARD_OBSERVATION_CONFIRMED_EARLY"


def test_classify_mixed():
    state = {"sent_to_broker_any": False}
    summary = {"resolved_count": 6, "mean_return": 0.005, "hit_rate": 0.50}

    result = classify_observation_drift(state, summary)

    assert result == "FORWARD_OBSERVATION_MIXED"


def test_classify_weak():
    state = {"sent_to_broker_any": False}
    summary = {"resolved_count": 6, "mean_return": -0.01, "hit_rate": 0.33}

    result = classify_observation_drift(state, summary)

    assert result == "FORWARD_OBSERVATION_WEAK"


def test_broker_flag_hard_fail():
    state = {"sent_to_broker_any": True}
    summary = {"resolved_count": 6, "mean_return": 0.03, "hit_rate": 0.67}

    result = classify_observation_drift(state, summary)

    assert result == "OBSERVATION_DRIFT_HARD_FAIL_BROKER_FLAG"


def test_compare_to_benchmark():
    summary = {"resolved_count": 6, "mean_return": 0.016305, "hit_rate": 0.50}
    bench = BacktestBenchmark(historical_mean=0.03261, historical_hit_rate=0.5574)

    comparison = compare_to_benchmark(summary, bench)

    assert comparison["mean_capture_ratio"] == 0.5
    assert comparison["hit_delta"] < 0


def test_next_action_mapping():
    assert (
        next_action_from_classification("OBSERVATION_DRIFT_PENDING")
        == "WAIT_FOR_OUTCOMES"
    )
    assert (
        next_action_from_classification("FORWARD_OBSERVATION_CONFIRMED_EARLY")
        == "CONTINUE_FORWARD_OBSERVATION"
    )
    assert (
        next_action_from_classification("FORWARD_OBSERVATION_WEAK")
        == "PAUSE_ESCALATION_CONTINUE_OBSERVATION_ONLY"
    )
