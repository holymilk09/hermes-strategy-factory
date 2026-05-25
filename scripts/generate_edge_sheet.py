#!/usr/bin/env python3
"""Phase output layer: Strategy Factory Edge Sheet generator.

Reads existing ledgers/results and writes retail-readable outputs:
- reports/edge_sheet/YYYY-MM-DD_edge_sheet.md
- reports/edge_sheet/YYYY-MM-DD_edge_sheet.json
- reports/edge_sheet/YYYY-MM-DD_scoreboard.md
- reports/edge_sheet/YYYY-MM-DD_scoreboard.json

Hard constraints:
- Read-only against strategy/selection logic and ledgers
- No order generation, broker execution, live hooks, or strategy mutation
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.paper.maturity_watchdog import find_symbol_ohlcv_path
from src.reporting.maturity_scoreboard import build_scoreboard_row, load_ohlcv_rows
from src.reporting.retail_wording import DISCLAIMER, build_retail_wording

ROOT = Path("/opt/data")
REPORT_DIR = ROOT / "reports" / "edge_sheet"

OBS_LEDGER = ROOT / "data" / "paper_observation" / "relative_strength_continuation_observation_ledger.csv"
OUTCOME_LEDGER = ROOT / "data" / "paper_observation" / "relative_strength_continuation_outcome_ledger.csv"
HYPOTHESIS_REGISTRY = ROOT / "reports" / "strategy_factory" / "hypothesis_registry.csv"
STATE_SNAPSHOT = ROOT / "reports" / "strategy_factory" / "feature_factory_state_snapshot.json"
MATURITY_JSON = ROOT / "reports" / "strategy_factory" / "relative_strength_maturity_watchdog.json"
SCOREBOARD_MD = ROOT / "reports" / "strategy_factory" / "research_scoreboard.md"


@dataclass
class TickerCard:
    symbol: str
    main_view: str
    time_range: str
    score: str
    price_area_that_matters: str
    setup_breaks_below: str
    setup_breaks_above: str
    why_it_looks_strong_or_weak: str
    main_risk: str
    what_changed: str
    plain_english: str
    maturity_status: str


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def grade_to_score(grade: str) -> str:
    mapping = {
        "A": "90",
        "B+": "84",
        "B": "80",
        "C+": "74",
        "C": "70",
        "D": "60",
        "F": "45",
    }
    return mapping.get(grade.strip().upper(), "No Reliable Rating Yet")


def build_cards(
    observations: list[dict[str, str]],
    maturity_rows: dict[str, dict[str, Any]],
    grade: str,
) -> list[TickerCard]:
    cards: list[TickerCard] = []
    score_value = grade_to_score(grade)

    for row in observations:
        symbol = row.get("symbol", "").strip().upper()
        signal_close = float(row.get("signal_close", "0") or 0)
        ret_5d = float(row.get("ret_5d", "0") or 0)
        ret_20d_rank = float(row.get("ret_20d_rank", "0") or 0)
        ret_60d_rank = float(row.get("ret_60d_rank", "0") or 0)
        outcome_status = (row.get("outcome_status", "") or "").upper().strip()

        maturity = maturity_rows.get(symbol, {})
        bars_remaining = maturity.get("bars_remaining")
        future_bars = maturity.get("future_bars")

        if bars_remaining is not None and future_bars is not None:
            progress = f"{future_bars}/10 bars recorded; {bars_remaining} bars remaining."
        else:
            progress = "Not enough proof yet; maturity progress unavailable."

        retail = build_retail_wording(
            outcome_status=outcome_status,
            signal_close=signal_close,
            ret_5d=ret_5d,
            ret_20d_rank=ret_20d_rank,
            ret_60d_rank=ret_60d_rank,
            progress_text=progress,
        )

        maturity_status = "still maturing" if outcome_status == "PENDING" else "matured"

        cards.append(
            TickerCard(
                symbol=symbol,
                main_view=retail.main_view,
                time_range=retail.time_range,
                score=str(score_value),
                price_area_that_matters=retail.price_area_that_matters,
                setup_breaks_below=retail.setup_breaks_below,
                setup_breaks_above=retail.setup_breaks_above,
                why_it_looks_strong_or_weak=retail.why_it_looks_strong_or_weak,
                main_risk=retail.main_risk,
                what_changed=retail.what_changed,
                plain_english=retail.plain_english,
                maturity_status=maturity_status,
            )
        )

    return cards


def markdown_card(card: TickerCard) -> str:
    return (
        f"### {card.symbol}\n"
        f"- Main View: {card.main_view}\n"
        f"- Time Range: {card.time_range}\n"
        f"- Score: {card.score}\n"
        f"- Price area that matters: {card.price_area_that_matters}\n"
        f"- Setup breaks below: {card.setup_breaks_below}\n"
        f"- Setup improves if: {card.setup_breaks_above}\n"
        f"- Why it looks strong / weak: {card.why_it_looks_strong_or_weak}\n"
        f"- Main risk: {card.main_risk}\n"
        f"- What changed: {card.what_changed}\n"
        f"- Plain-English explanation: {card.plain_english}\n"
        f"- Research-only disclaimer: {DISCLAIMER}\n"
    )


def make_reject_rows(hypothesis_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rejects: list[dict[str, str]] = []
    for row in hypothesis_rows:
        status = (row.get("status", "") or "").lower().strip()
        if status == "archived":
            rejects.append(
                {
                    "lineage": row.get("lineage", ""),
                    "phase": row.get("phase", ""),
                    "family": row.get("family", ""),
                    "grade": row.get("grade", ""),
                    "summary": "No Edge",
                }
            )
    return rejects


def render_scoreboard(scoreboard_rows: list[dict[str, Any]], as_of: str) -> str:
    lines = [
        "# Friday Scoreboard",
        "",
        f"As of: {as_of}",
        "",
        "Tracked observations only. No outcome is inferred or fabricated.",
        "",
    ]

    for row in scoreboard_rows:
        lines.extend(
            [
                f"- {row['ticker']}: {row['initial_main_view']}",
                f"  - Signal date: {row['signal_date']}",
                f"  - Observation ID: {row['observation_id']}",
                f"  - Initial score: {row['initial_score']}",
                f"  - Initial price: {row['initial_price']}",
                f"  - Current price: {row['current_price']}",
                f"  - Days elapsed: {row['days_elapsed']}",
                f"  - Maturity status: {row['maturity_status']}",
                f"  - 5-day result: {row['result_5_day'] if row['result_5_day'] is not None else 'Not enough proof yet'}",
                f"  - 10-day result: {row['result_10_day'] if row['result_10_day'] is not None else 'Not enough proof yet'}",
                f"  - 20-day result: {row['result_20_day'] if row['result_20_day'] is not None else 'Not enough proof yet'}",
                f"  - Result summary: {row['result_summary']}",
                f"  - Plain-English result: {row['plain_english_result']}",
                f"  - Price area that matters: {row['price_area_that_matters']}",
                f"  - Setup breaks below: {row['setup_break_level']}",
            ]
        )

    lines.extend(["", f"{DISCLAIMER}"])
    return "\n".join(lines) + "\n"


def render_edge_sheet(
    as_of: str,
    market_weather: str,
    cards: list[TickerCard],
    reject_rows: list[dict[str, str]],
    maturity_classification: str,
    next_action: str,
    scoreboard_rows: list[dict[str, Any]],
) -> str:
    bullish = [c for c in cards if c.main_view == "Bullish Swing Setup"]
    waiting = [c for c in cards if c.main_view in {"Waiting for Stronger Proof", "Waiting for Pullback", "Waiting for Breakout Confirmation"}]
    hype = [c for c in cards if c.main_risk == "Too Stretched"]

    lines = [
        f"# Strategy Factory Edge Sheet ({as_of})",
        "",
        "## Market Weather",
        f"- {market_weather}",
        f"- Maturity status: {maturity_classification}",
        f"- Next step: {next_action}",
        "",
        "## Top Bullish Swing Setups",
    ]

    if bullish:
        for c in bullish:
            lines.append(markdown_card(c))
    else:
        lines.append("- No Reliable Rating Yet. Current tracked setups are still in the proof window.")

    lines.extend(["", "## Waiting-for-Proof Setups", ""])
    if waiting:
        for c in waiting:
            lines.append(markdown_card(c))
    else:
        lines.append("- None")

    lines.extend(["", "## No Edge / Weakening Names", ""])
    if reject_rows:
        for r in reject_rows:
            lines.append(f"- {r['lineage']} (Phase {r['phase']}, {r['family']}, grade {r['grade']}): {r['summary']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Hype Trap Radar", ""])
    if hype:
        for c in hype:
            lines.append(f"- {c.symbol}: Too Stretched — sharp near-term move increased pullback risk.")
    else:
        lines.append("- No names currently flagged as Too Stretched.")

    lines.extend(["", "## Popular Ticker Pulse", ""])
    for c in cards:
        helper = "Market is helping this setup" if c.main_view != "No Edge" else "Market is not helping this setup"
        lines.append(f"- {c.symbol}: {c.main_view}; {helper}")

    lines.extend(["", "## Price Areas That Matter", ""])
    for c in cards:
        lines.append(f"- {c.symbol}: {c.price_area_that_matters}")

    lines.extend(["", "## Setup-Break Levels", ""])
    for c in cards:
        lines.append(f"- {c.symbol}: Setup breaks below {c.setup_breaks_below}; setup improves if {c.setup_breaks_above}")

    lines.extend(["", "## What Changed This Week", ""])
    for c in cards:
        lines.append(f"- {c.symbol}: {c.what_changed}")

    lines.extend(["", "## Friday Scoreboard", ""])
    for row in scoreboard_rows:
        lines.append(
            f"- {row['ticker']}: {row['maturity_status']}; "
            f"5d={row['result_5_day'] if row['result_5_day'] else 'Not enough proof yet'}; "
            f"10d={row['result_10_day'] if row['result_10_day'] else 'Not enough proof yet'}; "
            f"20d={row['result_20_day'] if row['result_20_day'] else 'Not enough proof yet'}"
        )

    lines.extend(["", "## Reject Ledger", ""])
    if reject_rows:
        for r in reject_rows:
            lines.append(f"- {r['lineage']} ({r['family']}): {r['summary']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Research-only Disclaimer", "", DISCLAIMER, ""])
    return "\n".join(lines)


def write_outputs(
    payload: dict[str, Any],
    markdown: str,
    scoreboard_markdown: str,
    scoreboard_json: dict[str, Any],
    as_of: str,
) -> dict[str, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    md_path = REPORT_DIR / f"{as_of}_edge_sheet.md"
    json_path = REPORT_DIR / f"{as_of}_edge_sheet.json"
    score_path = REPORT_DIR / f"{as_of}_scoreboard.md"
    score_json_path = REPORT_DIR / f"{as_of}_scoreboard.json"

    md_path.write_text(markdown)
    json_path.write_text(json.dumps(payload, indent=2))
    score_path.write_text(scoreboard_markdown)
    score_json_path.write_text(json.dumps(scoreboard_json, indent=2))

    return {
        "markdown": md_path,
        "json": json_path,
        "scoreboard": score_path,
        "scoreboard_json": score_json_path,
    }


def main() -> None:
    now = datetime.now(timezone.utc)
    as_of = now.strftime("%Y-%m-%d")

    observations = load_csv(OBS_LEDGER)
    outcomes = load_csv(OUTCOME_LEDGER)
    hypothesis = load_csv(HYPOTHESIS_REGISTRY)
    snapshot = load_json(STATE_SNAPSHOT)
    maturity = load_json(MATURITY_JSON)

    active_lineage = snapshot.get("active_lineage", "relative_strength_continuation")
    maturity_classification = snapshot.get("maturity_classification", "PENDING_MATURITY")
    next_action = snapshot.get("next_allowed_action", "CONTINUE_WAITING")

    grade = "No Reliable Rating Yet"
    for row in hypothesis:
        if row.get("lineage") == active_lineage:
            grade = row.get("grade", "No Reliable Rating Yet")
            break

    maturity_rows = {str(r.get("symbol", "")).upper(): r for r in maturity.get("rows", [])}

    cards = build_cards(observations, maturity_rows, grade)
    reject_rows = make_reject_rows(hypothesis)

    card_by_symbol = {c.symbol: c for c in cards}
    scoreboard_rows: list[dict[str, Any]] = []
    for obs in observations:
        symbol = (obs.get("symbol") or "").upper()
        card = card_by_symbol.get(symbol)
        if card is None:
            continue
        ohlcv_path = find_symbol_ohlcv_path(ROOT, symbol)
        ohlcv_rows = load_ohlcv_rows(ohlcv_path) if ohlcv_path else []
        row = build_scoreboard_row(observation=obs, card=card, ohlcv_rows=ohlcv_rows)
        scoreboard_rows.append(row.__dict__)

    market_weather = "Market is helping this setup" if grade in {"A", "B", "B+", "C+"} else "Market is not helping this setup"

    markdown = render_edge_sheet(
        as_of=as_of,
        market_weather=market_weather,
        cards=cards,
        reject_rows=reject_rows,
        maturity_classification=maturity_classification,
        next_action=next_action,
        scoreboard_rows=scoreboard_rows,
    )
    scoreboard = render_scoreboard(scoreboard_rows, as_of)

    scoreboard_payload = {
        "generated_at": now.isoformat(),
        "date": as_of,
        "rows": scoreboard_rows,
        "disclaimer": DISCLAIMER,
    }

    payload = {
        "generated_at": now.isoformat(),
        "date": as_of,
        "active_lineage": active_lineage,
        "market_weather": market_weather,
        "maturity_classification": maturity_classification,
        "next_action": next_action,
        "grade": grade,
        "ticker_cards": [c.__dict__ for c in cards],
        "reject_ledger": reject_rows,
        "counts": {
            "observations": len(observations),
            "outcomes": len(outcomes),
            "pending_cards": sum(1 for c in cards if c.maturity_status == "still maturing"),
        },
        "disclaimer": DISCLAIMER,
        "scoreboard": scoreboard_payload,
        "sources": {
            "observation_ledger": str(OBS_LEDGER),
            "outcome_ledger": str(OUTCOME_LEDGER),
            "hypothesis_registry": str(HYPOTHESIS_REGISTRY),
            "state_snapshot": str(STATE_SNAPSHOT),
            "maturity_report": str(MATURITY_JSON),
            "scoreboard_reference": str(SCOREBOARD_MD),
        },
    }

    paths = write_outputs(payload, markdown, scoreboard, scoreboard_payload, as_of)

    print("=== EDGE SHEET GENERATED ===")
    print(f"markdown={paths['markdown']}")
    print(f"json={paths['json']}")
    print(f"scoreboard={paths['scoreboard']}")
    print(f"scoreboard_json={paths['scoreboard_json']}")
    print("No strategy behavior changed.")


if __name__ == "__main__":
    main()
