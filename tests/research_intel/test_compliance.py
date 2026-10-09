from __future__ import annotations

from datetime import date

import pytest

from src.research_intel.brief import build_brief, render_brief_md
from src.research_intel.compliance import (
    CUSTOMER, PERSONAL_USE, REDISTRIBUTABLE, SELF, UNKNOWN, ComplianceError, LicenseError, Provenance,
    assert_clean, check_distribution, license_for, lint, operator_disclosure, provenance_of,
)
from src.research_intel.data import MemoryProvider, Series
from src.research_intel.interest import Profile
from tests.research_intel.conftest import series_from_returns


@pytest.mark.parametrize("bad", [
    "You should buy MU here.", "Sell NVDA into strength.", "Price target $300.", "Watch for a breakout.",
    "Look for a stock-specific cause.", "Consider buying the dip.", "This strategy is profitable.",
    "Our validated edge.", "Personalized to your portfolio.", "Guaranteed returns.", "Go long AMD.",
    "Stand aside today.", "We recommend caution.",
])
def test_lint_catches_calls_to_action_and_claims(bad):
    assert lint(bad), bad


@pytest.mark.parametrize("ok", [
    "MU moved -4.8% vs -3.6% implied by QQQ (z -0.9), within its own range.",
    "Holdings: MU, LLY. Household weights shown. Flag threshold ±2.5.",
    "Not a recommendation to buy, sell or hold any security.",
    "Shareholders of record; the stock holds above its 50-day average.",
    "Decoupling: MU/NVDA correlation 0.31 vs 0.68 (threshold drop 0.3).",
])
def test_lint_allows_descriptive_text(ok):
    assert lint(ok) == [], ok


def test_assert_clean_raises():
    with pytest.raises(ComplianceError):
        assert_clean("time to buy the dip", "x")


def test_license_classes():
    assert license_for(["robinhood:split", "synthetic"]) == PERSONAL_USE
    assert license_for(["synthetic"]) == REDISTRIBUTABLE
    assert license_for(["cache"]) == UNKNOWN
    assert license_for([]) == UNKNOWN


def test_customer_distribution_refused_on_personal_use_data():
    rh = Provenance(("robinhood:split",), PERSONAL_USE, "2026-10-07")
    check_distribution(rh, SELF)
    with pytest.raises(LicenseError):
        check_distribution(rh, CUSTOMER)
    check_distribution(Provenance(("vendor:x",), REDISTRIBUTABLE, "2026-10-07"), CUSTOMER)
    with pytest.raises(ValueError):
        check_distribution(rh, "public")


def test_disclosure_unconfigured_is_explicit(tmp_path):
    d = operator_disclosure(tmp_path / "missing.yaml")
    assert not d.configured and "NOT CONFIGURED" in d.text
    f = tmp_path / "d.yaml"
    f.write_text("configured: true\nas_of: 2026-10-09\nstatement: The operator holds no positions in named securities.\n")
    d = operator_disclosure(f)
    assert d.configured and d.as_of == "2026-10-09"


def test_brief_carries_provenance_and_is_linted(calendar, rng):
    days = calendar[:121]
    m = rng.normal(0.0005, 0.01, 120)
    p = MemoryProvider([series_from_returns("SPY", days, m), series_from_returns("QQQ", days, m),
                        series_from_returns("AAA", days, 1.3 * m)])
    b = build_brief(p, Profile.from_dict({"holdings": [{"symbol": "AAA", "shares": 3}]}), days[-1])
    assert b["data_provenance"]["license"] == REDISTRIBUTABLE
    assert b["disclosure"]["configured"] is False
    md = render_brief_md(b)
    assert "NOT CONFIGURED" in md and "licence class" in md
    assert provenance_of(p).sources == ("synthetic",)
