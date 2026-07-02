"""PHASE 7C-DATA-REPAIR — Source-only tests.

Covers:
  A. Universe refresh scope: resolve_refresh_universe, freshness floor
  B. Sector ETF freshness + Independent Strength overclaim guard
  C. Ghost outcome resolution (dry-run default, write mode, ledger safety)
  D. Healthcheck invariants (universe floor, ghost ledger reporting)
  E. Threshold constants unchanged

All tests use synthetic fixtures (tmp_path). No production ledgers,
OHLCV cache, or network access required.
"""

from __future__ import annotations

import csv
import hashlib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

_SCRIPTS_DIR = str(ROOT / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)


# ─── Helpers ──────────────────────────────────────────────────


def _write_ohlcv_csv(path: Path, dates: list[str], start_price: float = 100.0,
                     step: float = 1.0) -> None:
    """Write a synthetic OHLCV CSV in the cache layout."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close", "volume",
                    "dividends", "stock splits"])
        px = start_price
        for d in dates:
            w.writerow([f"{d} 04:00:00+00:00", px, px * 1.01, px * 0.99, px,
                        1000000, 0.0, 0.0])
            px += step


def _trading_dates(start: str, n: int) -> list[str]:
    """N consecutive weekdays starting at `start` (YYYY-MM-DD)."""
    out: list[str] = []
    d = datetime.strptime(start, "%Y-%m-%d")
    while len(out) < n:
        if d.isoweekday() <= 5:
            out.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    return out


def _make_tmp_universe(tmp_path: Path, n_symbols: int, dates: list[str]) -> Path:
    """Create a tmp root with an OHLCV cache holding n synthetic symbols."""
    cache = tmp_path / "data" / "cache" / "ohlcv_1d"
    for i in range(n_symbols):
        _write_ohlcv_csv(cache / f"SY{i:03d}_1D.csv", dates)
    return tmp_path


def _ghost_row(ghost_id: str, symbol: str, signal_date: str,
               price: float = 100.0, status: str = "PENDING") -> dict[str, str]:
    return {
        "ghost_id": ghost_id,
        "source_observation_id": "",
        "symbol": symbol,
        "strategy_id": "relative_strength_continuation",
        "setup_type": "swing",
        "signal_date": signal_date,
        "rejection_reason": "20d_momentum_too_weak",
        "failed_gate": "ret_20d_rank",
        "score_if_available": "0.5",
        "price_at_signal": str(price),
        "market_weather": "",
        "published_status": "GHOST_ONLY",
        "reason_not_published": "Rejected by ret_20d_rank",
        "outcome_5d": "",
        "outcome_10d": "",
        "outcome_20d": "",
        "outcome_30d": "",
        "max_favorable_move": "",
        "max_adverse_move": "",
        "setup_broke": "",
        "data_status": status,
        "created_at": "2026-06-01T00:00:00+00:00",
    }


def _write_ghost_ledger(path: Path, rows: list[dict[str, str]]) -> None:
    from src.reporting.ghost_ledger import GHOST_FIELDS

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=GHOST_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ─── A. Universe refresh scope ────────────────────────────────


def test_resolve_refresh_universe_not_limited_to_six(tmp_path):
    """Refresh scope must include all cached symbols, not just the 6 approved."""
    from refresh_stale_ohlcv import resolve_refresh_universe

    dates = _trading_dates("2026-06-01", 5)
    root = _make_tmp_universe(tmp_path, 60, dates)
    universe = resolve_refresh_universe(root)

    assert len(universe) >= 60, f"Universe collapsed: {len(universe)} symbols"
    # All discovered symbols present
    assert "SY000" in universe and "SY059" in universe


def test_resolve_refresh_universe_includes_benchmarks_and_sector_etfs(tmp_path):
    """SPY/QQQ and SMH/IGV/TAN must always be in refresh scope."""
    from refresh_stale_ohlcv import resolve_refresh_universe

    dates = _trading_dates("2026-06-01", 5)
    root = _make_tmp_universe(tmp_path, 10, dates)
    universe = resolve_refresh_universe(root)

    for required in ["SPY", "QQQ", "SMH", "IGV", "TAN",
                     "AMD", "ARM", "CRWD", "DDOG", "MRVL", "SEDG"]:
        assert required in universe, f"{required} missing from refresh scope"


def test_universe_floor_fails_when_only_six_fresh(tmp_path):
    """Freshness floor must FAIL when only 6 symbols have current bars."""
    from refresh_stale_ohlcv import (
        RefreshBatchResult, SymbolRefreshResult, summarize_freshness,
    )
    import refresh_stale_ohlcv as rso

    old_target = rso.TARGET_DATE
    rso.TARGET_DATE = "2026-06-30"
    try:
        batch = RefreshBatchResult()
        # 6 fresh symbols
        for i, sym in enumerate(["AMD", "ARM", "CRWD", "DDOG", "MRVL", "SEDG"]):
            batch.results.append(SymbolRefreshResult(
                symbol=sym, status="SKIPPED_CURRENT", latest_date="2026-06-30"))
        # 60 stale symbols
        for i in range(60):
            batch.results.append(SymbolRefreshResult(
                symbol=f"SY{i:03d}", status="FAILED", latest_date="2026-05-27"))

        summary = summarize_freshness(batch)
        assert summary["fresh_count"] == 6
        assert summary["floor_pass"] is False, (
            "Universe floor must fail closed with only 6 fresh symbols"
        )
    finally:
        rso.TARGET_DATE = old_target


def test_universe_floor_passes_with_fifty_plus_fresh(tmp_path):
    """Freshness floor must PASS when 50+ symbols have current bars."""
    from refresh_stale_ohlcv import (
        RefreshBatchResult, SymbolRefreshResult, summarize_freshness,
    )
    import refresh_stale_ohlcv as rso

    old_target = rso.TARGET_DATE
    rso.TARGET_DATE = "2026-06-30"
    try:
        batch = RefreshBatchResult()
        for i in range(55):
            batch.results.append(SymbolRefreshResult(
                symbol=f"SY{i:03d}", status="FETCHED", latest_date="2026-06-30"))
        summary = summarize_freshness(batch)
        assert summary["fresh_count"] == 55
        assert summary["floor_pass"] is True
    finally:
        rso.TARGET_DATE = old_target


def test_healthcheck_universe_floor_detects_collapse(tmp_path, monkeypatch):
    """Healthcheck universe floor fails when cross-section collapses to 6."""
    import run_feature_factory_healthcheck as hc

    dates_stale = _trading_dates("2026-05-01", 5)
    cache = tmp_path / "data" / "cache" / "ohlcv_1d"
    # 60 stale symbols
    for i in range(60):
        _write_ohlcv_csv(cache / f"SY{i:03d}_1D.csv", dates_stale)
    # 6 fresh symbols at a later session
    dates_fresh = dates_stale + ["2026-06-30"]
    for sym in ["AMD", "ARM", "CRWD", "DDOG", "MRVL", "SEDG"]:
        _write_ohlcv_csv(cache / f"{sym}_1D.csv", dates_fresh)

    monkeypatch.setattr(hc, "ROOT", tmp_path)
    result = hc.check_universe_freshness()
    assert result["latest_session"] == "2026-06-30"
    assert result["fresh_count"] == 6
    assert result["floor_pass"] is False


def test_healthcheck_universe_floor_passes_when_broad(tmp_path, monkeypatch):
    """Healthcheck universe floor passes when 50+ symbols share latest session."""
    import run_feature_factory_healthcheck as hc

    dates = _trading_dates("2026-06-01", 5)
    _make_tmp_universe(tmp_path, 55, dates)
    monkeypatch.setattr(hc, "ROOT", tmp_path)
    result = hc.check_universe_freshness()
    assert result["fresh_count"] >= 50
    assert result["floor_pass"] is True


# ─── B. Sector ETF freshness / overclaim guard ────────────────


def test_missing_sector_data_downgrades_independent_strength():
    """Sector mapping exists but data missing → conservative label, never full IS."""
    from src.reporting.drift_attribution import (
        classify_drift,
        LABEL_INDEPENDENT_STRENGTH,
        LABEL_INDEPENDENT_STRENGTH_SECTOR_PENDING,
    )

    label = classify_drift(
        stock_return=5.0, spy_return=1.0, qqq_return=2.0,
        sector_return=None, sector_expected=True,
    )
    assert label == LABEL_INDEPENDENT_STRENGTH_SECTOR_PENDING
    assert label != LABEL_INDEPENDENT_STRENGTH


def test_current_sector_data_allows_normal_classification():
    """With sector data present, normal sector-aware labels apply."""
    from src.reporting.drift_attribution import (
        classify_drift,
        LABEL_INDEPENDENT_STRENGTH,
        LABEL_SECTOR_DRIFT,
    )

    # Beats sector → full Independent Strength
    assert classify_drift(5.0, 1.0, 2.0, 3.0, sector_expected=True) == \
        LABEL_INDEPENDENT_STRENGTH
    # Loses to sector → Sector Drift
    assert classify_drift(3.0, 1.0, 2.0, 4.0, sector_expected=True) == \
        LABEL_SECTOR_DRIFT


def test_no_sector_mapping_preserves_original_behavior():
    """No sector mapping at all (sector_expected=False) — legacy behavior kept."""
    from src.reporting.drift_attribution import (
        classify_drift, LABEL_INDEPENDENT_STRENGTH,
    )

    assert classify_drift(5.0, 2.0, 3.0, None, sector_expected=False) == \
        LABEL_INDEPENDENT_STRENGTH


def test_stale_sector_etf_detected(tmp_path):
    """validate_sector_freshness flags stale and missing sector ETFs."""
    from src.reporting.drift_attribution import validate_sector_freshness

    cache = tmp_path / "data" / "cache" / "ohlcv_1d"
    stale_dates = _trading_dates("2026-05-01", 5)   # far in the past
    _write_ohlcv_csv(cache / "SMH_1D.csv", stale_dates)
    fresh_dates = _trading_dates("2026-06-25", 4)   # ends 2026-06-30
    _write_ohlcv_csv(cache / "IGV_1D.csv", fresh_dates)
    # TAN missing entirely

    now = datetime(2026, 7, 1, tzinfo=timezone.utc)
    result = validate_sector_freshness(tmp_path, now=now)

    assert result["SMH"]["exists"] is True
    assert result["SMH"]["fresh"] is False, "Stale SMH must be detected"
    assert result["IGV"]["fresh"] is True
    assert result["TAN"]["exists"] is False
    assert result["TAN"]["fresh"] is False, "Missing TAN must not be fresh"


def test_compute_drift_attribution_flags_missing_sector():
    """compute_drift_attribution downgrades label + records missing key
    when a sector mapping exists but no sector rows are available."""
    from src.reporting.drift_attribution import (
        compute_drift_attribution,
        LABEL_INDEPENDENT_STRENGTH_SECTOR_PENDING,
    )

    dates = _trading_dates("2026-06-01", 15)
    signal_ts = f"{dates[0]}T04:00:00+00:00"

    def _rows(step: float):
        out = []
        px = 100.0
        for d in dates:
            out.append({"dt": datetime.fromisoformat(f"{d}T04:00:00+00:00"),
                        "close": px})
            px += step
        return out

    obs = {
        "observation_id": "obs1",
        "symbol": "AMD",
        "signal_timestamp": signal_ts,
        "signal_close": "100.0",
        "outcome_window": "10",
    }
    metrics = compute_drift_attribution(
        observation=obs,
        stock_ohlcv_rows=_rows(5.0),   # strong stock
        spy_ohlcv_rows=_rows(0.5),
        qqq_ohlcv_rows=_rows(1.0),
        sector_ohlcv_rows=None,        # sector data MISSING
        sector_etf="SMH",              # ...but mapping EXISTS
    )
    assert metrics.drift_attribution_label == LABEL_INDEPENDENT_STRENGTH_SECTOR_PENDING
    assert any("sector_etf" in k for k in metrics.missing_data_keys)


def test_sector_mapping_for_approved_cohort():
    """Approved cohort symbols map to the required sector ETFs."""
    from src.reporting.drift_attribution import DEFAULT_SECTOR_ETFS

    assert DEFAULT_SECTOR_ETFS["AMD"] == "SMH"
    assert DEFAULT_SECTOR_ETFS["MRVL"] == "SMH"
    assert DEFAULT_SECTOR_ETFS["ARM"] == "SMH"
    assert DEFAULT_SECTOR_ETFS["CRWD"] == "IGV"
    assert DEFAULT_SECTOR_ETFS["DDOG"] == "IGV"
    assert DEFAULT_SECTOR_ETFS["SEDG"] == "TAN"


# ─── C. Ghost outcome resolution ──────────────────────────────


def test_ghost_pending_stays_pending_when_insufficient_bars(tmp_path):
    """PENDING remains PENDING when fewer than 5 forward bars exist."""
    from src.reporting.ghost_ledger import load_ghost_ledger, resolve_ghost_outcomes

    dates = _trading_dates("2026-06-01", 8)
    signal_date = f"{dates[5]} 04:00:00+00:00"  # only 2 bars after signal
    _write_ohlcv_csv(tmp_path / "data" / "cache" / "ohlcv_1d" / "ZZTEST_1D.csv", dates)

    ledger = tmp_path / "data" / "trust_calibration" / "ghost_ledger.csv"
    _write_ghost_ledger(ledger, [_ghost_row("g1", "ZZTEST", signal_date)])

    resolve_ghost_outcomes(root=tmp_path, ghost_path=ledger, dry_run=False)
    rows = load_ghost_ledger(ledger)
    assert rows[0]["data_status"] == "PENDING"
    assert rows[0]["outcome_5d"] == ""


def test_ghost_pending_becomes_mature_when_bars_exist(tmp_path):
    """PENDING → MATURE with outcome fields populated when bars exist."""
    from src.reporting.ghost_ledger import load_ghost_ledger, resolve_ghost_outcomes

    dates = _trading_dates("2026-05-01", 30)
    signal_date = f"{dates[5]} 04:00:00+00:00"  # 24 bars after signal
    _write_ohlcv_csv(tmp_path / "data" / "cache" / "ohlcv_1d" / "ZZTEST_1D.csv", dates)

    ledger = tmp_path / "data" / "trust_calibration" / "ghost_ledger.csv"
    _write_ghost_ledger(ledger, [_ghost_row("g1", "ZZTEST", signal_date, price=100.0)])

    updated = resolve_ghost_outcomes(root=tmp_path, ghost_path=ledger, dry_run=False)
    assert updated == 1
    rows = load_ghost_ledger(ledger)
    assert rows[0]["data_status"] == "MATURE"
    assert rows[0]["outcome_5d"] != ""
    assert rows[0]["outcome_10d"] != ""


def test_ghost_dry_run_is_default_and_writes_nothing(tmp_path):
    """Dry-run computes updates but never writes the ledger."""
    from src.reporting.ghost_ledger import resolve_ghost_outcomes

    dates = _trading_dates("2026-05-01", 30)
    signal_date = f"{dates[5]} 04:00:00+00:00"
    _write_ohlcv_csv(tmp_path / "data" / "cache" / "ohlcv_1d" / "ZZTEST_1D.csv", dates)

    ledger = tmp_path / "data" / "trust_calibration" / "ghost_ledger.csv"
    _write_ghost_ledger(ledger, [_ghost_row("g1", "ZZTEST", signal_date)])
    hash_before = hashlib.sha256(ledger.read_bytes()).hexdigest()

    would_update = resolve_ghost_outcomes(root=tmp_path, ghost_path=ledger, dry_run=True)
    assert would_update == 1
    hash_after = hashlib.sha256(ledger.read_bytes()).hexdigest()
    assert hash_after == hash_before, "Dry-run must not write the ghost ledger"


def test_ghost_resolution_does_not_mutate_observation_or_outcome_ledgers(tmp_path):
    """Ghost resolution must never touch observation/outcome ledgers."""
    from src.reporting.ghost_ledger import resolve_ghost_outcomes

    dates = _trading_dates("2026-05-01", 30)
    signal_date = f"{dates[5]} 04:00:00+00:00"
    _write_ohlcv_csv(tmp_path / "data" / "cache" / "ohlcv_1d" / "ZZTEST_1D.csv", dates)

    obs_dir = tmp_path / "data" / "paper_observation"
    obs_dir.mkdir(parents=True)
    obs_ledger = obs_dir / "relative_strength_continuation_observation_ledger.csv"
    out_ledger = obs_dir / "relative_strength_continuation_outcome_ledger.csv"
    obs_ledger.write_text("observation_id,symbol\nobs1,ZZTEST\n")
    out_ledger.write_text("observation_id,outcome_status\nobs1,RESOLVED\n")

    obs_hash = hashlib.sha256(obs_ledger.read_bytes()).hexdigest()
    out_hash = hashlib.sha256(out_ledger.read_bytes()).hexdigest()

    ghost_ledger = tmp_path / "data" / "trust_calibration" / "ghost_ledger.csv"
    _write_ghost_ledger(ghost_ledger, [_ghost_row("g1", "ZZTEST", signal_date)])

    resolve_ghost_outcomes(root=tmp_path, ghost_path=ghost_ledger, dry_run=False)

    assert hashlib.sha256(obs_ledger.read_bytes()).hexdigest() == obs_hash
    assert hashlib.sha256(out_ledger.read_bytes()).hexdigest() == out_hash


def test_ghost_resolution_preserves_row_count(tmp_path):
    """Resolution never adds or removes ghost rows."""
    from src.reporting.ghost_ledger import load_ghost_ledger, resolve_ghost_outcomes

    dates = _trading_dates("2026-05-01", 30)
    signal_date = f"{dates[5]} 04:00:00+00:00"
    _write_ohlcv_csv(tmp_path / "data" / "cache" / "ohlcv_1d" / "ZZTEST_1D.csv", dates)

    ledger = tmp_path / "data" / "trust_calibration" / "ghost_ledger.csv"
    rows_in = [
        _ghost_row("g1", "ZZTEST", signal_date),
        _ghost_row("g2", "NODATA1", signal_date),
        _ghost_row("g3", "NODATA2", signal_date),
    ]
    _write_ghost_ledger(ledger, rows_in)

    resolve_ghost_outcomes(root=tmp_path, ghost_path=ledger, dry_run=False)
    rows_out = load_ghost_ledger(ledger)
    assert len(rows_out) == len(rows_in)
    assert [r["ghost_id"] for r in rows_out] == ["g1", "g2", "g3"]


def test_ghost_impossible_resolution_becomes_insufficient_data(tmp_path):
    """PENDING → INSUFFICIENT_DATA when symbol has no OHLCV file."""
    from src.reporting.ghost_ledger import load_ghost_ledger, resolve_ghost_outcomes

    ledger = tmp_path / "data" / "trust_calibration" / "ghost_ledger.csv"
    _write_ghost_ledger(ledger, [_ghost_row("g1", "NOFILE", "2026-05-01 04:00:00+00:00")])

    resolve_ghost_outcomes(root=tmp_path, ghost_path=ledger, dry_run=False)
    rows = load_ghost_ledger(ledger)
    assert rows[0]["data_status"] == "INSUFFICIENT_DATA"
    assert rows[0]["outcome_10d"] == ""  # never fabricated


def test_ghost_baseline_populated_from_mature_ghosts():
    """Ghost baseline return computes when mature ghost outcomes exist."""
    from src.reporting.filter_quality_audit import compute_ghost_baseline_return

    ghosts = [
        {**_ghost_row("g1", "A", "2026-05-01"), "data_status": "MATURE", "outcome_10d": "+4.00%"},
        {**_ghost_row("g2", "B", "2026-05-01"), "data_status": "MATURE", "outcome_10d": "-2.00%"},
        {**_ghost_row("g3", "C", "2026-05-01"), "data_status": "PENDING"},
    ]
    baseline = compute_ghost_baseline_return(ghosts)
    assert baseline == pytest.approx(1.0)


def test_accepted_vs_rejected_lift_computes_with_both_sides():
    """Lift computes when >=5 accepted and >=5 mature ghost outcomes exist."""
    from src.reporting.filter_quality_audit import compute_accepted_vs_rejected_lift

    accepted = [{"outcome_return": "+3.00%"} for _ in range(5)]
    ghosts = [
        {**_ghost_row(f"g{i}", "X", "2026-05-01"),
         "data_status": "MATURE", "outcome_10d": "+1.00%"}
        for i in range(5)
    ]
    lift = compute_accepted_vs_rejected_lift(accepted, ghosts)
    assert lift == pytest.approx(2.0)


def test_ghost_resolver_script_exists_and_defaults_to_dry_run():
    """Operator script must exist and must not write unless --write passed."""
    script = ROOT / "scripts" / "update_ghost_outcomes.py"
    assert script.exists(), "scripts/update_ghost_outcomes.py missing"
    text = script.read_text()
    assert "--write" in text
    assert "dry_run = not args.write" in text, "Default must be dry-run"


def test_ghost_resolution_creates_no_observations(tmp_path):
    """Resolution must not create any observation ledger files."""
    from src.reporting.ghost_ledger import resolve_ghost_outcomes

    dates = _trading_dates("2026-05-01", 30)
    signal_date = f"{dates[5]} 04:00:00+00:00"
    _write_ohlcv_csv(tmp_path / "data" / "cache" / "ohlcv_1d" / "ZZTEST_1D.csv", dates)
    ledger = tmp_path / "data" / "trust_calibration" / "ghost_ledger.csv"
    _write_ghost_ledger(ledger, [_ghost_row("g1", "ZZTEST", signal_date)])

    resolve_ghost_outcomes(root=tmp_path, ghost_path=ledger, dry_run=False)
    obs_dir = tmp_path / "data" / "paper_observation"
    assert not obs_dir.exists() or not list(obs_dir.glob("*observation*")), (
        "Ghost resolution created observation artifacts"
    )


# ─── D. Healthcheck ghost ledger reporting ────────────────────


def test_healthcheck_ghost_ledger_counts(tmp_path, monkeypatch):
    import run_feature_factory_healthcheck as hc

    ledger = tmp_path / "data" / "trust_calibration" / "ghost_ledger.csv"
    _write_ghost_ledger(ledger, [
        _ghost_row("g1", "A", "2026-05-01", status="PENDING"),
        _ghost_row("g2", "B", "2026-05-01", status="MATURE"),
        _ghost_row("g3", "C", "2026-05-01", status="INSUFFICIENT_DATA"),
        _ghost_row("g4", "D", "2026-05-01", status="MATURE"),
    ])
    monkeypatch.setattr(hc, "ROOT", tmp_path)
    result = hc.check_ghost_ledger()
    assert result["exists"] and result["parse_ok"]
    assert result["rows"] == 4
    assert result["status_counts"] == {
        "PENDING": 1, "MATURE": 2, "INSUFFICIENT_DATA": 1,
    }


def test_healthcheck_ghost_ledger_missing(tmp_path, monkeypatch):
    import run_feature_factory_healthcheck as hc

    monkeypatch.setattr(hc, "ROOT", tmp_path)
    result = hc.check_ghost_ledger()
    assert result["exists"] is False
    assert result["rows"] == 0


# ─── E. Thresholds / scoring unchanged ────────────────────────


def test_no_threshold_constants_changed():
    """Phase 7C must not change strategy thresholds, scoring, or maturity rules."""
    from src.paper.relative_strength_observation import RelativeStrengthObservationConfig

    cfg = RelativeStrengthObservationConfig()
    assert cfg.ret_20d_rank_threshold == 0.85
    assert cfg.ret_60d_rank_threshold == 0.70
    assert cfg.outcome_window == 10
    assert cfg.max_stale_calendar_days == 5

    from src.reporting.drift_attribution import (
        POSITIVE_RETURN_THRESHOLD,
        SECTOR_OUTPERFORM_THRESHOLD,
        BETA_DOMINANCE_THRESHOLD,
        MARKET_RELATIVE_THRESHOLD,
    )
    assert POSITIVE_RETURN_THRESHOLD == 0.0
    assert SECTOR_OUTPERFORM_THRESHOLD == 0.0
    assert BETA_DOMINANCE_THRESHOLD == 0.5
    assert MARKET_RELATIVE_THRESHOLD == 0.0

    from src.reporting.filter_quality_audit import (
        MIN_OBSERVATIONS_FOR_LIFT,
        MIN_OBSERVATIONS_FOR_MONOTONIC,
        LIFT_SIGNIFICANCE_THRESHOLD,
    )
    assert MIN_OBSERVATIONS_FOR_LIFT == 5
    assert MIN_OBSERVATIONS_FOR_MONOTONIC == 10
    assert LIFT_SIGNIFICANCE_THRESHOLD == 0.5


def test_refresh_universe_floor_constant():
    """The universe floor is 50 and defined in both refresh + healthcheck."""
    import refresh_stale_ohlcv as rso
    import run_feature_factory_healthcheck as hc

    assert rso.MIN_FRESH_UNIVERSE == 50
    assert hc.MIN_FRESH_UNIVERSE == 50


# ─── VPS / data-backed tests ──────────────────────────────────


@pytest.mark.requires_ohlcv
def test_vps_full_universe_latest_date_count():
    """Report + assert the real cache has a broad universe (informational floor)."""
    import run_feature_factory_healthcheck as hc

    result = hc.check_universe_freshness()
    assert result["cache_exists"]
    assert result["universe_size"] >= 50, (
        f"OHLCV cache universe too small: {result['universe_size']}"
    )


@pytest.mark.requires_ohlcv
def test_vps_sector_etf_files_expected():
    """SMH must exist in the cache; IGV/TAN are required for full sector
    verification (reported, not asserted, until first full-universe refresh
    seeds them)."""
    cache = ROOT / "data" / "cache" / "ohlcv_1d"
    assert (cache / "SMH_1D.csv").exists(), "SMH missing from OHLCV cache"


@pytest.mark.requires_data
def test_vps_ghost_ledger_row_count_and_status():
    """Ghost ledger exists, parses, and reports status counts."""
    import run_feature_factory_healthcheck as hc

    result = hc.check_ghost_ledger()
    assert result["exists"] and result["parse_ok"]
    assert result["rows"] > 0
    total = sum(result["status_counts"].values())
    assert total <= result["rows"]


@pytest.mark.requires_data
@pytest.mark.requires_ohlcv
def test_vps_healthcheck_fails_if_universe_collapses():
    """The healthcheck must report floor_pass=False when fewer than 50
    symbols are fresh at the latest cross-section (fail-closed gate)."""
    import run_feature_factory_healthcheck as hc

    result = hc.check_universe_freshness()
    if result["fresh_count"] < hc.MIN_FRESH_UNIVERSE:
        assert result["floor_pass"] is False
    else:
        assert result["floor_pass"] is True
