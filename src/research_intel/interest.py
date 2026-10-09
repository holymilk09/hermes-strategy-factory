"""Interest profile -> ranked watchlist (BUILD_DOC §3.1, MCP_BUILD_SPEC §4).

The profile is a small distilled document, never raw chat history:

    {
      "tickers":  [{"symbol": "MU", "weight": 0.9, "last_mentioned": "2026-10-07"}],
      "sectors":  [{"sector": "semiconductors", "weight": 0.7}],
      "holdings": [{"symbol": "SKHY", "shares": 201}],      # or "weight" instead of shares
      "pins":     ["NVDA"],
      "half_life_days": 14
    }

Scoring (deterministic, every component reported as a reason code):
  HOLDING            1.00            no decay — you own it
  PINNED             0.80            no decay — you asked for it
  MENTIONED          weight * 0.5 ** (age_days / half_life)
  SECTOR_INTEREST    sector weight * 0.25, added only to names already on the list
Score = sum of components. Ranking only changes what is shown first, never what is true.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from datetime import date
from typing import Mapping

from .relationships import ClusterMap

HOLDING_SCORE = 1.0
PIN_SCORE = 0.8
SECTOR_FACTOR = 0.25
MIN_SCORE = 0.05
DEFAULT_HALF_LIFE = 14.0


@dataclass(frozen=True)
class Holding:
    symbol: str
    shares: float | None = None
    weight: float | None = None


@dataclass(frozen=True)
class Mention:
    symbol: str
    weight: float
    last_mentioned: date


@dataclass(frozen=True)
class Profile:
    holdings: tuple[Holding, ...] = ()
    mentions: tuple[Mention, ...] = ()
    sectors: Mapping[str, float] = field(default_factory=dict)
    pins: tuple[str, ...] = ()
    half_life_days: float = DEFAULT_HALF_LIFE
    flag_z: float = 2.5          # abnormal-move threshold (|residual z|); user-settable, reported in output

    @classmethod
    def from_dict(cls, d: Mapping) -> "Profile":
        def _w(x, default=1.0):
            v = float(x if x is not None else default)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"weight must be in [0, 1], got {v}")
            return v

        holdings = []
        for h in d.get("holdings", []) or []:
            shares = h.get("shares")
            if shares is not None and float(shares) < 0:
                raise ValueError(f"{h.get('symbol')}: negative shares")
            holdings.append(Holding(h["symbol"].upper(),
                                    float(shares) if shares is not None else None,
                                    _w(h["weight"]) if h.get("weight") is not None else None))
        mentions = tuple(
            Mention(t["symbol"].upper(), _w(t.get("weight")), date.fromisoformat(t["last_mentioned"]))
            for t in d.get("tickers", []) or [])
        sectors = {s["sector"]: _w(s.get("weight")) for s in d.get("sectors", []) or []}
        pins = tuple(p.upper() for p in d.get("pins", []) or [])
        hl = float(d.get("half_life_days", DEFAULT_HALF_LIFE))
        if hl <= 0:
            raise ValueError("half_life_days must be > 0")
        fz = float(d.get("flag_z", 2.5))
        if not 1.5 <= fz <= 5.0:
            raise ValueError("flag_z must be between 1.5 and 5.0")
        return cls(tuple(holdings), mentions, sectors, pins, hl, fz)

    @classmethod
    def load(cls, path: str | pathlib.Path) -> "Profile":
        with open(path) as f:
            return cls.from_dict(json.load(f))

    @property
    def held(self) -> set[str]:
        return {h.symbol for h in self.holdings}


@dataclass(frozen=True)
class WatchItem:
    symbol: str
    score: float
    reasons: tuple[str, ...]
    held: bool

    @property
    def why_shown(self) -> str:
        return "; ".join(self.reasons)


def mention_score(m: Mention, as_of: date, half_life: float) -> float:
    age = (as_of - m.last_mentioned).days
    if age < 0:
        return 0.0   # a mention dated after as_of does not exist yet (point-in-time)
    return m.weight * 0.5 ** (age / half_life)


def ranked_watchlist(profile: Profile, as_of: date, clusters: ClusterMap | None = None,
                     limit: int | None = None) -> list[WatchItem]:
    scores: dict[str, float] = {}
    reasons: dict[str, list[str]] = {}

    def add(sym: str, pts: float, why: str):
        scores[sym] = scores.get(sym, 0.0) + pts
        reasons.setdefault(sym, []).append(why)

    for h in profile.holdings:
        add(h.symbol, HOLDING_SCORE, "HOLDING")
    for p in profile.pins:
        add(p, PIN_SCORE, "PINNED")
    # one mention entry per symbol: keep the most recent
    latest: dict[str, Mention] = {}
    for m in profile.mentions:
        if m.symbol not in latest or m.last_mentioned > latest[m.symbol].last_mentioned:
            latest[m.symbol] = m
    for m in latest.values():
        s = mention_score(m, as_of, profile.half_life_days)
        if s > 0:
            age = (as_of - m.last_mentioned).days
            add(m.symbol, s, f"MENTIONED {age}d ago (weight {m.weight:.2f})")
    if clusters is not None and profile.sectors:
        for sym in list(scores):
            for c in clusters.clusters_of(sym):
                if c in profile.sectors:
                    add(sym, profile.sectors[c] * SECTOR_FACTOR, f"SECTOR_INTEREST {c}")
    items = [WatchItem(s, round(v, 6), tuple(reasons[s]), s in profile.held)
             for s, v in scores.items() if v >= MIN_SCORE]
    items.sort(key=lambda i: (-i.score, i.symbol))
    return items[:limit] if limit else items
