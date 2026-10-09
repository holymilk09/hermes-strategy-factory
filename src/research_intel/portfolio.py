"""Portfolio context (BUILD_DOC §3.2): weights, cluster exposure, portfolio beta.

Weights come from shares x last settled close when shares are given; otherwise from the
profile's stated weights (normalised). Mixed inputs are refused rather than guessed.
Any holding without a usable price or beta is listed, and the coverage of the
portfolio-beta figure is reported — a beta covering 60% of the book says so.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date

from .data import OK, PriceProvider, longest_complete_window
from .interest import Profile
from .relationships import ClusterMap, beta

UNCLUSTERED = "unclustered"


@dataclass(frozen=True)
class Position:
    symbol: str
    shares: float | None
    price: float | None
    value: float | None
    weight: float | None
    cluster: str
    beta: float | None
    beta_index: str
    beta_window: int
    beta_n: int


@dataclass(frozen=True)
class BookContext:
    as_of: str
    basis: str                      # "market_value" | "stated_weights" | "empty"
    positions: tuple[Position, ...]
    total_value: float | None
    cluster_weights: dict = field(default_factory=dict)
    portfolio_beta: float | None = None
    beta_coverage: float = 0.0      # share of book weight with a usable beta
    unpriced: tuple[str, ...] = ()
    no_beta: tuple[str, ...] = ()
    caveats: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        d = asdict(self)
        d["positions"] = [asdict(p) for p in self.positions]
        return d


def _last_close(provider: PriceProvider, sym: str, as_of: date) -> float | None:
    try:
        s = provider.series(sym).upto(as_of)
    except (FileNotFoundError, ValueError):
        return None
    return s.closes[-1] if s.closes else None


def book_context(provider: PriceProvider, clusters: ClusterMap, profile: Profile, as_of: date,
                 index: str = "QQQ", window: int = 60, short_floor: int = 40) -> BookContext:
    hs = profile.holdings
    if not hs:
        return BookContext(as_of.isoformat(), "empty", (), None)
    with_shares = [h for h in hs if h.shares is not None]
    with_weight = [h for h in hs if h.weight is not None]
    if with_shares and len(with_shares) != len(hs):
        raise ValueError("give shares for every holding or for none (mixed inputs are not guessed)")
    if not with_shares and len(with_weight) != len(hs):
        raise ValueError("holdings need shares or weights")

    caveats: list[str] = []
    prices = {h.symbol: _last_close(provider, h.symbol, as_of) for h in hs}
    unpriced = tuple(sorted(s for s, p in prices.items() if p is None))
    if with_shares:
        basis = "market_value"
        values = {h.symbol: (h.shares * prices[h.symbol]) if prices[h.symbol] is not None else None for h in hs}
        priced_total = sum(v for v in values.values() if v is not None)
        total = priced_total if priced_total > 0 else None
        weights = {s: (v / priced_total if (v is not None and priced_total > 0) else None) for s, v in values.items()}
        if unpriced:
            caveats.append(f"weights exclude unpriced holdings: {', '.join(unpriced)}")
    else:
        basis = "stated_weights"
        tw = sum(h.weight for h in hs)
        values = {h.symbol: None for h in hs}
        total = None
        weights = {h.symbol: (h.weight / tw if tw > 0 else None) for h in hs}

    positions, cw = [], {}
    b_num, b_cov, no_beta = 0.0, 0.0, []
    for h in hs:
        info = clusters.info(h.symbol)
        cl = info.primary or UNCLUSTERED
        b = beta(provider, h.symbol, as_of, index, window)
        used_window = window
        if b.status != OK:
            w = longest_complete_window(provider, [h.symbol, index], as_of, window, short_floor)
            if w.status == OK:
                used_window = w.n
                b = beta(provider, h.symbol, as_of, index, used_window)
                caveats.append(f"{h.symbol} beta uses a {used_window}-session window (short history)")
        w = weights[h.symbol]
        if w is not None:
            cw[cl] = cw.get(cl, 0.0) + w
        if b.status == OK and w is not None:
            b_num += w * b.beta
            b_cov += w
        else:
            no_beta.append(h.symbol)
        positions.append(Position(h.symbol, h.shares, prices[h.symbol], values[h.symbol], w, cl,
                                  b.beta if b.status == OK else None, index,
                                  used_window if b.status == OK else 0, b.n))
    pb = (b_num / b_cov) if b_cov > 0 else None
    if pb is not None and b_cov < 0.999:
        caveats.append(f"portfolio beta covers {b_cov:.0%} of the book")
    positions.sort(key=lambda p: (-(p.weight or 0.0), p.symbol))
    return BookContext(as_of.isoformat(), basis, tuple(positions), total,
                       {k: round(v, 6) for k, v in sorted(cw.items(), key=lambda kv: -kv[1])},
                       pb, round(b_cov, 6), unpriced, tuple(sorted(no_beta)), tuple(caveats))
