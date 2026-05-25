from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = [
    "Market Weather",
    "Top Bullish Swing Setups",
    "Waiting-for-Proof Setups",
    "No Edge / Weakening Names",
    "Hype Trap Radar",
    "Popular Ticker Pulse",
    "Price Areas That Matter",
    "Setup-Break Levels",
    "What Changed This Week",
    "Friday Scoreboard",
    "Reject Ledger",
]


def _h(v: Any) -> str:
    return html.escape(str(v))


def load_json(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def _style() -> str:
    return """
<style>
body{margin:0;padding:0;background:#f6f7fb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;color:#121826;}
.wrapper{max-width:720px;margin:0 auto;padding:16px;}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:14px;margin-bottom:12px;}
.badge{display:inline-block;padding:4px 8px;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:12px;font-weight:600;}
h1{font-size:24px;margin:0 0 8px 0;} h2{font-size:18px;margin:0 0 8px 0;} h3{font-size:16px;margin:0 0 8px 0;}
p,li{font-size:14px;line-height:1.45;} ul{padding-left:18px;margin:6px 0;}
.meta{color:#475467;font-size:13px;} .muted{color:#667085;} .grid{display:block;} .hero{background:#0f172a;color:#f8fafc;border:0;}
.footer{font-size:12px;color:#475467;}
@media (max-width:600px){.wrapper{padding:10px;} h1{font-size:21px;} h2{font-size:17px;} p,li{font-size:15px;}}
</style>
""".strip()


def _ticker_card_html(card: dict[str, Any]) -> str:
    return (
        "<div class='card'>"
        f"<h3>{_h(card['symbol'])} — {_h(card['main_view'])}</h3>"
        f"<p><strong>Time Range:</strong> {_h(card['time_range'])}</p>"
        f"<p><strong>Score:</strong> {_h(card['score'])}</p>"
        f"<p><strong>Price area that matters:</strong> {_h(card['price_area_that_matters'])}</p>"
        f"<p><strong>Setup breaks below:</strong> {_h(card['setup_breaks_below'])}</p>"
        f"<p><strong>Setup improves if:</strong> {_h(card['setup_breaks_above'])}</p>"
        f"<p><strong>Why it looks strong / weak:</strong> {_h(card['why_it_looks_strong_or_weak'])}</p>"
        f"<p><strong>Main risk:</strong> {_h(card['main_risk'])}</p>"
        f"<p><strong>What changed:</strong> {_h(card['what_changed'])}</p>"
        f"<p><strong>Plain-English explanation:</strong> {_h(card['plain_english'])}</p>"
        f"<p><strong>Maturity status:</strong> {_h(card['maturity_status'])}</p>"
        "</div>"
    )


def render_edge_sheet_html(edge_sheet: dict[str, Any]) -> str:
    cards = edge_sheet["ticker_cards"]
    bullish = [c for c in cards if c["main_view"] == "Bullish Swing Setup"]
    waiting = [c for c in cards if c["main_view"] in {"Waiting for Stronger Proof", "Waiting for Pullback", "Waiting for Breakout Confirmation"}]
    no_edge = [c for c in cards if c["main_view"] in {"No Edge", "Weakening", "No Reliable Rating Yet"}]
    hype = [c for c in cards if c["main_risk"] == "Too Stretched"]

    trend = edge_sheet.get("market_weather", "Not enough proof yet")
    volatility = "Not enough proof yet"
    breadth = "Not enough proof yet"
    market_explain = f"{trend}. Next action: {edge_sheet.get('next_action','CONTINUE_WAITING')}."

    parts = [
        "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
        _style(),
        "</head><body><div class='wrapper'>",
        "<div class='card'><span class='badge'>Research-only</span>",
        "<h1>Strategy Factory Edge Sheet</h1>",
        f"<p class='meta'>Date: {_h(edge_sheet['date'])}</p></div>",
        "<div class='card hero'><h2>The 60-second stock setup sheet</h2><p>See what’s strong, weak, and too risky before you chase it.</p></div>",
        "<div class='card'><h2>Market Weather</h2>",
        f"<p><strong>Trend:</strong> {_h(trend)}</p>",
        f"<p><strong>Volatility:</strong> {_h(volatility)}</p>",
        f"<p><strong>Breadth:</strong> {_h(breadth)}</p>",
        f"<p><strong>Plain-English explanation:</strong> {_h(market_explain)}</p></div>",
        "<div class='card'><h2>Top Bullish Swing Setups</h2></div>",
    ]

    parts.extend([_ticker_card_html(c) for c in bullish] or ["<div class='card'><p>No Reliable Rating Yet</p></div>"])
    parts.append("<div class='card'><h2>Waiting-for-Proof Setups</h2></div>")
    parts.extend([_ticker_card_html(c) for c in waiting] or ["<div class='card'><p>Not enough proof yet</p></div>"])

    parts.append("<div class='card'><h2>No Edge / Weakening Names</h2><ul>")
    if no_edge:
        parts.extend([f"<li>{_h(c['symbol'])}: {_h(c['main_view'])}</li>" for c in no_edge])
    else:
        parts.append("<li>None</li>")
    parts.append("</ul></div>")

    parts.append("<div class='card'><h2>Hype Trap Radar</h2><ul>")
    if hype:
        parts.extend([f"<li>{_h(c['symbol'])}: Too Stretched</li>" for c in hype])
    else:
        parts.append("<li>None</li>")
    parts.append("</ul></div>")

    parts.append("<div class='card'><h2>Popular Ticker Pulse</h2><ul>")
    for c in cards:
        parts.append(f"<li>{_h(c['symbol'])}: {_h(c['main_view'])}</li>")
    parts.append("</ul></div>")

    parts.append("<div class='card'><h2>Price Areas That Matter</h2><ul>")
    for c in cards:
        parts.append(f"<li>{_h(c['symbol'])}: {_h(c['price_area_that_matters'])}</li>")
    parts.append("</ul></div>")

    parts.append("<div class='card'><h2>Setup-Break Levels</h2><ul>")
    for c in cards:
        parts.append(f"<li>{_h(c['symbol'])}: Setup breaks below {_h(c['setup_breaks_below'])}; setup improves if {_h(c['setup_breaks_above'])}</li>")
    parts.append("</ul></div>")

    parts.append("<div class='card'><h2>What Changed This Week</h2><ul>")
    for c in cards:
        parts.append(f"<li>{_h(c['symbol'])}: {_h(c['what_changed'])}</li>")
    parts.append("</ul></div>")

    parts.append("<div class='card'><h2>Friday Scoreboard</h2><ul>")
    for row in edge_sheet["scoreboard"]["rows"]:
        r5 = row["result_5_day"] if row["result_5_day"] is not None else "Not enough proof yet"
        r10 = row["result_10_day"] if row["result_10_day"] is not None else "Not enough proof yet"
        r20 = row["result_20_day"] if row["result_20_day"] is not None else "Not enough proof yet"
        parts.append(f"<li>{_h(row['ticker'])}: {_h(row['maturity_status'])}; 5d={_h(r5)}; 10d={_h(r10)}; 20d={_h(r20)}</li>")
    parts.append("</ul></div>")

    parts.append("<div class='card'><h2>Reject Ledger</h2><ul>")
    for r in edge_sheet.get("reject_ledger", []):
        parts.append(f"<li>{_h(r['lineage'])}: {_h(r['summary'])}</li>")
    if not edge_sheet.get("reject_ledger"):
        parts.append("<li>None</li>")
    parts.append("</ul></div>")

    parts.extend([
        "<div class='card footer'><h2>Research-only Disclaimer</h2>",
        f"<p>{_h(edge_sheet['disclaimer'])}</p>",
        "<p>No trade recommendations. No personalized investment advice. No broker execution.</p>",
        "</div>",
        "</div></body></html>",
    ])
    return "".join(parts)


def render_scoreboard_html(scoreboard: dict[str, Any], disclaimer: str) -> str:
    parts = [
        "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
        _style(),
        "</head><body><div class='wrapper'>",
        "<div class='card'><span class='badge'>Research-only</span><h1>Friday Scoreboard</h1>",
        f"<p class='meta'>Date: {_h(scoreboard['date'])}</p></div>",
    ]

    for row in scoreboard["rows"]:
        r5 = row["result_5_day"] if row["result_5_day"] is not None else "Not enough proof yet"
        r10 = row["result_10_day"] if row["result_10_day"] is not None else "Not enough proof yet"
        r20 = row["result_20_day"] if row["result_20_day"] is not None else "Not enough proof yet"
        parts.append(
            "<div class='card'>"
            f"<h3>{_h(row['ticker'])}</h3>"
            f"<p><strong>Maturity status:</strong> {_h(row['maturity_status'])}</p>"
            f"<p><strong>5-day result:</strong> {_h(r5)}</p>"
            f"<p><strong>10-day result:</strong> {_h(r10)}</p>"
            f"<p><strong>20-day result:</strong> {_h(r20)}</p>"
            f"<p><strong>Plain-English result:</strong> {_h(row['plain_english_result'])}</p>"
            "</div>"
        )

    parts.append(f"<div class='card footer'><p>{_h(disclaimer)}</p></div>")
    parts.append("</div></body></html>")
    return "".join(parts)


def render_email_preview_html(edge_sheet: dict[str, Any], scoreboard: dict[str, Any]) -> str:
    return (
        "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        + _style()
        + "</head><body><div class='wrapper'>"
        + "<div class='card'><h1>Email Preview</h1><p class='meta'>Monday body + Friday scoreboard body</p></div>"
        + render_edge_sheet_html(edge_sheet).split("<body>", 1)[1].rsplit("</body>", 1)[0]
        + render_scoreboard_html(scoreboard, edge_sheet["disclaimer"]).split("<body>", 1)[1].rsplit("</body>", 1)[0]
        + "</div></body></html>"
    )


def render_from_paths(edge_json_path: Path, scoreboard_json_path: Path) -> dict[str, str]:
    edge = load_json(edge_json_path)
    score = load_json(scoreboard_json_path)
    return {
        "edge_html": render_edge_sheet_html(edge),
        "scoreboard_html": render_scoreboard_html(score, edge.get("disclaimer", "Research-only")),
        "email_preview_html": render_email_preview_html(edge, score),
    }
