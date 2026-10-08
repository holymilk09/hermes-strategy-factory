"""Corporate-action consistency audit: adjusted vs raw closes from the same source.

Found by validation Phase 1b (2026-10-08): Robinhood's split-adjusted HON series carries
an adjustment that scales history UP by an irregular 0.954 (2025-10-30 -> 2026-06-12),
then a 200.00 print and a +35% "move" on 2026-06-16. No split, spin-off or dividend
produces that. Trusting it would have produced a false alert and corrupted HON's betas.

ratio_t = raw_close_t / adjusted_close_t. Between corporate actions it is constant; at an
action it steps. With factor = ratio_before / ratio_after:
  CLEAN_SPLIT     factor is k or 1/k for an integer k in 2..50, or a simple ratio (3/2 ...)
  DISTRIBUTION    1 < factor <= 2: history scaled down (spin-off, special dividend)
  INVALID         anything else (factor < 1 and not a clean reverse split)
An INVALID step quarantines everything from the previous step (or series start) to
QUARANTINE_AFTER sessions after it. Quarantined dates are treated as missing sessions by
the data layer, so windows that touch them block (INSUFFICIENT_DATA) or shrink.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction

from .data import Series

TOL = 1e-6
QUARANTINE_AFTER = 3
CLEAN = sorted({float(Fraction(a, b)) for a in range(1, 51) for b in range(1, 51)
                if (a == 1 or b == 1 or (a <= 10 and b <= 10)) and a != b})

CLEAN_SPLIT = "CLEAN_SPLIT"
DISTRIBUTION = "DISTRIBUTION"
INVALID = "INVALID"


@dataclass(frozen=True)
class Step:
    date: str
    ratio_before: float
    ratio_after: float
    factor: float
    kind: str


@dataclass(frozen=True)
class AdjustmentAudit:
    symbol: str
    status: str                       # OK | QUARANTINED | NO_OVERLAP
    steps: tuple[Step, ...] = ()
    quarantine: tuple[str, ...] = ()
    notes: tuple[str, ...] = field(default_factory=tuple)


def _classify(factor: float) -> str:
    if any(abs(factor - c) <= 2e-3 * c for c in CLEAN):
        return CLEAN_SPLIT
    if 1.0 < factor <= 2.0:
        return DISTRIBUTION
    return INVALID


def adjustment_audit(adjusted: Series, raw: Series) -> AdjustmentAudit:
    a, r = adjusted.as_map(), raw.as_map()
    dates = sorted(a.keys() & r.keys())
    if len(dates) < 2:
        return AdjustmentAudit(adjusted.symbol, "NO_OVERLAP")
    ratios = [r[d] / a[d] for d in dates]
    steps, bounds = [], [0]
    for i in range(1, len(dates)):
        if abs(ratios[i] / ratios[i - 1] - 1) > TOL:
            f = ratios[i - 1] / ratios[i]
            steps.append(Step(dates[i].isoformat(), round(ratios[i - 1], 6), round(ratios[i], 6),
                              round(f, 6), _classify(f)))
            bounds.append(i)
    q: set[date] = set()
    for k, s in enumerate(steps):
        if s.kind != INVALID:
            continue
        i = bounds[k + 1]
        lo = bounds[k]
        hi = min(len(dates) - 1, i + QUARANTINE_AFTER)
        q.update(dates[lo:hi + 1])
    notes = []
    if ratios[-1] < 1 - TOL and not steps:
        notes.append("adjusted above raw with no step in range — check longer history")
    return AdjustmentAudit(adjusted.symbol, "QUARANTINED" if q else "OK", tuple(steps),
                           tuple(sorted(d.isoformat() for d in q)), tuple(notes))
