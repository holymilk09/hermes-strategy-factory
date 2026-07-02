from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from src.reporting import retail_wording
from src.reporting.maturity_scoreboard import (
    build_scoreboard_row,
    checkpoint_result,
    classify_maturity,
)

import pytest

ROOT = Path(__file__).resolve().parents[1]
EDGE_DIR = ROOT / "reports" / "edge_sheet"
SCRIPT = ROOT / "scripts" / "generate_edge_sheet.py"
HEALTHCHECK = ROOT / "scripts" / "run_feature_factory_healthcheck.py"

FORBIDDEN_RETAIL_WORDS = [
    "buy",
    "sell",
    "buy now",
    "sell now",
    "watch",
    "not covered",
    "constructive",
    "poor regime fit",
    "neutral",
    "weak confirmation",
    "alpha",
    "beta",
    "factor exposure",
    "regime fit",
    "signal decay",
]

ALLOWED_MAIN_VIEWS = {
    "Bullish Swing Setup",
    "Bearish Swing Setup",
    "Waiting for Stronger Proof",
    "Waiting for Pullback",
    "Waiting for Breakout Confirmation",
    "No Edge",
    "Weakening",
    "Too Stretched",
    "High Risk Setup",
    "No Reliable Rating Yet",
}

ALLOWED_TIME_RANGES = {
    "Short-Term Setup: 1–5 trading days",
    "Swing Setup: 5–30 trading days",
    "Long-Term Trend View: 1–6 months+",
}


def _today_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(ROOT)},
    )


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_scoreboard_json() -> dict:
    date_prefix = _today_stamp()
    path = EDGE_DIR / f"{date_prefix}_scoreboard.json"
    assert path.exists(), f"Missing scoreboard JSON: {path}"
    return json.loads(path.read_text())


@pytest.mark.requires_reports
def test_edge_sheet_generator_runs_and_creates_artifacts():
    result = _run([str(ROOT / ".venv/bin/python"), str(SCRIPT)])
    assert result.returncode == 0, result.stderr or result.stdout

    date_prefix = _today_stamp()
    md_path = EDGE_DIR / f"{date_prefix}_edge_sheet.md"
    json_path = EDGE_DIR / f"{date_prefix}_edge_sheet.json"
    scoreboard_path = EDGE_DIR / f"{date_prefix}_scoreboard.md"
    scoreboard_json_path = EDGE_DIR / f"{date_prefix}_scoreboard.json"

    assert md_path.exists(), f"Missing markdown report: {md_path}"
    assert json_path.exists(), f"Missing JSON report: {json_path}"
    assert scoreboard_path.exists(), f"Missing scoreboard: {scoreboard_path}"
    assert scoreboard_json_path.exists(), f"Missing scoreboard JSON: {scoreboard_json_path}"


@pytest.mark.requires_reports
def test_edge_sheet_contains_required_sections_and_disclaimer():
    date_prefix = _today_stamp()
    md_path = EDGE_DIR / f"{date_prefix}_edge_sheet.md"
    assert md_path.exists(), "Edge sheet markdown must exist before this test"

    text = md_path.read_text()
    required_sections = [
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
    for section in required_sections:
        assert section in text, f"Missing section: {section}"

    assert "Research-only" in text
    assert "no live trading" in text.lower()
    assert "no broker execution" in text.lower()


@pytest.mark.requires_reports
def test_forbidden_retail_words_absent_from_customer_output():
    date_prefix = _today_stamp()
    md_path = EDGE_DIR / f"{date_prefix}_edge_sheet.md"
    scoreboard_path = EDGE_DIR / f"{date_prefix}_scoreboard.md"

    all_text = (md_path.read_text() + "\n" + scoreboard_path.read_text()).lower()
    for forbidden in FORBIDDEN_RETAIL_WORDS:
        assert forbidden not in all_text, f"Forbidden retail wording found: {forbidden}"


def test_retail_wording_mapper_is_deterministic_and_uses_required_labels():
    card1 = retail_wording.build_retail_wording(
        outcome_status="PENDING",
        signal_close=100.0,
        ret_5d=0.10,
        ret_20d_rank=0.9,
        ret_60d_rank=0.95,
        progress_text="2/10 bars recorded; 8 bars remaining.",
    )
    card2 = retail_wording.build_retail_wording(
        outcome_status="PENDING",
        signal_close=100.0,
        ret_5d=0.10,
        ret_20d_rank=0.9,
        ret_60d_rank=0.95,
        progress_text="2/10 bars recorded; 8 bars remaining.",
    )

    assert card1 == card2
    assert card1.main_view in ALLOWED_MAIN_VIEWS
    assert card1.time_range in ALLOWED_TIME_RANGES


@pytest.mark.requires_reports
def test_every_ticker_card_has_time_range_next_step_and_disclaimer():
    date_prefix = _today_stamp()
    json_path = EDGE_DIR / f"{date_prefix}_edge_sheet.json"
    payload = json.loads(json_path.read_text())

    for card in payload["ticker_cards"]:
        assert card.get("main_view") in ALLOWED_MAIN_VIEWS
        assert card.get("time_range") in ALLOWED_TIME_RANGES
        assert card.get("setup_breaks_below")
        assert card.get("setup_breaks_above")
        assert card.get("price_area_that_matters")

    assert "Research-only" in payload.get("disclaimer", "")


@pytest.mark.requires_reports
def test_raw_ledgers_remain_unchanged_after_report_generation():
    obs = ROOT / "data/paper_observation/relative_strength_continuation_observation_ledger.csv"
    out = ROOT / "data/paper_observation/relative_strength_continuation_outcome_ledger.csv"

    before_obs = _file_sha256(obs)
    before_out = _file_sha256(out)

    result = _run([str(ROOT / ".venv/bin/python"), str(SCRIPT)])
    assert result.returncode == 0, result.stdout + result.stderr

    after_obs = _file_sha256(obs)
    after_out = _file_sha256(out)
    assert before_obs == after_obs
    assert before_out == after_out


@pytest.mark.requires_reports
def test_scoreboard_immature_rows_marked_still_maturing_when_under_5_days():
    payload = _load_scoreboard_json()
    assert payload["rows"], "Expected scoreboard rows"
    for row in payload["rows"]:
        if row["days_elapsed"] < 5 and row["maturity_status"] != "Insufficient Data":
            assert row["maturity_status"] == "Still Maturing"
            assert row["result_5_day"] is None
            assert row["result_10_day"] is None
            assert row["result_20_day"] is None


@pytest.mark.requires_reports
def test_5_10_20_day_results_gated_by_elapsed_days():
    payload = _load_scoreboard_json()
    for row in payload["rows"]:
        d = row["days_elapsed"]
        if d < 5:
            assert row["result_5_day"] is None
        if d < 10:
            assert row["result_10_day"] is None
        if d < 20:
            assert row["result_20_day"] is None


def test_missing_data_and_setup_broke_classification_logic():
    assert classify_maturity(days_elapsed=0, data_missing=True, setup_broke=False) == "Insufficient Data"
    assert classify_maturity(days_elapsed=7, data_missing=False, setup_broke=True) == "Setup Broke"
    assert classify_maturity(days_elapsed=3, data_missing=False, setup_broke=False) == "Still Maturing"
    assert classify_maturity(days_elapsed=5, data_missing=False, setup_broke=False) == "5-Day Mature"
    assert classify_maturity(days_elapsed=10, data_missing=False, setup_broke=False) == "10-Day Mature"
    assert classify_maturity(days_elapsed=20, data_missing=False, setup_broke=False) == "20-Day Mature"


def test_checkpoint_result_only_when_mature():
    future_rows = [{"close": 101.0}, {"close": 102.0}, {"close": 103.0}]
    assert checkpoint_result(100.0, future_rows, 5) is None
    future_rows = [{"close": 101.0}] * 5
    assert checkpoint_result(100.0, future_rows, 5) == "+1.00%"


def test_setup_broke_trigger_produces_setup_broke_status_in_row_builder():
    card = type("Card", (), {
        "main_view": "Waiting for Stronger Proof",
        "score": "80",
        "price_area_that_matters": "97 to 103",
        "setup_breaks_below": "96",
    })()
    obs = {
        "symbol": "XYZ",
        "signal_timestamp": "2026-05-20T04:00:00+00:00",
        "observation_id": "obs1",
        "signal_close": "100",
    }
    ohlcv_rows = [
        {"dt": datetime.fromisoformat("2026-05-21T04:00:00+00:00"), "close": 99.0, "low": 95.5},
    ]
    row = build_scoreboard_row(observation=obs, card=card, ohlcv_rows=ohlcv_rows)
    assert row.maturity_status == "Setup Broke"


@pytest.mark.requires_reports
def test_no_fake_win_rate_claims_appear():
    payload = _load_scoreboard_json()
    text = json.dumps(payload).lower()
    banned = ["win rate", "hit rate", "proven performance", "guaranteed"]
    for token in banned:
        assert token not in text


@pytest.mark.requires_reports
@pytest.mark.requires_venv
def test_existing_healthcheck_still_passes_and_blocks_active():
    result = _run([str(ROOT / ".venv/bin/python"), str(HEALTHCHECK)])
    assert result.returncode == 0, result.stdout + result.stderr

    stdout = result.stdout.lower()
    # Phase 7C: a FAIL decision caused ONLY by the fail-closed universe
    # freshness floor is correct behavior when OHLCV data is stale.
    if "decision: healthcheck_pass_continue_waiting" not in stdout:
        assert "decision: healthcheck_fail_fix_required" in stdout
        fails = [
            l.strip().lower()
            for l in result.stdout.splitlines()
            if l.strip().lower().startswith("fail")
        ]
        assert fails and all("universe freshness floor" in f for f in fails), (
            f"Healthcheck failed for reasons other than the universe floor: {fails}"
        )
    assert "production: blocked" in stdout
    assert "live: blocked" in stdout
    assert "broker: blocked" in stdout
    assert "shadow: blocked" in stdout


@pytest.mark.requires_reports
@pytest.mark.requires_venv
def test_generator_does_not_modify_strategy_source_files():
    pre = _run(["git", "status", "--short", "src", "scripts", "tests"])
    pre_lines = set(pre.stdout.splitlines())

    run_result = _run([str(ROOT / ".venv/bin/python"), str(SCRIPT)])
    assert run_result.returncode == 0, run_result.stdout + run_result.stderr

    post = _run(["git", "status", "--short", "src", "scripts", "tests"])
    post_lines = set(post.stdout.splitlines())

    new_lines = post_lines - pre_lines

    disallowed_changes = []
    for line in new_lines:
        parts = line.strip().split(maxsplit=1)
        if len(parts) != 2:
            continue
        path = parts[1]
        if path == "scripts/generate_edge_sheet.py":
            continue
        if path == "tests/test_edge_sheet_output_layer.py":
            continue
        if path.startswith("src/reporting/"):
            continue
        disallowed_changes.append(line)

    assert not disallowed_changes, f"Unexpected new source changes detected after generator run: {sorted(disallowed_changes)}"
