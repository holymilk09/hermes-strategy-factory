#!/usr/bin/env python3
"""
Momentum continuation (ret_5d + ma50) — NEW hypothesis, forward observation scanner/resolver.

Hypothesis ID: momentum_continuation_ret5d_ma50_v1
Status: PLANNED / EXPLORATORY — research only. No broker, no orders, no live trading.

This is NOT the frozen relative_strength_continuation lineage and must never write to its
ledgers. It writes only to its own ledger file (default: momentum_ret5d_ma50_observations.csv
in the working directory, or --ledger path).

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

Usage:
  scanner.py scan    --cache-dir /path/ohlcv --as-of 2026-07-01 --ledger obs.csv
  scanner.py scan    --fetch --as-of 2026-07-01 --ledger obs.csv
  scanner.py resolve --cache-dir /path/ohlcv --ledger obs.csv
  scanner.py summary --ledger obs.csv
"""
from __future__ import annotations
import argparse, csv, hashlib, pathlib, sys, statistics
from datetime import datetime, timezone

HYPOTHESIS = "momentum_continuation_ret5d_ma50_v1"
BENCHMARKS = {"SPY", "QQQ"}
DEFAULT_UNIVERSE = ['AAPL','ABBV','ADBE','ALB','AMD','AMGN','AMZN','ARM','ARQQ','ASML','AVGO','AXP','BA','BAC','BLK','BMY','C','CAT','COST','CRM','CRWD','DDOG','DE','DG','ENPH','FSLR','GD','GE','GILD','GOOGL','GS','HD','HON','IGV','IONQ','JNJ','JPM','LAC','LLY','LMT','LOW','MCD','META','MRK','MRVL','MS','MSFT','MU','NET','NFLX','NKE','NOC','NOW','NVDA','ON','ORCL','PFE','PLTR','QBTS','QCOM','REGN','RGTI','RTX','RUN','SBUX','SCHW','SEDG','SNOW','TAN','TGT','TJX','TSM','UNH','UNP','V','WFC','WMT','WOLF']

FIELDS = ["observation_id","hypothesis","signal_date","symbol","signal_close","ret_5d","close","ma50",
          "close_above_ma50","outcome_date","outcome_close","outcome_return_pp","outcome_status",
          "spy_return_pp","excess_vs_spy_pp","created_at","sent_to_broker"]

def obs_id(symbol: str, signal_date: str) -> str:
    return hashlib.sha256(f"{HYPOTHESIS}|{symbol}|{signal_date}".encode()).hexdigest()[:24]

def load_series(path: pathlib.Path):
    """Return sorted [(date_str, close)] from a Yahoo-format or generic OHLCV CSV."""
    with open(path, newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows: return []
    keys = {k.lower(): k for k in rows[0].keys()}
    dkey = keys.get('date') or keys.get('timestamp') or keys.get('datetime')
    ckey = keys.get('close')
    if not dkey or not ckey: raise ValueError(f"{path}: missing date/close columns")
    out = []
    for r in rows:
        f = _finite(r[ckey])
        if f is not None:
            out.append((r[dkey][:10], f))
    out.sort()
    # de-duplicate by date, keep last
    dedup = {}
    for d, c in out: dedup[d] = c
    return sorted(dedup.items())

def find_cache(cache_dir: pathlib.Path, symbol: str):
    for name in (f"{symbol}.csv", f"{symbol}_1D.csv", f"{symbol}_1d.csv"):
        p = cache_dir / name
        if p.exists(): return p
    return None

def _finite(v):
    try:
        f = float(v)
    except Exception:
        return None
    return f if f == f else None  # drop NaN closes (partial/session bars)

def fetch_series(symbol: str, start="2025-11-01", end=None):
    import yfinance as yf  # local import so cache-only use needs no yfinance
    h = yf.Ticker(symbol).history(start=start, end=end, auto_adjust=False)
    out = []
    for idx, v in zip(h.index, h['Close']):
        f = _finite(v)
        if f is not None:
            out.append((str(idx.date()), f))
    return out

def business_gap_check(series, idx, lookback=60):
    """Reject if the exchange-session spacing in the lookback looks gapped.
    Uses weekday spacing: >4 calendar days between consecutive bars in the last
    `lookback` bars (excluding known long weekends) is treated as suspect.
    This is a conservative completeness guard, not a trading-calendar proof."""
    from datetime import date
    start = max(0, idx - lookback + 1)
    seg = series[start:idx+1]
    for (d1, _), (d2, _) in zip(seg, seg[1:]):
        delta = (date.fromisoformat(d2) - date.fromisoformat(d1)).days
        if delta > 4:
            return f"gap {d1}->{d2} ({delta}d) in lookback"
    return None

def compute_features(series, signal_date):
    dates = [d for d, _ in series]
    if signal_date not in dates: return None, f"no bar on {signal_date}"
    i = dates.index(signal_date)
    if i < 50: return None, "fewer than 51 bars before signal (ma50 unavailable)"
    gap = business_gap_check(series, i)
    if gap: return None, gap
    closes = [c for _, c in series]
    ret_5d = closes[i] / closes[i-5] - 1.0
    ma50 = statistics.mean(closes[i-49:i+1])
    return {"close": closes[i], "ret_5d": ret_5d, "ma50": ma50, "above": closes[i] > ma50, "idx": i}, None

def tenth_bar(series, signal_date):
    dates = [d for d, _ in series]
    if signal_date not in dates: return None
    i = dates.index(signal_date)
    if i + 10 >= len(series): return None
    return series[i+10]

def load_ledger(path: pathlib.Path):
    if not path.exists(): return []
    with open(path, newline='') as f: return list(csv.DictReader(f))

def write_ledger(path: pathlib.Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

def get_series(symbol, cache_dir, fetch, end=None):
    if fetch: return fetch_series(symbol, end=end)
    p = find_cache(cache_dir, symbol) if cache_dir else None
    if p is None: raise FileNotFoundError(f"no cache file for {symbol}")
    return load_series(p)

def cmd_scan(args):
    rows = load_ledger(args.ledger)
    existing = {r["observation_id"] for r in rows}
    end = (args.as_of + "T23:59:59") if args.as_of and args.fetch else None
    selected, rejected_insufficient, scanned = [], [], 0
    for sym in DEFAULT_UNIVERSE:
        try: series = get_series(sym, args.cache_dir, args.fetch, end=end)
        except Exception as e:
            rejected_insufficient.append((sym, str(e))); continue
        if not series: continue
        signal_date = args.as_of or series[-1][0]
        # use latest bar <= as_of when as_of given
        if args.as_of:
            series = [(d, c) for d, c in series if d <= args.as_of]
            if not series: continue
            signal_date = series[-1][0]
        scanned += 1
        ft, err = compute_features(series, signal_date)
        if ft is None:
            rejected_insufficient.append((sym, err)); continue
        is_sel = ft["ret_5d"] > 0 and ft["above"]
        if getattr(args, "log_rejected", None) and not is_sel:
            rej_rows = load_ledger(args.log_rejected)
            roid = obs_id(sym, signal_date + "|rejected")
            if roid not in {r["observation_id"] for r in rej_rows}:
                rej_rows.append({"observation_id": roid, "hypothesis": HYPOTHESIS + "_rejected_cohort", "signal_date": signal_date,
                                 "symbol": sym, "signal_close": f"{ft['close']:.10g}", "ret_5d": f"{ft['ret_5d']:.10f}",
                                 "close": f"{ft['close']:.10g}", "ma50": f"{ft['ma50']:.10f}",
                                 "close_above_ma50": str(ft["above"]), "outcome_date": "", "outcome_close": "",
                                 "outcome_return_pp": "", "outcome_status": "PENDING", "spy_return_pp": "",
                                 "excess_vs_spy_pp": "", "created_at": datetime.now(timezone.utc).isoformat(),
                                 "sent_to_broker": "False"})
                write_ledger(args.log_rejected, rej_rows)
        if is_sel:
            oid = obs_id(sym, signal_date)
            selected.append(sym)
            if oid not in existing:
                rows.append({"observation_id": oid, "hypothesis": HYPOTHESIS, "signal_date": signal_date,
                             "symbol": sym, "signal_close": f"{ft['close']:.10g}", "ret_5d": f"{ft['ret_5d']:.10f}",
                             "close": f"{ft['close']:.10g}", "ma50": f"{ft['ma50']:.10f}",
                             "close_above_ma50": "True", "outcome_date": "", "outcome_close": "",
                             "outcome_return_pp": "", "outcome_status": "PENDING", "spy_return_pp": "",
                             "excess_vs_spy_pp": "", "created_at": datetime.now(timezone.utc).isoformat(),
                             "sent_to_broker": "False"})
    write_ledger(args.ledger, rows)
    print(f"scan as_of={args.as_of or 'latest'} scanned={scanned} selected={len(selected)} {selected}")
    print(f"insufficient/skipped={len(rejected_insufficient)}")
    for sym, why in rejected_insufficient[:15]: print(f"  SKIP {sym}: {why}")
    print(f"ledger rows total={len(rows)} -> {args.ledger}")

def cmd_resolve(args):
    rows = load_ledger(args.ledger)
    # SPY series for benchmarks
    try: spy = get_series("SPY", args.cache_dir, args.fetch)
    except Exception: spy = []
    changed = 0
    for r in rows:
        if r["outcome_status"] == "RESOLVED": continue  # preservation: never recompute resolved rows
        try: series = get_series(r["symbol"], args.cache_dir, args.fetch)
        except Exception: continue
        tenth = tenth_bar(series, r["signal_date"])
        if tenth is None: continue
        out_date, out_close = tenth
        sig = float(r["signal_close"])
        # series-consistent: recompute signal close from same series
        sdates = [d for d, _ in series]; si = sdates.index(r["signal_date"])
        sig_series = series[si][1]
        ret = (out_close / sig_series - 1.0) * 100
        r["outcome_date"] = out_date; r["outcome_close"] = f"{out_close:.10g}"
        r["outcome_return_pp"] = f"{ret:.4f}"; r["outcome_status"] = "RESOLVED"
        if spy:
            st = tenth_bar(spy, r["signal_date"])
            if st:
                sd = dict(spy); sret = (st[1] / sd[r["signal_date"]] - 1.0) * 100
                r["spy_return_pp"] = f"{sret:.4f}"; r["excess_vs_spy_pp"] = f"{ret - sret:.4f}"
        changed += 1
    write_ledger(args.ledger, rows)
    print(f"resolved {changed} rows; total {len(rows)}")

def cmd_summary(args):
    rows = load_ledger(args.ledger)
    res = [r for r in rows if r["outcome_status"] == "RESOLVED"]
    print(f"{HYPOTHESIS}: total={len(rows)} resolved={len(res)} pending={len(rows)-len(res)}")
    if res:
        vals = [float(r["outcome_return_pp"]) for r in res]
        exc = [float(r["excess_vs_spy_pp"]) for r in res if r["excess_vs_spy_pp"]]
        print(f"mean {statistics.mean(vals):+.4f}% median {statistics.median(vals):+.4f}% hit {sum(v>0 for v in vals)}/{len(vals)}")
        if exc: print(f"mean excess vs SPY {statistics.mean(exc):+.4f}pp (n={len(exc)})")
        by_date = {}
        for r in res: by_date.setdefault(r["signal_date"], []).append(float(r["outcome_return_pp"]))
        for d, v in sorted(by_date.items()): print(f"  {d}: n={len(v)} mean {statistics.mean(v):+.4f}%")

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("scan", "resolve", "summary"):
        p = sub.add_parser(name)
        p.add_argument("--ledger", type=pathlib.Path, default=pathlib.Path("momentum_ret5d_ma50_observations.csv"))
        p.add_argument("--cache-dir", type=pathlib.Path, default=None)
        p.add_argument("--fetch", action="store_true", help="fetch from Yahoo Finance instead of cache")
        p.add_argument("--as-of", default=None, help="YYYY-MM-DD (scan only)")
        p.add_argument("--log-rejected", type=pathlib.Path, default=None, help="also log non-selected names to this ledger (scan only)")
    args = ap.parse_args()
    {"scan": cmd_scan, "resolve": cmd_resolve, "summary": cmd_summary}[args.cmd](args)

if __name__ == "__main__":
    main()
