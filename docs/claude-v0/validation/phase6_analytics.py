#!/usr/bin/env python3
"""Amendment B — attribution (B1), VaR coverage (B2), scoreboard recomputation (B3).
OOS 2025-07-01..2026-10-07 on the quarantined v2 cache. Gates frozen in VALIDATION_PLAN.md §9."""
from __future__ import annotations

import json
import math
import random
import statistics
from datetime import date

import numpy as np
import pandas as pd

from common import OOS_START, OUT, UNIVERSE_STOCKS, store
from src.research_intel.attribution import attribute
from src.research_intel.brief import product_clusters
from src.research_intel.data import OK, MemoryProvider, aligned_returns
from src.research_intel.interest import Profile
from src.research_intel.risk import risk_panel
from src.research_intel.scoreboard import score

SEED = 20261009
VAR_BOOK = ["MU", "NVDA", "LLY", "JPM", "AAPL", "MSFT"]


def main():
    st = store()
    p = MemoryProvider([st.series(s) for s in st.symbols()])
    cm = product_clusters()
    sessions = list(st.series("SPY").dates)
    oos = [d for d in sessions if OOS_START <= d <= date(2026, 10, 7)]
    res = {}

    # ---- B1 attribution
    per = {}
    for s in UNIVERSE_STOCKS:
        etf = cm.info(s).etf
        if not etf or etf.upper() not in p.symbols():
            continue
        e2, e1 = [], []
        for d in oos:
            a = attribute(p, s, d, cm)
            if a.status != OK or a.sector_etf is None:
                continue
            # market-only residual from the SAME baseline: move - beta_market_only * r_m
            w = aligned_returns(p, [s, "SPY"], d, a.baseline_n + 1)
            r, m = np.array(w.returns[s][:-1]), np.array(w.returns["SPY"][:-1])
            b0, a0 = np.polyfit(m, r, 1)
            e1.append(((w.returns[s][-1] - a0 - b0 * w.returns["SPY"][-1]) * 100) ** 2)
            e2.append(a.idiosyncratic_pp ** 2)
        if len(e2) >= 30:
            per[s] = {"etf": etf, "n": len(e2), "mse_two_factor": round(statistics.fmean(e2), 4),
                      "mse_market_only": round(statistics.fmean(e1), 4)}
    pooled2 = statistics.fmean(v["mse_two_factor"] * v["n"] for v in per.values()) / statistics.fmean(v["n"] for v in per.values())
    pooled1 = statistics.fmean(v["mse_market_only"] * v["n"] for v in per.values()) / statistics.fmean(v["n"] for v in per.values())
    wins = sum(1 for v in per.values() if v["mse_two_factor"] < v["mse_market_only"])
    res["B1"] = {"stocks": len(per), "two_factor_better": wins, "share": round(wins / len(per), 4),
                 "pooled_mse_reduction": round(1 - pooled2 / pooled1, 4),
                 "pass": (1 - pooled2 / pooled1) >= 0.05 and wins / len(per) >= 0.60,
                 "per_stock": per}

    # ---- B2 VaR coverage
    prof = Profile.from_dict({"holdings": [{"symbol": s, "weight": 1 / len(VAR_BOOK)} for s in VAR_BOOK]})
    idx = {d: i for i, d in enumerate(sessions)}
    exc95 = exc99 = n = 0
    rows = []
    for d in oos:
        prev = sessions[idx[d] - 1]
        rp = risk_panel(p, cm, prof, prev, window=250, floor=60)
        if rp.status != OK or rp.window_n < 250:
            continue
        w = aligned_returns(p, VAR_BOOK, d, 1)
        if w.status != OK:
            continue
        ret = sum(rp.weights[s] * w.returns[s][0] for s in VAR_BOOK) * 100
        n += 1
        e95, e99 = ret < -rp.var_95_pp, ret < -rp.var_99_pp
        exc95 += e95
        exc99 += e99
        rows.append((d.isoformat(), round(ret, 3), rp.var_95_pp, rp.var_99_pp, bool(e95), bool(e99)))
    rate95, rate99 = exc95 / n, exc99 / n
    # Kupiec POF likelihood-ratio test for the 95% VaR
    def lr(x, n, pexp):
        phat = x / n
        if phat in (0, 1):
            return None
        return -2 * (x * math.log(pexp) + (n - x) * math.log(1 - pexp)) + 2 * (x * math.log(phat) + (n - x) * math.log(1 - phat))
    res["B2"] = {"book": VAR_BOOK, "sessions_tested": n, "exceptions_95": exc95, "rate_95": round(rate95, 4),
                 "exceptions_99": exc99, "rate_99": round(rate99, 4),
                 "kupiec_LR_95": round(lr(exc95, n, 0.05), 3) if lr(exc95, n, 0.05) is not None else None,
                 "kupiec_reject_at_5pct": (lr(exc95, n, 0.05) or 0) > 3.841,
                 "pass": 0.025 <= rate95 <= 0.08, "exception_days_95": [r for r in rows if r[4]]}

    # ---- B3 scoreboard recomputation
    rng = random.Random(SEED)
    closes = pd.DataFrame({s: pd.Series(dict(zip(v.dates, v.closes))) for s, v in
                           ((s, p.series(s)) for s in p.symbols())}).reindex(pd.Index(sessions))
    rets = closes.pct_change()
    mism, checked, labels = [], 0, {}
    stocks = [s for s in UNIVERSE_STOCKS if s in p.symbols()]
    for _ in range(200):
        s, d = rng.choice(stocks), rng.choice(oos)
        r = score(p, s, d)
        if r.status != OK:
            continue
        seg = rets.loc[:d].iloc[-r.history_n:][[s, "SPY"]]
        if seg.isna().any().any():
            continue
        checked += 1
        for k in (20, 60, 120):
            mine = getattr(r, f"ret_{k}_pp")
            ref = ((1 + seg[s].iloc[-k:]).prod() - 1) * 100
            if abs(mine - ref) > 1e-3:
                mism.append((s, d.isoformat(), f"ret_{k}", mine, ref))
            ex = getattr(r, f"excess_{k}_pp")
            refx = ref - ((1 + seg["SPY"].iloc[-k:]).prod() - 1) * 100
            if abs(ex - refx) > 1e-3:
                mism.append((s, d.isoformat(), f"excess_{k}", ex, refx))
        v = seg[s].iloc[-20:].std(ddof=1) * math.sqrt(252) * 100
        if abs(r.vol_20d_ann_pp - v) > 1e-3:
            mism.append((s, d.isoformat(), "vol20", r.vol_20d_ann_pp, v))
        labels[r.relative_strength] = labels.get(r.relative_strength, 0) + 1
        labels[r.extension] = labels.get(r.extension, 0) + 1
    res["B3"] = {"checked": checked, "mismatches": mism, "pass": not mism, "label_counts": labels}

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "phase6.json").write_text(json.dumps(res, indent=1, default=str))
    for k in ("B1", "B2", "B3"):
        v = {a: b for a, b in res[k].items() if a not in ("per_stock", "exception_days_95", "mismatches")}
        print(k, "PASS" if res[k]["pass"] else "FAIL", v)
    print("B1 per stock:", {k: (v["mse_two_factor"], v["mse_market_only"]) for k, v in res["B1"]["per_stock"].items()})
    print("B2 exception days (95):", res["B2"]["exception_days_95"][:12])
    print("B3 mismatches:", res["B3"]["mismatches"][:5])


if __name__ == "__main__":
    main()
