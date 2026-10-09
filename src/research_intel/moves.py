"""Single-name move context and move alerts (BUILD_DOC §3.4 event-triggered, M5).

For a symbol on `as_of`:
  actual move       = last settled session return
  benchmark         = SPY or QQQ, whichever fits the name better (higher r2) on the baseline
  implied move      = beta * benchmark move
  residual          = actual - implied
  residual z        = residual / sd(baseline residuals)

The baseline (beta, residual sd) is estimated on the window ENDING THE SESSION BEFORE
as_of, so the move being judged never contaminates its own yardstick.

An alert fires only when |z| >= alert_z (default 2.5, HEURISTIC). A big raw move that
the market explains is not an alert; a modest move that the market does NOT explain can be.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date
from typing import Sequence

from .data import INSUFFICIENT_DATA, OK, PriceProvider, aligned_returns, longest_complete_window
from .relationships import (
    EVIDENCE_COMPUTED, EVIDENCE_HEURISTIC, EVIDENCE_SHORT, FULL, SHORT_HISTORY, _corr, _cov,
)

ALERT = "ALERT"
NORMAL = "NORMAL"


@dataclass(frozen=True)
class MoveContext:
    symbol: str
    as_of: str
    status: str                     # NORMAL | ALERT | INSUFFICIENT_DATA
    move_pp: float | None = None
    move_5d_pp: float | None = None
    benchmark: str = ""
    benchmark_move_pp: float | None = None
    beta: float | None = None
    fit_r2: float | None = None
    implied_pp: float | None = None
    residual_pp: float | None = None
    residual_z: float | None = None
    baseline_n: int = 0
    sample: str = FULL
    alert_z: float = 2.5
    reason: str = ""
    evidence: tuple[str, ...] = (EVIDENCE_COMPUTED, EVIDENCE_HEURISTIC)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["evidence"] = list(self.evidence)
        return d


def _fit(y, x):
    vx = _cov(x, x)
    if vx <= 0:
        return None
    b = _cov(x, y) / vx
    r = _corr(x, y)
    resid = [a - b * c for a, c in zip(y, x)]
    sd = math.sqrt(_cov(resid, resid))
    return b, (r * r if r is not None else 0.0), sd


def move_context(provider: PriceProvider, symbol: str, as_of: date,
                 benchmarks: Sequence[str] = ("SPY", "QQQ"), window: int = 60,
                 min_window: int = 40, alert_z: float = 2.5) -> MoveContext:
    sym = symbol.upper()
    syms = [sym, *[b.upper() for b in benchmarks]]
    sample, evidence = FULL, (EVIDENCE_COMPUTED, EVIDENCE_HEURISTIC)
    w = aligned_returns(provider, syms, as_of, window + 1)
    if w.status != OK:
        w = longest_complete_window(provider, syms, as_of, window + 1, min_window + 1)
        sample, evidence = SHORT_HISTORY, (EVIDENCE_COMPUTED, EVIDENCE_HEURISTIC, EVIDENCE_SHORT)
    if w.status != OK:
        return MoveContext(sym, as_of.isoformat(), INSUFFICIENT_DATA, alert_z=alert_z, reason=w.reason)

    y = w.returns[sym]
    base_y, today_y = y[:-1], y[-1]
    best = None
    for b in benchmarks:
        x = w.returns[b.upper()]
        f = _fit(base_y, x[:-1])
        if f is None:
            continue
        if best is None or f[1] > best[1][1]:
            best = (b.upper(), f, x[-1])
    if best is None:
        return MoveContext(sym, as_of.isoformat(), INSUFFICIENT_DATA, alert_z=alert_z,
                           reason="benchmark returns have zero variance")
    bname, (b, r2, sd), bmove = best
    implied = b * bmove
    resid = today_y - implied
    if sd <= 0:
        return MoveContext(sym, as_of.isoformat(), INSUFFICIENT_DATA, alert_z=alert_z,
                           reason="zero-variance baseline (stale or halted prices)")
    z = resid / sd
    last5 = y[-5:] if len(y) >= 5 else y
    move5 = math.prod(1 + r for r in last5) - 1
    status = ALERT if abs(z) >= alert_z else NORMAL
    reason = (f"residual z {z:+.2f} (|z| >= {alert_z})" if status == ALERT
              else f"residual z {z:+.2f} within ±{alert_z}")
    return MoveContext(sym, as_of.isoformat(), status, today_y * 100, move5 * 100, bname,
                       bmove * 100, b, r2, implied * 100, resid * 100, z, len(base_y), sample,
                       alert_z, reason, evidence)


def move_alerts(provider: PriceProvider, symbols: Sequence[str], as_of: date,
                alert_z: float = 2.5) -> list[MoveContext]:
    """Only the ALERT contexts, most extreme first."""
    out = [m for m in (move_context(provider, s, as_of, alert_z=alert_z) for s in symbols)
           if m.status == ALERT]
    out.sort(key=lambda m: (-abs(m.residual_z or 0.0), m.symbol))
    return out
