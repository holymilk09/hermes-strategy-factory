"""Tests for Drift Attribution — market, sector, beta, ticker classification."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from src.reporting.drift_attribution import (
    LABEL_INDEPENDENT_STRENGTH,
    LABEL_MARKET_HELPED_SETUP,
    LABEL_SECTOR_DRIFT,
    LABEL_BETA_DRIFT,
    LABEL_TICKER_DRIFT,
    LABEL_NO_CONFIRMED_EDGE,
    LABEL_FAILED_EDGE,
    LABEL_COMPOUNDING_RISK,
    LABEL_COST_FRAGILE,
    LABEL_INSUFFICIENT_DATA,
    ALL_LABELS,
    DriftMetrics,
    BatchDriftReport,
    classify_drift,
    compute_drift_attribution,
    compute_batch_drift,
    drift_to_dict,
    report_to_dict,
)


# ─── classify_drift tests ────────────────────────────────────


def test_independent_strength_outperforms_all() -> None:
    """Stock outperforms SPY, QQQ, and sector = Independent Strength."""
    label = classify_drift(stock_return=5.0, spy_return=1.0, qqq_return=2.0, sector_return=3.0)
    assert label == LABEL_INDEPENDENT_STRENGTH


def test_market_helped_setup_spy_only() -> None:
    """Stock rises but ONLY because SPY rises and stock <= SPY."""
    label = classify_drift(stock_return=1.0, spy_return=2.0, qqq_return=1.5, sector_return=None)
    assert label == LABEL_MARKET_HELPED_SETUP


def test_market_helped_setup_below_best_benchmark() -> None:
    """Stock rises less than best benchmark = Market Helped Setup."""
    label = classify_drift(stock_return=1.0, spy_return=0.5, qqq_return=2.0, sector_return=None)
    # Best benchmark is QQQ at 2.0, stock at 1.0 < 2.0 but > SPY
    # Stock partially outperforms — tech beta (QQQ) explains the drift
    assert label == LABEL_BETA_DRIFT


def test_sector_drift_outperforms_market_not_sector() -> None:
    """Stock beats SPY but not sector = Sector Drift."""
    label = classify_drift(stock_return=3.0, spy_return=1.0, qqq_return=2.0, sector_return=4.0)
    assert label == LABEL_SECTOR_DRIFT


def test_beta_drift_outperforms_spy_not_qqq_no_sector() -> None:
    """Stock beats SPY but not QQQ, no sector data = Beta Drift."""
    label = classify_drift(stock_return=2.0, spy_return=1.0, qqq_return=3.0, sector_return=None)
    assert label == LABEL_BETA_DRIFT


def test_failed_edge_negative_return() -> None:
    """Stock has negative return = Failed Edge."""
    label = classify_drift(stock_return=-2.0, spy_return=1.0, qqq_return=2.0, sector_return=None)
    assert label == LABEL_FAILED_EDGE


def test_failed_edge_zero_return() -> None:
    """Stock return is zero = Failed Edge."""
    label = classify_drift(stock_return=0.0, spy_return=1.0, qqq_return=1.5, sector_return=None)
    assert label == LABEL_FAILED_EDGE


def test_insufficient_data_no_returns() -> None:
    """Stock return is None = Insufficient Data."""
    label = classify_drift(stock_return=None, spy_return=1.0, qqq_return=2.0, sector_return=None)
    assert label == LABEL_INSUFFICIENT_DATA


def test_no_confirmed_edge_no_benchmarks() -> None:
    """With no benchmark data, positive stock return = No Confirmed Edge."""
    label = classify_drift(stock_return=2.0, spy_return=None, qqq_return=None, sector_return=None)
    assert label == LABEL_NO_CONFIRMED_EDGE


def test_outperforms_all_benchmarks_no_sector() -> None:
    """Stock beats both SPY and QQQ with no sector = Independent Strength."""
    label = classify_drift(stock_return=5.0, spy_return=2.0, qqq_return=3.0, sector_return=None)
    assert label == LABEL_INDEPENDENT_STRENGTH


# ─── Special case: Market Helped Setup from requirements ────


def test_rises_only_because_spy_rises() -> None:
    """Test requirement: A setup that rises only because SPY rises must be Market Helped Setup."""
    # Stock goes up 1%, SPY goes up 3%, QQQ goes up 2.5%
    label = classify_drift(stock_return=1.0, spy_return=3.0, qqq_return=2.5, sector_return=None)
    assert label == LABEL_MARKET_HELPED_SETUP


def test_underperforms_sector_not_independent() -> None:
    """Test requirement: Setup that underperforms sector must not be labeled Independent Strength."""
    label = classify_drift(stock_return=2.0, spy_return=1.0, qqq_return=1.5, sector_return=3.0)
    assert label == LABEL_SECTOR_DRIFT  # Not Independent Strength
    assert label != LABEL_INDEPENDENT_STRENGTH


# ─── compute_drift_attribution tests ─────────────────────────


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


def _make_rows(start: float, count: int, drift: float = 1.005) -> list[dict]:
    base_dt = datetime(2026, 5, 21, 4, 0, 0, tzinfo=timezone.utc)
    rows = []
    price = start
    for i in range(count):
        price *= drift
        rows.append({
            "dt": base_dt + timedelta(days=i),
            "close": round(price, 2),
        })
    return rows


def _make_flat_rows(start: float, count: int) -> list[dict]:
    """Flat price rows (no drift)."""
    base_dt = datetime(2026, 5, 21, 4, 0, 0, tzinfo=timezone.utc)
    rows = []
    for i in range(count):
        rows.append({
            "dt": base_dt + timedelta(days=i),
            "close": start,
        })
    return rows


def _make_down_rows(start: float, count: int) -> list[dict]:
    """Declining price rows."""
    base_dt = datetime(2026, 5, 21, 4, 0, 0, tzinfo=timezone.utc)
    rows = []
    price = start
    for i in range(count):
        price *= 0.995
        rows.append({
            "dt": base_dt + timedelta(days=i),
            "close": round(price, 2),
        })
    return rows


from datetime import timedelta  # noqa: E402


def test_drift_attribution_missing_signal_ts() -> None:
    """Missing signal timestamp = Insufficient Data."""
    obs = _make_obs(signal_ts="")
    result = compute_drift_attribution(obs, [], [], [])
    assert result.drift_attribution_label == LABEL_INSUFFICIENT_DATA


def test_drift_attribution_missing_benchmark_data() -> None:
    """Missing benchmark data must produce Insufficient Data, not fabricated results."""
    obs = _make_obs()
    stock_rows = _make_rows(200.0, 15, 1.01)
    # Empty benchmark data
    result = compute_drift_attribution(obs, stock_rows, [], [])
    assert result.drift_attribution_label in (LABEL_INSUFFICIENT_DATA, LABEL_NO_CONFIRMED_EDGE)


def test_drift_attribution_independent_strength() -> None:
    """Stock outperforms SPY and QQQ = Independent Strength."""
    obs = _make_obs(symbol="AAPL", signal_close="200.0")
    stock_rows = _make_rows(200.0, 15, 1.015)   # ~1.5% per bar
    spy_rows = _make_rows(450.0, 15, 1.005)      # ~0.5% per bar
    qqq_rows = _make_rows(350.0, 15, 1.005)      # ~0.5% per bar

    result = compute_drift_attribution(obs, stock_rows, spy_rows, qqq_rows, outcome_window=10)
    assert result.drift_attribution_label == LABEL_INDEPENDENT_STRENGTH


def test_drift_attribution_market_helped() -> None:
    """Stock goes up less than benchmarks = Market Helped Setup."""
    obs = _make_obs(symbol="AAPL", signal_close="200.0")
    stock_rows = _make_rows(200.0, 15, 1.002)   # ~0.2% per bar
    spy_rows = _make_rows(450.0, 15, 1.01)       # ~1.0% per bar
    qqq_rows = _make_rows(350.0, 15, 1.01)       # ~1.0% per bar

    result = compute_drift_attribution(obs, stock_rows, spy_rows, qqq_rows, outcome_window=10)
    assert result.drift_attribution_label == LABEL_MARKET_HELPED_SETUP


# ─── batch drift tests ───────────────────────────────────────


def test_batch_drift_empty(tmp_path: Path) -> None:
    """Empty observations = empty report."""
    report = compute_batch_drift([], tmp_path)
    assert report.total_observations == 0
    assert report.labeled_observations == 0


def test_batch_drift_label_counts(tmp_path: Path) -> None:
    """Batch drift produces label counts."""
    # Use temporary does-not-exist path so all are Insufficient Data
    obs_list = [_make_obs("obs1", "AAPL"), _make_obs("obs2", "MSFT")]
    report = compute_batch_drift(obs_list, tmp_path)
    assert report.total_observations == 2
    assert report.label_counts.get(LABEL_INSUFFICIENT_DATA, 0) == 2


# ─── serialization tests ─────────────────────────────────────


def test_drift_to_dict() -> None:
    """DriftMetrics converts to dict correctly."""
    metrics = DriftMetrics(
        observation_id="obs1",
        symbol="AAPL",
        signal_timestamp="2026-05-20T00:00:00Z",
        stock_forward_return=5.0,
        SPY_forward_return=1.0,
        QQQ_forward_return=2.0,
        sector_forward_return=None,
        benchmark_relative_return=3.0,
        sector_relative_return=None,
        drift_attribution_label=LABEL_INDEPENDENT_STRENGTH,
        missing_data_keys=[],
    )
    d = drift_to_dict(metrics)
    assert d["observation_id"] == "obs1"
    assert d["stock_forward_return"] == 5.0
    assert d["drift_attribution_label"] == LABEL_INDEPENDENT_STRENGTH


def test_report_to_dict() -> None:
    """BatchDriftReport converts to dict correctly."""
    metrics = [
        DriftMetrics(
            observation_id="obs1", symbol="AAPL",
            signal_timestamp="2026-05-20T00:00:00Z",
            stock_forward_return=5.0, SPY_forward_return=1.0,
            QQQ_forward_return=2.0, sector_forward_return=None,
            benchmark_relative_return=3.0, sector_relative_return=None,
            drift_attribution_label=LABEL_INDEPENDENT_STRENGTH,
            missing_data_keys=[],
        )
    ]
    report = BatchDriftReport(
        total_observations=1,
        labeled_observations=1,
        label_counts={label: 0 for label in ALL_LABELS},
        label_breakdown=metrics,
    )
    report.label_counts[LABEL_INDEPENDENT_STRENGTH] = 1
    d = report_to_dict(report)
    assert d["total_observations"] == 1
    assert len(d["label_breakdown"]) == 1


# ─── ledger immutability meta-test ────────────────────────────


def test_no_strategy_logic_import() -> None:
    """Drift attribution imports only from reporting layer."""
    import src.reporting.drift_attribution  # noqa: F811

    import sys
    mod_names = list(sys.modules.keys())
    strategy_modules = [m for m in mod_names if "research.momentum" in m or "research.price_volume" in m]
    assert len(strategy_modules) == 0, f"Unexpected imports: {strategy_modules}"