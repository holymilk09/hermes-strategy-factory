#!/usr/bin/env python3
"""Phase 1 — data integrity (VALIDATION_PLAN.md §3). Read-only over the caches.

Usage: python docs/claude-v0/validation/phase1_data.py  (from repo root)
Writes cache/research_intel/validation/phase1.json (gitignored) and prints a summary.
"""
from __future__ import annotations

import glob
import json
import pathlib
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.research_intel.data import CacheStore, build_series, parse_robinhood_historicals  # noqa: E402

RAW = ROOT / "cache/research_intel/raw"
OUT = ROOT / "cache/research_intel/validation"
SETTLED = date(2026, 10, 7)
HOLIDAYS = [date(2025, 12, 25), date(2026, 1, 1), date(2025, 7, 4), date(2024, 12, 25)]


def load(pattern):
    out = {}
    for f in sorted(glob.glob(str(RAW / pattern))):
        for s in parse_robinhood_historicals(json.load(open(f)), settled_through=SETTLED):
            out[s.symbol] = s
    return out


def main():
    split = CacheStore(ROOT / "cache/research_intel/ohlcv_v2")
    raw = load("hist_raw_*.json")
    res = {}

    # 1b adjustment consistency: ratio raw/split per date; changes must be single-date steps
    adj = {}
    for sym in split.symbols():
        s = split.series(sym).as_map()
        r = raw[sym].as_map()
        common = sorted(s.keys() & r.keys())
        ratios = [(d, r[d] / s[d]) for d in common]
        steps = []
        for (d0, a), (d1, b) in zip(ratios, ratios[1:]):
            if abs(b / a - 1) > 1e-6:
                steps.append({"date": d1.isoformat(), "ratio_before": round(a, 6), "ratio_after": round(b, 6),
                              "factor": round(a / b, 6)})
        adj[sym] = {"dates_compared": len(common), "steps": steps,
                    "final_ratio": round(ratios[-1][1], 9) if ratios else None,
                    "missing_in_raw": len(set(s) - set(r)), "missing_in_split": len(set(r) - set(s))}
    res["1b"] = adj
    pass_1b = all(v["final_ratio"] is not None and abs(v["final_ratio"] - 1) < 1e-9
                  and v["missing_in_raw"] == 0 and v["missing_in_split"] == 0 for v in adj.values())

    # 1c calendar: SPY sanity + every stock has every SPY session inside its own listed range
    spy = split.series("SPY")
    weekend = [d.isoformat() for d in spy.dates if d.weekday() >= 5]
    holiday = [d.isoformat() for d in spy.dates if d in HOLIDAYS]
    gaps = {}
    for sym in split.symbols():
        ser = split.series(sym)
        first = ser.dates[0]
        have = set(ser.dates)
        miss = [d.isoformat() for d in spy.dates if d >= first and d not in have]
        extra = [d.isoformat() for d in ser.dates if d not in set(spy.dates)]
        if miss or extra:
            gaps[sym] = {"missing": miss, "extra": extra}
    res["1c"] = {"spy_sessions": len(spy.dates), "weekend_dates": weekend, "holiday_dates": holiday,
                 "symbol_gaps": gaps}
    pass_1c = not weekend and not holiday and not gaps

    # 1d idempotency: earlier (2026-03-25..) cache vs v2 on overlapping dates
    old = CacheStore(ROOT / "cache/research_intel/ohlcv")
    conflicts = {}
    compared = 0
    for sym in old.symbols():
        if sym not in split.symbols():
            continue
        a, b = old.series(sym).as_map(), split.series(sym).as_map()
        for d in a.keys() & b.keys():
            compared += 1
            if abs(a[d] - b[d]) > 1e-9:
                conflicts.setdefault(sym, []).append([d.isoformat(), a[d], b[d]])
    res["1d"] = {"overlapping_closes_compared": compared, "conflicts": conflicts}
    pass_1d = compared > 0 and not conflicts

    # 1e extreme moves (> 15% daily) listed for explanation
    ext = []
    for sym in split.symbols():
        ser = split.series(sym)
        for i in range(1, len(ser.closes)):
            r = ser.closes[i] / ser.closes[i - 1] - 1
            if abs(r) > 0.15:
                ext.append({"symbol": sym, "date": ser.dates[i].isoformat(),
                            "prev_date": ser.dates[i - 1].isoformat(), "ret_pp": round(r * 100, 2)})
    res["1e_candidates"] = ext

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "phase1.json").write_text(json.dumps(res, indent=1))
    print("1b adjustment:", "PASS" if pass_1b else "CHECK",
          {k: v["steps"] for k, v in adj.items() if v["steps"]})
    print("1c calendar:", "PASS" if pass_1c else "FAIL", res["1c"]["spy_sessions"], "SPY sessions;",
          "gaps:", gaps or "none", "weekend:", weekend, "holiday:", holiday)
    print("1d idempotency:", "PASS" if pass_1d else "FAIL", compared, "closes compared;", conflicts or "no conflicts")
    print("1e extreme moves (>15%):", len(ext))
    for e in ext:
        print("  ", e)


if __name__ == "__main__":
    main()
