"""Scoreboard: the Edge Sheet's "strong, weak, too stretched" as DEFINED descriptive facts.

Per symbol, as of a session (all point-in-time, settled closes):
  ret_20/60/120_pp        total return over the last k sessions
  excess_20/60/120_pp     the same minus SPY's return over the same sessions
  vol_20d_ann_pp          realised volatility, last 20 sessions, annualised
  vol_percentile          where today's vol_20d sits in the symbol's own trailing-250 distribution
                          of 20-session vols (0 = lowest year, 100 = highest)
  ext_z                   today's 20-session return as a z-score against the symbol's own
                          trailing-250 distribution of 20-session returns ("extension")
  off_high_120_pp         distance below the highest close of the last 120 sessions

Labels are rules on those numbers, printed with the rule so nobody mistakes them for views:
  relative_strength  LEADING  = excess_20 > 0 and excess_60 > 0
                     LAGGING  = excess_20 < 0 and excess_60 < 0
                     MIXED    = otherwise
  extension          STRETCHED_UP / STRETCHED_DOWN = |ext_z| >= 2.0 ; else NORMAL
  vol_regime         HIGH = percentile >= 80 ; LOW = percentile <= 20 ; else MID
The rules are HEURISTIC (documented defaults). Nothing here is a forecast.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date
from typing import Sequence

from .data import INSUFFICIENT_DATA, OK, PriceProvider, aligned_returns
from .relationships import EVIDENCE_COMPUTED, EVIDENCE_HEURISTIC, _cov

LOOKBACK = 250
EXT_Z = 2.0
VOL_HI, VOL_LO = 80.0, 20.0
RULES = {
    "relative_strength": "LEADING if excess_20 > 0 and excess_60 > 0; LAGGING if both < 0; else MIXED",
    "extension": f"STRETCHED if |ext_z| >= {EXT_Z} (20-session return vs own trailing-{LOOKBACK} distribution)",
    "vol_regime": f"HIGH if vol percentile >= {VOL_HI:.0f}; LOW if <= {VOL_LO:.0f}; else MID",
}


@dataclass(frozen=True)
class ScoreRow:
    symbol: str
    as_of: str
    status: str
    ret_20_pp: float | None = None
    ret_60_pp: float | None = None
    ret_120_pp: float | None = None
    excess_20_pp: float | None = None
    excess_60_pp: float | None = None
    excess_120_pp: float | None = None
    vol_20d_ann_pp: float | None = None
    vol_percentile: float | None = None
    ext_z: float | None = None
    off_high_120_pp: float | None = None
    relative_strength: str = ""
    extension: str = ""
    vol_regime: str = ""
    history_n: int = 0
    reason: str = ""
    evidence: tuple[str, ...] = (EVIDENCE_COMPUTED, EVIDENCE_HEURISTIC)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["evidence"] = list(self.evidence)
        return d


def _cum(rets: Sequence[float]) -> float:
    return math.prod(1 + r for r in rets) - 1


def _vol20(rets: Sequence[float]) -> float:
    return math.sqrt(_cov(list(rets), list(rets))) * math.sqrt(252) * 100


def _percentile(x: float, pop: Sequence[float]) -> float:
    return 100.0 * sum(1 for v in pop if v <= x) / len(pop)


def score(provider: PriceProvider, symbol: str, as_of: date, market: str = "SPY") -> ScoreRow:
    sym = symbol.upper()
    need = LOOKBACK + 20                         # 20-session windows over a 250-session lookback
    w = aligned_returns(provider, [sym, market], as_of, need)
    if w.status != OK:
        # fall back to what the 120-session block needs; percentiles/z then unavailable
        w = aligned_returns(provider, [sym, market], as_of, 120)
        if w.status != OK:
            return ScoreRow(sym, as_of.isoformat(), INSUFFICIENT_DATA, reason=w.reason)
    r, m = w.returns[sym], w.returns[market]
    n = len(r)
    out = {}
    for k in (20, 60, 120):
        rk, mk = _cum(r[-k:]), _cum(m[-k:])
        out[f"ret_{k}_pp"] = round(rk * 100, 4)
        out[f"excess_{k}_pp"] = round((rk - mk) * 100, 4)
    v20 = _vol20(r[-20:])
    pct = z = None
    if n >= need:
        vols = [_vol20(r[i - 20:i]) for i in range(20, n + 1)]          # 20-session vols, rolling
        rets20 = [_cum(r[i - 20:i]) for i in range(20, n + 1)]
        pct = round(_percentile(v20, vols[:-1]), 2)                      # own history, excluding today's
        hist = rets20[:-1]
        mu, sd = sum(hist) / len(hist), math.sqrt(_cov(hist, hist))
        z = round((rets20[-1] - mu) / sd, 4) if sd > 0 else None
    # 120-session high from closes
    closes = provider.series(sym).upto(as_of).closes[-121:]
    off_high = round((closes[-1] / max(closes) - 1) * 100, 4)
    rs = ("LEADING" if out["excess_20_pp"] > 0 and out["excess_60_pp"] > 0
          else "LAGGING" if out["excess_20_pp"] < 0 and out["excess_60_pp"] < 0 else "MIXED")
    ext = ("NOT_AVAILABLE" if z is None else "STRETCHED_UP" if z >= EXT_Z
           else "STRETCHED_DOWN" if z <= -EXT_Z else "NORMAL")
    vr = ("NOT_AVAILABLE" if pct is None else "HIGH" if pct >= VOL_HI else "LOW" if pct <= VOL_LO else "MID")
    return ScoreRow(sym, as_of.isoformat(), OK, out["ret_20_pp"], out["ret_60_pp"], out["ret_120_pp"],
                    out["excess_20_pp"], out["excess_60_pp"], out["excess_120_pp"], round(v20, 4), pct, z,
                    off_high, rs, ext, vr, n)


def scoreboard(provider: PriceProvider, symbols: Sequence[str], as_of: date, market: str = "SPY") -> dict:
    rows = [score(provider, s, as_of, market).to_dict() for s in dict.fromkeys(x.upper() for x in symbols)]
    ok = [r for r in rows if r["status"] == OK]
    ok.sort(key=lambda r: -(r["excess_60_pp"] or 0))
    return {
        "as_of": as_of.isoformat(),
        "market": market.upper(),
        "rows": ok + [r for r in rows if r["status"] != OK],
        "rules": RULES,
        "evidence": [EVIDENCE_COMPUTED, EVIDENCE_HEURISTIC],
        "note": "Ranked by 60-session excess return vs the market. Labels are rules on the printed "
                "numbers, not views. Nothing here is a forecast.",
    }
