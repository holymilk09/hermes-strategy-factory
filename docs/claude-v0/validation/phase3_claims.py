#!/usr/bin/env python3
"""Phase 3 — out-of-sample validation of product claims (VALIDATION_PLAN.md §5).

Gates are evaluated on OOS (2025-07-01..2026-10-07) exactly as registered. The same
metrics on IS are reported for stability only. Thresholds are the product defaults.
"""
from __future__ import annotations

import itertools
import json
import math
import random
import statistics
import sys
from datetime import date

from common import OOS_START, OUT, UNIVERSE_STOCKS, calendar, store
from src.research_intel.brief import product_clusters
from src.research_intel.data import OK, MemoryProvider, aligned_returns
from src.research_intel.events import NOT_COVERED
from src.research_intel.moves import ALERT, move_context
from src.research_intel.relationships import (
    DECOUPLING, DIVERGENCE, HEALTHY, INSUFFICIENT_DATA, NOT_LINKED, _corr, pair_health,
)

SEED = 20261008
B = 2000
LINKED = (HEALTHY, DECOUPLING, DIVERGENCE)


def boot_ratio(a, b, rng, reps=B):
    """Bootstrap CI of mean(a)/mean(b), resampling each group independently."""
    est = statistics.fmean(a) / statistics.fmean(b)
    rs = []
    for _ in range(reps):
        ma = statistics.fmean(rng.choices(a, k=len(a)))
        mb = statistics.fmean(rng.choices(b, k=len(b)))
        rs.append(ma / mb)
    rs.sort()
    return est, rs[int(0.025 * reps)], rs[int(0.975 * reps)]


def fwd_corr(p, a, b, t_idx, sessions, n=60):
    """corr of daily returns over sessions t+1..t+n (window ends at t+n)."""
    if t_idx + n >= len(sessions):
        return None
    w = aligned_returns(p, [a, b], sessions[t_idx + n], n)
    if w.status != OK:
        return None
    return _corr(w.returns[a], w.returns[b])


def run(period, p, cal, cm, sessions_all, lo, hi, rng):
    sess = [d for d in sessions_all if lo <= d <= hi]
    idx = {d: i for i, d in enumerate(sessions_all)}
    stocks = [s for s in UNIVERSE_STOCKS if s in p.symbols()]
    out = {"period": period, "sessions": len(sess), "first": sess[0].isoformat(), "last": sess[-1].isoformat()}

    # ---- move contexts for every stock-day (3a, 3c, 3d, 3g)
    mc = {}
    for s in stocks:
        for d in sess:
            m = move_context(p, s, d)
            if m.status != INSUFFICIENT_DATA:
                mc[(s, d)] = m

    # 3a beta-implied vs zero forecast
    per, xs, ys = {}, [], []
    for s in stocks:
        rows = [mc[(s, d)] for d in sess if (s, d) in mc]
        if len(rows) < 30:
            continue
        mse_i = statistics.fmean((r.move_pp - r.implied_pp) ** 2 for r in rows)
        mse_0 = statistics.fmean(r.move_pp ** 2 for r in rows)
        per[s] = {"n": len(rows), "mse_implied": round(mse_i, 4), "mse_zero": round(mse_0, 4),
                  "skill": round(1 - mse_i / mse_0, 4)}
        xs += [r.implied_pp for r in rows]
        ys += [r.move_pp for r in rows]
    wins = sum(1 for v in per.values() if v["mse_implied"] < v["mse_zero"])
    pooled = _corr(xs, ys)
    out["3a"] = {"stocks": len(per), "implied_beats_zero": wins, "share": round(wins / len(per), 4),
                 "pooled_corr": round(pooled, 4), "n_obs": len(xs),
                 "pass": wins / len(per) >= 0.80 and pooled >= 0.30,
                 "worst": sorted(per.items(), key=lambda kv: kv[1]["skill"])[:4]}

    # pairs (unordered within any shared cluster)
    pairs = sorted({tuple(sorted((a, b))) for a in stocks for b in cm.all_peers(a) if b in stocks})
    sample_t = [d for d in sess[::5] if idx[d] + 60 < len(sessions_all)]

    # 3b linked-peer stability; 3e decoupling vs healthy (same sampling)
    stab, dec_fwd, hea_fwd = [], [], []
    for d in sample_t:
        for a, b in pairs:
            h = pair_health(p, a, b, d)
            if h.status not in LINKED:
                continue
            fc = fwd_corr(p, a, b, idx[d], sessions_all)
            if fc is None:
                continue
            stab.append(fc >= 0.40)
            if h.status == DECOUPLING:
                dec_fwd.append(fc)
            elif h.status == HEALTHY:
                hea_fwd.append(fc)
    out["3b"] = {"linked_pair_dates": len(stab), "share_still_ge_0.40": round(sum(stab) / len(stab), 4),
                 "pass": sum(stab) / len(stab) >= 0.70, "sampled_every": "5 sessions"}
    diff = (statistics.fmean(dec_fwd) - statistics.fmean(hea_fwd)) if dec_fwd and hea_fwd else None
    out["3e"] = {"n_decoupling": len(dec_fwd), "n_healthy": len(hea_fwd),
                 "fwd_corr_decoupling": round(statistics.fmean(dec_fwd), 4) if dec_fwd else None,
                 "fwd_corr_healthy": round(statistics.fmean(hea_fwd), 4) if hea_fwd else None,
                 "difference": round(diff, 4) if diff is not None else None,
                 "pass": diff is not None and diff <= -0.10}

    # 3c alerts: rate + next-day abnormality
    alerts = [(s, d) for (s, d), m in mc.items() if m.status == ALERT]
    rate = len(alerts) / len(mc)
    nxt_alert, nxt_other = [], []
    for (s, d), m in mc.items():
        i = idx[d] + 1
        if i >= len(sessions_all) or sessions_all[i] > hi:
            continue
        n = mc.get((s, sessions_all[i]))
        if n is None:
            continue
        (nxt_alert if m.status == ALERT else nxt_other).append(abs(n.residual_pp))
    est, lo_ci, hi_ci = boot_ratio(nxt_alert, nxt_other, rng)
    out["3c"] = {"stock_days": len(mc), "alerts": len(alerts), "rate": round(rate, 4),
                 "rate_in_band": 0.005 <= rate <= 0.03,
                 "next_day_abs_resid_ratio": round(est, 4), "ci95": [round(lo_ci, 4), round(hi_ci, 4)],
                 "n_alert_next": len(nxt_alert), "n_other_next": len(nxt_other),
                 "pass_rate": 0.005 <= rate <= 0.03, "pass_meaningful": est >= 1.20 and lo_ci > 1.0}

    # 3d peer earnings read-through
    peer_days, other = [], []
    detail = []
    for f in stocks:
        own = {d for d in sess if cal.reaction_to(f, d, sessions_all[idx[d] - 1]) not in (None, NOT_COVERED)}
        pd_set = set()
        for d in sess:
            prev = sessions_all[idx[d] - 1]
            if d in own:
                continue
            for q in cm.all_peers(f):
                if q not in stocks:
                    continue
                if cal.reaction_to(q, d, prev) in (None, NOT_COVERED):
                    continue
                if pair_health(p, f, q, prev).status in LINKED:   # linked as of the prior session
                    pd_set.add(d)
                    detail.append((f, q, d.isoformat()))
                    break
        for d in sess:
            m = mc.get((f, d))
            if m is None:
                continue
            (peer_days if d in pd_set else other).append(abs(m.residual_pp))
    est, lo_ci, hi_ci = boot_ratio(peer_days, other, rng)
    out["3d"] = {"peer_reaction_follower_days": len(peer_days), "other_days": len(other),
                 "ratio": round(est, 4), "ci95": [round(lo_ci, 4), round(hi_ci, 4)],
                 "pass": est >= 1.20 and lo_ci > 1.0, "examples": detail[:8]}

    # 3f divergence descriptive
    fwd5, fwd10, signs = [], [], []
    for d in sample_t:
        for a, b in itertools.permutations(stocks, 2):
            if b not in cm.all_peers(a):
                continue
            h = pair_health(p, a, b, d)
            if h.status != DIVERGENCE:
                continue
            for k, acc in ((5, fwd5), (10, fwd10)):
                j = idx[d] + k
                if j >= len(sessions_all):
                    continue
                w = aligned_returns(p, [a, b], sessions_all[j], k)
                if w.status != OK:
                    continue
                res = sum(x - h.beta_a_on_b * y for x, y in zip(w.returns[a], w.returns[b])) * 100
                acc.append(res)
                if k == 5:
                    signs.append(math.copysign(1, res) == -math.copysign(1, h.residual_z))
    out["3f"] = {"n": len(fwd5),
                 "mean_next5_resid_pp": round(statistics.fmean(fwd5), 4) if fwd5 else None,
                 "mean_next10_resid_pp": round(statistics.fmean(fwd10), 4) if fwd10 else None,
                 "share_gap_narrowed_5d": round(sum(signs) / len(signs), 4) if signs else None,
                 "note": "descriptive only; no directional guidance is added"}

    # 3g earnings labelling of alerts inside coverage
    lab, unl = 0, []
    for s, d in alerts:
        prev = sessions_all[idx[d] - 1]
        rx = cal.reaction_to(s, d, prev)
        if rx is NOT_COVERED:
            continue
        if rx is not None:
            lab += 1
        else:
            unl.append((s, d))
    near = []
    for s, d in unl:
        i = idx[d]
        around = [sessions_all[j] for j in (i - 2, i - 1, i + 1) if 0 < j < len(sessions_all)]
        hit = [e for e in cal.events if e.symbol == s and e.date in around]
        if hit:
            near.append((s, d.isoformat(), [(e.date.isoformat(), e.timing) for e in hit]))
    rng.shuffle(unl)
    out["3g"] = {"alerts_in_coverage": lab + len(unl), "labelled_earnings": lab,
                 "share": round(lab / (lab + len(unl)), 4) if (lab + len(unl)) else None,
                 "unlabelled_with_report_within_2_sessions": near,
                 "spot_check_10": [(s, d.isoformat()) for s, d in unl[:10]]}
    return out


def main():
    st = store()
    p = MemoryProvider([st.series(s) for s in st.symbols()])    # quarantine applied
    cal, cm = calendar(), product_clusters()
    sessions_all = list(st.series("SPY").dates)
    rng = random.Random(SEED)
    oos = run("OOS", p, cal, cm, sessions_all, OOS_START, date(2026, 10, 7), rng)
    is_ = run("IS", p, cal, cm, sessions_all, date(2024, 10, 1), date(2025, 6, 30), rng)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "phase3.json").write_text(json.dumps({"OOS": oos, "IS": is_}, indent=1, default=str))
    for r in (oos, is_):
        print(f"== {r['period']} {r['first']}..{r['last']} ({r['sessions']} sessions)")
        for k in ("3a", "3b", "3c", "3d", "3e", "3f", "3g"):
            v = {x: y for x, y in r[k].items() if x not in ("worst", "examples", "spot_check_10",
                                                             "unlabelled_with_report_within_2_sessions")}
            print(" ", k, v)
    print("OOS worst 3a:", oos["3a"]["worst"])
    print("OOS 3d examples:", oos["3d"]["examples"])
    print("OOS 3g near-miss:", oos["3g"]["unlabelled_with_report_within_2_sessions"][:6])
    print("OOS 3g spot:", oos["3g"]["spot_check_10"])


if __name__ == "__main__":
    sys.exit(main())
