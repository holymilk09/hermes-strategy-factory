#!/usr/bin/env python3
"""
Tests for momentum_ret5d_ma50_scanner guarded resolution (P0, 2026-10-14) and
verify_ledger_preservation. Unit tests for code correctness — synthetic price
series are used here ONLY as software test fixtures (market conclusions always
come from real data; see the repo's no-synthetic-data rule for models).

Run:  python -m pytest docs/v0/tools/test_momentum_scanner.py -q
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import pathlib
import subprocess
import sys
from datetime import date, timedelta

HERE = pathlib.Path(__file__).parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scanner = _load("momentum_scanner", "momentum_ret5d_ma50_scanner.py")


def gen_dates(start: str, count: int) -> list[str]:
    """Trading-session dates (weekdays minus NYSE holidays) from start, inclusive."""
    d = date.fromisoformat(start)
    out = []
    while len(out) < count:
        if d.weekday() < 5 and d.isoformat() not in scanner.NYSE_HOLIDAYS:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def write_cache(cache_dir: pathlib.Path, symbol: str, dates: list[str], closes: list[float]):
    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(cache_dir / f"{symbol}.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["Date", "Close"])
        for d, c in zip(dates, closes):
            w.writerow([d, c])


def make_ledger(path: pathlib.Path, rows: list[dict]):
    with open(path, "w", newline='') as f:
        w = csv.DictWriter(f, fieldnames=scanner.FIELDS)
        w.writeheader()
        w.writerows(rows)


def pending_row(symbol: str, signal_date: str, signal_close: float = 100.0) -> dict:
    return {
        "observation_id": scanner.obs_id(symbol, signal_date),
        "hypothesis": scanner.HYPOTHESIS,
        "signal_date": signal_date, "symbol": symbol,
        "signal_close": f"{signal_close:.10g}", "ret_5d": "0.0100000000",
        "close": f"{signal_close:.10g}", "ma50": "90.0000000000",
        "close_above_ma50": "True", "outcome_date": "", "outcome_close": "",
        "outcome_return_pp": "", "outcome_status": "PENDING", "spy_return_pp": "",
        "excess_vs_spy_pp": "", "created_at": "2026-10-01T00:00:00+00:00",
        "sent_to_broker": "False",
    }


def resolve_args(ledger: pathlib.Path, cache_dir: pathlib.Path) -> argparse.Namespace:
    return argparse.Namespace(ledger=ledger, cache_dir=cache_dir, fetch=False,
                              as_of=None, log_rejected=None)


def read_rows(path: pathlib.Path) -> list[dict]:
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def setup_series(tmp_path: pathlib.Path, n_bars: int = 75, drop_symbol_bar: int | None = None,
                 drop_spy_bar: int | None = None):
    """SPY flat at 100; AAA rises +1/bar after index 60 (the signal bar)."""
    dates = gen_dates("2026-07-01", n_bars)
    signal_idx = 60
    spy_closes = [100.0] * n_bars
    aaa_closes = [100.0] * (signal_idx + 1) + [100.0 + k for k in range(1, n_bars - signal_idx)]
    spy_dates, aaa_dates = list(dates), list(dates)
    if drop_spy_bar is not None:
        del spy_dates[drop_spy_bar], spy_closes[drop_spy_bar]
    if drop_symbol_bar is not None:
        del aaa_dates[drop_symbol_bar], aaa_closes[drop_symbol_bar]
    write_cache(tmp_path, "SPY", spy_dates, spy_closes)
    write_cache(tmp_path, "AAA", aaa_dates, aaa_closes)
    return dates, dates[signal_idx]


# ---------------------------------------------------------------- calendar

def test_expected_sessions_october_2026():
    assert scanner.expected_sessions("2026-10-02") == [
        "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-09",
        "2026-10-12", "2026-10-13", "2026-10-14", "2026-10-15", "2026-10-16"]


def test_expected_sessions_thanksgiving_week():
    # Nov 26 2026 is a full closure; Fri Nov 27 IS a session.
    assert scanner.expected_sessions("2026-11-20") == [
        "2026-11-23", "2026-11-24", "2026-11-25", "2026-11-27", "2026-11-30",
        "2026-12-01", "2026-12-02", "2026-12-03", "2026-12-04", "2026-12-07"]


# ---------------------------------------------------------------- resolve

def test_complete_window_resolves_with_benchmark(tmp_path):
    dates, signal = setup_series(tmp_path)
    ledger = tmp_path / "obs.csv"
    make_ledger(ledger, [pending_row("AAA", signal)])
    scanner.cmd_resolve(resolve_args(ledger, tmp_path))
    (row,) = read_rows(ledger)
    assert row["outcome_status"] == "RESOLVED"
    assert row["outcome_date"] == dates[70]
    assert row["outcome_return_pp"] == "10.0000"
    assert row["spy_return_pp"] == "0.0000"
    assert row["excess_vs_spy_pp"] == "10.0000"


def test_missing_symbol_session_blocks_no_slide(tmp_path):
    dates, signal = setup_series(tmp_path, drop_symbol_bar=65)  # hole inside the window
    ledger = tmp_path / "obs.csv"
    make_ledger(ledger, [pending_row("AAA", signal)])
    scanner.cmd_resolve(resolve_args(ledger, tmp_path))
    (row,) = read_rows(ledger)
    assert row["outcome_status"] == "PENDING"
    assert row["outcome_date"] == "" and row["outcome_return_pp"] == ""


def test_vendor_wide_dropped_session_blocks_via_calendar(tmp_path):
    # SPY and AAA both miss the same session: symbol-vs-SPY dates agree, but the
    # NYSE calendar cross-check must still block the shifted window.
    dates, signal = setup_series(tmp_path, drop_symbol_bar=65, drop_spy_bar=65)
    ledger = tmp_path / "obs.csv"
    make_ledger(ledger, [pending_row("AAA", signal)])
    scanner.cmd_resolve(resolve_args(ledger, tmp_path))
    (row,) = read_rows(ledger)
    assert row["outcome_status"] == "PENDING"


def test_missing_benchmark_blocks_and_leaves_ledger_untouched(tmp_path):
    dates = gen_dates("2026-07-01", 75)
    signal = dates[60]
    write_cache(tmp_path, "AAA", dates, [100.0] * 75)  # no SPY.csv at all
    ledger = tmp_path / "obs.csv"
    make_ledger(ledger, [pending_row("AAA", signal)])
    before = ledger.read_bytes()
    scanner.cmd_resolve(resolve_args(ledger, tmp_path))
    assert ledger.read_bytes() == before
    (row,) = read_rows(ledger)
    assert row["outcome_status"] == "PENDING"


def test_not_mature_stays_pending(tmp_path):
    dates, signal = setup_series(tmp_path, n_bars=66)  # only 5 bars after signal
    ledger = tmp_path / "obs.csv"
    make_ledger(ledger, [pending_row("AAA", signal)])
    scanner.cmd_resolve(resolve_args(ledger, tmp_path))
    (row,) = read_rows(ledger)
    assert row["outcome_status"] == "PENDING"


def test_resolved_rows_preserved_byte_identical(tmp_path):
    dates, signal = setup_series(tmp_path)
    old_signal = dates[40]
    old = pending_row("AAA", old_signal)
    old.update({"outcome_date": dates[50], "outcome_close": "105",
                "outcome_return_pp": "5.0000", "outcome_status": "RESOLVED",
                "spy_return_pp": "1.0000", "excess_vs_spy_pp": "4.0000"})
    ledger = tmp_path / "obs.csv"
    make_ledger(ledger, [old, pending_row("AAA", signal)])
    scanner.cmd_resolve(resolve_args(ledger, tmp_path))
    rows = read_rows(ledger)
    assert rows[0] == old
    assert rows[1]["outcome_status"] == "RESOLVED"


# ---------------------------------------------------------------- tracks

def test_holdings_track_scan_uses_own_ids_and_universe(tmp_path):
    dates = gen_dates("2026-07-01", 75)
    # GME in a steady uptrend: ret_5d > 0 and close > ma50 at the last bar.
    write_cache(tmp_path, "GME", dates, [100.0 + i for i in range(75)])
    ledger = tmp_path / "h_obs.csv"
    rejected = tmp_path / "h_rej.csv"
    args = argparse.Namespace(ledger=ledger, cache_dir=tmp_path, fetch=False,
                              as_of=None, log_rejected=rejected, track="holdings")
    scanner.cmd_scan(args)
    (row,) = read_rows(ledger)
    assert row["symbol"] == "GME"
    assert row["hypothesis"] == scanner.HOLDINGS_HYPOTHESIS
    # holdings obs_id differs from the v1 id for the same symbol/date
    import hashlib
    v1_id = hashlib.sha256(
        f"{scanner.HYPOTHESIS}|GME|{dates[-1]}".encode()).hexdigest()[:24]
    assert row["observation_id"] != v1_id
    assert row["observation_id"] == hashlib.sha256(
        f"{scanner.HOLDINGS_HYPOTHESIS}|GME|{dates[-1]}".encode()).hexdigest()[:24]
    # scanner state must reset cleanly for a following v1 call
    scanner._apply_track(argparse.Namespace(track="v1"))
    assert scanner.ACTIVE_HYPOTHESIS == scanner.HYPOTHESIS


def test_v1_obs_id_unchanged_by_track_support():
    import hashlib
    scanner._apply_track(argparse.Namespace(track="v1"))
    assert scanner.obs_id("MU", "2026-10-02") == hashlib.sha256(
        b"momentum_continuation_ret5d_ma50_v1|MU|2026-10-02").hexdigest()[:24]


# ---------------------------------------------------------------- verifier

def _run_verifier(before: pathlib.Path, after: pathlib.Path, *extra: str) -> int:
    return subprocess.run(
        [sys.executable, str(HERE / "verify_ledger_preservation.py"),
         str(before), str(after), *extra],
        capture_output=True, text=True).returncode


def test_verifier_pass_and_fail(tmp_path):
    dates, signal = setup_series(tmp_path)
    before = tmp_path / "before.csv"
    make_ledger(before, [pending_row("AAA", signal)])
    after = tmp_path / "after.csv"
    make_ledger(after, [pending_row("AAA", signal)])
    assert _run_verifier(before, after) == 0

    rows = read_rows(after)
    rows[0].update({"outcome_date": dates[70], "outcome_close": "110",
                    "outcome_return_pp": "10.0000", "outcome_status": "RESOLVED",
                    "spy_return_pp": "0.0000", "excess_vs_spy_pp": "10.0000"})
    make_ledger(after, rows)
    assert _run_verifier(before, after) == 0  # clean PENDING -> RESOLVED transition

    rows[0]["spy_return_pp"] = ""  # incomplete resolution must fail
    make_ledger(after, rows)
    assert _run_verifier(before, after) == 1
