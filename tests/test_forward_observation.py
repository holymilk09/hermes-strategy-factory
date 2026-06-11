from pathlib import Path

import pandas as pd

from src.paper.forward_observation import (
    ForwardObservationConfig,
    build_observation_rows,
    close_location,
    compute_spy_drawdown_60d,
    latest_fresh_signals,
    resolve_observation_outcomes,
)


def test_close_location():
    df = pd.DataFrame(
        {
            "high": [10],
            "low": [0],
            "close": [7],
        }
    )

    loc = close_location(df)

    assert loc.iloc[0] == 0.7


def test_compute_spy_drawdown_60d():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=100, tz="UTC"),
            "close": list(range(100, 200)),
        }
    )

    out = compute_spy_drawdown_60d(df)

    assert "spy_drawdown_60d" in out.columns
    assert out["spy_drawdown_60d"].notna().sum() > 0


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
        config=ForwardObservationConfig(max_stale_calendar_days=5),
    )

    assert freshness["fresh"] is True
    assert len(selected) == 1


def test_build_observation_rows():
    selected = pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2026-05-19", tz="UTC")],
            "symbol": ["AAPL"],
            "close": [100.0],
            "ret_3d_z": [-2.0],
            "volume_z_20": [1.5],
            "close_location": [0.7],
            "spy_drawdown_60d": [-0.05],
        }
    )

    obs = build_observation_rows(selected)

    assert len(obs) == 1
    assert obs["outcome_status"].iloc[0] == "PENDING"
    assert bool(obs["sent_to_broker"].iloc[0]) is False


def test_resolve_observation_outcomes(tmp_path: Path):
    root = tmp_path
    data_dir = root / "data" / "cache" / "ohlcv_1d"
    data_dir.mkdir(parents=True)

    prices = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-05-01", periods=10, tz="UTC"),
            "open": [100] * 10,
            "high": [101] * 10,
            "low": [99] * 10,
            "close": [100, 101, 102, 103, 104, 110, 111, 112, 113, 114],
            "volume": [1000] * 10,
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
            "outcome_window": [5],
            "outcome_status": ["PENDING"],
        }
    )
    obs.to_csv(obs_path, index=False)

    result = resolve_observation_outcomes(obs_path, root, out_path)

    assert result["resolved"] == 1
    saved = pd.read_csv(out_path)
    assert saved["outcome_status"].iloc[0] == "RESOLVED"
