"""Minimal compliance lint for the P1 research MCP server.

Basis: docs/claude-v0/COMPLIANCE.md on the sibling branch (read-only reference;
this module is an independent implementation for this server). The Investment
Advisers Act reaches "analyses or reports concerning securities" even without
recommendations; what keeps a publisher outside it is output that is impersonal
in substance — one methodology, descriptive statistics, no call to action
(Lowe v. SEC). Disclaimers don't change status, so the rules below are enforced
at render time, not merely stated.

This is NOT legal advice. A counsel-reviewed adviser-status memo is required
before any paid distribution.
"""
from __future__ import annotations

import re

DISCLAIMER = ("Research only. Not investment advice and not a recommendation to "
              "buy, sell or hold any security. No orders are placed by this system.")

# Phrases that mark a recommendation, a call to action, or a performance claim.
FORBIDDEN_PHRASES: tuple[str, ...] = (
    "buy ", "sell ", " hold ", "overweight", "underweight", "price target",
    "you should", "we recommend", "recommend", "consider buying",
    "consider selling", "take profit", "stop loss", "entry point", "exit point",
    "watch for", "act now", "get in", "get out", "go long", "go short",
    "trade idea",
    "guaranteed", "proven winner", "beat the market", "risk-free", "risk free",
    "can't lose", "cannot lose", "profitable", "ready to trade",
    "high confidence", "validated", "edge confirmed",
    "personalized", "personalised", "tailored to you", "for your situation",
)

# Allowed despite containing a forbidden fragment (removed before linting).
ALLOWLIST: tuple[str, ...] = (
    "not a recommendation", "not investment advice", "buy, sell or hold",
    "buy or sell", "holdings", "household", "threshold", "withhold",
    "stakeholder", "holds", "holding", "shareholder", "placeholder",
)

_FORBIDDEN_RE = re.compile("|".join(re.escape(p) for p in FORBIDDEN_PHRASES), re.IGNORECASE)
_ALLOW_RE = re.compile("|".join(re.escape(p) for p in ALLOWLIST), re.IGNORECASE)


def lint(text: str) -> list[str]:
    """Return the forbidden phrases found in text (empty list = clean)."""
    t = _ALLOW_RE.sub("", text)
    return sorted(set(_FORBIDDEN_RE.findall(t)))


class ComplianceError(ValueError):
    pass


def assert_clean(text: str, where: str) -> None:
    """Raise ComplianceError if text contains a forbidden phrase."""
    bad = lint(text)
    if bad:
        raise ComplianceError(f"{where}: forbidden phrase(s) {bad}")
