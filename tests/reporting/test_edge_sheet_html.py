from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EDGE_DIR = ROOT / "reports" / "edge_sheet"

# All HTML tests read today's reports/edge_sheet/*.json and call .venv/bin/python
pytestmark = [pytest.mark.requires_reports, pytest.mark.requires_venv]
GEN = ROOT / "scripts" / "generate_edge_sheet.py"
RENDER = ROOT / "scripts" / "render_edge_sheet_html.py"

REQUIRED_SECTIONS = [
    "Strategy Factory Edge Sheet",
    "The 60-second stock setup sheet",
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
    "Research-only Disclaimer",
]

FORBIDDEN = [
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


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(ROOT)},
    )


def _paths() -> tuple[Path, Path, Path, Path, Path]:
    d = _today()
    return (
        EDGE_DIR / f"{d}_edge_sheet.json",
        EDGE_DIR / f"{d}_scoreboard.json",
        EDGE_DIR / f"{d}_edge_sheet.html",
        EDGE_DIR / f"{d}_scoreboard.html",
        EDGE_DIR / f"{d}_email_preview.html",
    )


def _norm_hash_json(path: Path) -> str:
    obj = json.loads(path.read_text())
    obj["generated_at"] = "<normalized>"
    if isinstance(obj.get("scoreboard"), dict):
        obj["scoreboard"]["generated_at"] = "<normalized>"
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def test_html_renderer_creates_files():
    assert _run(GEN).returncode == 0
    result = _run(RENDER)
    assert result.returncode == 0, result.stdout + result.stderr

    _, _, edge_html, score_html, preview_html = _paths()
    assert edge_html.exists()
    assert score_html.exists()
    assert preview_html.exists()


def test_edge_html_sections_disclaimer_no_js_no_external_css_and_no_forbidden_words():
    _, _, edge_html, _, _ = _paths()
    text = edge_html.read_text()
    lower = text.lower()

    for s in REQUIRED_SECTIONS:
        assert s in text

    assert "research-only" in lower
    assert "<script" not in lower
    assert "javascript:" not in lower
    assert "<link rel='stylesheet'" not in lower
    assert "<link rel=\"stylesheet\"" not in lower

    for token in FORBIDDEN:
        assert token not in lower, f"Forbidden word present in HTML: {token}"


def test_html_ticker_cards_match_json_symbols():
    edge_json, _, edge_html, _, _ = _paths()
    payload = json.loads(edge_json.read_text())
    html_text = edge_html.read_text()

    symbols = [c["symbol"] for c in payload["ticker_cards"]]
    for sym in symbols:
        assert f">{sym} —" in html_text


def test_scoreboard_html_no_fake_immature_outcomes():
    _, score_json, _, score_html, _ = _paths()
    scoreboard = json.loads(score_json.read_text())
    html_text = score_html.read_text()

    for row in scoreboard["rows"]:
        if row["days_elapsed"] < 5 and row["maturity_status"] != "Insufficient Data":
            assert row["maturity_status"] == "Still Maturing"
            assert row["result_5_day"] is None
            assert row["result_10_day"] is None
            assert row["result_20_day"] is None
            assert "Not enough proof yet" in html_text


def test_repeated_render_is_deterministic_for_same_json_inputs():
    assert _run(GEN).returncode == 0
    assert _run(RENDER).returncode == 0

    edge_json, score_json, edge_html, score_html, preview_html = _paths()

    before = {
        "edge_json": _norm_hash_json(edge_json),
        "score_json": _norm_hash_json(score_json),
        "edge_html": hashlib.sha256(edge_html.read_bytes()).hexdigest(),
        "score_html": hashlib.sha256(score_html.read_bytes()).hexdigest(),
        "preview_html": hashlib.sha256(preview_html.read_bytes()).hexdigest(),
    }

    assert _run(RENDER).returncode == 0

    after = {
        "edge_json": _norm_hash_json(edge_json),
        "score_json": _norm_hash_json(score_json),
        "edge_html": hashlib.sha256(edge_html.read_bytes()).hexdigest(),
        "score_html": hashlib.sha256(score_html.read_bytes()).hexdigest(),
        "preview_html": hashlib.sha256(preview_html.read_bytes()).hexdigest(),
    }

    assert before == after
