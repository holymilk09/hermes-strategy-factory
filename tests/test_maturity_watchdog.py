from pathlib import Path

import pandas as pd

from src.paper.maturity_watchdog import compute_maturity_status


def test_pending_maturity(tmp_path: Path):
    root = tmp_path

    data_dir = root / "data" / "cache" / "ohlcv_1d"
    data_dir.mkdir(parents=True)

    obs_dir = root / "data" / "paper_observation"
    obs_dir.mkdir(parents=True)

    obs_path = obs_dir / "relative_strength_continuation_observation_ledger.csv"

    obs = pd.DataFrame(
        {
            "observation_id": ["x"],
            "signal_timestamp": [pd.Timestamp("2026-05-20", tz="UTC")],
            "symbol": ["AMD"],
            "signal_close": [100.0],
            "outcome_window": [10],
            "outcome_status": ["PENDING"],
            "sent_to_broker": [False],
        }
    )
    obs.to_csv(obs_path, index=False)

    prices = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-05-20", periods=5, freq="D", tz="UTC"
            ),
            "open": [100] * 5,
            "high": [101] * 5,
            "low": [99] * 5,
            "close": [100] * 5,
            "volume": [1000] * 5,
        }
    )
    prices.to_csv(data_dir / "AMD.csv", index=False)

    result = compute_maturity_status(root, obs_path)

    assert result["classification"] == "PENDING_MATURITY"
    assert result["mature_count"] == 0


def test_outcomes_ready(tmp_path: Path):
    root = tmp_path

    data_dir = root / "data" / "cache" / "ohlcv_1d"
    data_dir.mkdir(parents=True)

    obs_dir = root / "data" / "paper_observation"
    obs_dir.mkdir(parents=True)

    obs_path = obs_dir / "relative_strength_continuation_observation_ledger.csv"

    obs = pd.DataFrame(
        {
            "observation_id": ["x"],
            "signal_timestamp": [pd.Timestamp("2026-05-20", tz="UTC")],
            "symbol": ["AMD"],
            "signal_close": [100.0],
            "outcome_window": [10],
            "outcome_status": ["PENDING"],
            "sent_to_broker": [False],
        }
    )
    obs.to_csv(obs_path, index=False)

    prices = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-05-20", periods=12, freq="D", tz="UTC"
            ),
            "open": [100] * 12,
            "high": [101] * 12,
            "low": [99] * 12,
            "close": [100] * 12,
            "volume": [1000] * 12,
        }
    )
    prices.to_csv(data_dir / "AMD.csv", index=False)

    result = compute_maturity_status(root, obs_path)

    assert result["classification"] == "OUTCOMES_READY"
    assert result["mature_count"] == 1
    assert result["ready_for_outcome_update"] is True


def test_broker_flag_hard_fail(tmp_path: Path):
    root = tmp_path

    obs_dir = root / "data" / "paper_observation"
    obs_dir.mkdir(parents=True)

    obs_path = obs_dir / "relative_strength_continuation_observation_ledger.csv"

    obs = pd.DataFrame(
        {
            "observation_id": ["x"],
            "signal_timestamp": [pd.Timestamp("2026-05-20", tz="UTC")],
            "symbol": ["AMD"],
            "signal_close": [100.0],
            "outcome_window": [10],
            "outcome_status": ["PENDING"],
            "sent_to_broker": [True],
        }
    )
    obs.to_csv(obs_path, index=False)

    result = compute_maturity_status(root, obs_path)

    assert result["classification"] == "WATCHDOG_HARD_FAIL_BROKER_FLAG"
