"""Daily brief (product #1, M4).

Deterministic: every number and every note is produced by code from the data layer. No LLM
is needed to produce a correct brief; an agent may restyle the wording, but there is nothing
for it to invent. Notes are descriptive statistics with their thresholds — never a call to
action (see compliance.py; every rendered brief is linted).

Structure:
  headline   flags for the session, or an explicit statement of what could not be judged
  book       portfolio weights, group exposure, portfolio beta (if holdings given)
  items      per watched name, in interest order: move vs implied, flags, events, notes,
             and why the name is shown
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
from .compliance import (
    DISCLAIMER, METHODOLOGY_NOTE, assert_clean, footer, operator_disclosure, provenance_of,
)
from .interest import Profile, ranked_watchlist
from .moves import ALERT, INSUFFICIENT_DATA, move_context
from .portfolio import book_context
from .relationships import (
    DECOUPLING, DIVERGENCE, HEALTHY, SHORT_HISTORY, ClusterMap, Thresholds, pair_health,
)

EXTRA_CLUSTERS = pathlib.Path(__file__).with_name("extra_clusters.yaml")

NOTABLE_Z = 1.0
LOW_FIT_R2 = 0.10
HEADLINE_EVENT_DAYS = 7
FOLLOW_THROUGH_SESSIONS = 2


def _follow_through(cal: EventCalendar, sym: str, ref_dates: Sequence[date]):
    """A covered report whose reaction session was 1..FOLLOW_THROUGH_SESSIONS sessions ago."""
    for k in range(1, FOLLOW_THROUGH_SESSIONS + 1):
        if len(ref_dates) < k + 2:
            break
        rx = cal.reaction_to(sym, ref_dates[-1 - k], ref_dates[-2 - k])
        if rx is not None and rx is not NOT_COVERED:
            return rx
    return None

def product_clusters() -> ClusterMap:
    with open(EXTRA_CLUSTERS) as f:
        extra = yaml.load(f, Loader=yaml.BaseLoader) or {}
    return ClusterMap.from_yaml(extra=extra)


def _pp(x: float | None, digits: int = 1) -> str:
    if x is None:
        return "n/a"
    if abs(x) < 0.5 * 10 ** -digits:      # never print "-0.0%"
        return f"{0:.{digits}f}%"
    return f"{x:+.{digits}f}%"


def _item(provider: PriceProvider, clusters: ClusterMap, cal: EventCalendar, wi, as_of: date,
          th: Thresholds, available: set[str], event_days: int, ref_dates: Sequence[date],
          flag_z: float = 2.5) -> dict:
    prev_session = ref_dates[-2] if len(ref_dates) >= 2 else None
    sym = wi.symbol
    mc = move_context(provider, sym, as_of, alert_z=flag_z)
    info = clusters.info(sym)
    candidates = [p for p in clusters.all_peers(sym) if p in available] if sym in available else []
    peers = []
    for p in candidates:
        h = pair_health(provider, sym, p, as_of, th)
        if h.status != INSUFFICIENT_DATA:
            peers.append(h)
    # Peer lists ("moves most with") and the peer-earnings line were REMOVED after failing
    # validation gates 3b and 3d (docs/claude-v0/VALIDATION_RESULTS.md). Peers are still
    # computed internally because decoupling/divergence flags (gate 3e passed) need them.
    flagged = [h for h in peers if h.status in (DECOUPLING, DIVERGENCE)]
    own_events = cal.upcoming([sym], as_of, event_days)

    g: list[str] = []
    quiet = False
    if mc.status == INSUFFICIENT_DATA:
        g.append(f"Not enough clean price history to measure {sym}'s move ({mc.reason}).")
    elif mc.status == ALERT:
        rx = cal.reaction_to(sym, as_of, prev_session)
        if rx is NOT_COVERED:
            g.append(f"{sym} moved {_pp(mc.move_pp)} vs {_pp(mc.implied_pp)} implied by {mc.benchmark} "
                     f"(z {mc.residual_z:+.1f}), beyond its own ±{mc.alert_z} threshold. The loaded "
                     f"earnings calendar does not cover this date, so an earnings cause is not ruled out.")
        elif rx is not None:
            g.append(f"{sym} moved {_pp(mc.move_pp)} vs {_pp(mc.implied_pp)} implied by {mc.benchmark} "
                     f"(z {mc.residual_z:+.1f}): earnings reaction session — it reported {rx.label()}.")
        elif (fx := _follow_through(cal, sym, ref_dates)) is not None:
            g.append(f"{sym} moved {_pp(mc.move_pp)} vs {_pp(mc.implied_pp)} implied by {mc.benchmark} "
                     f"(z {mc.residual_z:+.1f}), within {FOLLOW_THROUGH_SESSIONS} sessions of its "
                     f"report ({fx.label()}): earnings follow-through period.")
        else:
            g.append(f"{sym} moved {_pp(mc.move_pp)} vs {_pp(mc.implied_pp)} implied by {mc.benchmark} "
                     f"(z {mc.residual_z:+.1f}), beyond its own ±{mc.alert_z} threshold. No scheduled "
                     f"earnings for {sym} fall on this session in the loaded calendar.")
    elif abs(mc.residual_z) >= NOTABLE_Z:
        word = "outperformed" if mc.residual_pp > 0 else "underperformed"
        g.append(f"Moved {_pp(mc.move_pp)} vs {_pp(mc.implied_pp)} implied by {mc.benchmark}: "
                 f"{word} by {abs(mc.residual_pp):.1f}pp, within {sym}'s own stock-specific range "
                 f"(z {mc.residual_z:+.1f}; flag threshold ±{mc.alert_z}).")
    else:
        quiet = True
        g.append(f"In line with the market: moved {_pp(mc.move_pp)} vs {_pp(mc.implied_pp)} "
                 f"implied by {mc.benchmark}.")
    for h in flagged:
        if h.status == DIVERGENCE:
            g.append(f"Divergence: {h.direction} over {h.thresholds['divergence_days']} sessions "
                     f"({sym} {_pp(h.recent_return_a_pp)} vs {h.b} {_pp(h.recent_return_b_pp)}; "
                     f"residual z {h.residual_z:+.1f}, threshold ±{h.thresholds['divergence_z']}).")
        else:
            g.append(f"Decoupling: {sym}/{h.b} correlation {h.corr_short:.2f} over the last {h.n_short} "
                     f"sessions vs {h.corr_long:.2f} over {h.n_long} (threshold: drop of "
                     f"{h.thresholds['decouple_drop']} and z {h.thresholds['decouple_z']}).")
    for e in own_events:
        g.append(f"{sym} reports {e.label()}.")
    if mc.status != INSUFFICIENT_DATA and mc.fit_r2 is not None and mc.fit_r2 < LOW_FIT_R2:
        g.append(f"The {mc.benchmark} fit explains {mc.fit_r2:.0%} of {sym}'s daily variance over the "
                 f"baseline, so the implied move is a weak yardstick for this name.")
    short_pairs = [h for h in flagged if h.sample == SHORT_HISTORY]
    if mc.sample == SHORT_HISTORY:
        g.append(f"{sym}'s move baseline uses only {mc.baseline_n} sessions (short history): small sample.")
    for h in short_pairs:
        g.append(f"The {sym}/{h.b} flag is measured over a short history ({h.n_long} sessions): "
                 f"small sample.")
    if quiet and len(g) == 1:
        g.append("No flags for this name this session.")

    return {
        "symbol": sym,
        "why_shown": wi.why_shown,
        "score": wi.score,
        "held": wi.held,
        "cluster": info.primary,
        "move": mc.to_dict(),
        "flags": [h.to_dict() for h in flagged],
        "events": [e.to_dict() for e in own_events],
        "notes": g,
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
    items = [_item(provider, clusters, cal, wi, as_of, th, available, event_days, ref_dates, profile.flag_z)
             for wi in wl]

    headline = []
    for it in items:
        m = it["move"]
        if m["status"] == ALERT:
            g0 = it["notes"][0]
            kind = ("earnings reaction" if "earnings reaction" in g0
                    else "earnings follow-through" if "follow-through" in g0
                    else "abnormal move (earnings not checked)" if "not ruled out" in g0
                    else "abnormal move, no scheduled earnings")
            headline.append(f"{it['symbol']}: {kind} {_pp(m['move_pp'])} "
                            f"(implied {_pp(m['implied_pp'])}, z {m['residual_z']:+.1f}).")
        for f in it["flags"]:
            headline.append(f"{it['symbol']}/{f['b']}: {f['status'].lower()} — {f['reason']}.")
        for e in it["events"]:
            if (date.fromisoformat(e["date"]) - as_of).days <= HEADLINE_EVENT_DAYS:
                headline.append(f"{it['symbol']} reports earnings within {HEADLINE_EVENT_DAYS} days.")
    judged = [it for it in items if it["move"]["status"] != INSUFFICIENT_DATA]
    if not headline and not items:
        headline.append("Your watchlist is empty: add holdings, pins or tickers to the profile.")
    elif not headline and not judged:
        reason = items[0]["move"].get("reason", "") if items else ""
        headline.append(f"No names could be judged for {as_of.isoformat()}: {reason or 'no clean data'}.")
    elif not headline:
        skipped = len(items) - len(judged)
        headline.append("No flags across the watchlist this session: every measured move is within its "
                        "name's own range and no tracked pair changed state"
                        + (f" ({skipped} name(s) could not be judged)." if skipped else "."))

    book = book_context(provider, clusters, profile, as_of).to_dict() if profile.holdings else None
    ref = provider.series(DEFAULT_REFERENCE).upto(as_of)
    prov = provenance_of(provider, [w.symbol for w in wl] + [DEFAULT_REFERENCE], ref.last_date)
    disc = operator_disclosure()
    return {
        "product": "daily_brief",
        "as_of": as_of.isoformat(),
        "data_through": ref.last_date.isoformat() if ref.last_date else None,
        "calendar_fetched_on": cal.fetched_on.isoformat() if cal.fetched_on else None,
        "headline": headline,
        "book": book,
        "items": items,
        "record": list(record),
        "thresholds": asdict(th) | {"headline_event_days": HEADLINE_EVENT_DAYS,
                                    "low_fit_r2": LOW_FIT_R2, "flag_z": profile.flag_z},
        "disclaimer": DISCLAIMER,
        "methodology": METHODOLOGY_NOTE,
        "data_provenance": prov.to_dict(),
        "disclosure": disc.to_dict(),
        "sent_to_broker": False,
    }


def render_brief_md(b: dict) -> str:
    out = [f"# Daily brief — {b['as_of']}", "",
           f"Settled closes through {b['data_through']}."
           + (f" Earnings calendar as of {b['calendar_fetched_on']}." if b['calendar_fetched_on'] else ""),
           "", "## Flags this session", ""]
    out += [f"- {h}" for h in b["headline"]]
    bk = b.get("book")
    if bk and bk["positions"]:
        out += ["", "## Book statistics", ""]
        if bk["portfolio_beta"] is not None:
            out.append(f"Portfolio beta to {bk['positions'][0]['beta_index']} over the last "
                       f"{bk['positions'][0]['beta_window']} sessions: {bk['portfolio_beta']:.2f} "
                       f"(the book moved about {bk['portfolio_beta']:.1f}x the index per 1% index move "
                       f"in that window).")
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
        out.append("")
        out += [f"- {g}" for g in it["notes"]]
        out.append("")
        out.append(f"_Shown because: {it['why_shown']}._")
        out.append("")
    if b["record"]:
        out += ["## Research record", ""]
        for r in b["record"]:
            out.append(render_record_line(r))
        out.append("")
    from .compliance import Disclosure, Provenance
    prov = Provenance(tuple(b["data_provenance"]["sources"]), b["data_provenance"]["license"],
                      b["data_provenance"]["data_through"])
    disc = Disclosure(**b["disclosure"])
    out += ["---", ""] + footer(prov, disc, b["as_of"])
    text = "\n".join(out) + "\n"
    assert_clean(text, f"brief {b['as_of']}")
    return text


def render_record_line(r: dict) -> str:
    if r.get("status") != "LOADED":
        return f"- {r['ledger']}: {r['status'].replace('_', ' ').lower()}."
    if not r.get("n_resolved"):
        return f"- {r['ledger']}: 0 resolved, {r.get('n_pending', 0)} pending. No results yet."
    return (f"- {r['ledger']}: {r['n_resolved']} resolved, {r['n_pending']} pending. "
            f"Mean {_pp(r['mean_pp'], 2)}, median {_pp(r['median_pp'], 2)}, hit rate "
            f"{r['hit_rate']:.0%} (n={r['n_resolved']}). Not a validated edge.")
