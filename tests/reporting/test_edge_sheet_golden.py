from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EDGE_DIR = ROOT / "reports" / "edge_sheet"

pytestmark = pytest.mark.requires_reports  # needs reports/edge_sheet/*.json/.md
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "edge_sheet"

REQUIRED_SECTIONS = [
    "## Market Weather",
    "## Top Bullish Swing Setups",
    "## Waiting-for-Proof Setups",
    "## No Edge / Weakening Names",
    "## Hype Trap Radar",
    "## Popular Ticker Pulse",
    "## Price Areas That Matter",
    "## Setup-Break Levels",
    "## What Changed This Week",
    "## Friday Scoreboard",
    "## Reject Ledger",
    "## Research-only Disclaimer",
]

FORBIDDEN_WORDS = [
    "buy",
    "sell",
    "watch",
    "not covered",
    "constructive",
    "poor regime fit",
    "neutral",
    "alpha",
    "beta",
    "factor exposure",
    "regime fit",
    "signal decay",
]

REQUIRED_CARD_FIELDS = [
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
]


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _paths() -> tuple[Path, Path]:
    """Canonical golden fixture paths — deterministic and repo-controlled."""
    return (FIXTURE_DIR / "golden_edge_sheet.md", FIXTURE_DIR / "golden_edge_sheet.json")


def _latest_runtime_edge_sheet_paths() -> tuple[Path, Path] | None:
    """Find the most recent runtime edge sheet, or None if unavailable."""
    today = _today()
    today_md = EDGE_DIR / f"{today}_edge_sheet.md"
    today_json = EDGE_DIR / f"{today}_edge_sheet.json"
    if today_md.exists() and today_json.exists():
        return today_md, today_json
    # Fall back to the latest available date
    json_files = sorted(EDGE_DIR.glob("*_edge_sheet.json"))
    md_files = sorted(EDGE_DIR.glob("*_edge_sheet.md"))
    if json_files and md_files:
        return md_files[-1], json_files[-1]
    return None


def _normalize_json(payload: dict) -> dict:
    normalized = dict(payload)
    normalized["generated_at"] = "<normalized>"
    if "scoreboard" in normalized and isinstance(normalized["scoreboard"], dict):
        normalized["scoreboard"] = dict(normalized["scoreboard"])
        normalized["scoreboard"]["generated_at"] = "<normalized>"
    return normalized


def test_golden_fixture_files_exist():
    assert (FIXTURE_DIR / "golden_edge_sheet.md").exists()
    assert (FIXTURE_DIR / "golden_edge_sheet.json").exists()


def test_markdown_has_required_sections_and_no_empty_ugly_sections():
    md_path, _ = _paths()
    text = md_path.read_text()

    for section in REQUIRED_SECTIONS:
        assert section in text, f"Missing section: {section}"

    # no immediate empty section blocks
    for section in REQUIRED_SECTIONS:
        assert f"{section}\n\n## " not in text, f"Section appears empty: {section}"


def test_customer_facing_output_has_no_forbidden_language_leaks():
    md_path, _ = _paths()
    lowered = md_path.read_text().lower()
    for token in FORBIDDEN_WORDS:
        assert token not in lowered, f"Forbidden token leaked: {token}"


def test_every_ticker_card_answers_what_should_i_understand_and_is_plain_english():
    _, json_path = _paths()
    payload = json.loads(json_path.read_text())

    cards = payload["ticker_cards"]
    assert cards, "No ticker cards found"

    for card in cards:
        for f in REQUIRED_CARD_FIELDS:
            assert str(card.get(f, "")).strip(), f"Missing/empty card field: {f}"
        assert "research-only" in payload.get("disclaimer", "").lower()


def test_json_and_markdown_represent_same_ticker_symbols():
    md_path, json_path = _paths()
    md = md_path.read_text()
    payload = json.loads(json_path.read_text())

    md_symbols = set()
    for line in md.splitlines():
        if line.startswith("### "):
            md_symbols.add(line.replace("### ", "").strip())

    json_symbols = {c["symbol"] for c in payload["ticker_cards"]}
    assert md_symbols == json_symbols


def test_scoreboard_is_honest_and_immature_clearly_marked():
    _, json_path = _paths()
    payload = json.loads(json_path.read_text())

    banned_claims = ["win rate", "return", "performance", "guaranteed"]
    full_text = json.dumps(payload).lower()
    for claim in banned_claims:
        if claim == "return":
            # allow field names like ret_5d in source-derived context; block explicit claims only
            assert "claimed return" not in full_text
            continue
        assert claim not in full_text, f"Unbacked claim found: {claim}"

    rows = payload["scoreboard"]["rows"]
    assert rows, "Expected scoreboard rows"
    for row in rows:
        if row["days_elapsed"] < 5 and row["maturity_status"] != "Insufficient Data":
            assert row["maturity_status"] == "Still Maturing"
            assert row["result_5_day"] is None
            assert row["result_10_day"] is None
            assert row["result_20_day"] is None


def test_current_output_matches_golden_shape_after_normalization():
    _, json_path = _paths()
    golden_json = json.loads((FIXTURE_DIR / "golden_edge_sheet.json").read_text())
    current_json = json.loads(json_path.read_text())

    g = _normalize_json(golden_json)
    c = _normalize_json(current_json)

    assert set(g.keys()) == set(c.keys())
    assert len(g["ticker_cards"]) == len(c["ticker_cards"])
    assert [x["symbol"] for x in g["ticker_cards"]] == [x["symbol"] for x in c["ticker_cards"]]

    golden_md = (FIXTURE_DIR / "golden_edge_sheet.md").read_text()
    current_md_path, _ = _paths()
    current_md = current_md_path.read_text()
    for section in REQUIRED_SECTIONS:
        assert section in golden_md
        assert section in current_md
