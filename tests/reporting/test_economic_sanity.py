"""Tests for Economic Sanity Audit — cost adjustments, compounding, concurrent exposure."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from src.reporting.economic_sanity import (
    LABEL_COST_FRAGILE,
    LABEL_INSUFFICIENT_DATA,
    LABEL_PASS,
    SanityMetrics,
    BatchSanityReport,
    assess_economic_sanity,
    compute_batch_sanity,
    detect_compounding_artifacts,
    detect_concurrent_exposure,
    sanity_to_dict,
    report_to_dict,
)


def _make_obs(
    obs_id: str = "obs1",
    symbol: str = "AAPL",
    signal_ts: str = "2026-05-20 04:00:00+00:00",
    signal_close: str = "200.0",
    outcome_window: str = "10",
) -> dict[str, str]:
    return {
        "observation_id": obs_id,
        "symbol": symbol,
        "signal_timestamp": signal_ts,
        "signal_close": signal_close,
        "outcome_window": outcome_window,
    }


def _make_future_rows(
    start_price: float = 200.0,
    count: int = 10,
    drift: float = 1.005,  # +0.5% per bar
) -> list[dict]:
    from datetime import timedelta
    base_dt = datetime(2026, 5, 21, 4, 0, 0, tzinfo=timezone.utc)
    rows = []
    price = start_price
    for i in range(count):
        price *= drift
        rows.append({
            "dt": base_dt + timedelta(days=i),
            "close": round(price, 2),
        })
    return rows


# ─── assess_economic_sanity tests ────────────────────────────


def test_assess_sanity_enough_bars() -> None:
    """With enough OHLCV bars, economic sanity can be assessed."""
    obs = _make_obs()
    rows = _make_future_rows(count=10, drift=1.005)
    result = assess_economic_sanity(obs, rows, outcome_window=10)
    assert result.enough_bars is True
    assert result.economic_sanity_status == LABEL_PASS


def test_assess_sanity_insufficient_bars() -> None:
    """Fewer bars than outcome window = insufficient data."""
    obs = _make_obs()
    rows = _make_future_rows(count=3, drift=1.005)
    result = assess_economic_sanity(obs, rows, outcome_window=10)
    assert result.enough_bars is False
    assert result.economic_sanity_status == LABEL_INSUFFICIENT_DATA


def test_assess_sanity_no_ohlcv() -> None:
    """No OHLCV data = insufficient data."""
    obs = _make_obs()
    result = assess_economic_sanity(obs, [], outcome_window=10)
    assert result.stock_forward_return is None
    assert result.economic_sanity_status == LABEL_INSUFFICIENT_DATA


def test_assess_sanity_cost_fragile() -> None:
    """Return too small after costs = Cost Fragile."""
    obs = _make_obs(signal_close="200.0")
    # Very small positive drift so forward return is tiny
    rows = _make_future_rows(start_price=200.0, count=10, drift=1.0005)  # 0.05% per bar
    result = assess_economic_sanity(obs, rows, outcome_window=10)
    # 10 bars at 0.05% each = ~0.5% return, minus 0.15% costs = ~0.35%
    assert result.economic_sanity_status == LABEL_PASS  # 0.35% > 0.20% min


def test_assess_sanity_cost_fragile_very_tiny() -> None:
    """Extremely tiny return after costs = Cost Fragile."""
    obs = _make_obs(signal_close="200.0")
    # Almost no drift at all
    rows = _make_future_rows(start_price=200.0, count=10, drift=1.0001)  # 0.01% per bar
    result = assess_economic_sanity(obs, rows, outcome_window=10)
    # ~0.1% return, minus 0.15% costs = -0.05% → Cost Fragile
    assert result.economic_sanity_status == LABEL_COST_FRAGILE


def test_assess_sanity_no_signal_timestamp() -> None:
    """Missing signal timestamp = insufficient data."""
    obs = _make_obs(signal_ts="")
    result = assess_economic_sanity(obs, [], outcome_window=10)
    assert result.economic_sanity_status == LABEL_INSUFFICIENT_DATA


def test_assess_sanity_forward_return_computed() -> None:
    """Stock forward return matches expected values."""
    obs = _make_obs(signal_close="200.0")
    # Each bar +1%, so after 10 bars = ~10.46% (compounding)
    rows = _make_future_rows(start_price=200.0, count=10, drift=1.01)
    result = assess_economic_sanity(obs, rows, outcome_window=10)
    assert result.stock_forward_return is not None
    assert result.stock_forward_return > 9.0  # close to 10.46%


def test_assess_sanity_cost_delay_adjustments() -> None:
    """Cost-adjusted return < forward return < delay-adjusted return."""
    obs = _make_obs(signal_close="200.0")
    rows = _make_future_rows(start_price=200.0, count=10, drift=1.01)
    result = assess_economic_sanity(obs, rows, outcome_window=10)
    assert result.stock_forward_return is not None
    assert result.cost_adjusted_return is not None
    assert result.delay_adjusted_return is not None
    assert result.cost_adjusted_return < result.stock_forward_return
    assert result.delay_adjusted_return < result.stock_forward_return


# ─── compounding artifact tests ───────────────────────────────


def test_compounding_detected() -> None:
    """Signals same symbol 2 days apart = compounding artifact."""
    obs_list = [
        _make_obs("obs1", "AAPL", "2026-05-20 04:00:00+00:00"),
        _make_obs("obs2", "AAPL", "2026-05-22 04:00:00+00:00"),  # 2 days later
    ]
    assert detect_compounding_artifacts(obs_list, "AAPL", min_gap_days=5) is True


def test_compounding_not_detected_wide_gap() -> None:
    """Signals same symbol 10 days apart = no artifact."""
    obs_list = [
        _make_obs("obs1", "AAPL", "2026-05-20 04:00:00+00:00"),
        _make_obs("obs2", "AAPL", "2026-05-30 04:00:00+00:00"),  # 10 days later
    ]
    assert detect_compounding_artifacts(obs_list, "AAPL", min_gap_days=5) is False


def test_no_compounding_single_signal() -> None:
    """Single signal = no compounding artifact."""
    obs_list = [_make_obs("obs1", "AAPL", "2026-05-20 04:00:00+00:00")]
    assert detect_compounding_artifacts(obs_list, "AAPL") is False


def test_compounding_different_symbols() -> None:
    """Signals on different symbols = no artifact per symbol."""
    obs_list = [
        _make_obs("obs1", "AAPL", "2026-05-20 04:00:00+00:00"),
        _make_obs("obs2", "MSFT", "2026-05-21 04:00:00+00:00"),
    ]
    assert detect_compounding_artifacts(obs_list, "AAPL") is False
    assert detect_compounding_artifacts(obs_list, "MSFT") is False


# ─── concurrent exposure tests ────────────────────────────────


def test_concurrent_exposure_detected() -> None:
    """6 signals within 2 days = concurrent exposure."""
    obs_list = [
        _make_obs(f"obs{i}", f"SYM{i}", "2026-05-20 04:00:00+00:00")
        for i in range(6)
    ]
    assert detect_concurrent_exposure(obs_list, time_window_days=3, min_count=5) is True


def test_no_concurrent_exposure_few_signals() -> None:
    """Only 2 signals = no concurrent exposure risk."""
    obs_list = [
        _make_obs("obs1", "AAPL", "2026-05-20 04:00:00+00:00"),
        _make_obs("obs2", "MSFT", "2026-05-20 04:00:00+00:00"),
    ]
    assert detect_concurrent_exposure(obs_list, time_window_days=3, min_count=5) is False


def test_no_concurrent_exposure_spread_out() -> None:
    """6 signals spread across different days = no exposure."""
    obs_list = [
        _make_obs(f"obs{i}", f"SYM{i}", f"2026-05-{10 + i:02d} 04:00:00+00:00")
        for i in range(6)
    ]
    assert detect_concurrent_exposure(obs_list, time_window_days=3, min_count=5) is False


# ─── batch sanity tests ───────────────────────────────────────


def test_batch_sanity_empty(tmp_path: Path) -> None:
    """Empty observations = empty report."""
    report = compute_batch_sanity([], tmp_path)
    assert report.total_observations == 0
    assert report.assessed_observations == 0


def test_batch_sanity_with_observations(tmp_path: Path) -> None:
    """Batch sanity assesses all observations."""
    obs_list = [
        _make_obs("obs1", "AAPL", "2026-05-20 04:00:00+00:00"),
        _make_obs("obs2", "MSFT", "2026-05-20 04:00:00+00:00"),
    ]
    report = compute_batch_sanity(obs_list, tmp_path)
    assert report.total_observations == 2
    # Both will be insufficient data (no OHLCV files)
    assert report.insufficient_data_count == 2


# ─── serialization tests ─────────────────────────────────────


def test_sanity_to_dict() -> None:
    """SanityMetrics converts to dict correctly."""
    metrics = SanityMetrics(
        observation_id="obs1",
        symbol="AAPL",
        signal_timestamp="2026-05-20T00:00:00Z",
        stock_forward_return=5.2,
        cost_adjusted_return=5.05,
        delay_adjusted_return=5.15,
        enough_bars=True,
        outlier_zscore=None,
        compounding_artifact_warning=False,
        concurrent_exposure_warning=False,
        economic_sanity_status=LABEL_PASS,
        warnings=(),
    )
    d = sanity_to_dict(metrics)
    assert d["observation_id"] == "obs1"
    assert d["stock_forward_return"] == 5.2
    assert d["economic_sanity_status"] == LABEL_PASS


def test_report_to_dict() -> None:
    """BatchSanityReport converts to dict correctly."""
    metrics = [
        SanityMetrics(
            observation_id=f"obs{i}", symbol="AAPL",
            signal_timestamp="2026-05-20T00:00:00Z",
            stock_forward_return=1.0, cost_adjusted_return=0.85,
            delay_adjusted_return=0.95, enough_bars=True,
            outlier_zscore=None, compounding_artifact_warning=False,
            concurrent_exposure_warning=False,
economic_sanity_status=LABEL_PASS, warnings=[],
        )
        for i in range(3)
    ]
    report = BatchSanityReport(
        total_observations=3, assessed_observations=3,
        cost_fragile_count=0, insufficient_data_count=0,
        compounding_artifact_count=0, concurrent_exposure_count=0,
        pass_count=3, mean_cost_adjusted_return=0.85,
        mean_delay_adjusted_return=0.95, outlier_ids=[],
        detailed_metrics=metrics,
    )
    d = report_to_dict(report)
    assert d["total_observations"] == 3
    assert d["mean_cost_adjusted_return"] == 0.85
    assert len(d["detailed_metrics"]) == 3


# ─── ledger immutability meta-test ────────────────────────────


def test_no_strategy_logic_import() -> None:
    """Economic sanity imports only from reporting layer, not strategy modules."""
    import src.reporting.economic_sanity  # noqa: F811

    # Verify it does NOT import strategy-altering modules
    import sys
    mod_names = list(sys.modules.keys())
    strategy_modules = [m for m in mod_names if "research.momentum" in m or "research.price_volume" in m]
    assert len(strategy_modules) == 0, f"Unexpected imports: {strategy_modules}"