"""MCP server: the research layer for personal AI agents (stdio transport).

    python -m src.research_intel.server            # env: SF_CACHE, SF_MODE, SF_EVENTS, SF_LEDGER_*

Design rules (docs/claude-v0/COMPLIANCE.md):
  * Read-only. No orders, no broker, no writes to ledgers. `sent_to_broker` is False everywhere.
  * Impersonal in substance: one published methodology applied identically to every request.
    The agent sends holdings/interest per request as a FILTER over generally available data;
    the server computes, never judges, and keeps nothing (profiles are not logged or stored).
  * Licence gate: in SF_MODE=customer the server refuses to start unless the cache's data
    licence permits redistribution of derived analytics (Robinhood data is personal-use only).
  * Every response carries: as_of, data provenance, evidence labels, disclaimer, methodology
    note and the operator's position disclosure.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from datetime import date
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from .attribution import book_attribution
from .brief import build_brief, product_clusters
from .compliance import (
    CUSTOMER, DISCLAIMER, METHODOLOGY_NOTE, SELF, check_distribution, operator_disclosure,
    provenance_of,
)
from .data import DEFAULT_REFERENCE, CacheStore
from .events import EventCalendar
from .interest import Profile, ranked_watchlist
from .relationships import relationship_map as _relationship_map
from .report import build_report, render_report_md
from .research_record import FROZEN_LINEAGE, HYPOTHESIS_V1, summarize
from .research_record import hypothesis_status as _hypothesis_status
from .risk import risk_panel
from .scoreboard import scoreboard as _scoreboard

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


class Config:
    def __init__(self, env: dict[str, str] | None = None):
        e = env or os.environ
        self.cache = pathlib.Path(e.get("SF_CACHE", "cache/research_intel/ohlcv_v2"))
        self.mode = e.get("SF_MODE", CUSTOMER)  # restrictive default: must opt in to self
        self.events = [s for s in e.get("SF_EVENTS", "").split(",") if s]
        self.ledger_frozen = e.get("SF_LEDGER_FROZEN") or None
        self.ledger_hyp = e.get("SF_LEDGER_HYP") or None
        self.ledger_hyp_rejected = e.get("SF_LEDGER_HYP_REJECTED") or None
        self.events_date = e.get("SF_EVENTS_DATE") or None


class Service:
    """Everything the tools need, built once. Holds no user data."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.store = CacheStore(cfg.cache)
        ref = self.store.series(DEFAULT_REFERENCE)
        self.sessions = set(ref.dates)
        self.last = ref.last_date
        self.clusters = product_clusters()
        self.calendar = None
        for spec in cfg.events:
            fp, start, end = spec.rsplit(":", 2)
            c = EventCalendar.load(fp, date.fromisoformat(cfg.events_date) if cfg.events_date else self.last,
                                   date.fromisoformat(start), date.fromisoformat(end))
            self.calendar = c if self.calendar is None else self.calendar.merged(c)
        self.provenance = provenance_of(self.store, data_through=self.last)
        check_distribution(self.provenance, cfg.mode)      # raises LicenseError in customer mode on personal-use data
        self.disclosure = operator_disclosure()
        if cfg.mode == CUSTOMER and not self.disclosure.configured:
            raise PermissionError("customer mode requires a configured operator disclosure (disclosures.yaml)")

    def as_of(self, s: str | None) -> date:
        """Anticipated failures (bad date, non-session) become ToolErrors the agent can read."""
        if not s:
            return self.last
        try:
            d = date.fromisoformat(s)
        except ValueError:
            raise ToolError(f"as_of must be YYYY-MM-DD, got {s!r}") from None
        if d not in self.sessions:
            prior = self.store.series(DEFAULT_REFERENCE).upto(d).last_date
            raise ToolError(f"{d} is not a settled session in the data; last session on or before it: {prior}")
        return d

    def stamp(self, payload: dict, as_of: date) -> dict:
        payload.setdefault("as_of", as_of.isoformat())
        payload["data_provenance"] = self.provenance.to_dict()
        payload["disclaimer"] = DISCLAIMER
        payload["methodology"] = METHODOLOGY_NOTE
        payload["disclosure"] = self.disclosure.to_dict()
        payload["sent_to_broker"] = False
        return payload


def build_server(svc: Service) -> MCPServer:
    srv = MCPServer(
        name="strategy-factory-research",
        instructions=(
            "Research-only descriptive analytics on US equities. Send the user's holdings/interest "
            "profile with each call; nothing is stored. Outputs are statistics with thresholds and "
            "sample sizes, never recommendations. Quote figures with their as_of date and caveats."),
        version="0.1.0",
    )

    def _profile(profile: dict | None) -> Profile:
        try:
            return Profile.from_dict(profile or {})
        except (KeyError, ValueError, TypeError) as e:
            raise ToolError(f"invalid profile: {e}") from None

    @srv.tool(annotations=READ_ONLY, description=(
        "Daily brief for a profile: abnormal-move flags vs each name's own history, earnings context, "
        "decoupling/divergence flags, book beta and group exposure. Profile: {holdings:[{symbol,shares|weight}], "
        "tickers:[{symbol,weight,last_mentioned}], pins:[...], sectors:[{sector,weight}]}."))
    def brief(profile: dict[str, Any] | None = None, as_of: str | None = None) -> dict:
        d = svc.as_of(as_of)
        return svc.stamp(build_brief(svc.store, _profile(profile), d, svc.calendar, svc.clusters), d)

    @srv.tool(annotations=READ_ONLY, description=(
        "Full report = brief + book attribution + risk panel + scoreboard, as JSON plus a markdown rendering."))
    def report(profile: dict[str, Any] | None = None, as_of: str | None = None) -> dict:
        d = svc.as_of(as_of)
        r = build_report(svc.store, _profile(profile), d, svc.calendar, svc.clusters)
        r["markdown"] = render_report_md(r)
        return svc.stamp(r, d)

    @srv.tool(annotations=READ_ONLY, description=(
        "Same-day return attribution of each holding and the book: market + sector + stock-specific "
        "(two-factor, orthogonalised sector ETF). Explains the session after the fact; not a forecast."))
    def attribution(profile: dict[str, Any], as_of: str | None = None) -> dict:
        d = svc.as_of(as_of)
        return svc.stamp(book_attribution(svc.store, svc.clusters, _profile(profile), d), d)

    @srv.tool(annotations=READ_ONLY, description=(
        "Pro-forma risk panel for the book: realised vol, betas, concentration (HHI, effective N), "
        "average pairwise correlation, diversification ratio, max drawdown, 1-day historical VaR/ES, "
        "risk contribution per holding. Today's weights replayed over up to 250 sessions."))
    def risk(profile: dict[str, Any], as_of: str | None = None) -> dict:
        d = svc.as_of(as_of)
        return svc.stamp(risk_panel(svc.store, svc.clusters, _profile(profile), d).to_dict(), d)

    @srv.tool(annotations=READ_ONLY, description=(
        "Scoreboard: trailing 20/60/120-session returns vs SPY, realised vol and its own-history "
        "percentile, extension z-score, distance from 120-session high, with the labelling rules printed."))
    def scoreboard(symbols: list[str], as_of: str | None = None) -> dict:
        d = svc.as_of(as_of)
        return svc.stamp(_scoreboard(svc.store, symbols, d), d)

    @srv.tool(annotations=READ_ONLY, description=(
        "Relationship map for symbols: configured group, betas to SPY/QQQ (60/120d) and any "
        "decoupling/divergence events among configured peers. Point-in-time correlations, never causal."))
    def relationship_map(symbols: list[str], as_of: str | None = None) -> dict:
        d = svc.as_of(as_of)
        return svc.stamp(_relationship_map(svc.store, svc.clusters, symbols, d), d)

    @srv.tool(annotations=READ_ONLY, description=(
        "Forward-test status of the preregistered hypothesis (rule, n resolved/pending, success and kill "
        "bars, verdict). Signal tools stay gated until a verdict; a failed hypothesis never gets one."))
    def hypothesis_status(as_of: str | None = None) -> dict:
        d = svc.as_of(as_of)
        from dataclasses import asdict
        return svc.stamp(asdict(_hypothesis_status(svc.cfg.ledger_hyp, svc.cfg.ledger_hyp_rejected, d)), d)

    @srv.tool(annotations=READ_ONLY, description=(
        "Resolved forward-observation records (frozen lineage and current hypothesis): n, mean, median, "
        "hit rate, per-cohort breakdown, with sample-size caveats. Never a validated edge."))
    def cohort_summary(as_of: str | None = None) -> dict:
        d = svc.as_of(as_of)
        return svc.stamp({"records": [summarize(svc.cfg.ledger_frozen, FROZEN_LINEAGE).to_dict(),
                                      summarize(svc.cfg.ledger_hyp, HYPOTHESIS_V1).to_dict()]}, d)

    @srv.tool(annotations=READ_ONLY, description=(
        "What this server is running on: data sources and licence class, settled-through date, symbols "
        "covered, quarantined symbols, calendar coverage, distribution mode."))
    def data_status() -> dict:
        q = svc.store.quarantine()
        cov = [(a.isoformat(), b.isoformat()) for a, b in (svc.calendar.coverage if svc.calendar else ())]
        return svc.stamp({"symbols": svc.store.symbols(), "settled_through": svc.last.isoformat(),
                          "quarantined": {k: len(v) for k, v in q.items() if v},
                          "calendar_coverage": cov, "mode": svc.cfg.mode,
                          "watchlist_preview_for_empty_profile": [w.symbol for w in ranked_watchlist(Profile(), svc.last)]},
                         svc.last)

    return srv


def main() -> int:
    cfg = Config()
    try:
        svc = Service(cfg)
    except (PermissionError, FileNotFoundError, ValueError) as e:
        print(f"strategy-factory-research: refusing to start: {e}", file=sys.stderr)
        return 2
    build_server(svc).run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
