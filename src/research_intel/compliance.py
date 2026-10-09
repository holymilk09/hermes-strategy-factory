"""Compliance layer: what every output must carry, and what no output may say.

Design basis (docs/claude-v0/COMPLIANCE.md, sourced): the Investment Advisers Act reaches
"analyses or reports concerning securities" even without recommendations; what keeps a
publisher outside it is output that is impersonal in substance — one published methodology,
applied identically to every request, producing descriptive statistics of generally available
market data, selected by the user's own holdings and interests, with no call to action
(Lowe v. SEC; Lingley v. Seeking Alpha, 2024; NASD NTM 01-23 on "call to action").
Disclaimers do not change status (FTC Deception Policy Statement), so the rules below are
enforced in code and tested, not merely stated.

Three enforcement points:
  1. `lint(text)`            — user-facing text may not contain calls to action or forbidden
                               claims (list below, from docs/commercial/COMPLIANCE_LANGUAGE.md
                               plus the FINRA/SEC vocabulary that marks a recommendation).
  2. `Provenance`            — every output states its data source and licence; customer
                               distribution is refused on personal-use data (Robinhood
                               Customer Agreement §2.B bars commercial use/redistribution).
  3. `operator_disclosure()` — outputs that name securities carry the operator's position/
                               compensation disclosure (Securities Act §17(b); scalping cases).
"""
from __future__ import annotations

import pathlib
import re
from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable

import yaml

DISCLAIMER = ("Research only. Not investment advice and not a recommendation to buy, sell or hold "
              "any security. No orders are placed by this system.")

METHODOLOGY_NOTE = (
    "Every figure is a descriptive statistic of generally available market data, produced by one "
    "published methodology applied identically to every request. Names appear because the user's "
    "own holdings, pins or mentions selected them. Nothing here takes account of any person's "
    "objectives, financial situation or needs, and nothing here is a forecast.")

# Phrases that mark a recommendation, a performance claim, or a call to action.
# Matched case-insensitively on user-facing text with the disclaimer removed.
FORBIDDEN_PHRASES: tuple[str, ...] = (
    # recommendation / call to action
    "buy ", "sell ", " hold ", "overweight", "underweight", "price target", "you should",
    "we recommend", "recommend", "consider buying", "consider selling", "accumulate", "load up",
    "take profit", "stop loss", "entry point", "exit point", "watch for", "look for", "watch whether",
    "act now", "get in", "get out", "stand aside", "go long", "go short", "trade this", "trade idea",
    # performance / hype claims (docs/commercial/COMPLIANCE_LANGUAGE.md)
    "guaranteed", "proven winner", "trade alert", "buy alert", "sell alert", "beat the market",
    "risk-free", "risk free", "can't lose", "cannot lose", "prediction engine", "profitable",
    "ready to trade", "high confidence", "validated", "edge confirmed",
    # advice framing
    "personalized", "personalised", "tailored to you", "for your situation",
)

# Allowed despite containing a forbidden fragment (checked first, removed before linting).
ALLOWLIST: tuple[str, ...] = (
    "not a recommendation", "not investment advice", "sell or hold any security",
    "buy, sell or hold", "buy or sell", "holdings", "household", "threshold", "withhold",
    "stakeholder", "holds", "holding", "shareholder", "placeholder",
)

_FORBIDDEN_RE = re.compile("|".join(re.escape(p) for p in FORBIDDEN_PHRASES), re.IGNORECASE)
_ALLOW_RE = re.compile("|".join(re.escape(p) for p in ALLOWLIST), re.IGNORECASE)


def lint(text: str, *, strip: Iterable[str] = (DISCLAIMER, METHODOLOGY_NOTE)) -> list[str]:
    """Return the forbidden phrases found in `text` (empty list = clean)."""
    t = text
    for s in strip:
        t = t.replace(s, " ")
    t = _ALLOW_RE.sub(" ", t)
    return sorted({m.group(0).strip().lower() for m in _FORBIDDEN_RE.finditer(t)})


class ComplianceError(ValueError):
    pass


def assert_clean(text: str, where: str = "output") -> None:
    found = lint(text)
    if found:
        raise ComplianceError(f"{where} contains forbidden language: {found}")


# --------------------------------------------------------------------------- provenance

PERSONAL_USE = "personal-use-only"
REDISTRIBUTABLE = "licensed-redistributable"
UNKNOWN = "unknown"

# Data-source prefix -> licence class. Robinhood: Customer Agreement §2.B ("not reproduce,
# distribute, sell or commercially exploit the Market Data"), §2.C (personal, non-business use).
SOURCE_LICENSES: dict[str, str] = {
    "robinhood": PERSONAL_USE,
    "synthetic": REDISTRIBUTABLE,   # test fixtures only
    "cache": UNKNOWN,
}

SELF = "self"          # operator's own use (dogfood, research)
CUSTOMER = "customer"  # anything shown to a third party, paid or free


@dataclass(frozen=True)
class Provenance:
    sources: tuple[str, ...]
    license: str
    data_through: str | None
    note: str = ""

    @property
    def redistributable(self) -> bool:
        return self.license == REDISTRIBUTABLE

    def to_dict(self) -> dict:
        d = asdict(self)
        d["sources"] = list(self.sources)
        d["redistributable"] = self.redistributable
        return d


def license_for(sources: Iterable[str]) -> str:
    """Most restrictive licence class among the sources (UNKNOWN counts as restrictive)."""
    classes = set()
    for s in sources:
        key = s.split(":")[0].lower()
        classes.add(SOURCE_LICENSES.get(key, UNKNOWN))
    if not classes:
        return UNKNOWN
    if PERSONAL_USE in classes:
        return PERSONAL_USE
    if UNKNOWN in classes:
        return UNKNOWN
    return REDISTRIBUTABLE


class LicenseError(PermissionError):
    pass


def check_distribution(prov: Provenance, mode: str) -> None:
    """Refuse customer distribution of outputs built on data that may not be redistributed."""
    if mode not in (SELF, CUSTOMER):
        raise ValueError(f"unknown distribution mode {mode!r}")
    if mode == CUSTOMER and not prov.redistributable:
        raise LicenseError(
            f"outputs built on {prov.license} data ({', '.join(prov.sources)}) may not be distributed "
            "to customers; import data from a vendor whose licence permits display of derived "
            "analytics to end users (see docs/claude-v0/COMPLIANCE.md §3).")


def provenance_of(provider, symbols: Iterable[str] | None = None, data_through=None) -> Provenance:
    """Provenance of a price provider's series (sources read from the cached files)."""
    srcs: set[str] = set()
    for s in (list(symbols) if symbols is not None else provider.symbols()):
        try:
            srcs.add(provider.series(s).source)
        except Exception:        # a missing or corrupt file is reported elsewhere
            continue
    dt = data_through.isoformat() if hasattr(data_through, "isoformat") else data_through
    return Provenance(tuple(sorted(srcs)), license_for(srcs), dt)


# --------------------------------------------------------------------------- disclosures

DISCLOSURES = pathlib.Path(__file__).with_name("disclosures.yaml")


@dataclass(frozen=True)
class Disclosure:
    configured: bool
    text: str
    as_of: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def operator_disclosure(path: pathlib.Path = DISCLOSURES) -> Disclosure:
    """The operator's standing disclosure about positions in, and compensation relating to,
    securities named in outputs. Unconfigured is reported as such, never silently omitted."""
    if not path.exists():
        return Disclosure(False, "Operator position and compensation disclosure: NOT CONFIGURED.")
    doc = yaml.load(path.read_text(), Loader=yaml.BaseLoader) or {}
    text = (doc.get("statement") or "").strip()
    if not text or doc.get("configured", "false").lower() != "true":
        return Disclosure(False, "Operator position and compensation disclosure: NOT CONFIGURED.")
    return Disclosure(True, text, doc.get("as_of"))


def footer(prov: Provenance, disc: Disclosure, as_of: date | str) -> list[str]:
    """Standard trailer lines for any rendered output."""
    return [
        DISCLAIMER,
        METHODOLOGY_NOTE,
        f"Data: {', '.join(prov.sources) or 'none'}; licence class {prov.license}"
        + ("" if prov.redistributable else " (not for redistribution)")
        + f"; settled through {prov.data_through or 'n/a'}; produced for {as_of}.",
        disc.text,
    ]
