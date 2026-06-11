from __future__ import annotations

"""Economic Sanity Audit — assess whether observation outcomes are economically plausible.

Pure audit layer. Never modifies strategy behavior, thresholds, scoring, or ledgers.
Produces additive audit labels only.
"""

import csv
from dataclasses import dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Any


# ─── Constants ────────────────────────────────────────────────

TRANSACTION_COST_BPS = 10  # 10 bps round-trip (5 entry + 5 exit)
DELAY_SLIPPAGE_BPS = 5     # 5 bps estimated delay slippage
ANNUAL_TRADING_DAYS = 252
MIN_RETURN_BASIS_PTS = 20  # 20 bps minimum for economically meaningful return

LABEL_COST_FRAGILE = "Cost Fragile"
LABEL_INSUFFICIENT_DATA = "Insufficient Data"
LABEL_PASS = "Pass"

WARNING_COMPOUNDING = "compounding_artifact_warning"
WARNING_CONCURRENT = "concurrent_exposure_warning"


# ─── Dataclasses ──────────────────────────────────────────────


@dataclass(frozen=True)
class SanityMetrics:
    """Per-observation economic sanity metrics."""

    observation_id: str
    symbol: str
    signal_timestamp: str
    stock_forward_return: float | None
    cost_adjusted_return: float | None
    delay_adjusted_return: float | None
    enough_bars: bool
    outlier_zscore: float | None
    compounding_artifact_warning: bool
    concurrent_exposure_warning: bool
    economic_sanity_status: str = LABEL_PASS
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class BatchSanityReport:
    """Aggregate economic sanity report across all observations."""

    total_observations: int
    assessed_observations: int
    cost_fragile_count: int
    insufficient_data_count: int
    compounding_artifact_count: int
    concurrent_exposure_count: int
    pass_count: int
    mean_cost_adjusted_return: float | None
    mean_delay_adjusted_return: float | None
    outlier_ids: list[str]
    detailed_metrics: list[SanityMetrics]


# ─── Helpers ──────────────────────────────────────────────────


def _parse_pct(s: str) -> float | None:
    """Parse percentage string like '+2.34%' or '-1.5%' to float."""
    if not s or s.strip() == "":
        return None
    try:
        return float(s.replace("%", "").replace("+", ""))
    except (ValueError, TypeError):
        return None


def _to_dt(text: str) -> datetime:
    """Parse ISO datetime string."""
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def load_ohlcv_rows(path: Path) -> list[dict[str, Any]]:
    """Load OHLCV CSV rows sorted by date."""
    if not path.exists():
        return []
    with path.open() as f:
        rows = list(csv.DictReader(f))
    out: list[dict[str, Any]] = []
    for r in rows:
        date_raw = r.get("date") or r.get("timestamp") or r.get("datetime") or r.get("time")
        if not date_raw:
            continue
        try:
            dt = _to_dt(date_raw)
        except Exception:
            continue
        try:
            close = float(r.get("close") or "nan")
        except Exception:
            close = float("nan")
        out.append({"dt": dt, "close": close})
    out.sort(key=lambda x: x["dt"])
    return out


def compute_forward_return(
    initial_price: float,
    future_rows: list[dict[str, Any]],
    bars: int,
) -> float | None:
    """Compute forward return over N bars from future_rows."""
    if len(future_rows) < bars:
        return None
    px = future_rows[bars - 1]["close"]
    return (px / initial_price - 1.0) * 100.0


# ─── Core audit functions ────────────────────────────────────


def assess_economic_sanity(
    observation: dict[str, str],
    ohlcv_rows: list[dict[str, Any]],
    outcome_window: int | None = None,
) -> SanityMetrics:
    """Compute economic sanity metrics for a single observation.

    Pure function — never modifies observation.
    """
    obs_id = observation.get("observation_id", "")
    symbol = (observation.get("symbol") or "").upper()
    signal_ts = observation.get("signal_timestamp", "")

    if not signal_ts:
        return SanityMetrics(
            observation_id=obs_id,
            symbol=symbol,
            signal_timestamp=signal_ts,
            stock_forward_return=None,
            cost_adjusted_return=None,
            delay_adjusted_return=None,
            enough_bars=False,
            outlier_zscore=None,
            compounding_artifact_warning=False,
            concurrent_exposure_warning=False,
            economic_sanity_status=LABEL_INSUFFICIENT_DATA,
            warnings=("No signal timestamp",),
        )

    try:
        signal_dt = _to_dt(signal_ts)
    except Exception:
        return SanityMetrics(
            observation_id=obs_id,
            symbol=symbol,
            signal_timestamp=signal_ts,
            stock_forward_return=None,
            cost_adjusted_return=None,
            delay_adjusted_return=None,
            enough_bars=False,
            outlier_zscore=None,
            compounding_artifact_warning=False,
            concurrent_exposure_warning=False,
            economic_sanity_status=LABEL_INSUFFICIENT_DATA,
            warnings=("Cannot parse signal timestamp",),
        )

    try:
        initial_price = float(observation.get("signal_close") or 0.0)
    except (ValueError, TypeError):
        initial_price = 0.0

    if initial_price <= 0.0:
        return SanityMetrics(
            observation_id=obs_id,
            symbol=symbol,
            signal_timestamp=signal_ts,
            stock_forward_return=None,
            cost_adjusted_return=None,
            delay_adjusted_return=None,
            enough_bars=False,
            outlier_zscore=None,
            compounding_artifact_warning=False,
            concurrent_exposure_warning=False,
            economic_sanity_status=LABEL_INSUFFICIENT_DATA,
            warnings=("Invalid initial price",),
        )

    if not ohlcv_rows:
        return SanityMetrics(
            observation_id=obs_id,
            symbol=symbol,
            signal_timestamp=signal_ts,
            stock_forward_return=None,
            cost_adjusted_return=None,
            delay_adjusted_return=None,
            enough_bars=False,
            outlier_zscore=None,
            compounding_artifact_warning=False,
            concurrent_exposure_warning=False,
            economic_sanity_status=LABEL_INSUFFICIENT_DATA,
            warnings=("No OHLCV data",),
        )

    future_rows = [r for r in ohlcv_rows if r["dt"] > signal_dt]
    days_elapsed = len(future_rows)

    # Resolve outcome window
    window = outcome_window
    if window is None:
        try:
            window = int(observation.get("outcome_window", "10"))
        except (ValueError, TypeError):
            window = 10

    if days_elapsed < window:
        return SanityMetrics(
            observation_id=obs_id,
            symbol=symbol,
            signal_timestamp=signal_ts,
            stock_forward_return=None,
            cost_adjusted_return=None,
            delay_adjusted_return=None,
            enough_bars=False,
            outlier_zscore=None,
            compounding_artifact_warning=False,
            concurrent_exposure_warning=False,
            economic_sanity_status=LABEL_INSUFFICIENT_DATA,
            warnings=(f"Only {days_elapsed} bars, need {window}",),
        )

    # Compute forward return
    forward_ret = compute_forward_return(initial_price, future_rows, window)
    if forward_ret is None:
        return SanityMetrics(
            observation_id=obs_id,
            symbol=symbol,
            signal_timestamp=signal_ts,
            stock_forward_return=None,
            cost_adjusted_return=None,
            delay_adjusted_return=None,
            enough_bars=True,
            outlier_zscore=None,
            compounding_artifact_warning=False,
            concurrent_exposure_warning=False,
            economic_sanity_status=LABEL_INSUFFICIENT_DATA,
            warnings=("Cannot compute forward return",),
        )

# Cost adjustments
    tc_bps = TRANSACTION_COST_BPS
    delay_bps = DELAY_SLIPPAGE_BPS
    total_cost_bps = tc_bps + delay_bps
    cost_adjusted = forward_ret - (total_cost_bps / 100.0)
    delay_adjusted = forward_ret - (delay_bps / 100.0)

    # Status determination
    warnings_list: list[str] = []
    status = LABEL_PASS

    if cost_adjusted < (MIN_RETURN_BASIS_PTS / 100.0):
        status = LABEL_COST_FRAGILE
        warnings_list.append(
            f"Cost-adjusted return ({cost_adjusted:.2f}%) is below "
            f"minimum ({MIN_RETURN_BASIS_PTS / 100:.2f}%)"
        )

    return SanityMetrics(
        observation_id=obs_id,
        symbol=symbol,
        signal_timestamp=signal_ts,
        stock_forward_return=forward_ret,
        cost_adjusted_return=cost_adjusted,
        delay_adjusted_return=delay_adjusted,
        enough_bars=True,
        outlier_zscore=None,
        compounding_artifact_warning=False,
        concurrent_exposure_warning=False,
        economic_sanity_status=status,
        warnings=tuple(warnings_list),
    )


def detect_compounding_artifacts(
    observations: list[dict[str, str]],
    symbol: str,
    min_gap_days: int = 5,
) -> bool:
    """Check if the same symbol has overlapping/near-overlapping signals.

    A compounding artifact occurs when the same symbol gets signaled
    again before the previous signal's outcome window has elapsed,
    which can artificially compound returns.
    """
    relevant = [
        obs for obs in observations
        if (obs.get("symbol") or "").upper() == symbol
    ]
    if len(relevant) < 2:
        return False

    timestamps: list[datetime] = []
    for obs in relevant:
        ts = obs.get("signal_timestamp", "")
        if not ts:
            continue
        try:
            timestamps.append(_to_dt(ts))
        except Exception:
            continue

    timestamps.sort()
    for i in range(1, len(timestamps)):
        delta_days = (timestamps[i] - timestamps[i - 1]).days
        if delta_days < min_gap_days:
            return True

    return False


def detect_concurrent_exposure(
    observations: list[dict[str, str]],
    time_window_days: int = 3,
    min_count: int = 5,
) -> bool:
    """Check if too many signals cluster within a short time window.

    Concurrent exposure happens when many signals trigger on the
    same or near-same date, creating concentrated risk.
    """
    if len(observations) < min_count:
        return False

    timestamps: list[datetime] = []
    for obs in observations:
        ts = obs.get("signal_timestamp", "")
        if not ts:
            continue
        try:
            timestamps.append(_to_dt(ts))
        except Exception:
            continue

    timestamps.sort()
    for i in range(len(timestamps) - min_count + 1):
        cluster_start = timestamps[i]
        cluster_end = timestamps[i + min_count - 1]
        delta = (cluster_end - cluster_start).days
        if delta <= time_window_days:
            return True

    return False


def compute_batch_sanity(
    observations: list[dict[str, str]],
    root: Path,
    ohlcv_dir: Path = Path("data/cache/ohlcv_1d"),
    outcome_window: int | None = None,
) -> BatchSanityReport:
    """Compute economic sanity across all observations in a batch.

    Pure audit — never modifies observations or ledgers.
    """
    if not observations:
        return BatchSanityReport(
            total_observations=0,
            assessed_observations=0,
            cost_fragile_count=0,
            insufficient_data_count=0,
            compounding_artifact_count=0,
            concurrent_exposure_count=0,
            pass_count=0,
            mean_cost_adjusted_return=None,
            mean_delay_adjusted_return=None,
            outlier_ids=[],
            detailed_metrics=[],
        )

    # Check batch-level warnings
    symbol_set = {str((o.get("symbol") or "")).upper() for o in observations if o.get("symbol")}
    compounding_warned_symbols: set[str] = set()
    for sym in symbol_set:
        if detect_compounding_artifacts(observations, sym):
            compounding_warned_symbols.add(sym)

    concurrent_warning = detect_concurrent_exposure(observations)

    # Per-observation assessment
    metrics_list: list[SanityMetrics] = []
    cost_fragile = 0
    insufficient = 0
    pass_count = 0
    cost_adjusted_vals: list[float] = []
    delay_adjusted_vals: list[float] = []
    outlier_ids: list[str] = []

    for obs in observations:
        symbol = (obs.get("symbol") or "").upper()
        ohlcv_path = ohlcv_dir / f"{symbol}_1D.csv"
        full_path = root / ohlcv_path if not ohlcv_path.is_absolute() else ohlcv_path
        rows = load_ohlcv_rows(full_path)

        metrics = assess_economic_sanity(obs, rows, outcome_window)

        # Apply batch-level warnings
        comp_warn = symbol in compounding_warned_symbols
        conc_warn = concurrent_warning

        metrics = SanityMetrics(
            observation_id=metrics.observation_id,
            symbol=metrics.symbol,
            signal_timestamp=metrics.signal_timestamp,
            stock_forward_return=metrics.stock_forward_return,
            cost_adjusted_return=metrics.cost_adjusted_return,
            delay_adjusted_return=metrics.delay_adjusted_return,
            enough_bars=metrics.enough_bars,
            outlier_zscore=metrics.outlier_zscore,
            compounding_artifact_warning=comp_warn,
            concurrent_exposure_warning=conc_warn,
            economic_sanity_status=metrics.economic_sanity_status,
            warnings=metrics.warnings,
        )

        if metrics.economic_sanity_status == LABEL_COST_FRAGILE:
            cost_fragile += 1
        elif metrics.economic_sanity_status == LABEL_INSUFFICIENT_DATA:
            insufficient += 1
        else:
            pass_count += 1

        if metrics.cost_adjusted_return is not None:
            cost_adjusted_vals.append(metrics.cost_adjusted_return)
        if metrics.delay_adjusted_return is not None:
            delay_adjusted_vals.append(metrics.delay_adjusted_return)

        metrics_list.append(metrics)

    mean_cost = sum(cost_adjusted_vals) / len(cost_adjusted_vals) if cost_adjusted_vals else None
    mean_delay = sum(delay_adjusted_vals) / len(delay_adjusted_vals) if delay_adjusted_vals else None

    return BatchSanityReport(
        total_observations=len(observations),
        assessed_observations=len(metrics_list),
        cost_fragile_count=cost_fragile,
        insufficient_data_count=insufficient,
        compounding_artifact_count=len(compounding_warned_symbols),
        concurrent_exposure_count=1 if concurrent_warning else 0,
        pass_count=pass_count,
        mean_cost_adjusted_return=mean_cost,
        mean_delay_adjusted_return=mean_delay,
        outlier_ids=outlier_ids,
        detailed_metrics=metrics_list,
    )


def sanity_to_dict(metrics: SanityMetrics) -> dict[str, Any]:
    """Convert SanityMetrics to a JSON-serializable dict."""
    return {
        "observation_id": metrics.observation_id,
        "symbol": metrics.symbol,
        "signal_timestamp": metrics.signal_timestamp,
        "stock_forward_return": metrics.stock_forward_return,
        "cost_adjusted_return": metrics.cost_adjusted_return,
        "delay_adjusted_return": metrics.delay_adjusted_return,
        "enough_bars": metrics.enough_bars,
        "outlier_zscore": metrics.outlier_zscore,
        "compounding_artifact_warning": metrics.compounding_artifact_warning,
        "concurrent_exposure_warning": metrics.concurrent_exposure_warning,
        "economic_sanity_status": metrics.economic_sanity_status,
        "warnings": list(metrics.warnings),
    }


def report_to_dict(report: BatchSanityReport) -> dict[str, Any]:
    """Convert BatchSanityReport to a JSON-serializable dict."""
    return {
        "total_observations": report.total_observations,
        "assessed_observations": report.assessed_observations,
        "cost_fragile_count": report.cost_fragile_count,
        "insufficient_data_count": report.insufficient_data_count,
        "compounding_artifact_count": report.compounding_artifact_count,
        "concurrent_exposure_count": report.concurrent_exposure_count,
        "pass_count": report.pass_count,
        "mean_cost_adjusted_return": report.mean_cost_adjusted_return,
        "mean_delay_adjusted_return": report.mean_delay_adjusted_return,
        "outlier_ids": report.outlier_ids,
        "detailed_metrics": [sanity_to_dict(m) for m in report.detailed_metrics],
    }