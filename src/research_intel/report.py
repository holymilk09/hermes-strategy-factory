"""The full research report: brief + attribution + risk panel + scoreboard, one as-of.

One assembled dict, two renderers (markdown for agents/email text, HTML for direct delivery).
Both renderers are linted (compliance.assert_clean) before they return.
"""
from __future__ import annotations

import html
from datetime import date
from typing import Sequence

from .attribution import book_attribution
from .brief import _pp, build_brief, product_clusters, render_brief_md
from .compliance import Disclosure, Provenance, assert_clean, footer
from .data import OK, PriceProvider
from .events import EventCalendar
from .interest import Profile, ranked_watchlist
from .relationships import ClusterMap
from .risk import risk_panel
from .scoreboard import scoreboard


def build_report(provider: PriceProvider, profile: Profile, as_of: date,
                 calendar: EventCalendar | None = None, clusters: ClusterMap | None = None,
                 record: Sequence[dict] = (), limit: int = 10) -> dict:
    clusters = clusters or product_clusters()
    b = build_brief(provider, profile, as_of, calendar, clusters, record=record, limit=limit)
    syms = [w.symbol for w in ranked_watchlist(profile, as_of, clusters, limit)]
    return {
        "product": "research_report",
        "as_of": as_of.isoformat(),
        "brief": b,
        "attribution": book_attribution(provider, clusters, profile, as_of) if profile.holdings else None,
        "risk": risk_panel(provider, clusters, profile, as_of).to_dict() if profile.holdings else None,
        "scoreboard": scoreboard(provider, syms, as_of) if syms else None,
        "disclaimer": b["disclaimer"],
        "methodology": b["methodology"],
        "data_provenance": b["data_provenance"],
        "disclosure": b["disclosure"],
        "sent_to_broker": False,
    }


# --------------------------------------------------------------------------- markdown

def _fmt(x, d=2):
    return "n/a" if x is None else f"{x:.{d}f}"


def render_report_md(r: dict) -> str:
    b = r["brief"]
    out = [render_brief_md(b).split("\n---\n")[0].rstrip()]      # brief body without its footer
    a, k, s = r.get("attribution"), r.get("risk"), r.get("scoreboard")
    if a and a["positions"]:
        t = a["totals_pp"]
        out += ["", "## Book attribution (this session)", "",
                f"Book move {_pp(t['move_pp'])}: market {_pp(t['market_pp'])}, sector {_pp(t['sector_pp'])}, "
                f"stock-specific {_pp(t['idiosyncratic_pp'])} (weight covered {a['weight_covered']:.0%}; "
                f"{a['window']}-session baselines; same-day decomposition)."]
        for p in a["positions"]:
            sec = "" if p["sector_pp"] is None else f", sector {_pp(p['sector_pp'])}"
            out.append(f"- {p['symbol']} ({p['weight']:.0%}): {_pp(p['move_pp'])} = market {_pp(p['market_pp'])}"
                       f"{sec}, stock-specific {_pp(p['idiosyncratic_pp'])}"
                       + (f" [{p['sector_etf']}]" if p["sector_etf"] else " [market-only]"))
        for x in a["skipped"]:
            out.append(f"- {x['symbol']}: not attributed ({x['reason']}).")
    if k and k["status"] == OK:
        out += ["", f"## Book risk (pro forma, {k['window_n']} sessions)", "",
                f"Realised vol: {_fmt(k['vol_20d_ann_pp'],1)}% (20d), {_fmt(k['vol_60d_ann_pp'],1)}% (60d), annualised.",
                f"Beta (60d): {_fmt(k['beta_spy_60d'])} to SPY, {_fmt(k['beta_qqq_60d'])} to QQQ.",
                f"Concentration: HHI {_fmt(k['hhi'],3)}, effective names {_fmt(k['effective_n'],1)}; "
                f"average pairwise correlation {_fmt(k['avg_pairwise_corr_60d'])}; "
                f"diversification ratio {_fmt(k['diversification_ratio_60d'])}.",
                f"Max drawdown over the window {_fmt(k['max_drawdown_pp'],1)}%; worst day {_fmt(k['worst_day_pp'],1)}%.",
                f"1-day historical VaR: {_fmt(k['var_95_pp'])}% (95%), {_fmt(k['var_99_pp'])}% (99%); "
                f"ES 95% {_fmt(k['es_95_pp'])}%. Losses, as % of book value."]
        if k["risk_contribution"]:
            rc = ", ".join(f"{s} {v:.0%}" for s, v in sorted(k["risk_contribution"].items(), key=lambda kv: -kv[1]))
            out.append(f"Risk contribution (60d variance share): {rc}.")
        for sym, why in k["excluded"].items():
            out.append(f"Excluded from the pro forma: {sym} ({why}).")
        if k["sample"] != "FULL":
            out.append("Short history: the window is shorter than the 250-session target.")
    elif k:
        out += ["", "## Book risk", "", f"Not available: {k['reason']}."]
    if s:
        out += ["", "## Scoreboard (trailing, vs SPY)", ""]
        for row in s["rows"]:
            if row["status"] != OK:
                out.append(f"- {row['symbol']}: {row['reason']}")
                continue
            out.append(f"- {row['symbol']}: 20d {_pp(row['ret_20_pp'])} ({_pp(row['excess_20_pp'])} vs SPY), "
                       f"60d {_pp(row['ret_60_pp'])} ({_pp(row['excess_60_pp'])}), 120d {_pp(row['ret_120_pp'])} "
                       f"({_pp(row['excess_120_pp'])}); vol {_fmt(row['vol_20d_ann_pp'],0)}%"
                       + (f" (pct {row['vol_percentile']:.0f})" if row["vol_percentile"] is not None else "")
                       + f"; off 120-session high {_pp(row['off_high_120_pp'])}"
                       + (f"; extension z {row['ext_z']:+.1f}" if row["ext_z"] is not None else "")
                       + f". {row['relative_strength']} / {row['extension']} / vol {row['vol_regime']}.")
        out.append("")
        out.append("Rules: " + "; ".join(f"{k}: {v}" for k, v in s["rules"].items()) + ".")
    prov = Provenance(tuple(r["data_provenance"]["sources"]), r["data_provenance"]["license"],
                      r["data_provenance"]["data_through"])
    out += ["", "---", ""] + footer(prov, Disclosure(**r["disclosure"]), r["as_of"])
    text = "\n".join(out) + "\n"
    assert_clean(text, f"report {r['as_of']}")
    return text


# --------------------------------------------------------------------------- html

_CSS = """
:root{--fg:#1b1b1b;--muted:#5c5c5c;--bg:#fff;--line:#e3e3e3;--flag:#8a2f00}
@media (prefers-color-scheme:dark){:root{--fg:#ececec;--muted:#a8a8a8;--bg:#121212;--line:#2a2a2a;--flag:#ffb07a}}
body{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:720px;margin-inline:auto}
h1{font-size:1.35rem;margin:0 0 4px}h2{font-size:1.05rem;margin:22px 0 6px;border-bottom:1px solid var(--line);padding-bottom:4px}
h3{font-size:1rem;margin:14px 0 4px}p,li{margin:4px 0}ul{padding-left:18px}.muted{color:var(--muted);font-size:.9rem}
.flag{color:var(--flag);font-weight:600}.foot{margin-top:28px;border-top:1px solid var(--line);padding-top:10px;font-size:.82rem;color:var(--muted)}
code{font-size:.9em}
"""


def render_report_html(r: dict) -> str:
    """Self-contained, phone-width page built from the markdown renderer's lines."""
    md = render_report_md(r)
    body: list[str] = []
    in_list = False
    for line in md.splitlines():
        if line.startswith("- "):
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{_inline(line[2:])}</li>")
            continue
        if in_list:
            body.append("</ul>")
            in_list = False
        if line.startswith("# "):
            body.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith("### "):
            body.append(f"<h3>{_inline(line[4:])}</h3>")
        elif line.strip() == "---":
            body.append('<div class="foot">')
        elif line.strip():
            cls = ' class="muted"' if line.startswith("_") else ""
            body.append(f"<p{cls}>{_inline(line.strip('_'))}</p>")
    if in_list:
        body.append("</ul>")
    if '<div class="foot">' in body:
        body.append("</div>")
    title = f"Research report {r['as_of']}"
    page = (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(title)}</title><style>{_CSS}</style></head><body>"
            + "\n".join(body) + "</body></html>")
    assert_clean(page, f"report html {r['as_of']}")
    return page


def _inline(s: str) -> str:
    s = html.escape(s)
    for kind in ("abnormal move", "earnings reaction", "earnings follow-through", "Divergence:", "Decoupling:"):
        if kind in s:
            s = s.replace(kind, f'<span class="flag">{kind}</span>', 1)
    return s
