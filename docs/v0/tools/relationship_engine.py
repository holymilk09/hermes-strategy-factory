#!/usr/bin/env python3
"""
Relationship engine — Strategy Factory v0 research-intel (built 2026-10-17).

Computes the portfolio relationship layer the MCP spec promised, from real
daily bars (Massive cache written by massive_data.py):

  - Beta (and R²) of each name vs SPY and QQQ over trailing windows.
  - Correlation clusters among non-benchmark names (connected components at
    a correlation threshold) over the trailing window.
  - Lead-lag: cross-correlation of daily returns at lags -5..+5 sessions for
    focus pairs; a pair is only called lead-lag when the best lag is non-zero
    and clears a minimum correlation, otherwise it is reported as
    contemporaneous/no-link. Correlations are measured point-in-time: every
    statistic uses only bars on or before --as-of. Nothing is asserted from
    a fitted story — the numbers are the output.

Conventions: daily log returns; windows are trailing N return observations
ending at the as-of date, using each pair's common dates (pairwise-complete);
every statistic reports its n. Benchmarks: SPY, QQQ. Reference ETFs (SMH,
XLU, URA) get betas/correlations but are excluded from cluster membership
reporting as context nodes — they are included in pairs output.

Output: JSON (machine-readable, consumed by the MCP server's
relationship_map tool) + a short Markdown map for humans.

Usage:
  relationship_engine.py --cache-dir DIR --as-of 2026-10-16 \
      --out-json map.json --out-md map.md
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
from datetime import datetime, timezone

BENCHMARKS = ["SPY", "QQQ"]
CONTEXT_ETFS = ["SMH", "XLU", "URA"]
DEFAULT_WINDOWS = (60, 120)
CLUSTER_THRESHOLD = 0.60
LEADLAG_MAX_LAG = 5
LEADLAG_MIN_CORR = 0.15


# ---------------------------------------------------------------- data

def load_closes(cache_dir: pathlib.Path) -> dict[str, list[tuple[str, float]]]:
    out: dict[str, list[tuple[str, float]]] = {}
    for p in sorted(cache_dir.glob("*.csv")):
        sym = p.stem.upper()
        with open(p, newline='') as f:
            rows = list(csv.DictReader(f))
        series = []
        for r in rows:
            try:
                close = float(r["Close"])
            except (KeyError, TypeError, ValueError):
                continue
            if close == close and close > 0:
                series.append((r["Date"][:10], close))
        if series:
            out[sym] = sorted(series)
    return out


def returns_map(series: list[tuple[str, float]], as_of: str) -> dict[str, float]:
    """Daily log returns keyed by the return's end date, bars <= as_of only."""
    pts = [(d, c) for d, c in series if d <= as_of]
    return {pts[i][0]: math.log(pts[i][1] / pts[i - 1][1])
            for i in range(1, len(pts))}


# ---------------------------------------------------------------- stats

def _paired(a: dict[str, float], b: dict[str, float], window: int):
    dates = sorted(set(a) & set(b))[-window:]
    return [(a[d], b[d]) for d in dates], dates


def pearson(pairs: list[tuple[float, float]]) -> float | None:
    n = len(pairs)
    if n < 10:
        return None
    ma = sum(x for x, _ in pairs) / n
    mb = sum(y for _, y in pairs) / n
    cov = sum((x - ma) * (y - mb) for x, y in pairs)
    va = sum((x - ma) ** 2 for x, _ in pairs)
    vb = sum((y - mb) ** 2 for _, y in pairs)
    if va == 0 or vb == 0:
        return None
    return cov / math.sqrt(va * vb)


def beta_r2(asset: dict[str, float], bench: dict[str, float], window: int):
    """OLS slope of asset returns on benchmark returns + R², trailing window."""
    pairs, dates = _paired(asset, bench, window)
    n = len(pairs)
    if n < 20:
        return None
    mb = sum(y for _, y in pairs) / n
    ma = sum(x for x, _ in pairs) / n
    cov = sum((x - ma) * (y - mb) for x, y in pairs)
    vb = sum((y - mb) ** 2 for _, y in pairs)
    va = sum((x - ma) ** 2 for x, _ in pairs)
    if vb == 0 or va == 0:
        return None
    beta = cov / vb
    corr = cov / math.sqrt(va * vb)
    return {"beta": round(beta, 3), "r2": round(corr * corr, 3), "n": n,
            "window_end": dates[-1] if dates else None}


def cross_corr(a: dict[str, float], b: dict[str, float], lag: int,
               window: int) -> float | None:
    """corr(A_t, B_{t+lag}) on dates where both exist. lag > 0: A leads B."""
    a_dates = sorted(a)
    b_dates = sorted(b)
    b_pos = {d: i for i, d in enumerate(b_dates)}
    pairs = []
    for d in a_dates:
        j = b_pos.get(d)
        if j is None:
            continue
        k = j + lag
        if 0 <= k < len(b_dates):
            pairs.append((a[d], b[b_dates[k]]))
    pairs = pairs[-window:]
    return pearson(pairs)


def lead_lag(a: dict[str, float], b: dict[str, float], window: int = 120):
    """Best cross-correlation over lags -5..+5 for the ordered pair (A, B)."""
    results = {}
    for lag in range(-LEADLAG_MAX_LAG, LEADLAG_MAX_LAG + 1):
        c = cross_corr(a, b, lag, window)
        if c is not None:
            results[lag] = c
    if not results:
        return None
    best_lag = max(results, key=lambda k: abs(results[k]))
    return {"best_lag": best_lag, "best_corr": round(results[best_lag], 3),
            "contemporaneous": round(results.get(0, 0.0), 3),
            "by_lag": {str(k): round(v, 3) for k, v in sorted(results.items())}}


# ---------------------------------------------------------------- engine

def build(cache_dir: pathlib.Path, as_of: str,
          windows: tuple[int, ...] = DEFAULT_WINDOWS) -> dict:
    closes = load_closes(cache_dir)
    if "SPY" not in closes:
        raise SystemExit("SPY missing from cache — cannot compute relationships")
    rets = {sym: returns_map(s, as_of) for sym, s in closes.items()}
    names = sorted(s for s in closes if s not in BENCHMARKS)
    main_window = max(windows)

    betas = {}
    for sym in names:
        entry = {}
        for w in windows:
            for bench in BENCHMARKS:
                res = beta_r2(rets[sym], rets[bench], w)
                if res:
                    entry[f"{bench.lower()}_{w}d"] = res
        if entry:
            betas[sym] = entry

    # correlation clusters (non-benchmark, non-context names), main window
    cluster_names = [s for s in names if s not in CONTEXT_ETFS]
    corr_pairs: dict[tuple[str, str], float] = {}
    for i, a in enumerate(cluster_names):
        for b in cluster_names[i + 1:]:
            pairs, _ = _paired(rets[a], rets[b], main_window)
            c = pearson(pairs)
            if c is not None:
                corr_pairs[(a, b)] = c
    parent = {s: s for s in cluster_names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b), c in corr_pairs.items():
        if abs(c) >= CLUSTER_THRESHOLD:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    groups: dict[str, list[str]] = {}
    for s in cluster_names:
        groups.setdefault(find(s), []).append(s)
    clusters = [sorted(v) for v in groups.values() if len(v) > 1]
    clusters.sort(key=lambda v: (-len(v), v))

    top_pairs = sorted(
        ({"pair": f"{a}/{b}", "corr": round(c, 3)}
         for (a, b), c in corr_pairs.items()),
        key=lambda d: -abs(d["corr"]))[:10]

    # Lead-lag: one entry per unordered pair, direction taken from the sign of
    # the best lag (positive lag on (A, B) means A leads B). A link is only
    # reported when the best non-zero lag beats the contemporaneous correlation
    # in magnitude — otherwise the pair is same-day correlated, not lead-lag.
    links = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ll = lead_lag(rets[a], rets[b], window=main_window)
            if not ll or ll["best_lag"] == 0:
                continue
            if abs(ll["best_corr"]) < LEADLAG_MIN_CORR:
                continue
            if abs(ll["best_corr"]) <= abs(ll["contemporaneous"]):
                continue
            if ll["best_lag"] > 0:
                frm, to, lag = a, b, ll["best_lag"]
            else:
                frm, to, lag = b, a, -ll["best_lag"]
            links.append({"from": frm, "to": to, "lag_sessions": lag,
                          "corr": ll["best_corr"],
                          "contemporaneous_corr": ll["contemporaneous"]})
    links.sort(key=lambda d: -abs(d["corr"]))
    links = links[:15]

    return {
        "as_of": as_of,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Massive daily bars, split+dividend adjusted (massive_data.py cache)",
        "method": ("daily log returns; pairwise-complete common dates; "
                   f"windows {list(windows)} sessions; cluster threshold "
                   f"|corr| >= {CLUSTER_THRESHOLD} on {main_window}d; lead-lag "
                   f"searched over lags -{LEADLAG_MAX_LAG}..+{LEADLAG_MAX_LAG} "
                   f"on {main_window}d, min |corr| {LEADLAG_MIN_CORR}"),
        "symbols": sorted(closes),
        "betas": betas,
        "clusters": clusters,
        "top_correlated_pairs": top_pairs,
        "lead_lag_links": links,
        "caveat": ("Point-in-time statistics on data up to as_of only; samples "
                   "differ per pair where listing history is short (e.g. SKHY). "
                   "Correlations are descriptive, not causal, and decay."),
    }


def render_md(m: dict) -> str:
    lines = [f"# Relationship map — as of {m['as_of']}", "",
             f"Source: {m['source']}", f"Method: {m['method']}", "",
             "## Clusters (120d, |corr| >= 0.60)"]
    if m["clusters"]:
        for c in m["clusters"]:
            lines.append(f"- {' · '.join(c)}")
    else:
        lines.append("- none at threshold")
    lines += ["", "## Betas (120d vs SPY / QQQ)"]
    for sym, e in sorted(m["betas"].items()):
        s = e.get("spy_120d") or e.get("spy_60d") or {}
        q = e.get("qqq_120d") or e.get("qqq_60d") or {}
        lines.append(f"- **{sym}**: beta SPY {s.get('beta')} (R² {s.get('r2')}, n={s.get('n')})"
                     f" · beta QQQ {q.get('beta')} (R² {q.get('r2')}, n={q.get('n')})")
    lines += ["", "## Strongest correlated pairs (120d)"]
    for p in m["top_correlated_pairs"]:
        lines.append(f"- {p['pair']}: {p['corr']}")
    lines += ["", "## Lead-lag links (best non-zero lag, 120d)"]
    if m["lead_lag_links"]:
        for l in m["lead_lag_links"]:
            lines.append(f"- {l['from']} → {l['to']}: lag {l['lag_sessions']} session(s), "
                         f"corr {l['corr']} (contemporaneous {l['contemporaneous_corr']})")
    else:
        lines.append("- none clearing threshold")
    lines += ["", f"_{m['caveat']}_", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache-dir", type=pathlib.Path, required=True)
    ap.add_argument("--as-of", required=True, help="YYYY-MM-DD (point-in-time cutoff)")
    ap.add_argument("--out-json", type=pathlib.Path, required=True)
    ap.add_argument("--out-md", type=pathlib.Path, default=None)
    args = ap.parse_args()
    m = build(args.cache_dir, args.as_of)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(m, indent=2))
    if args.out_md:
        args.out_md.write_text(render_md(m))
    print(f"relationship map as_of={m['as_of']}: {len(m['symbols'])} symbols, "
          f"{len(m['clusters'])} clusters, {len(m['lead_lag_links'])} lead-lag links "
          f"-> {args.out_json}")


if __name__ == "__main__":
    main()
