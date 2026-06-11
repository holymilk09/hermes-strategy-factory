import pandas as pd

from src.paper.freshness_gates import (
    FreshnessConfig,
    evaluate_candidate_freshness,
    filter_latest_fresh_selected_candidates,
)
from src.paper.shadow_monitor import classify_shadow_ops


def test_freshness_passes_recent_selected_signal():
    as_of = pd.Timestamp("2026-05-10", tz="UTC")

    df = pd.DataFrame(
        {
            "timestamp": ["2026-05-09"],
            "symbol": ["AAPL"],
            "selected": [True],
        }
    )

    result = evaluate_candidate_freshness(
        df,
        as_of=as_of,
        config=FreshnessConfig(max_stale_calendar_days=5),
    )

    assert result["pass"] is True
    assert result["reason"] == "FRESH"


def test_freshness_blocks_stale_candidate_ledger():
    as_of = pd.Timestamp("2026-05-10", tz="UTC")

    df = pd.DataFrame(
        {
            "timestamp": ["2026-04-01"],
            "symbol": ["AAPL"],
            "selected": [True],
        }
    )

    result = evaluate_candidate_freshness(
        df,
        as_of=as_of,
        config=FreshnessConfig(max_stale_calendar_days=5),
    )

    assert result["pass"] is False
    assert result["reason"] == "STALE_CANDIDATE_LEDGER"


def test_freshness_blocks_missing_selected_signal():
    as_of = pd.Timestamp("2026-05-10", tz="UTC")

    df = pd.DataFrame(
        {
            "timestamp": ["2026-05-09"],
            "symbol": ["AAPL"],
            "selected": [False],
        }
    )

    result = evaluate_candidate_freshness(
        df,
        as_of=as_of,
        config=FreshnessConfig(max_stale_calendar_days=5),
    )

    assert result["pass"] is False
    assert result["reason"] == "STALE_OR_MISSING_SELECTED_SIGNAL"


def test_filter_latest_fresh_selected_candidates():
    as_of = pd.Timestamp("2026-05-10", tz="UTC")

    df = pd.DataFrame(
        {
            "timestamp": ["2026-05-08", "2026-05-09", "2026-05-09"],
            "symbol": ["AAPL", "MSFT", "NVDA"],
            "selected": [True, True, False],
        }
    )

    latest, freshness = filter_latest_fresh_selected_candidates(
        df,
        as_of=as_of,
        config=FreshnessConfig(max_stale_calendar_days=5),
    )

    assert freshness["pass"] is True
    assert len(latest) == 1
    assert latest["symbol"].iloc[0] == "MSFT"


def test_classify_shadow_ops_stale():
    freshness = {"pass": False}

    result = classify_shadow_ops(freshness, orders_written=0)

    assert result == "SHADOW_READY_BUT_STALE_SOURCE"


def test_classify_shadow_ops_no_signals():
    freshness = {"pass": True}

    result = classify_shadow_ops(freshness, orders_written=0)

    assert result == "SHADOW_READY_NO_SIGNALS"


def test_classify_shadow_ops_active():
    freshness = {"pass": True}

    result = classify_shadow_ops(freshness, orders_written=2)

    assert result == "SHADOW_OBSERVATION_ACTIVE"
