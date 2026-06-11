from pathlib import Path

import pandas as pd

from src.paper.relative_strength_observation import (
    RelativeStrengthObservationConfig,
    build_observation_rows,
    latest_fresh_signals,
    resolve_observation_outcomes,
)


def test_latest_fresh_signals():
    as_of = pd.Timestamp("2026-05-20", tz="UTC")

    universe = pd.DataFrame(
        {
            "timestamp": ["2026-05-19", "2026-05-19"],
            "symbol": ["A", "B"],
            "selected": [True, False],
        }
    )

    selected, freshness = latest_fresh_signals(
        universe,
        as_of=as_of,
        config=RelativeStrengthObservationConfig(max_stale_calendar_days=5),
    )

    assert freshness["fresh"] is True
    assert len(selected) == 1


def test_build_observation_rows():
    selected = pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2026-05-19", tz="UTC")],
            "symbol": ["AAPL"],
            "close": [100.0],
            "ret_5d": [0.03],
            "ret_20d": [0.10],
            "ret_60d": [0.20],
            "ret_20d_rank": [0.90],
            "ret_60d_rank": [0.80],
            "close_above_ma50": [True],
        }
    )

    obs = build_observation_rows(selected)

    assert len(obs) == 1
    assert obs["outcome_status"].iloc[0] == "PENDING"
    assert bool(obs["sent_to_broker"].iloc[0]) is False
    assert obs["outcome_window"].iloc[0] == 10


def test_resolve_observation_outcomes(tmp_path: Path):
    root = tmp_path
    data_dir = root / "data" / "cache" / "ohlcv_1d"
    data_dir.mkdir(parents=True)

    prices = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-05-01", periods=20, tz="UTC"),
            "open": [100] * 20,
            "high": [101] * 20,
            "low": [99] * 20,
            "close": [100 + i for i in range(20)],
            "volume": [1000] * 20,
        }
    )
    prices.to_csv(data_dir / "AAPL.csv", index=False)

    obs_path = tmp_path / "obs.csv"
    out_path = tmp_path / "out.csv"

    obs = pd.DataFrame(
        {
            "observation_id": ["x"],
            "signal_timestamp": [pd.Timestamp("2026-05-01", tz="UTC")],
            "symbol": ["AAPL"],
            "signal_close": [100.0],
            "outcome_window": [10],
            "outcome_status": ["PENDING"],
        }
    )
    obs.to_csv(obs_path, index=False)

    result = resolve_observation_outcomes(obs_path, root, out_path)

    assert result["resolved"] == 1
    saved = pd.read_csv(out_path)
    assert saved["outcome_status"].iloc[0] == "RESOLVED"
