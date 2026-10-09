#!/usr/bin/env python3
"""Forward test (Phase 5 precursor): score sessions the system has never seen.

For each new settled session D appended to the forward cache:
  - run the brief as of D (demo profile) -> it must build cleanly on fresh data
  - for every universe stock: engine residual vs naive (beta=1 to SPY) residual on D,
    using only data <= D (the engine baseline already excludes D)
  - list alerts fired on D
Appends one record per session to cache/research_intel/validation/forward_log.jsonl.
A single session is a smoke test, not evidence; gates are evaluated only once the
forward sample reaches the size registered in VALIDATION_PLAN.md.
"""
from __future__ import annotations

import json
import shutil
import statistics
import sys
from datetime import date

from common import OUT, ROOT, UNIVERSE_STOCKS, calendar
from src.research_intel.brief import build_brief, render_brief_md
from src.research_intel.data import CacheStore, build_series
from src.research_intel.events import EventCalendar
from src.research_intel.interest import Profile
from src.research_intel.moves import ALERT, move_context

V2 = ROOT / "cache/research_intel/ohlcv_v2"
FWD = ROOT / "cache/research_intel/ohlcv_fwd"


def main(session: str, closes_file: str):
    d = date.fromisoformat(session)
    if not FWD.exists():
        shutil.copytree(V2, FWD)
    st = CacheStore(FWD)
    rows = json.loads(open(closes_file).read())["rows"]
    for sym, close, _last in rows:
        st.write(build_series(sym, [(d, float(close))], "robinhood:quotes-official-close"))
    st = CacheStore(FWD)
    spy = st.series("SPY")
    assert spy.last_date == d, f"SPY last {spy.last_date} != {d}"
    prev = spy.dates[-2]
    spy_ret = (spy.closes[-1] / spy.closes[-2] - 1) * 100
    per, alerts = {}, []
    for s in UNIVERSE_STOCKS:
        m = move_context(st, s, d)
        if m.status == "INSUFFICIENT_DATA":
            per[s] = {"status": m.status, "reason": m.reason}
            continue
        per[s] = {"move_pp": round(m.move_pp, 3), "implied_pp": round(m.implied_pp, 3),
                  "engine_abs_err": round(abs(m.move_pp - m.implied_pp), 3),
                  "naive_abs_err": round(abs(m.move_pp - spy_ret), 3),
                  "z": round(m.residual_z, 2), "status": m.status}
        if m.status == ALERT:
            alerts.append(s)
    ok = [v for v in per.values() if "engine_abs_err" in v]
    fwd = EventCalendar.load(ROOT / "cache/research_intel/events/earnings_2026-10-08_31d.json",
                             date(2026, 10, 8), date(2026, 10, 8), date(2026, 11, 7))
    cal = calendar().merged(fwd)
    prof = Profile.from_dict(json.loads((ROOT / "docs/claude-v0/examples/demo_profile.json").read_text()))
    b = build_brief(st, prof, d, cal)
    md = render_brief_md(b)
    (OUT / f"forward_brief_{d}.md").write_text(md)
    (OUT / f"forward_brief_{d}.json").write_text(json.dumps(b, indent=1, default=str))
    rec = {"session": session, "prev_session": prev.isoformat(), "spy_move_pp": round(spy_ret, 3),
           "stocks_judged": len(ok), "insufficient": [s for s, v in per.items() if "engine_abs_err" not in v],
           "engine_mean_abs_err": round(statistics.fmean(v["engine_abs_err"] for v in ok), 4),
           "naive_mean_abs_err": round(statistics.fmean(v["naive_abs_err"] for v in ok), 4),
           "engine_wins": sum(v["engine_abs_err"] < v["naive_abs_err"] for v in ok),
           "alerts": alerts, "headline": b["headline"], "per_stock": per}
    with open(OUT / "forward_log.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({k: v for k, v in rec.items() if k != "per_stock"}, indent=1))
    for s in alerts:
        print("ALERT", s, per[s])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
