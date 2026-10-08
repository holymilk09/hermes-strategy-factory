#!/usr/bin/env python3
"""Phase 1e — explain every |daily return| > 15% (VALIDATION_PLAN.md §3).

Classes:
  EARNINGS      the session is the reaction session of the symbol's own report
  MARKET        QQQ or SMH moved >= 5% the same session (index/sector-wide event)
  PEER_EARNINGS a configured peer's earnings reaction landed that session
  DATA_ERROR    corporate-action / bad-print signature (raw vs adjusted inconsistency,
                identical consecutive closes, round-number print)
  UNEXPLAINED   none of the above (real news we can't see, or an unknown problem)
"""
from __future__ import annotations

import json

from common import OUT, calendar, store
from src.research_intel.brief import product_clusters
from src.research_intel.events import NOT_COVERED


def main():
    st, cal, cm = store(), calendar(), product_clusters()
    ph1 = json.loads((OUT / "phase1.json").read_text())
    qqq, smh = st.series("QQQ").as_map(), st.series("SMH").as_map()
    sessions = st.series("SPY").dates
    prev = {sessions[i]: sessions[i - 1] for i in range(1, len(sessions))}
    adj_steps = {s: {x["date"] for x in v["steps"]} for s, v in ph1["1b"].items()}
    rows = []
    for e in ph1["1e_candidates"]:
        from datetime import date
        sym, d = e["symbol"], date.fromisoformat(e["date"])
        p = prev[d]
        mkt = max(abs(qqq[d] / qqq[p] - 1), abs(smh[d] / smh[p] - 1)) * 100
        cls, why = "UNEXPLAINED", ""
        rx = cal.reaction_to(sym, d, p)
        quar = st.quarantine().get(sym, set())
        listed = st.raw_series(sym).dates[0]
        n_since_listing = sum(1 for x in sessions if listed <= x <= d)
        if d in quar or p in quar:
            cls, why = "DATA_ERROR", "inside corporate-action quarantine (adjustment audit)"
        elif rx is not NOT_COVERED and rx is not None:
            cls, why = "EARNINGS", f"reported {rx.date} {rx.timing}"
        elif n_since_listing <= 10:
            cls, why = "NEW_LISTING", f"session {n_since_listing} since first real bar {listed}"
        elif mkt >= 5:
            cls, why = "MARKET", f"QQQ/SMH max |move| {mkt:.1f}%"
        else:
            info = cm.info(sym)
            peers = cm.members(info.primary) if info.primary else ()
            hits = [x for x in peers if x != sym and cal.reaction_to(x, d, p) not in (None, NOT_COVERED)]
            if hits:
                cls, why = "PEER_EARNINGS", f"{info.primary} peer reaction: " + ",".join(hits[:4])
            elif rx is NOT_COVERED:
                why = "calendar does not cover this date"
        rows.append({**e, "class": cls, "why": why.strip(), "market_move_pp": round(mkt, 2)})
    (OUT / "phase1e.json").write_text(json.dumps(rows, indent=1))
    from collections import Counter
    print("1e classes:", dict(Counter(r["class"] for r in rows)), "of", len(rows))
    for r in rows:
        if r["class"] in ("UNEXPLAINED", "DATA_ERROR", "PEER_EARNINGS"):
            print(f"  {r['class']:13} {r['symbol']:5} {r['date']} {r['ret_pp']:+7.2f}%  mkt {r['market_move_pp']:.1f}%  {r['why']}")


if __name__ == "__main__":
    main()
