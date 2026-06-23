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


def test_juneteenth_not_counted_as_trading_bar(tmp_path: Path):
    """Verify Juneteenth 2026 is excluded from maturity future-bar count.

    Simulates MRVL scenario: signal_date=2026-06-05, outcome_window=10.
    Real Alpaca trading dates after June 5:
      Jun 6, 8, 9, 10, 11, 12, 15, 16, (skip 19=Juneteenth), 22, 23, 24

    With OHLCV through Jun 16: future_bars=7, bars_remaining=3, NOT mature.
    With OHLCV through Jun 22: future_bars=10, bars_remaining=0, mature.
    June 19 must NOT appear and must NOT count toward the 10-bar window.
    """
    root = tmp_path

    data_dir = root / "data" / "cache" / "ohlcv_1d"
    data_dir.mkdir(parents=True)

    obs_dir = root / "data" / "paper_observation"
    obs_dir.mkdir(parents=True)

    obs_path = obs_dir / "relative_strength_continuation_observation_ledger.csv"

    obs = pd.DataFrame(
        {
            "observation_id": ["f6fda996fae00a3e35ed61c6"],
            "signal_timestamp": [pd.Timestamp("2026-06-05", tz="UTC")],
            "symbol": ["MRVL"],
            "signal_close": [263.47],
            "outcome_window": [10],
            "outcome_status": ["PENDING"],
            "sent_to_broker": [False],
        }
    )
    obs.to_csv(obs_path, index=False)

    # ── Scenario A: OHLCV through Jun 16 (7 bars) ──
    # Real Alpaca trading dates after June 5 through June 16, 2026.
    # June 5 = Friday (signal). June 6-7 = weekend (skip).
    # June 8 (Mon), 9, 10, 11, 12, 15 (Mon), 16 (Tue) = 7 bars.
    bars_to_jun16 = pd.DataFrame(
        {
            "timestamp": pd.DatetimeIndex(
                [
                    "2026-06-05",  # signal day included
                    "2026-06-08",
                    "2026-06-09",
                    "2026-06-10",
                    "2026-06-11",
                    "2026-06-12",
                    "2026-06-15",
                    "2026-06-16",
                ],
                tz="UTC",
            ),
            "open": [260] * 8,
            "high": [262] * 8,
            "low": [259] * 8,
            "close": [261] * 8,
            "volume": [1000] * 8,
        }
    )
    bars_to_jun16.to_csv(data_dir / "MRVL.csv", index=False)

    result_a = compute_maturity_status(root, obs_path)
    assert result_a["classification"] == "PENDING_MATURITY"
    assert result_a["mature_count"] == 0
    assert result_a["pending_count"] == 1

    row_a = result_a["rows"][0]
    assert row_a["future_bars"] == 7, (
        f"Expected 7 future bars (through Jun 16), got {row_a['future_bars']}"
    )
    assert row_a["bars_remaining"] == 3, (
        f"Expected 3 remaining bars, got {row_a['bars_remaining']}"
    )
    assert row_a["mature"] is False

    # ── Scenario B: OHLCV through Jun 22 (10 bars) — maturity ──
    # Add Jun 17, 18, (skip 19 Juneteenth), 22 = 3 more bars → total 10.
    bars_through_jun22 = pd.DataFrame(
        {
            "timestamp": pd.DatetimeIndex(
                [
                    "2026-06-05",
                    "2026-06-08",
                    "2026-06-09",
                    "2026-06-10",
                    "2026-06-11",
                    "2026-06-12",
                    "2026-06-15",
                    "2026-06-16",
                    "2026-06-17",
                    "2026-06-18",
                    # June 19 DELIBERATELY ABSENT — Juneteenth holiday
                    "2026-06-22",
                ],
                tz="UTC",
            ),
            "open": [260] * 11,
            "high": [262] * 11,
            "low": [259] * 11,
            "close": [261] * 11,
            "volume": [1000] * 11,
        }
    )
    bars_through_jun22.to_csv(data_dir / "MRVL.csv", index=False)

    result_b = compute_maturity_status(root, obs_path)
    row_b = result_b["rows"][0]

    # Confirm June 19 is NOT in the OHLCV data
    timestamps_str = [
        "2026-06-19" for ts in bars_through_jun22["timestamp"] if ts.strftime("%Y-%m-%d") == "2026-06-19"
    ]
    assert len(timestamps_str) == 0, (
        "June 19 (Juneteenth) must NOT appear as a trading bar"
    )

    assert row_b["future_bars"] == 10, (
        f"Expected 10 future bars (through Jun 22), got {row_b['future_bars']}"
    )
    assert row_b["bars_remaining"] == 0
    assert row_b["mature"] is True

    assert result_b["classification"] == "OUTCOMES_READY"
    assert result_b["ready_for_outcome_update"] is True
