"""Book risk panel: pro-forma statistics of the CURRENT weights applied to history.

"Pro forma" means: the book as it is held today, replayed over the last `window` sessions.
It describes the risk of today's weights, not what the account actually earned (holdings
changed over time). Every figure is a sample statistic over the stated window.

Metrics (knowledge-base/.../05-Risk-Portfolio-Execution/Risk-Metrics.md):
  realised vol 20d/60d (annualised, √252)        beta to SPY and QQQ (60d)
  concentration: HHI = Σw², effective N = 1/HHI  average pairwise correlation (60d)
  diversification ratio = Σ wᵢσᵢ / σ_p (60d)     max drawdown over the window (pro forma)
  1-day historical VaR 95/99 and ES 95 (pp of book value, positive = loss)
  risk contribution per holding = wᵢ(Σw)ᵢ / σ_p²  (sums to 1)

Window: target 250 sessions (≈1 year), floor 60. Holdings with less history than the floor
are excluded from the pro-forma series and listed, so a 60-session-old listing never
silently shortens a 250-session VaR for the whole book.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import date

from .data import INSUFFICIENT_DATA, OK, PriceProvider, aligned_returns, longest_complete_window
from .interest import Profile
from .portfolio import book_context
from .relationships import EVIDENCE_COMPUTED, EVIDENCE_SHORT, FULL, SHORT_HISTORY, ClusterMap, _corr, _cov

EVIDENCE_PROFORMA = "PRO FORMA — today's weights replayed over the window; not realised account returns"
ANN = math.sqrt(252)


@dataclass(frozen=True)
class RiskPanel:
    as_of: str
    status: str
    window_n: int = 0
    sample: str = FULL
    basis: str = ""
    weights: dict = field(default_factory=dict)
    excluded: dict = field(default_factory=dict)         # symbol -> reason
    weight_covered: float = 0.0
    vol_20d_ann_pp: float | None = None
    vol_60d_ann_pp: float | None = None
    beta_spy_60d: float | None = None
    beta_qqq_60d: float | None = None
    hhi: float | None = None
    effective_n: float | None = None
    avg_pairwise_corr_60d: float | None = None
    diversification_ratio_60d: float | None = None
    max_drawdown_pp: float | None = None
    worst_day_pp: float | None = None
    var_95_pp: float | None = None
    var_99_pp: float | None = None
    es_95_pp: float | None = None
    risk_contribution: dict = field(default_factory=dict)
    holding_vol_60d_ann_pp: dict = field(default_factory=dict)
    reason: str = ""
    evidence: tuple[str, ...] = (EVIDENCE_COMPUTED, EVIDENCE_PROFORMA)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["evidence"] = list(self.evidence)
        return d


def _quantile(xs: list[float], q: float) -> float:
    """Linear-interpolated sample quantile (numpy default), q in [0, 1]."""
    s = sorted(xs)
    pos = (len(s) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def _max_drawdown(rets: list[float]) -> float:
    peak, level, mdd = 1.0, 1.0, 0.0
    for r in rets:
        level *= 1 + r
        peak = max(peak, level)
        mdd = min(mdd, level / peak - 1)
    return mdd


def risk_panel(provider: PriceProvider, clusters: ClusterMap, profile: Profile, as_of: date,
               window: int = 250, floor: int = 60) -> RiskPanel:
    book = book_context(provider, clusters, profile, as_of)
    weights = {p.symbol: p.weight for p in book.positions if p.weight is not None}
    if not weights:
        return RiskPanel(as_of.isoformat(), INSUFFICIENT_DATA, basis=book.basis,
                         reason="no priced holdings with weights")
    excluded: dict[str, str] = {}
    for sym in list(weights):
        try:
            hist = provider.series(sym).upto(as_of)
            if len(hist.dates) < floor + 1:
                excluded[sym] = f"only {max(len(hist.dates) - 1, 0)} sessions of history (floor {floor})"
                del weights[sym]
        except (FileNotFoundError, ValueError) as e:
            excluded[sym] = str(e)
            del weights[sym]
    if not weights:
        return RiskPanel(as_of.isoformat(), INSUFFICIENT_DATA, basis=book.basis, excluded=excluded,
                         reason="no holding has enough history")
    covered = sum(weights.values())
    w = {k: v / covered for k, v in weights.items()}             # renormalise over included names
    syms = list(w) + ["SPY", "QQQ"]
    sample, evidence = FULL, (EVIDENCE_COMPUTED, EVIDENCE_PROFORMA)
    win = aligned_returns(provider, syms, as_of, window)
    if win.status != OK:
        win = longest_complete_window(provider, syms, as_of, window, floor)
        sample, evidence = SHORT_HISTORY, (EVIDENCE_COMPUTED, EVIDENCE_PROFORMA, EVIDENCE_SHORT)
    if win.status != OK:
        return RiskPanel(as_of.isoformat(), INSUFFICIENT_DATA, basis=book.basis, excluded=excluded,
                         reason=win.reason)
    n = win.n
    rets = {s: win.returns[s] for s in syms}
    book_r = [sum(w[s] * rets[s][i] for s in w) for i in range(n)]

    def vol(xs):
        return math.sqrt(_cov(xs, xs)) * ANN * 100 if len(xs) > 1 else None

    def beta(y, x):
        vx = _cov(x, x)
        return _cov(x, y) / vx if vx > 0 else None

    last60 = slice(-min(60, n), None)
    b60 = book_r[last60]
    hv = {s: vol(rets[s][last60]) for s in w}
    corrs = []
    names = list(w)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            c = _corr(rets[names[i]][last60], rets[names[j]][last60])
            if c is not None:
                corrs.append(c)
    sig_p = math.sqrt(_cov(b60, b60)) if len(b60) > 1 else 0.0
    div_ratio = (sum(w[s] * math.sqrt(_cov(rets[s][last60], rets[s][last60])) for s in w) / sig_p
                 if sig_p > 0 else None)
    rc = {}
    if sig_p > 0:
        for s in w:
            rc[s] = round(w[s] * _cov(rets[s][last60], b60) / (sig_p ** 2), 6)
    losses = [-r for r in book_r]
    hhi = sum(v * v for v in w.values())
    return RiskPanel(
        as_of.isoformat(), OK, n, sample, book.basis,
        {k: round(v, 6) for k, v in w.items()}, excluded, round(covered, 6),
        vol(book_r[-min(20, n):]), vol(b60),
        beta(b60, rets["SPY"][last60]), beta(b60, rets["QQQ"][last60]),
        round(hhi, 6), round(1 / hhi, 4),
        round(sum(corrs) / len(corrs), 4) if corrs else None,
        round(div_ratio, 4) if div_ratio is not None else None,
        round(_max_drawdown(book_r) * 100, 4), round(min(book_r) * 100, 4),
        round(_quantile(losses, 0.95) * 100, 4), round(_quantile(losses, 0.99) * 100, 4),
        round(sum(x for x in losses if x >= _quantile(losses, 0.95)) /
              max(1, sum(1 for x in losses if x >= _quantile(losses, 0.95))) * 100, 4),
        rc, {k: round(v, 4) for k, v in hv.items() if v is not None},
        "", evidence,
    )
