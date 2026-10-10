"""Regression tests for the 2026-10-10 code audit (findings reproduced before fixing)."""
import pytest

from src.research_intel.compliance import lint


@pytest.mark.parametrize("text", [
    "Hold NVDA into the print.", "Trim MU into strength.", "We rate it hold.",
    "Buy or sell NVDA", "buy, sell or hold any security NVDA", "Buy\nNVDA", "Buy\tNVDA",
    "**Buy** NVDA", "<b>buy</b> NVDA", "ｂｕｙ NVDA", "ac­cumulate NVDA", "ac​cumulate NVDA",
    "аccumulate NVDA",          # Cyrillic a
    "Target +12% over 60 sessions", "Consider NVDA", "Reduce exposure", "Add to MU", "Exit MU",
    "The name looks bullish.", "Outperform the index", "Avoid MU here", "Go long NVDA",
])
def test_known_bypasses_are_caught(text):
    assert lint(text), text


@pytest.mark.parametrize("text", [
    "SHORT_HISTORY: window shrinks to 45 sessions.",
    "Holdings and household names are unaffected.",
    "Not a recommendation to buy, sell or hold any security.",
    "Longest complete window: 120 sessions.",
])
def test_legitimate_text_is_clean(text):
    assert lint(text) == [], text


def test_mode_defaults_to_customer(monkeypatch):
    from src.research_intel.server import Config
    assert Config({}).mode == "customer"
    assert Config({"SF_MODE": "self"}).mode == "self"


def test_mixed_sources_are_not_labelled_by_last_row(tmp_path):
    from datetime import date, timedelta
    from src.research_intel.data import CacheStore
    p = tmp_path / "AAA.csv"
    rows = ["date,close,source"]
    d0 = date(2026, 1, 5)
    for i in range(3):
        rows.append(f"{d0 + timedelta(days=i)},10,robinhood:split")
    rows.append(f"{d0 + timedelta(days=3)},10,synthetic")
    (tmp_path / "AAA_1D.csv").write_text("\n".join(rows) + "\n")
    st = CacheStore(tmp_path)
    s = st.series("AAA")
    assert s.source == "mixed"
