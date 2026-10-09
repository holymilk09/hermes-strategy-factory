#!/usr/bin/env python3
"""Phase 2 — engine correctness on real data (VALIDATION_PLAN.md §4)."""
from __future__ import annotations

import json
import random
from dataclasses import asdict

import numpy as np
import pandas as pd

from common import OOS_START, OUT, UNIVERSE_STOCKS, store
from src.research_intel.brief import build_brief, product_clusters
from src.research_intel.data import MemoryProvider
from src.research_intel.interest import Profile
from src.research_intel.moves import move_context
from src.research_intel.relationships import beta, pair_health
from src.research_intel.attribution import attribute
from src.research_intel.scoreboard import score
from src.research_intel.risk import risk_panel
from src.research_intel.weekly import weekly_map

SEED = 20261008
N_CASES = 200


def main():
    st = store()
    rng = random.Random(SEED)
    cm = product_clusters()
    sessions = [d for d in st.series("SPY").dates if d >= OOS_START]
    syms = [s for s in UNIVERSE_STOCKS if s in st.symbols()]
    full = {s: st.series(s) for s in st.symbols()}
    res = {}

    # 2a no look-ahead: truncated provider == full provider
    mism = []
    for _ in range(N_CASES):
        sym, d = rng.choice(syms), rng.choice(sessions)
        peers = [p for p in cm.all_peers(sym) if p in full] or ["QQQ"]
        peer = rng.choice(peers)
        trunc = MemoryProvider([s.upto(d) for s in full.values()])
        prof2 = Profile.from_dict({"holdings": [{"symbol": sym, "weight": 0.6}, {"symbol": peer, "weight": 0.4}]})
        a = [move_context(st, sym, d).to_dict(), asdict(beta(st, sym, d, "QQQ", 60)),
             asdict(beta(st, sym, d, "SPY", 120)), pair_health(st, sym, peer, d).to_dict(),
             attribute(st, sym, d, cm).to_dict(), score(st, sym, d).to_dict(),
             risk_panel(st, cm, prof2, d).to_dict()]
        b = [move_context(trunc, sym, d).to_dict(), asdict(beta(trunc, sym, d, "QQQ", 60)),
             asdict(beta(trunc, sym, d, "SPY", 120)), pair_health(trunc, sym, peer, d).to_dict(),
             attribute(trunc, sym, d, cm).to_dict(), score(trunc, sym, d).to_dict(),
             risk_panel(trunc, cm, prof2, d).to_dict()]
        if a != b:
            mism.append((sym, d.isoformat(), peer))
    res["2a"] = {"cases": N_CASES, "mismatches": mism, "pass": not mism}

    # 2b independent recomputation with pandas/numpy (own alignment, own returns)
    closes = pd.DataFrame({s: pd.Series(dict(zip(v.dates, v.closes))) for s, v in full.items()})
    closes = closes.reindex(pd.Index(full["SPY"].dates))
    rets = closes.pct_change()
    worst_b, worst_c, n_ok, n_skip = 0.0, 0.0, 0, 0
    for _ in range(N_CASES):
        sym, d = rng.choice(syms), rng.choice(sessions)
        ix, w = rng.choice(["SPY", "QQQ"]), rng.choice([60, 120])
        seg = rets.loc[:d].iloc[-w:][[sym, ix]]
        mine = beta(st, sym, d, ix, w)
        if seg.isna().any().any():
            if mine.status != "INSUFFICIENT_DATA":
                worst_b = float("inf")
            n_skip += 1
            continue
        b_np = np.polyfit(seg[ix].values, seg[sym].values, 1)[0]
        c_np = np.corrcoef(seg[ix].values, seg[sym].values)[0, 1]
        worst_b = max(worst_b, abs(b_np - mine.beta))
        worst_c = max(worst_c, abs(c_np - mine.corr))
        n_ok += 1
    res["2b"] = {"cases": N_CASES, "compared": n_ok, "insufficient_agreed": n_skip,
                 "max_abs_beta_diff": worst_b, "max_abs_corr_diff": worst_c,
                 "pass": worst_b < 1e-9 and worst_c < 1e-9}

    # 2c determinism
    prof = Profile.from_dict({"holdings": [{"symbol": "MU", "shares": 10}, {"symbol": "LLY", "shares": 5}],
                              "pins": ["NVDA", "JPM", "HON", "SKHY"]})
    d = sessions[-1]
    b1 = json.dumps(build_brief(st, prof, d), sort_keys=True)
    b2 = json.dumps(build_brief(st, prof, d), sort_keys=True)
    w1 = json.dumps(weekly_map(st, prof, d), sort_keys=True)
    w2 = json.dumps(weekly_map(st, prof, d), sort_keys=True)
    from src.research_intel.report import build_report
    r1 = json.dumps(build_report(st, prof, d), sort_keys=True)
    r2 = json.dumps(build_report(st, prof, d), sort_keys=True)
    res["2c"] = {"brief_identical": b1 == b2, "weekly_identical": w1 == w2, "report_identical": r1 == r2,
                 "pass": b1 == b2 and w1 == w2 and r1 == r2}

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "phase2.json").write_text(json.dumps(res, indent=1, default=str))
    for k, v in res.items():
        print(k, "PASS" if v["pass"] else "FAIL", {x: y for x, y in v.items() if x != "pass"})


if __name__ == "__main__":
    main()
