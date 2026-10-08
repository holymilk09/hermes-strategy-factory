"""Weekly relationship map (product #3, M6).

The map for the watchlist plus what CHANGED since the previous map: betas that moved,
pairs that linked/unlinked or started diverging, clusters that tightened or loosened.
The change list is the product — last week's map is passed in, nothing is stored here.
"""
from __future__ import annotations

from datetime import date

from .data import PriceProvider
from .interest import Profile, ranked_watchlist
from .relationships import (
    INSUFFICIENT_DATA, ClusterMap, Thresholds, beta, cluster_cohesion, pair_health,
)
from .brief import DISCLAIMER, product_clusters

BETA_CHANGE = 0.30
COHESION_CHANGE = 0.10


def weekly_map(provider: PriceProvider, profile: Profile, as_of: date,
               previous: dict | None = None, clusters: ClusterMap | None = None,
               th: Thresholds = Thresholds()) -> dict:
    clusters = clusters or product_clusters()
    available = set(provider.symbols())
    syms = [w.symbol for w in ranked_watchlist(profile, as_of, clusters)]
    names, pairs, cl_names = {}, {}, set()
    for s in syms:
        info = clusters.info(s)
        if info.primary:
            cl_names.add(info.primary)
        bs = {}
        for ix in ("SPY", "QQQ"):
            for wnd in (60, 120):
                r = beta(provider, s, as_of, ix, wnd)
                bs[f"{ix}_{wnd}"] = None if r.beta is None else round(r.beta, 4)
        names[s] = {"cluster": info.primary, "betas": bs}
        for p in clusters.all_peers(s):
            if p in available and s in available:
                h = pair_health(provider, s, p, as_of, th)
                if h.status != INSUFFICIENT_DATA:
                    pairs[f"{s}/{p}"] = {"status": h.status, "corr_long": round(h.corr_long, 4),
                                         "corr_short": round(h.corr_short, 4), "n_long": h.n_long,
                                         "sample": h.sample}
    cohesion = {}
    for c in sorted(cl_names):
        co = cluster_cohesion(provider, clusters, c, as_of)
        cohesion[c] = {"status": co.status, "mean_pairwise_corr": co.mean_pairwise_corr,
                       "weak_members": list(co.weak_members), "unavailable": list(co.unavailable)}

    changes = []
    if previous:
        for s, cur in names.items():
            old = previous.get("names", {}).get(s)
            if not old:
                changes.append(f"{s} is new on the map.")
                continue
            a, b = old["betas"].get("QQQ_60"), cur["betas"].get("QQQ_60")
            if a is not None and b is not None and abs(b - a) >= BETA_CHANGE:
                changes.append(f"{s} beta to QQQ (60d) moved {a:.2f} -> {b:.2f}.")
        for k, cur in pairs.items():
            old = previous.get("pairs", {}).get(k)
            if old and old["status"] != cur["status"]:
                changes.append(f"{k}: {old['status'].lower()} -> {cur['status'].lower()} "
                               f"(corr {old['corr_long']:.2f} -> {cur['corr_long']:.2f}).")
        for c, cur in cohesion.items():
            old = previous.get("cohesion", {}).get(c)
            if (old and old.get("mean_pairwise_corr") is not None
                    and cur["mean_pairwise_corr"] is not None
                    and abs(cur["mean_pairwise_corr"] - old["mean_pairwise_corr"]) >= COHESION_CHANGE):
                word = "tightened" if cur["mean_pairwise_corr"] > old["mean_pairwise_corr"] else "loosened"
                changes.append(f"{c} {word}: mean corr {old['mean_pairwise_corr']:.2f} -> "
                               f"{cur['mean_pairwise_corr']:.2f}.")
        for s in previous.get("names", {}):
            if s not in names:
                changes.append(f"{s} dropped off the map (interest faded or position closed).")
    return {
        "product": "weekly_relationship_map",
        "as_of": as_of.isoformat(),
        "previous_as_of": previous.get("as_of") if previous else None,
        "names": names,
        "pairs": pairs,
        "cohesion": cohesion,
        "changes": changes if previous else None,
        "thresholds": {"beta_change": BETA_CHANGE, "cohesion_change": COHESION_CHANGE,
                       "link_floor": th.link_floor},
        "disclaimer": DISCLAIMER,
        "sent_to_broker": False,
    }


def render_weekly_md(m: dict) -> str:
    out = [f"# Weekly relationship map — {m['as_of']}", ""]
    out += ["## What changed", ""]
    if m["changes"] is None:
        out.append("First map — no previous week to compare against.")
    elif not m["changes"]:
        out.append(f"No material changes since {m['previous_as_of']}.")
    else:
        out += [f"- {c}" for c in m["changes"]]
    out += ["", "## Groups", ""]
    for c, co in m["cohesion"].items():
        if co["status"] != "OK":
            miss = ", ".join(co["unavailable"]) or "members"
            out.append(f"**{c}**: not enough clean history to measure (short or missing: {miss}).")
            out.append("")
            continue
        line = f"**{c}**: members co-move at mean corr {co['mean_pairwise_corr']:.2f}."
        if co["weak_members"]:
            line += f" Weak links: {', '.join(co['weak_members'])}."
        if co["unavailable"]:
            line += f" No data: {', '.join(co['unavailable'])}."
        out.append(line)
        out.append("")
    out += ["## Names", ""]
    for s, n in m["names"].items():
        b = n["betas"]
        bq = b.get("QQQ_60")
        out.append(f"**{s}** ({n['cluster'] or 'no group'}): beta to QQQ "
                   + ("n/a" if bq is None else f"{bq:.2f}") + " (60d).")
        ps = sorted(((k.split('/')[1], v) for k, v in m["pairs"].items() if k.startswith(s + "/")),
                    key=lambda kv: -kv[1]["corr_long"])
        linked = [f"{p} {v['corr_long']:.2f}" for p, v in ps if v["status"] != "NOT_LINKED"]
        if linked:
            out.append(f"Linked: {', '.join(linked[:4])}.")
        flagged = [f"{p} ({v['status'].lower()})" for p, v in ps if v["status"] in ("DECOUPLING", "DIVERGENCE")]
        if flagged:
            out.append(f"Flags: {', '.join(flagged)}.")
        out.append("")
    out += ["---", "", m["disclaimer"]]
    return "\n".join(out) + "\n"
