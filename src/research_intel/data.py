"""Data layer: daily close series, local cache, Robinhood importer, completeness guard.

Design rules (from docs/v0/QC_CONTINUITY_2026-10-04.md and HANDOFF_NEXT_OPERATOR.md):

- One price source per calculation; split-adjusted daily closes.
- Settled closes only. A bar on/after the session that has not settled is dropped
  at import time (`settled_through`), never "fixed up" later.
- Completeness is judged against a REFERENCE CALENDAR (by default the SPY series):
  every session the reference has inside the window must exist for the symbol.
  A missing session makes the calculation INSUFFICIENT_DATA. We never take the
  "Nth available bar" — that is exactly the gapped-cache error that produced the
  false July-2026 ret_5d values.
- Returns are simple daily returns as fractions. Conversion to percentage points
  happens only at the presentation edge (see `to_pp`), so units never mix.

The provider is an interface so a licensed, redistributable feed can replace the
Robinhood development source without changing anything above this module.
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Mapping, Protocol, Sequence

DEFAULT_REFERENCE = "SPY"


# --------------------------------------------------------------------------- series

@dataclass(frozen=True)
class Series:
    """Sorted, de-duplicated daily closes for one symbol from one source."""

    symbol: str
    dates: tuple[date, ...]
    closes: tuple[float, ...]
    source: str = "unknown"

    def __post_init__(self) -> None:
        if len(self.dates) != len(self.closes):
            raise ValueError(f"{self.symbol}: dates/closes length mismatch")
        for i in range(1, len(self.dates)):
            if self.dates[i] <= self.dates[i - 1]:
                raise ValueError(f"{self.symbol}: dates not strictly increasing at {self.dates[i]}")
        for c in self.closes:
            if not (math.isfinite(c) and c > 0):
                raise ValueError(f"{self.symbol}: non-finite or non-positive close {c!r}")

    def upto(self, as_of: date) -> "Series":
        """Point-in-time view: only bars dated <= as_of."""
        n = sum(1 for d in self.dates if d <= as_of)
        return Series(self.symbol, self.dates[:n], self.closes[:n], self.source)

    def as_map(self) -> dict[date, float]:
        return dict(zip(self.dates, self.closes))

    @property
    def last_date(self) -> date | None:
        return self.dates[-1] if self.dates else None


def build_series(symbol: str, rows: Iterable[tuple[date, float]], source: str) -> Series:
    """Build a Series from (date, close) rows, dropping non-finite closes and
    rejecting conflicting duplicates."""
    seen: dict[date, float] = {}
    for d, c in rows:
        if c is None or not math.isfinite(c) or c <= 0:
            continue
        if d in seen and seen[d] != c:
            raise ValueError(f"{symbol}: conflicting closes for {d}: {seen[d]} vs {c}")
        seen[d] = c
    ds = tuple(sorted(seen))
    return Series(symbol.upper(), ds, tuple(seen[d] for d in ds), source)


# --------------------------------------------------------------------------- provider

class PriceProvider(Protocol):
    def series(self, symbol: str) -> Series: ...
    def symbols(self) -> list[str]: ...


class CacheStore:
    """Local cache of `<SYM>_1D.csv` files with columns date,close (extra columns ignored).

    Lives under a gitignored directory (default `cache/research_intel/ohlcv`).
    Price CSVs are never committed — repo rule #10.
    """

    def __init__(self, root: str | pathlib.Path):
        self.root = pathlib.Path(root)

    def path(self, symbol: str) -> pathlib.Path:
        return self.root / f"{symbol.upper()}_1D.csv"

    def symbols(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(p.name[: -len("_1D.csv")] for p in self.root.glob("*_1D.csv"))

    def series(self, symbol: str) -> Series:
        p = self.path(symbol)
        if not p.exists():
            raise FileNotFoundError(f"no cached series for {symbol} at {p}")
        with open(p, newline="") as f:
            reader = csv.DictReader(f)
            meta_source = "cache"
            rows = []
            for r in reader:
                rows.append((date.fromisoformat(r["date"][:10]), _finite(r.get("close"))))
                meta_source = r.get("source") or meta_source
        return build_series(symbol, rows, meta_source)

    def write(self, s: Series) -> pathlib.Path:
        """Write a whole series. Refuses to silently change existing settled history:
        any date present in both old and new files must have an identical close."""
        self.root.mkdir(parents=True, exist_ok=True)
        p = self.path(s.symbol)
        if p.exists():
            old = self.series(s.symbol).as_map()
            new = s.as_map()
            conflicts = [d for d in old.keys() & new.keys() if abs(old[d] - new[d]) > 1e-9]
            if conflicts:
                raise ValueError(
                    f"{s.symbol}: refusing to overwrite settled closes on {sorted(conflicts)[:5]} "
                    "(different adjustment or source?). Write to a new cache dir instead."
                )
            merged = {**old, **new}
            s = Series(s.symbol, tuple(sorted(merged)), tuple(merged[d] for d in sorted(merged)), s.source)
        tmp = p.with_suffix(".tmp")
        with open(tmp, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "close", "source"])
            for d, c in zip(s.dates, s.closes):
                w.writerow([d.isoformat(), repr(c), s.source])
        tmp.replace(p)
        return p


class MemoryProvider:
    """In-memory provider (tests, fixtures)."""

    def __init__(self, series: Iterable[Series]):
        self._s = {s.symbol: s for s in series}

    def series(self, symbol: str) -> Series:
        try:
            return self._s[symbol.upper()]
        except KeyError:
            raise FileNotFoundError(symbol) from None

    def symbols(self) -> list[str]:
        return sorted(self._s)


# --------------------------------------------------------------------------- robinhood import

def parse_robinhood_historicals(
    payload: Mapping | str, *, settled_through: date
) -> list[Series]:
    """Convert a Robinhood `get_equity_historicals` response (daily interval) into Series.

    - Drops `interpolated: true` bars (gap-fill, no information).
    - Drops bars dated after `settled_through` — the newest bar's close is not the
      official settled close until the session is complete.
    - Uses `close_price` only. Requests should use the default split adjustment.
    """
    data = json.loads(payload) if isinstance(payload, str) else payload
    results = data.get("data", data).get("results", [])
    out: list[Series] = []
    for res in results:
        interval = res.get("interval")
        if interval not in (None, "day"):
            raise ValueError(f"{res.get('symbol')}: expected daily bars, got interval={interval!r}")
        rows = []
        for b in res.get("bars", []):
            if b.get("interpolated"):
                continue
            if b.get("session") not in (None, "reg"):
                continue
            d = date.fromisoformat(b["begins_at"][:10])
            if d > settled_through:
                continue
            rows.append((d, _finite(b.get("close_price"))))
        out.append(build_series(res["symbol"], rows, "robinhood:split"))
    return out


# --------------------------------------------------------------------------- completeness

INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
OK = "OK"


@dataclass(frozen=True)
class Window:
    """Aligned daily returns for several symbols over the last `n_returns` sessions
    of the reference calendar ending at `as_of` (inclusive)."""

    status: str
    as_of: date
    sessions: tuple[date, ...]               # n_returns + 1 closes -> n_returns returns
    returns: Mapping[str, tuple[float, ...]] = field(default_factory=dict)
    missing: Mapping[str, tuple[date, ...]] = field(default_factory=dict)
    reason: str = ""

    @property
    def n(self) -> int:
        return max(len(self.sessions) - 1, 0)


def reference_sessions(reference: Series, as_of: date, count: int) -> tuple[date, ...] | None:
    ref = reference.upto(as_of)
    if len(ref.dates) < count:
        return None
    return ref.dates[-count:]


def aligned_returns(
    provider: PriceProvider,
    symbols: Sequence[str],
    as_of: date,
    n_returns: int,
    reference: str = DEFAULT_REFERENCE,
) -> Window:
    """Simple daily returns for `symbols`, aligned to the reference calendar.

    INSUFFICIENT_DATA (with the exact missing sessions listed) if any symbol lacks
    any reference session in the window. Never shifts to available bars.
    """
    ref = provider.series(reference)
    sessions = reference_sessions(ref, as_of, n_returns + 1)
    if sessions is None:
        return Window(INSUFFICIENT_DATA, as_of, (), reason=f"reference {reference} has < {n_returns + 1} sessions by {as_of}")
    if sessions[-1] != as_of:
        return Window(INSUFFICIENT_DATA, as_of, sessions,
                      reason=f"{as_of} is not a reference session (last is {sessions[-1]})")
    missing: dict[str, tuple[date, ...]] = {}
    rets: dict[str, tuple[float, ...]] = {}
    for sym in dict.fromkeys(s.upper() for s in symbols):
        try:
            m = provider.series(sym).as_map()
        except FileNotFoundError:
            missing[sym] = sessions
            continue
        gaps = tuple(d for d in sessions if d not in m)
        if gaps:
            missing[sym] = gaps
            continue
        closes = [m[d] for d in sessions]
        rets[sym] = tuple(closes[i] / closes[i - 1] - 1.0 for i in range(1, len(closes)))
    if missing:
        return Window(INSUFFICIENT_DATA, as_of, sessions, rets, missing,
                      reason="missing reference sessions: " + ", ".join(
                          f"{k}({len(v)})" for k, v in sorted(missing.items())))
    return Window(OK, as_of, sessions, rets)


def longest_complete_window(
    provider: PriceProvider,
    symbols: Sequence[str],
    as_of: date,
    cap: int,
    floor: int,
    reference: str = DEFAULT_REFERENCE,
) -> Window:
    """Largest n in [floor, cap] for which `aligned_returns` is OK, i.e. the longest
    contiguous, gap-free window ending at `as_of`. Used for recent listings
    (short history): the window shrinks, it is never padded, and a gap inside the
    window still blocks. Returns the failing cap-window when nothing qualifies."""
    w = aligned_returns(provider, symbols, as_of, cap, reference)
    if w.status == OK or cap <= floor:
        return w
    syms = [s.upper() for s in symbols]
    # The newest gap (or listing start) across all symbols bounds the window.
    newest_gap = None
    for sym, gaps in w.missing.items():
        if gaps and (newest_gap is None or gaps[-1] > newest_gap):
            newest_gap = gaps[-1]
    if newest_gap is None:
        return w
    n = sum(1 for d in w.sessions if d > newest_gap) - 1
    if n < floor:
        return Window(INSUFFICIENT_DATA, as_of, w.sessions, w.returns, w.missing,
                      reason=f"longest gap-free window is {max(n, 0)} returns (< {floor}); " + w.reason)
    short = aligned_returns(provider, syms, as_of, n, reference)
    return short


# --------------------------------------------------------------------------- helpers

def to_pp(fraction: float) -> float:
    """Fraction -> percentage points. Presentation edge only."""
    return fraction * 100.0


def _finite(v) -> float | None:
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None
