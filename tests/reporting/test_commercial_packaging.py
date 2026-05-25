from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOCS = [
    ROOT / "docs/commercial/FOUNDING_ACCESS_PAGE.md",
    ROOT / "docs/commercial/PRODUCT_COPY.md",
    ROOT / "docs/commercial/FAQ.md",
    ROOT / "docs/commercial/COMPLIANCE_LANGUAGE.md",
    ROOT / "docs/commercial/MANUAL_SHOPIFY_SETUP_CHECKLIST.md",
]
PREVIEW = ROOT / "reports/edge_sheet/commercial_preview_page.html"

REQUIRED_SECTIONS = [
    "Strategy Factory Edge Sheet — Founding Access",
    "$5/month",
    "The 60-second stock setup sheet",
    "See what’s strong, weak, and too risky before you chase it.",
    "Research-only Disclaimer",
]

FORBIDDEN_CLAIMS = [
    "guaranteed returns",
    "proven winners",
    "trade alerts",
    "buy alerts",
    "sell alerts",
    "beat the market",
    "risk-free",
    "can’t lose",
    "prediction engine",
]


def _run_healthcheck() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/run_feature_factory_healthcheck.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(ROOT)},
    )


def test_commercial_docs_exist():
    for p in DOCS:
        assert p.exists(), f"Missing commercial doc: {p}"


def test_static_preview_exists_and_has_required_sections():
    assert PREVIEW.exists(), f"Missing preview: {PREVIEW}"
    text = PREVIEW.read_text()
    for section in REQUIRED_SECTIONS:
        assert section in text


def test_price_and_research_disclaimer_present():
    text = PREVIEW.read_text().lower()
    assert "$5/month" in text
    assert "research-only" in text


def test_forbidden_claims_do_not_appear_in_docs_or_preview():
    corpus = PREVIEW.read_text().lower() + "\n"
    for p in DOCS:
        corpus += p.read_text().lower() + "\n"

    # allow compliance doc to list forbidden terms; assert they don't appear in preview and selling copy
    selling_copy = (
        (ROOT / "docs/commercial/FOUNDING_ACCESS_PAGE.md").read_text().lower()
        + (ROOT / "docs/commercial/PRODUCT_COPY.md").read_text().lower()
        + PREVIEW.read_text().lower()
    )
    for token in FORBIDDEN_CLAIMS:
        assert token not in selling_copy, f"Forbidden claim leaked in customer-facing copy: {token}"


def test_static_preview_has_no_javascript_or_external_css():
    text = PREVIEW.read_text().lower()
    assert "<script" not in text
    assert "javascript:" not in text
    assert "<link rel='stylesheet'" not in text
    assert "<link rel=\"stylesheet\"" not in text


def test_strategy_behavior_and_execution_layers_untouched_by_commercial_scope():
    # In a pre-dirty working tree, assert behavior-level guardrails instead of git-clean assumptions.
    corpus = (
        (ROOT / "docs/commercial/FOUNDING_ACCESS_PAGE.md").read_text().lower()
        + (ROOT / "docs/commercial/PRODUCT_COPY.md").read_text().lower()
        + (ROOT / "docs/commercial/FAQ.md").read_text().lower()
        + (ROOT / "docs/commercial/COMPLIANCE_LANGUAGE.md").read_text().lower()
        + (ROOT / "docs/commercial/MANUAL_SHOPIFY_SETUP_CHECKLIST.md").read_text().lower()
        + PREVIEW.read_text().lower()
    )

    blocked_terms = [
        "shopify api",
        "checkout logic",
        "payment automation",
        "customer accounts",
        "broker execution enabled",
        "live trading enabled",
    ]
    for token in blocked_terms:
        assert token not in corpus


def test_healthcheck_still_passes_and_blocks_active():
    result = _run_healthcheck()
    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout.lower()
    assert "decision: healthcheck_pass_continue_waiting" in out
    assert "production: blocked" in out
    assert "live: blocked" in out
    assert "broker: blocked" in out
    assert "shadow: blocked" in out
