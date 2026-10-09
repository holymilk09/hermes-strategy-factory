"""Scheduled events (earnings) from a saved Robinhood `get_earnings_calendar` response.

Rules from the source's own guide: `eps.actual == null` means not yet reported;
`report.verified == false` means the date is tentative and must be presented as such.
Events are dated facts with an as-of: an event list fetched on day D says nothing
about announcements made after D.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable, Mapping


@dataclass(frozen=True)
class EarningsEvent:
    symbol: str
    date: date
    timing: str            # "am" | "pm" | ""
    verified: bool
    reported: bool

    def label(self) -> str:
        when = {"am": "before the open", "pm": "after the close"}.get(self.timing, "time not given")
        tent = "" if self.verified else ", date tentative"
        return f"{self.date.strftime('%a %b')} {self.date.day} ({when}{tent})"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["date"] = self.date.isoformat()
        return d


NOT_COVERED = "NOT_COVERED"


class EventCalendar:
    """Events plus the date ranges the source was actually queried for. A date outside
    every covered range is unknown, not empty — absence of an event there proves nothing."""

    def __init__(self, events: Iterable[EarningsEvent], fetched_on: date | None = None,
                 coverage: Iterable[tuple[date, date]] = ()):
        self.events = sorted(events, key=lambda e: (e.date, e.symbol))
        self.fetched_on = fetched_on
        self.coverage = tuple(sorted(coverage))

    @classmethod
    def empty(cls) -> "EventCalendar":
        return cls([], None)

    def covers(self, d: date) -> bool:
        return any(a <= d <= b for a, b in self.coverage)

    @classmethod
    def from_robinhood(cls, payload: Mapping | str, fetched_on: date,
                       start: date | None = None, end: date | None = None) -> "EventCalendar":
        data = json.loads(payload) if isinstance(payload, str) else payload
        rows = data.get("data", data).get("results", [])
        ev = []
        for r in rows:
            rep = r.get("report") or {}
            if not rep.get("date") or not r.get("symbol"):
                continue
            eps = r.get("eps") or {}
            ev.append(EarningsEvent(r["symbol"].upper(), date.fromisoformat(rep["date"][:10]),
                                    (rep.get("timing") or "").lower(), bool(rep.get("verified")),
                                    eps.get("actual") is not None))
        cov = [(start, end)] if start and end else []
        return cls(ev, fetched_on, cov)

    @classmethod
    def load(cls, path: str | pathlib.Path, fetched_on: date,
             start: date | None = None, end: date | None = None) -> "EventCalendar":
        with open(path) as f:
            return cls.from_robinhood(json.load(f), fetched_on, start, end)

    def merged(self, other: "EventCalendar") -> "EventCalendar":
        """Union of two calendars (e.g. a look-back fetch and a forward fetch)."""
        seen = {(e.symbol, e.date): e for e in self.events}
        for e in other.events:
            cur = seen.get((e.symbol, e.date))
            if cur is None or (e.reported and not cur.reported):
                seen[(e.symbol, e.date)] = e
        dates = [d for d in (self.fetched_on, other.fetched_on) if d]
        return EventCalendar(seen.values(), min(dates) if dates else None,
                             self.coverage + other.coverage)

    def reaction_to(self, symbol: str, session: date, prev_session: date | None):
        """The report whose market reaction lands on `session`: a before-the-open report
        dated `session`, or an after-the-close report dated `prev_session`.
        Returns the event, None (covered, no report), or NOT_COVERED."""
        s = symbol.upper()
        if not self.covers(session) or (prev_session is not None and not self.covers(prev_session)):
            hit = None
        else:
            hit = False
        for e in self.events:
            if e.symbol != s:
                continue
            if e.timing == "am" and e.date == session:
                return e
            if e.timing == "pm" and prev_session is not None and e.date == prev_session:
                return e
        return NOT_COVERED if hit is None else None

    def upcoming(self, symbols: Iterable[str], as_of: date, days: int = 14) -> list[EarningsEvent]:
        want = {s.upper() for s in symbols}
        # "reported" reflects the fetch date, not as_of: an event dated on/after as_of is
        # upcoming from as_of's point of view even if it had reported by fetch time
        # (review finding: replays hid MU's 2026-09-30 report).
        return [e for e in self.events
                if e.symbol in want and 0 <= (e.date - as_of).days <= days
                and (not e.reported or (self.fetched_on is not None and self.fetched_on > as_of))]
