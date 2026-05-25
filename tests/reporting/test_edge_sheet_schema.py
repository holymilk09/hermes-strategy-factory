from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDGE_DIR = ROOT / "reports" / "edge_sheet"


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_payload() -> dict:
    path = EDGE_DIR / f"{_today()}_edge_sheet.json"
    assert path.exists(), f"Missing edge sheet json: {path}"
    return json.loads(path.read_text())


def test_edge_sheet_json_schema_minimal_contract():
    payload = _load_payload()

    required_top = {
        "generated_at": str,
        "date": str,
        "active_lineage": str,
        "market_weather": str,
        "maturity_classification": str,
        "next_action": str,
        "grade": str,
        "ticker_cards": list,
        "reject_ledger": list,
        "counts": dict,
        "disclaimer": str,
        "scoreboard": dict,
        "sources": dict,
    }

    for k, t in required_top.items():
        assert k in payload, f"Missing key: {k}"
        assert isinstance(payload[k], t), f"Bad type for {k}: expected {t}, got {type(payload[k])}"

    assert payload["ticker_cards"], "ticker_cards cannot be empty"
    for card in payload["ticker_cards"]:
        for field in [
            "symbol",
            "main_view",
            "time_range",
            "score",
            "price_area_that_matters",
            "setup_breaks_below",
            "setup_breaks_above",
            "why_it_looks_strong_or_weak",
            "main_risk",
            "what_changed",
            "plain_english",
            "maturity_status",
        ]:
            assert field in card, f"Missing card field: {field}"
            assert str(card[field]).strip(), f"Empty card field: {field}"

    scoreboard = payload["scoreboard"]
    for field in ["generated_at", "date", "rows", "disclaimer"]:
        assert field in scoreboard, f"Missing scoreboard field: {field}"
    assert isinstance(scoreboard["rows"], list)

    for row in scoreboard["rows"]:
        for field in [
            "ticker",
            "signal_date",
            "observation_id",
            "initial_main_view",
            "initial_score",
            "initial_price",
            "price_area_that_matters",
            "setup_break_level",
            "current_price",
            "days_elapsed",
            "maturity_status",
            "result_summary",
            "plain_english_result",
        ]:
            assert field in row, f"Missing scoreboard row field: {field}"


def test_markdown_and_json_card_count_match():
    payload = _load_payload()
    md_path = EDGE_DIR / f"{_today()}_edge_sheet.md"
    md = md_path.read_text()

    md_card_count = sum(1 for line in md.splitlines() if line.startswith("### "))
    json_card_count = len(payload["ticker_cards"])
    assert md_card_count == json_card_count
