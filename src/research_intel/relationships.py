"""Relationship engine (BUILD_DOC §3.3, milestone M2).

Deterministic. No LLM. Every result is computed point-in-time from settled closes
via `data.aligned_returns`, and carries: status, sample size, as-of date, and an
evidence label. Nothing here asserts a relationship — clusters come from config and
are *checked* empirically; co-movement is measured, never assumed.

Statuses
  INSUFFICIENT_DATA  a reference session is missing in the window (no sliding)
  NOT_LINKED         long-window correlation below the linkage floor; no expectation
  HEALTHY            linked pair behaving like its history
  DECOUPLING         short-window correlation has broken down vs the long window
  DIVERGENCE         recent cumulative residual vs the pair's own beta is extreme
                     (the "MU moved, its peer didn't follow" case)

Thresholds are HEURISTIC (documented defaults, not validated). They are reported
with every result so a consumer can see exactly what fired.
"""
from __future__ import annotations

import itertools
import math
import pathlib
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Iterable, Mapping, Sequence

import yaml

from .data import INSUFFICIENT_DATA, OK, PriceProvider, aligned_returns

NOT_LINKED = "NOT_LINKED"
HEALTHY = "HEALTHY"
DECOUPLING = "DECOUPLING"
DIVERGENCE = "DIVERGENCE"

EVIDENCE_COMPUTED = "COMPUTED — POINT-IN-TIME (settled daily closes)"
EVIDENCE_CONFIGURED = "CONFIGURED — config/sector_etf_map.yaml (membership asserted, not measured)"
EVIDENCE_HEURISTIC = "HEURISTIC — thresholds are documented defaults, not validated"

DEFAULT_SECTOR_MAP = pathlib.Path(__file__).resolve().parents[2] / "config" / "sector_etf_map.yaml"


@dataclass(frozen=True)
class Thresholds:
    link_floor: float = 0.50          # long corr below this -> NOT_LINKED
    decouple_drop: float = 0.30       # short corr must fall at least this far below long
    decouple_z: float = -2.0          # and Fisher-z of the change at or below this
    divergence_z: float = 2.5         # |cumulative residual z| at or above this
    long_window: int = 120
    short_window: int = 20
    divergence_days: int = 5


# --------------------------------------------------------------------------- clusters

@dataclass(frozen=True)
class ClusterInfo:
    ticker: str
    primary: str | None
    clusters: tuple[str, ...]
    peers: tuple[str, ...]
    etf: str | None
    evidence: str = EVIDENCE_CONFIGURED


class ClusterMap:
    """Ticker -> cluster membership. Primary cluster = the most specific (smallest)
    cluster containing the ticker; ties broken alphabetically."""

    def __init__(self, sectors: Mapping[str, Mapping]):
        self._members: dict[str, tuple[str, ...]] = {}
        self._etf: dict[str, str | None] = {}
        for name, spec in sectors.items():
            stocks = tuple(s.upper() for s in (spec or {}).get("stocks", []) or [])
            if stocks:
                self._members[name] = stocks
                self._etf[name] = (spec or {}).get("etf")

    @classmethod
    def from_yaml(cls, path: str | pathlib.Path = DEFAULT_SECTOR_MAP,
                  extra: Mapping[str, Mapping] | None = None) -> "ClusterMap":
        # BaseLoader keeps every scalar a string. With safe_load, YAML 1.1 turns the
        # ticker ON (ON Semiconductor) into the boolean True.
        with open(path) as f:
            doc = yaml.load(f, Loader=yaml.BaseLoader) or {}
        sectors = dict(doc.get("sectors", {}))
        sectors.update(extra or {})
        return cls(sectors)

    def clusters_of(self, ticker: str) -> tuple[str, ...]:
        t = ticker.upper()
        return tuple(sorted(n for n, m in self._members.items() if t in m))

    def members(self, cluster: str) -> tuple[str, ...]:
        return self._members.get(cluster, ())

    def info(self, ticker: str) -> ClusterInfo:
        t = ticker.upper()
        cs = self.clusters_of(t)
        if not cs:
            return ClusterInfo(t, None, (), (), None)
        primary = min(cs, key=lambda n: (len(self._members[n]), n))
        peers = tuple(m for m in self._members[primary] if m != t)
        return ClusterInfo(t, primary, cs, peers, self._etf.get(primary))


# --------------------------------------------------------------------------- stats

def _mean(x: Sequence[float]) -> float:
    return sum(x) / len(x)


def _cov(x: Sequence[float], y: Sequence[float]) -> float:
    mx, my = _mean(x), _mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (len(x) - 1)


def _corr(x: Sequence[float], y: Sequence[float]) -> float | None:
    vx, vy = _cov(x, x), _cov(y, y)
    if vx <= 0 or vy <= 0:
        return None
    return max(-1.0, min(1.0, _cov(x, y) / math.sqrt(vx * vy)))


def _fisher(r: float) -> float:
    r = max(-0.999999, min(0.999999, r))
    return math.atanh(r)


# --------------------------------------------------------------------------- beta

@dataclass(frozen=True)
class BetaResult:
    ticker: str
    index: str
    window: int
    as_of: str
    status: str
    beta: float | None = None
    stderr: float | None = None
    r2: float | None = None
    corr: float | None = None
    n: int = 0
    reason: str = ""
    evidence: str = EVIDENCE_COMPUTED


def beta(provider: PriceProvider, ticker: str, as_of: date, index: str = "SPY",
         window: int = 60) -> BetaResult:
    """OLS beta of `ticker` daily returns on `index` daily returns over `window` sessions."""
    t, ix = ticker.upper(), index.upper()
    w = aligned_returns(provider, [t, ix], as_of, window)
    if w.status != OK:
        return BetaResult(t, ix, window, as_of.isoformat(), INSUFFICIENT_DATA, n=0, reason=w.reason)
    y, x = w.returns[t], w.returns[ix]
    vx = _cov(x, x)
    if vx <= 0:
        return BetaResult(t, ix, window, as_of.isoformat(), INSUFFICIENT_DATA, n=w.n,
                          reason=f"{ix} returns have zero variance")
    b = _cov(x, y) / vx
    r = _corr(x, y)
    r2 = r * r if r is not None else None
    se = None
    if r2 is not None and w.n > 2:
        vy = _cov(y, y)
        se = math.sqrt(max(1 - r2, 0.0) / (w.n - 2)) * math.sqrt(vy / vx)
    return BetaResult(t, ix, window, as_of.isoformat(), OK, b, se, r2, r, w.n)


# --------------------------------------------------------------------------- pair health

@dataclass(frozen=True)
class PairHealth:
    a: str
    b: str
    as_of: str
    status: str
    corr_long: float | None = None
    corr_short: float | None = None
    corr_change_z: float | None = None
    beta_a_on_b: float | None = None
    recent_return_a_pp: float | None = None
    recent_return_b_pp: float | None = None
    residual_pp: float | None = None
    residual_z: float | None = None
    direction: str = ""
    n_long: int = 0
    n_short: int = 0
    reason: str = ""
    thresholds: dict = field(default_factory=dict)
    evidence: tuple[str, ...] = (EVIDENCE_COMPUTED, EVIDENCE_HEURISTIC)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["evidence"] = list(self.evidence)
        return d


def pair_health(provider: PriceProvider, a: str, b: str, as_of: date,
                th: Thresholds = Thresholds()) -> PairHealth:
    """Is the a/b relationship behaving like its own history as of `as_of`?

    Correlation breakdown: long-window vs short-window correlation, Fisher-z of the change
    (windows overlap, so z is a screening heuristic, not a hypothesis test).

    Divergence: beta and residual sd are estimated on the long window that ENDS
    `divergence_days` sessions before as_of (so the move under test does not
    contaminate its own baseline); then the cumulative residual over the last
    `divergence_days` sessions is standardized by sd * sqrt(days).
    """
    A, B = a.upper(), b.upper()
    tdict = asdict(th)
    k = th.divergence_days
    w = aligned_returns(provider, [A, B], as_of, th.long_window + k)
    if w.status != OK:
        return PairHealth(A, B, as_of.isoformat(), INSUFFICIENT_DATA, reason=w.reason, thresholds=tdict)

    ra, rb = w.returns[A], w.returns[B]
    base_a, base_b = ra[:-k], rb[:-k]                 # long_window returns ending k sessions back
    long_a, long_b = ra[-th.long_window:], rb[-th.long_window:]
    short_a, short_b = ra[-th.short_window:], rb[-th.short_window:]

    c_long = _corr(long_a, long_b)
    c_short = _corr(short_a, short_b)
    if c_long is None or c_short is None:
        return PairHealth(A, B, as_of.isoformat(), INSUFFICIENT_DATA,
                          reason="zero-variance returns in window", thresholds=tdict)
    se = math.sqrt(1.0 / (th.short_window - 3) + 1.0 / (th.long_window - 3))
    z_change = (_fisher(c_short) - _fisher(c_long)) / se

    vb = _cov(base_b, base_b)
    beta_ab = _cov(base_b, base_a) / vb if vb > 0 else 0.0
    resid = [x - beta_ab * y for x, y in zip(base_a, base_b)]
    sd = math.sqrt(_cov(resid, resid)) if len(resid) > 1 else 0.0
    recent_a = ra[-k:]
    recent_b = rb[-k:]
    cum_resid = sum(x - beta_ab * y for x, y in zip(recent_a, recent_b))
    z_resid = cum_resid / (sd * math.sqrt(k)) if sd > 0 else 0.0
    cum_a = math.prod(1 + x for x in recent_a) - 1
    cum_b = math.prod(1 + x for x in recent_b) - 1

    c_base = _corr(base_a, base_b)
    linked = c_long >= th.link_floor or (c_base is not None and c_base >= th.link_floor)

    status, direction, reason = HEALTHY, "", ""
    if not linked:
        status, reason = NOT_LINKED, f"long corr {c_long:.2f} < link floor {th.link_floor}"
    elif abs(z_resid) >= th.divergence_z:
        status = DIVERGENCE
        direction = (f"{A} outperformed its {B}-implied move" if z_resid > 0
                     else f"{A} lagged its {B}-implied move")
        reason = f"cumulative {k}d residual z={z_resid:+.2f} (|z| >= {th.divergence_z})"
    elif z_change <= th.decouple_z and c_short <= c_long - th.decouple_drop:
        status = DECOUPLING
        reason = (f"corr {th.short_window}d {c_short:.2f} vs {th.long_window}d {c_long:.2f}, "
                  f"z={z_change:+.2f}")

    return PairHealth(
        A, B, as_of.isoformat(), status,
        corr_long=c_long, corr_short=c_short, corr_change_z=z_change,
        beta_a_on_b=beta_ab,
        recent_return_a_pp=cum_a * 100, recent_return_b_pp=cum_b * 100,
        residual_pp=cum_resid * 100, residual_z=z_resid, direction=direction,
        n_long=th.long_window, n_short=th.short_window, reason=reason, thresholds=tdict,
    )


# --------------------------------------------------------------------------- lead / lag

@dataclass(frozen=True)
class LeadLag:
    leader: str
    follower: str
    as_of: str
    status: str
    window: int
    lag_corr: dict = field(default_factory=dict)   # lag -> corr(follower_t, leader_{t-lag})
    reason: str = ""
    evidence: tuple[str, ...] = (EVIDENCE_COMPUTED, "DESCRIPTIVE — lagged correlation is not causation")


def lead_lag(provider: PriceProvider, leader: str, follower: str, as_of: date,
             window: int = 120, max_lag: int = 3) -> LeadLag:
    L, F = leader.upper(), follower.upper()
    w = aligned_returns(provider, [L, F], as_of, window + max_lag)
    if w.status != OK:
        return LeadLag(L, F, as_of.isoformat(), INSUFFICIENT_DATA, window, reason=w.reason)
    rl, rf = w.returns[L], w.returns[F]
    out = {}
    for lag in range(0, max_lag + 1):
        f_seg = rf[max_lag:]
        l_seg = rl[max_lag - lag: len(rl) - lag]
        c = _corr(f_seg, l_seg)
        out[lag] = None if c is None else round(c, 6)
    return LeadLag(L, F, as_of.isoformat(), OK, window, out)


# --------------------------------------------------------------------------- cohesion

@dataclass(frozen=True)
class Cohesion:
    cluster: str
    as_of: str
    status: str
    window: int
    mean_pairwise_corr: float | None = None
    member_mean_corr: dict = field(default_factory=dict)
    weak_members: tuple[str, ...] = ()
    unavailable: tuple[str, ...] = ()
    evidence: tuple[str, ...] = (EVIDENCE_COMPUTED, EVIDENCE_HEURISTIC)


def cluster_cohesion(provider: PriceProvider, clusters: ClusterMap, cluster: str, as_of: date,
                     window: int = 120, weak_below: float = 0.30) -> Cohesion:
    """Empirical check of a configured cluster: does each member actually co-move with the rest?
    Members without complete data are listed in `unavailable`, not silently dropped."""
    members = clusters.members(cluster)
    avail, unavailable, rets = [], [], {}
    for m in members:
        w = aligned_returns(provider, [m], as_of, window)
        if w.status == OK:
            avail.append(m)
            rets[m] = w.returns[m]
        else:
            unavailable.append(m)
    if len(avail) < 2:
        return Cohesion(cluster, as_of.isoformat(), INSUFFICIENT_DATA, window,
                        unavailable=tuple(unavailable))
    pair_c = {}
    for x, y in itertools.combinations(avail, 2):
        pair_c[(x, y)] = _corr(rets[x], rets[y])
    vals = [c for c in pair_c.values() if c is not None]
    per = {}
    for m in avail:
        cs = [c for (x, y), c in pair_c.items() if m in (x, y) and c is not None]
        per[m] = round(_mean(cs), 6) if cs else None
    weak = tuple(sorted(m for m, c in per.items() if c is not None and c < weak_below))
    return Cohesion(cluster, as_of.isoformat(), OK, window,
                    round(_mean(vals), 6) if vals else None, per, weak, tuple(unavailable))


# --------------------------------------------------------------------------- scans

def decouplings(provider: PriceProvider, clusters: ClusterMap, symbols: Iterable[str],
                as_of: date, th: Thresholds = Thresholds()) -> list[PairHealth]:
    """Within-primary-cluster pairs among `symbols` (plus each symbol vs its cluster peers
    that have data) whose status is DECOUPLING or DIVERGENCE. Deterministic order."""
    syms = sorted(dict.fromkeys(s.upper() for s in symbols))
    available = set(provider.symbols())
    pairs: set[tuple[str, str]] = set()
    for s in syms:
        info = clusters.info(s)
        for p in info.peers:
            if p in available and s in available:
                pairs.add((s, p))
    events = []
    for a, b in sorted(pairs):
        h = pair_health(provider, a, b, as_of, th)
        if h.status in (DECOUPLING, DIVERGENCE):
            events.append(h)
    return events


def relationship_map(provider: PriceProvider, clusters: ClusterMap, symbols: Iterable[str],
                     as_of: date, indexes: Sequence[str] = ("SPY", "QQQ"),
                     windows: Sequence[int] = (60, 120), th: Thresholds = Thresholds()) -> dict:
    """JSON-serializable relationship map for `symbols` as of `as_of`."""
    syms = sorted(dict.fromkeys(s.upper() for s in symbols))
    per = {}
    for s in syms:
        ci = clusters.info(s)
        betas = []
        for ix in indexes:
            for wnd in windows:
                betas.append(asdict(beta(provider, s, as_of, ix, wnd)))
        per[s] = {"cluster": asdict(ci), "betas": betas}
    events = [e.to_dict() for e in decouplings(provider, clusters, syms, as_of, th)]
    return {
        "as_of": as_of.isoformat(),
        "symbols": per,
        "events": events,
        "thresholds": asdict(th),
        "caveats": [
            "Correlations and betas are descriptive and point-in-time; they are not forecasts.",
            "Cluster membership is configured, then checked; a configured peer can stop co-moving.",
            "DECOUPLING/DIVERGENCE thresholds are heuristic defaults, not validated signals.",
            "Research only. Not investment advice. No orders are placed by this system.",
        ],
        "sent_to_broker": False,
    }
