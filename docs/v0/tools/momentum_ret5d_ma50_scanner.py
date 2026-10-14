#!/usr/bin/env python3
"""
Momentum continuation (ret_5d + ma50) — NEW hypothesis, forward observation scanner/resolver.

Hypothesis ID: momentum_continuation_ret5d_ma50_v1
Status: EXPLORATORY — research only. No broker, no orders, no live trading.

This is NOT the frozen relative_strength_continuation lineage and must never write to its
ledgers. It writes only to its own ledger file (--ledger) and optionally a same-date
rejected-cohort ledger (--log-rejected).

Rule (preregistered, see HYPOTHESIS_momentum_ret5d_ma50_v1.md):
  select if ret_5d > 0 AND close > ma50, computed on a COMPLETE daily series.
  A series with a missing expected session in the 60 bars before the signal is
  rejected as INSUFFICIENT_DATA for that symbol (no available-bar shifting).

Data conventions:
  - One source per calculation, series-consistent (split-adjusted) closes.
  - Partial/pre-market bars with NaN closes are dropped before any feature or
    signal-date computation (2026-10-08 fix: a Yahoo Oct-7 pre-market bar with NaN
    closes once produced a spurious zero-selection scan).
  - scan source: local cache dir of <SYM>.csv / <SYM>_1D.csv (Yahoo-format or date,close,...),
    or Yahoo Finance fetch with --fetch (auto_adjust=False).
  - Resolution: 10 completed trading bars after signal, signal excluded, raw return in pp.
    Cost-adj = raw - 0.15pp, delay-adj = raw - 0.05pp are reporting-only (not stored).
  - Resolution is GUARDED (2026-10-14, P0 hardening, Matt-approved): the SPY series is
    the session calendar. A row resolves only if the symbol's bars on the 10 expected
    sessions after the signal exactly match SPY's sessions for that window (a missing
    session blocks resolution — the window never slides over available bars), and only
    if the SPY benchmark window itself is complete (a row is never stamped RESOLVED
    with blank spy/excess fields, because preservation would make that permanent).
    Ledger writes are atomic (temp file + replace in the same directory).

Ledger format (frozen — do not reorder FIELDS or change obs_id; existing ledgers
in the wild depend on both):
  observation_id = sha256("<hypothesis>|<symbol>|<signal_date>")[:24]
  rejected-cohort ids use signal_date + "|rejected" as the date component.

Usage:
  scanner.py scan    --cache-dir /path/ohlcv --as-of 2026-07-01 --ledger obs.csv
  scanner.py scan    --fetch --as-of 2026-07-01 --ledger obs.csv --log-rejected rej.csv
  scanner.py resolve --cache-dir /path/ohlcv --ledger obs.csv
  scanner.py summary --ledger obs.csv
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import statistics
import sys
from datetime import date, datetime, timedelta, timezone

HYPOTHESIS = "momentum_continuation_ret5d_ma50_v1"
BENCHMARKS = {"SPY", "QQQ"}

DEFAULT_UNIVERSE = [
    'AAPL', 'ABBV', 'ADBE', 'ALB', 'AMD', 'AMGN', 'AMZN', 'ARM', 'ARQQ', 'ASML',
    'AVGO', 'AXP', 'BA', 'BAC', 'BLK', 'BMY', 'C', 'CAT', 'COST', 'CRM', 'CRWD',
    'DDOG', 'DE', 'DG', 'ENPH', 'FSLR', 'GD', 'GE', 'GILD', 'GOOGL', 'GS', 'HD',
    'HON', 'IGV', 'IONQ', 'JNJ', 'JPM', 'LAC', 'LLY', 'LMT', 'LOW', 'MCD', 'META',
    'MRK', 'MRVL', 'MS', 'MSFT', 'MU', 'NET', 'NFLX', 'NKE', 'NOC', 'NOW', 'NVDA',
    'ON', 'ORCL', 'PFE', 'PLTR', 'QBTS', 'QCOM', 'REGN', 'RGTI', 'RTX', 'RUN',
    'SBUX', 'SCHW', 'SEDG', 'SNOW', 'TAN', 'TGT', 'TJX', 'TSM', 'UNH', 'UNP',
    'V', 'WFC', 'WMT', 'WOLF',
]

# FROZEN column order — see module docstring.
FIELDS = ["observation_id", "hypothesis", "signal_date", "symbol", "signal_close",
          "ret_5d", "close", "ma50", "close_above_ma50", "outcome_date",
          "outcome_close", "outcome_return_pp", "outcome_status", "spy_return_pp",
          "excess_vs_spy_pp", "created_at", "sent_to_broker"]

LOOKBACK_BARS = 60   # completeness-guard window
MA_WINDOW = 50       # moving-average window
RET_WINDOW = 5       # momentum window
RESOLVE_BARS = 10    # bars after signal for resolution


# ---------------------------------------------------------------- series I/O

def _finite(value) -> float | None:
    """Return float(value), or None for missing/NaN input (partial session bars)."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if f == f else None


def obs_id(symbol: str, signal_date: str) -> str:
    """Stable observation id. Format frozen — existing ledgers depend on it."""
    return hashlib.sha256(f"{HYPOTHESIS}|{symbol}|{signal_date}".encode()).hexdigest()[:24]


def load_series(path: pathlib.Path) -> list[tuple[str, float]]:
    """Sorted, date-deduplicated [(date_str, close)] from a Yahoo-format or generic OHLCV CSV."""
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return []
    keys = {k.lower(): k for k in rows[0].keys()}
    dkey = keys.get('date') or keys.get('timestamp') or keys.get('datetime')
    ckey = keys.get('close')
    if not dkey or not ckey:
        raise ValueError(f"{path}: missing date/close columns")
    by_date: dict[str, float] = {}
    for r in rows:
        close = _finite(r[ckey])
        if close is not None:
            by_date[r[dkey][:10]] = close  # keep last on duplicates
    return sorted(by_date.items())


def find_cache(cache_dir: pathlib.Path, symbol: str) -> pathlib.Path | None:
    for name in (f"{symbol}.csv", f"{symbol}_1D.csv", f"{symbol}_1d.csv"):
        p = cache_dir / name
        if p.exists():
            return p
    return None


def fetch_series(symbol: str, start: str = "2025-11-01", end: str | None = None) -> list[tuple[str, float]]:
    """Fetch daily closes from Yahoo Finance. NaN/partial bars are dropped."""
    import yfinance as yf  # local import so cache-only use needs no yfinance
    h = yf.Ticker(symbol).history(start=start, end=end, auto_adjust=False)
    out = []
    for idx, v in zip(h.index, h['Close']):
        close = _finite(v)
        if close is not None:
            out.append((str(idx.date()), close))
    return out


def get_series(symbol: str, cache_dir: pathlib.Path | None, fetch: bool,
               end: str | None = None) -> list[tuple[str, float]]:
    if fetch:
        return fetch_series(symbol, end=end)
    p = find_cache(cache_dir, symbol) if cache_dir else None
    if p is None:
        raise FileNotFoundError(f"no cache file for {symbol}")
    return load_series(p)


# ---------------------------------------------------------------- features

def business_gap_check(series: list[tuple[str, float]], idx: int,
                       lookback: int = LOOKBACK_BARS) -> str | None:
    """Return a reason string if the lookback window looks gapped, else None.

    Weekday spacing check: >4 calendar days between consecutive bars in the last
    `lookback` bars is treated as suspect. Conservative completeness guard, not a
    trading-calendar proof. A missing session makes the symbol/date INSUFFICIENT —
    we never slide the window over gaps.
    """
    start = max(0, idx - lookback + 1)
    seg = series[start:idx + 1]
    for (d1, _), (d2, _) in zip(seg, seg[1:]):
        delta = (date.fromisoformat(d2) - date.fromisoformat(d1)).days
        if delta > 4:
            return f"gap {d1}->{d2} ({delta}d) in lookback"
    return None


def compute_features(series: list[tuple[str, float]],
                     signal_date: str) -> tuple[dict | None, str | None]:
    """Features at signal_date. Returns (features, None) or (None, reason)."""
    dates = [d for d, _ in series]
    if signal_date not in dates:
        return None, f"no bar on {signal_date}"
    i = dates.index(signal_date)
    if i < MA_WINDOW:
        return None, f"fewer than {MA_WINDOW + 1} bars before signal (ma50 unavailable)"
    if (gap := business_gap_check(series, i)):
        return None, gap
    closes = [c for _, c in series]
    ret_5d = closes[i] / closes[i - RET_WINDOW] - 1.0
    ma50 = statistics.mean(closes[i - MA_WINDOW + 1:i + 1])
    return {"close": closes[i], "ret_5d": ret_5d, "ma50": ma50,
            "above": closes[i] > ma50, "idx": i}, None


def nth_bar(series: list[tuple[str, float]], signal_date: str,
            n: int = RESOLVE_BARS) -> tuple[str, float] | None:
    """The nth completed bar after signal (signal excluded)."""
    dates = [d for d, _ in series]
    if signal_date not in dates:
        return None
    i = dates.index(signal_date)
    if i + n >= len(series):
        return None
    return series[i + n]


# NYSE full-closure holidays, used to cross-check the SPY-derived session calendar
# (a vendor-wide dropped session would shift SPY and every symbol together; the
# symbol-vs-SPY check alone cannot see that). Fail-closed: a disagreement blocks
# resolution and is logged for operator review. Extend this set before 2028.
NYSE_HOLIDAYS = {
    # 2026
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
    # 2027
    "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31",
    "2027-06-18", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24",
}


def expected_sessions(signal_date: str, n: int = RESOLVE_BARS) -> list[str] | None:
    """The n expected trading sessions after signal_date per the NYSE calendar.

    Returns None when the window runs past the holiday table's coverage, in
    which case callers fall back to the SPY-calendar check alone.
    """
    d = date.fromisoformat(signal_date)
    out: list[str] = []
    while len(out) < n:
        d += timedelta(days=1)
        if d.isoformat()[:4] not in ("2026", "2027"):
            return None
        if d.weekday() < 5 and d.isoformat() not in NYSE_HOLIDAYS:
            out.append(d.isoformat())
    return out


def forward_window_check(symbol_series: list[tuple[str, float]],
                         spy_series: list[tuple[str, float]],
                         signal_date: str,
                         n: int = RESOLVE_BARS) -> tuple[tuple[str, float] | None, str, str | None]:
    """Guarded resolution window check (P0, 2026-10-14). SPY is the session calendar.

    Returns (outcome, category, detail):
      - ((outcome_date, outcome_close), "OK", None) — safe to resolve.
      - (None, "NOT_MATURE", None) — fewer than n SPY sessions after the signal yet.
      - (None, "BENCHMARK", detail) — SPY lacks the signal bar or its window is
        unusable; the row must NOT resolve (its excess-vs-SPY would be blank forever).
      - (None, "WINDOW", detail) — the symbol is missing an expected session inside
        the window (or its signal bar); block, never slide to the nth available bar.
    """
    spy_dates = [d for d, _ in spy_series]
    if signal_date not in spy_dates:
        return None, "BENCHMARK", f"SPY has no bar on signal date {signal_date}"
    si = spy_dates.index(signal_date)
    if si + n >= len(spy_series):
        return None, "NOT_MATURE", None
    spy_sessions = spy_dates[si + 1: si + n + 1]
    expected_outcome_date = spy_sessions[-1]

    cal_sessions = expected_sessions(signal_date, n)
    if cal_sessions is not None and cal_sessions != spy_sessions:
        return None, "BENCHMARK", (f"SPY window sessions {spy_sessions} disagree with "
                                   f"the NYSE calendar {cal_sessions}; possible dropped "
                                   f"session in the benchmark series — do not resolve")

    sym_by_date = dict(symbol_series)
    if signal_date not in sym_by_date:
        return None, "WINDOW", f"symbol has no bar on signal date {signal_date}"
    missing = [d for d in spy_sessions if d not in sym_by_date]
    if missing:
        return None, "WINDOW", (f"missing expected session(s) {missing} in forward "
                                f"window -> {expected_outcome_date}; window must not slide")
    return (expected_outcome_date, sym_by_date[expected_outcome_date]), "OK", None


# ---------------------------------------------------------------- ledgers

def load_ledger(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def write_ledger(path: pathlib.Path, rows: list[dict]) -> None:
    """Write the ledger atomically: temp file in the same dir, then os.replace.

    A crash mid-write must never leave a truncated ledger behind — the ledger is
    the forward record and cannot be recreated.
    """
    import os
    import tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline='') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def make_row(symbol: str, signal_date: str, features: dict, selected: bool) -> dict:
    """Build one ledger row. Format must match FIELDS exactly."""
    oid = obs_id(symbol, signal_date if selected else signal_date + "|rejected")
    return {
        "observation_id": oid,
        "hypothesis": HYPOTHESIS if selected else HYPOTHESIS + "_rejected_cohort",
        "signal_date": signal_date,
        "symbol": symbol,
        "signal_close": f"{features['close']:.10g}",
        "ret_5d": f"{features['ret_5d']:.10f}",
        "close": f"{features['close']:.10g}",
        "ma50": f"{features['ma50']:.10f}",
        "close_above_ma50": str(features["above"]) if not selected else "True",
        "outcome_date": "", "outcome_close": "", "outcome_return_pp": "",
        "outcome_status": "PENDING", "spy_return_pp": "", "excess_vs_spy_pp": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sent_to_broker": "False",
    }


# ---------------------------------------------------------------- commands

def cmd_scan(args) -> None:
    rows = load_ledger(args.ledger)
    existing = {r["observation_id"] for r in rows}
    rej_existing: set[str] = set()
    if args.log_rejected:
        rej_existing = {r["observation_id"] for r in load_ledger(args.log_rejected)}
    # yfinance `end` is exclusive: to include as_of's bar, fetch through the next day
    end = None
    if args.as_of and args.fetch:
        end = (date.fromisoformat(args.as_of) + timedelta(days=1)).isoformat()

    new_selected: list[dict] = []
    new_rejected: list[dict] = []
    selected_syms: list[str] = []
    skipped: list[tuple[str, str]] = []
    scanned = 0

    for sym in DEFAULT_UNIVERSE:
        try:
            series = get_series(sym, args.cache_dir, args.fetch, end=end)
        except Exception as e:
            skipped.append((sym, str(e)))
            continue
        if not series:
            continue
        if args.as_of:
            # use latest bar <= as_of as the signal date
            series = [(d, c) for d, c in series if d <= args.as_of]
            if not series:
                continue
        # signal date: explicit --as-of, else the latest complete bar
        signal_date = series[-1][0]
        scanned += 1

        ft, err = compute_features(series, signal_date)
        if ft is None:
            skipped.append((sym, err))
            continue
        is_sel = ft["ret_5d"] > 0 and ft["above"]
        row = make_row(sym, signal_date, ft, selected=is_sel)
        seen = existing if is_sel else rej_existing
        if row["observation_id"] in seen:
            continue  # idempotent: never duplicate
        seen.add(row["observation_id"])
        if is_sel:
            selected_syms.append(sym)
            new_selected.append(row)
        else:
            new_rejected.append(row)

    rows.extend(new_selected)
    write_ledger(args.ledger, rows)

    if args.log_rejected and new_rejected:
        rej_rows = load_ledger(args.log_rejected)
        rej_have = {r["observation_id"] for r in rej_rows}
        rej_rows.extend(r for r in new_rejected if r["observation_id"] not in rej_have)
        write_ledger(args.log_rejected, rej_rows)

    print(f"scan as_of={args.as_of or 'latest'} scanned={scanned} "
          f"selected={len(selected_syms)} {selected_syms}")
    print(f"new rows: selected={len(new_selected)} rejected={len(new_rejected)} "
          f"insufficient/skipped={len(skipped)}")
    for sym, why in skipped[:15]:
        print(f"  SKIP {sym}: {why}")
    print(f"ledger rows total={len(rows)} -> {args.ledger}")


def cmd_resolve(args) -> None:
    """Guarded resolution (P0, 2026-10-14). See forward_window_check.

    A row resolves only with a complete SPY-calendar window for the symbol AND a
    complete benchmark window. Otherwise it stays PENDING and the block is logged.
    Resolved rows are never recomputed (preservation).
    """
    rows = load_ledger(args.ledger)
    try:
        spy = get_series("SPY", args.cache_dir, args.fetch)
    except Exception as e:
        spy = []
        print(f"resolve BLOCKED: SPY benchmark series unavailable ({e}); "
              f"0 rows resolved, ledger untouched")
    if not spy:
        print("resolve BLOCKED: SPY benchmark series empty; "
              "0 rows resolved, ledger untouched")
        print(f"resolved 0 rows; total {len(rows)}")
        return
    spy_by_date = dict(spy)
    changed = 0
    counts = {"NOT_MATURE": 0, "BENCHMARK": 0, "WINDOW": 0, "FETCH": 0}
    for r in rows:
        if r["outcome_status"] == "RESOLVED":
            continue  # preservation: never recompute a resolved row
        try:
            series = get_series(r["symbol"], args.cache_dir, args.fetch)
        except Exception:
            counts["FETCH"] += 1
            continue
        outcome, category, detail = forward_window_check(series, spy, r["signal_date"])
        if outcome is None:
            counts[category] += 1
            if detail:
                print(f"  BLOCK {r['symbol']} signal {r['signal_date']}: {detail}")
            continue
        out_date, out_close = outcome
        # series-consistent: signal close comes from the same series, never the ledger level
        sig_close = dict(series)[r["signal_date"]]
        ret = (out_close / sig_close - 1.0) * 100
        # benchmark window is guaranteed complete by the check above
        spy_out_close = spy_by_date[out_date]
        sret = (spy_out_close / spy_by_date[r["signal_date"]] - 1.0) * 100
        r["outcome_date"] = out_date
        r["outcome_close"] = f"{out_close:.10g}"
        r["outcome_return_pp"] = f"{ret:.4f}"
        r["outcome_status"] = "RESOLVED"
        r["spy_return_pp"] = f"{sret:.4f}"
        r["excess_vs_spy_pp"] = f"{ret - sret:.4f}"
        changed += 1
    write_ledger(args.ledger, rows)
    print(f"resolved {changed} rows; total {len(rows)}; "
          f"not_mature={counts['NOT_MATURE']} blocked_window={counts['WINDOW']} "
          f"blocked_benchmark={counts['BENCHMARK']} fetch_failed={counts['FETCH']}")


def cmd_summary(args) -> None:
    rows = load_ledger(args.ledger)
    res = [r for r in rows if r["outcome_status"] == "RESOLVED"]
    print(f"{HYPOTHESIS}: total={len(rows)} resolved={len(res)} pending={len(rows) - len(res)}")
    if not res:
        return
    vals = [float(r["outcome_return_pp"]) for r in res]
    exc = [float(r["excess_vs_spy_pp"]) for r in res if r["excess_vs_spy_pp"]]
    print(f"mean {statistics.mean(vals):+.4f}% median {statistics.median(vals):+.4f}% "
          f"hit {sum(v > 0 for v in vals)}/{len(vals)}")
    if exc:
        print(f"mean excess vs SPY {statistics.mean(exc):+.4f}pp (n={len(exc)})")
    by_date: dict[str, list[float]] = {}
    for r in res:
        by_date.setdefault(r["signal_date"], []).append(float(r["outcome_return_pp"]))
    for d, v in sorted(by_date.items()):
        print(f"  {d}: n={len(v)} mean {statistics.mean(v):+.4f}%")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("scan", "resolve", "summary"):
        p = sub.add_parser(name)
        p.add_argument("--ledger", type=pathlib.Path,
                       default=pathlib.Path("momentum_ret5d_ma50_observations.csv"))
        p.add_argument("--cache-dir", type=pathlib.Path, default=None)
        p.add_argument("--fetch", action="store_true",
                       help="fetch from Yahoo Finance instead of cache")
        p.add_argument("--as-of", default=None, help="YYYY-MM-DD (scan only)")
        p.add_argument("--log-rejected", type=pathlib.Path, default=None,
                       help="also log non-selected names to this ledger (scan only)")
    args = ap.parse_args()
    {"scan": cmd_scan, "resolve": cmd_resolve, "summary": cmd_summary}[args.cmd](args)


if __name__ == "__main__":
    main()
