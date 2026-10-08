"""Adaptive daily brief (product #1, M4).

Deterministic: every number and every guidance line is produced by code from the
data layer. No LLM is needed to produce a correct brief; an agent may restyle the
wording, but there is nothing for it to invent. Guidance is research framing
("check", "expect", "no signal") — never buy/sell instructions.

Structure:
  headline   the few things that matter today, or an explicit "nothing unusual"
  book       portfolio weights, cluster exposure, portfolio beta (if holdings given)
  items      per watched name, in interest order: move vs implied, peers, events,
             guidance lines, and why the name is shown
  record     research-record summaries, if ledgers are supplied
"""
from __future__ import annotations

import pathlib
from dataclasses import asdict
from datetime import date
from typing import Sequence

import yaml

from .data import DEFAULT_REFERENCE, PriceProvider
from .events import NOT_COVERED, EventCalendar
from .interest import Profile, ranked_watchlist
from .moves import ALERT, INSUFFICIENT_DATA, move_context
from .portfolio import book_context
from .relationships import (
    DECOUPLING, DIVERGENCE, HEALTHY, SHORT_HISTORY, ClusterMap, Thresholds, pair_health,
)

EXTRA_CLUSTERS = pathlib.Path(__file__).with_name("extra_clusters.yaml")

NOTABLE_Z = 1.0

DISCLAIMER = ("Research only. Not investment advice, not a recommendation to buy or sell. "
              "No orders are placed by this system.")


def product_clusters() -> ClusterMap:
    with open(EXTRA_CLUSTERS) as f:
        extra = yaml.load(f, Loader=yaml.BaseLoader) or {}
    return ClusterMap.from_yaml(extra=extra)


def _pp(x: float | None, digits: int = 1) -> str:
    return "n/a" if x is None else f"{x:+.{digits}f}%"


def _item(provider: PriceProvider, clusters: ClusterMap, cal: EventCalendar, wi, as_of: date,
          th: Thresholds, available: set[str], event_days: int, prev_session: date | None) -> dict:
    sym = wi.symbol
    mc = move_context(provider, sym, as_of)
    info = clusters.info(sym)
    candidates = [p for p in clusters.all_peers(sym) if p in available] if sym in available else []
    peers = []
    for p in candidates:
        h = pair_health(provider, sym, p, as_of, th)
        if h.status != INSUFFICIENT_DATA:
            peers.append(h)
    linked = sorted([h for h in peers if h.status in (HEALTHY, DECOUPLING, DIVERGENCE)],
                    key=lambda h: (-(h.corr_long or 0.0), h.b))
    flagged = [h for h in peers if h.status in (DECOUPLING, DIVERGENCE)]
    own_events = cal.upcoming([sym], as_of, event_days)
    peer_events = [(e, next(h for h in linked if h.b == e.symbol))
                   for e in cal.upcoming([h.b for h in linked], as_of, event_days)]

    g: list[str] = []
    quiet = False
    if mc.status == INSUFFICIENT_DATA:
        g.append(f"Not enough clean price history to judge {sym}'s move ({mc.reason}).")
    elif mc.status == ALERT:
        rx = cal.reaction_to(sym, as_of, prev_session)
        if rx is NOT_COVERED:
            g.append(f"{sym} moved {_pp(mc.move_pp)} when its {mc.benchmark} beta implied "
                     f"{_pp(mc.implied_pp)} (z {mc.residual_z:+.1f}). That is unusual for its own "
                     f"history. The loaded earnings calendar doesn't cover this date, so an earnings "
                     f"cause can't be ruled out — check for one first.")
        elif rx is not None:
            g.append(f"{sym} moved {_pp(mc.move_pp)} vs {_pp(mc.implied_pp)} implied by {mc.benchmark} "
                     f"(z {mc.residual_z:+.1f}): an earnings reaction — it reported "
                     f"{rx.label()}. The report, not the market, explains most of this move.")
        else:
            g.append(f"{sym} moved {_pp(mc.move_pp)} when its {mc.benchmark} beta implied "
                     f"{_pp(mc.implied_pp)} (z {mc.residual_z:+.1f}). That is unusual for its own "
                     f"history and no scheduled earnings explain it — look for a stock-specific "
                     f"cause before reading it as a signal.")
    elif abs(mc.residual_z) >= NOTABLE_Z:
        word = "outperformed" if mc.residual_pp > 0 else "underperformed"
        g.append(f"Moved {_pp(mc.move_pp)} vs {_pp(mc.implied_pp)} implied by {mc.benchmark}: "
                 f"{word} by {abs(mc.residual_pp):.1f}pp, but that is within {sym}'s usual "
                 f"stock-specific swings (z {mc.residual_z:+.1f}, alert at ±{mc.alert_z}).")
    else:
        quiet = True
        g.append(f"In line with the market: moved {_pp(mc.move_pp)} vs {_pp(mc.implied_pp)} "
                 f"implied by {mc.benchmark}.")
    for h in flagged:
        if h.status == DIVERGENCE:
            g.append(f"{h.direction} over {h.thresholds['divergence_days']} sessions "
                     f"({sym} {_pp(h.recent_return_a_pp)} vs {h.b} {_pp(h.recent_return_b_pp)}, "
                     f"residual z {h.residual_z:+.1f}). Watch whether the gap closes or the link is breaking.")
        else:
            g.append(f"{sym}/{h.b} correlation dropped to {h.corr_short:.2f} over {h.n_short} sessions from "
                     f"{h.corr_long:.2f} over {h.n_long}. Treat {h.b} as a weaker guide to {sym} until it recovers.")
    for e in own_events:
        g.append(f"{sym} reports {e.label()}. Around the print, company news matters more than the beta.")
    for e, h in peer_events:
        g.append(f"Linked peer {e.symbol} reports {e.label()}; {sym} has tracked it at corr "
                 f"{h.corr_long:.2f} over {h.n_long} sessions, so its result may move {sym} too.")
    short_pairs = [h.b for h in linked if h.sample == SHORT_HISTORY]
    if mc.sample == SHORT_HISTORY:
        g.append(f"{sym}'s move baseline uses only {mc.baseline_n} sessions (short history): read loosely.")
    if short_pairs:
        g.append(f"The {sym}/{', '.join(short_pairs)} link is measured over a short history "
                 f"({min(h.n_long for h in linked if h.sample == SHORT_HISTORY)} sessions): small sample.")
    if quiet and len(g) == 1:
        g.append("No guidance today: nothing in the data stands out for this name.")
    if info.primary and not candidates:
        g.append(f"No price data cached for any of {sym}'s configured peers, so its group context "
                 f"is unchecked.")
    elif candidates and not linked:
        checked = ", ".join(h.b for h in peers) or "none with enough history"
        g.append(f"None of {sym}'s configured peers co-move with it above the {th.link_floor:.2f} "
                 f"link floor (checked: {checked}) — the group label isn't telling you much.")

    return {
        "symbol": sym,
        "why_shown": wi.why_shown,
        "score": wi.score,
        "held": wi.held,
        "cluster": info.primary,
        "move": mc.to_dict(),
        "linked_peers": [{"symbol": h.b, "corr_long": round(h.corr_long, 4), "n": h.n_long,
                          "status": h.status, "sample": h.sample} for h in linked[:5]],
        "flags": [h.to_dict() for h in flagged],
        "events": [e.to_dict() for e in own_events],
        "peer_events": [e.to_dict() for e, _ in peer_events],
        "guidance": g,
    }


def build_brief(provider: PriceProvider, profile: Profile, as_of: date,
                calendar: EventCalendar | None = None, clusters: ClusterMap | None = None,
                record: Sequence[dict] = (), limit: int = 10, event_days: int = 14,
                th: Thresholds = Thresholds()) -> dict:
    clusters = clusters or product_clusters()
    cal = calendar or EventCalendar.empty()
    available = set(provider.symbols())
    wl = ranked_watchlist(profile, as_of, clusters, limit)
    ref_dates = provider.series(DEFAULT_REFERENCE).upto(as_of).dates
    prev_session = ref_dates[-2] if len(ref_dates) >= 2 else None
    items = [_item(provider, clusters, cal, wi, as_of, th, available, event_days, prev_session)
             for wi in wl]

    headline = []
    for it in items:
        m = it["move"]
        if m["status"] == ALERT:
            g0 = it["guidance"][0]
            kind = ("earnings reaction" if "earnings reaction" in g0
                    else "unusual move (earnings not checked)" if "can't be ruled out" in g0
                    else "unexplained move")
            headline.append(f"{it['symbol']}: {kind} {_pp(m['move_pp'])} "
                            f"(implied {_pp(m['implied_pp'])}, z {m['residual_z']:+.1f}).")
        for f in it["flags"]:
            headline.append(f"{it['symbol']}/{f['b']}: {f['status'].lower()} — {f['reason']}.")
        for e in it["events"]:
            if (date.fromisoformat(e["date"]) - as_of).days <= 7:
                headline.append(f"{it['symbol']} reports earnings within 7 days.")
    if not headline:
        headline.append("Nothing unusual across your watchlist today: moves are explained by the market "
                        "and no tracked relationships broke.")

    book = book_context(provider, clusters, profile, as_of).to_dict() if profile.holdings else None
    ref = provider.series(DEFAULT_REFERENCE).upto(as_of)
    return {
        "product": "daily_brief",
        "as_of": as_of.isoformat(),
        "data_through": ref.last_date.isoformat() if ref.last_date else None,
        "calendar_fetched_on": cal.fetched_on.isoformat() if cal.fetched_on else None,
        "headline": headline,
        "book": book,
        "items": items,
        "record": list(record),
        "thresholds": asdict(th),
        "disclaimer": DISCLAIMER,
        "sent_to_broker": False,
    }


def render_brief_md(b: dict) -> str:
    out = [f"# Daily brief — {b['as_of']}", "",
           f"Settled closes through {b['data_through']}."
           + (f" Earnings calendar as of {b['calendar_fetched_on']}." if b['calendar_fetched_on'] else ""),
           "", "## What matters today", ""]
    out += [f"- {h}" for h in b["headline"]]
    bk = b.get("book")
    if bk and bk["positions"]:
        out += ["", "## Your book", ""]
        if bk["portfolio_beta"] is not None:
            out.append(f"Portfolio beta to {bk['positions'][0]['beta_index']} is about "
                       f"{bk['portfolio_beta']:.2f}: over the last 60 sessions the book has moved "
                       f"roughly {bk['portfolio_beta']:.1f}x the index. That describes the past, "
                       f"not a forecast.")
        exp = ", ".join(f"{k} {v:.0%}" for k, v in bk["cluster_weights"].items())
        out.append(f"Exposure by group: {exp}.")
        for c in bk["caveats"]:
            out.append(f"Note: {c}.")
    out += ["", "## Names", ""]
    for it in b["items"]:
        m = it["move"]
        tag = " (held)" if it["held"] else ""
        out.append(f"### {it['symbol']}{tag}")
        out.append("")
        if m["status"] != INSUFFICIENT_DATA:
            out.append(f"Last session {_pp(m['move_pp'])}, 5 sessions {_pp(m['move_5d_pp'])}. "
                       f"Beta {m['beta']:.2f} to {m['benchmark']} over {m['baseline_n']} sessions.")
        if it["linked_peers"]:
            ps = ", ".join(f"{p['symbol']} {p['corr_long']:.2f}" for p in it["linked_peers"][:3])
            out.append(f"Moves most with: {ps}.")
        out.append("")
        out += [f"- {g}" for g in it["guidance"]]
        out.append("")
        out.append(f"_Shown because: {it['why_shown']}._")
        out.append("")
    if b["record"]:
        out += ["## Research record", ""]
        for r in b["record"]:
            out.append(render_record_line(r))
        out.append("")
    out += ["---", "", b["disclaimer"],
            "Betas, correlations and alert thresholds are descriptive and point-in-time, not forecasts."]
    return "\n".join(out) + "\n"


def render_record_line(r: dict) -> str:
    if r.get("status") != "LOADED":
        return f"- {r['ledger']}: {r['status'].replace('_', ' ').lower()}."
    return (f"- {r['ledger']}: {r['n_resolved']} resolved, {r['n_pending']} pending. "
            f"Mean {_pp(r['mean_pp'], 2)}, median {_pp(r['median_pp'], 2)}, hit rate "
            f"{r['hit_rate']:.0%} (n={r['n_resolved']}). Not a validated edge.")
