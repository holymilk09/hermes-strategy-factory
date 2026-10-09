"""Return attribution: market + sector + idiosyncratic, per holding and for the book.

Two-factor model with an orthogonalised sector factor (the stat-arb convention — Avellaneda &
Lee; the repo's residual doctrine in knowledge-base/.../00-Anti-Cookie-Cutter-Insights.md §11):

    sector_excess_t = r_sector_t − β(sector, market) · r_market_t        (sector net of market)
    r_t = α + β_m · r_market_t + β_s · sector_excess_t + ε_t

Because sector_excess is the OLS residual of the sector ETF on the market over the baseline,
it is uncorrelated with the market factor there, so β_m and β_s are not fighting over shared
variance (SPY and XLK are ~0.9 correlated; a naive two-regressor fit would be unstable).

Same-day decomposition of the judged session (NOT a forecast):
    market_pp = β_m · r_market_t,   sector_pp = β_s · sector_excess_t,
    idiosyncratic_pp = r_t − market_pp − sector_pp          (so the three always sum to the move)

The baseline window ends the session BEFORE `as_of`, so the judged move never contaminates
its own yardstick. Short history shrinks the window (labelled); a gap blocks; a name whose
sector ETF is not available gets a market-only decomposition (sector = None), stated.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import date

from .data import INSUFFICIENT_DATA, OK, PriceProvider, aligned_returns, longest_complete_window
from .interest import Profile
from .portfolio import book_context
from .relationships import (
    EVIDENCE_COMPUTED, EVIDENCE_SHORT, FULL, SHORT_HISTORY, ClusterMap, _corr, _cov,
)

EVIDENCE_ATTRIB = "SAME-DAY DECOMPOSITION — explains the judged session after the fact; not a forecast"


@dataclass(frozen=True)
class Attribution:
    symbol: str
    as_of: str
    status: str
    market: str = "SPY"
    sector_etf: str | None = None
    move_pp: float | None = None
    market_pp: float | None = None
    sector_pp: float | None = None
    idiosyncratic_pp: float | None = None
    beta_market: float | None = None
    beta_sector: float | None = None
    r2_two_factor: float | None = None
    r2_market_only: float | None = None
    residual_var_reduction: float | None = None   # 1 − var(ε_2f)/var(ε_market-only) on the baseline
    baseline_n: int = 0
    sample: str = FULL
    reason: str = ""
    evidence: tuple[str, ...] = (EVIDENCE_COMPUTED, EVIDENCE_ATTRIB)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["evidence"] = list(self.evidence)
        return d


def _ols2(y, x1, x2):
    """OLS of y on [1, x1, x2] with x2 already orthogonal to x1 (so coefficients separate)."""
    v1, v2 = _cov(x1, x1), _cov(x2, x2)
    b1 = _cov(x1, y) / v1 if v1 > 0 else 0.0
    b2 = _cov(x2, y) / v2 if v2 > 0 else 0.0
    my, m1, m2 = sum(y) / len(y), sum(x1) / len(x1), sum(x2) / len(x2)
    a = my - b1 * m1 - b2 * m2
    resid = [yy - a - b1 * a1 - b2 * a2 for yy, a1, a2 in zip(y, x1, x2)]
    return a, b1, b2, resid


def attribute(provider: PriceProvider, symbol: str, as_of: date, clusters: ClusterMap,
              window: int = 60, min_window: int = 40, market: str = "SPY") -> Attribution:
    sym, mkt = symbol.upper(), market.upper()
    etf = clusters.info(sym).etf
    etf = etf.upper() if etf else None
    avail = set(provider.symbols())
    if etf is not None and (etf not in avail or etf == sym):
        etf = None
    syms = [sym, mkt] + ([etf] if etf else [])
    sample, evidence = FULL, (EVIDENCE_COMPUTED, EVIDENCE_ATTRIB)
    w = aligned_returns(provider, syms, as_of, window + 1)
    if w.status != OK:
        w = longest_complete_window(provider, syms, as_of, window + 1, min_window + 1)
        sample, evidence = SHORT_HISTORY, (EVIDENCE_COMPUTED, EVIDENCE_ATTRIB, EVIDENCE_SHORT)
    if w.status != OK:
        return Attribution(sym, as_of.isoformat(), INSUFFICIENT_DATA, mkt, etf, reason=w.reason)

    r, m = w.returns[sym], w.returns[mkt]
    base_r, base_m, today_r, today_m = r[:-1], m[:-1], r[-1], m[-1]
    n = len(base_r)
    vm = _cov(base_m, base_m)
    if vm <= 0:
        return Attribution(sym, as_of.isoformat(), INSUFFICIENT_DATA, mkt, etf,
                           reason="market factor has zero variance")

    # market-only fit (for the comparison statistic)
    bm0 = _cov(base_m, base_r) / vm
    a0 = sum(base_r) / n - bm0 * sum(base_m) / n
    res0 = [y - a0 - bm0 * x for y, x in zip(base_r, base_m)]
    var0 = _cov(res0, res0)
    vr = _cov(base_r, base_r)
    r2_0 = 1 - var0 / vr if vr > 0 else None

    if etf is None:
        return Attribution(sym, as_of.isoformat(), OK, mkt, None, today_r * 100, bm0 * today_m * 100, None,
                           (today_r - bm0 * today_m) * 100, bm0, None, None, r2_0, None, n, sample,
                           "sector ETF not available; market-only decomposition", evidence)

    s = w.returns[etf]
    base_s, today_s = s[:-1], s[-1]
    bsm = _cov(base_m, base_s) / vm
    asm = sum(base_s) / n - bsm * sum(base_m) / n
    sx = [y - asm - bsm * x for y, x in zip(base_s, base_m)]         # orthogonal to base_m
    today_sx = today_s - asm - bsm * today_m
    a, bm, bs, res = _ols2(base_r, base_m, sx)
    var2 = _cov(res, res)
    r2_2 = 1 - var2 / vr if vr > 0 else None
    red = 1 - var2 / var0 if var0 > 0 else None
    mk, se = bm * today_m, bs * today_sx
    return Attribution(sym, as_of.isoformat(), OK, mkt, etf, today_r * 100, mk * 100, se * 100,
                       (today_r - mk - se) * 100, bm, bs, r2_2, r2_0, red, n, sample, "", evidence)


def book_attribution(provider: PriceProvider, clusters: ClusterMap, profile: Profile, as_of: date,
                     window: int = 60, market: str = "SPY") -> dict:
    """Weight-sum of each holding's decomposition. Weights from book_context (market value or
    stated). Holdings that cannot be attributed are listed; totals cover only those that can."""
    book = book_context(provider, clusters, profile, as_of)
    rows, skipped = [], []
    tot = {"move_pp": 0.0, "market_pp": 0.0, "sector_pp": 0.0, "idiosyncratic_pp": 0.0}
    covered = 0.0
    for pos in book.positions:
        a = attribute(provider, pos.symbol, as_of, clusters, window=window, market=market)
        if a.status != OK or pos.weight is None:
            skipped.append({"symbol": pos.symbol, "reason": a.reason or "no weight"})
            continue
        wgt = pos.weight
        rows.append({"symbol": pos.symbol, "weight": round(wgt, 6), **{k: (round(v, 4) if isinstance(v, float) else v)
                     for k, v in a.to_dict().items() if k not in ("symbol", "as_of", "evidence")}})
        tot["move_pp"] += wgt * a.move_pp
        tot["market_pp"] += wgt * a.market_pp
        tot["sector_pp"] += wgt * (a.sector_pp or 0.0)
        tot["idiosyncratic_pp"] += wgt * a.idiosyncratic_pp
        covered += wgt
    return {
        "as_of": as_of.isoformat(),
        "basis": book.basis,
        "market": market.upper(),
        "window": window,
        "positions": rows,
        "skipped": skipped,
        "totals_pp": {k: round(v, 4) for k, v in tot.items()},
        "weight_covered": round(covered, 6),
        "note": ("Totals are weight-sums over attributed holdings only; a market-only name contributes "
                 "zero to the sector column. Same-day decomposition, not a forecast."),
        "evidence": [EVIDENCE_COMPUTED, EVIDENCE_ATTRIB],
    }
