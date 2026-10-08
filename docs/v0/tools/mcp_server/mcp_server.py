#!/usr/bin/env python3
"""
Strategy Factory MCP server — P1 prototype (research layer only).

Exposes read-only research tools over MCP (stdio). No execution, no broker,
no ledger writes. Signal tools are gated behind the forward-test verdict.

Tools:
  brief             interest-ranked research brief
  cohort_summary    resolved forward-observation record
  relationship_map  sector clusters / betas / lead-lag (status: pending data build)
  hypothesis_status forward-test state, bars, next resolution date
  scan_setups       GATED — returns gating reason until the hypothesis passes

Data sources (local, read-only):
  --forward-dir : forward observation ledgers (observations.csv, rejected.csv)
  --research-root : goal workspace (audit reports, QC docs)

Run:
  python mcp_server.py --forward-dir <dir> --research-root <dir>
Test with the MCP inspector or: python mcp_server.py --self-test
"""
from __future__ import annotations
import argparse, csv, json, pathlib, statistics, sys
from datetime import datetime, timezone

HYPOTHESIS = "momentum_continuation_ret5d_ma50_v1"
GATE_REASON = (
    "scan_setups is gated: hypothesis momentum_continuation_ret5d_ma50_v1 has not "
    "passed its preregistered success bars (>=30 resolved across >=3 dates, excess vs SPY > 0, "
    "hit rate >= 55%). Forward test in progress; see hypothesis_status."
)

def load_csv(path: pathlib.Path):
    if not path or not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def summarize_rows(rows):
    res = [r for r in rows if r.get("outcome_status") == "RESOLVED"]
    out = {"total": len(rows), "resolved": len(res), "pending": len(rows) - len(res)}
    if res:
        vals = [float(r["outcome_return_pp"]) for r in res if r.get("outcome_return_pp")]
        exc = [float(r["excess_vs_spy_pp"]) for r in res if r.get("excess_vs_spy_pp")]
        out.update({
            "mean_return_pp": round(statistics.mean(vals), 4),
            "median_return_pp": round(statistics.median(vals), 4),
            "hit_rate": f"{sum(v > 0 for v in vals)}/{len(vals)}",
            "mean_excess_vs_spy_pp": round(statistics.mean(exc), 4) if exc else None,
        })
    by_date = {}
    for r in rows:
        by_date.setdefault(r.get("signal_date", "?"), []).append(r)
    out["by_signal_date"] = {
        d: {"n": len(v), "resolved": sum(1 for x in v if x.get("outcome_status") == "RESOLVED")}
        for d, v in sorted(by_date.items())
    }
    return out

def rank_by_profile(items, profile):
    """Rank items by interest-profile weights. Each item: {symbols:[...], sectors:[...]}."""
    tickers = {t["symbol"]: t.get("weight", 1.0) for t in profile.get("tickers", [])}
    sectors = {s["sector"]: s.get("weight", 1.0) for s in profile.get("sectors", [])}
    holdings = {h["symbol"]: t_weight for h, t_weight in
                ((h, h.get("weight", 1.0)) for h in profile.get("holdings", []))}
    ranked = []
    for it in items:
        score, why = 0.0, []
        for s in it.get("symbols", []):
            if s in tickers:
                score += tickers[s]; why.append(f"ticker {s} in profile")
            if s in holdings:
                score += holdings[s]; why.append(f"holding {s} in profile")
        for s in it.get("sectors", []):
            if s in sectors:
                score += sectors[s]; why.append(f"sector {s} in profile")
        ranked.append({**it, "interest_score": round(score, 3), "why_shown": why or ["general research"]})
    ranked.sort(key=lambda x: -x["interest_score"])
    return ranked

class ResearchStore:
    def __init__(self, forward_dir: pathlib.Path, research_root: pathlib.Path):
        self.forward_dir = forward_dir
        self.research_root = research_root

    def observations(self):
        return load_csv(self.forward_dir / "observations.csv")

    def rejected(self):
        return load_csv(self.forward_dir / "rejected.csv")

    def brief_items(self):
        items = []
        for r in self.observations():
            items.append({
                "kind": "forward_observation",
                "symbols": [r["symbol"]], "sectors": [],
                "headline": f"{r['symbol']} selected {r['signal_date']} "
                            f"(ret_5d {float(r['ret_5d'])*100:+.2f}%, above ma50)",
                "status": r["outcome_status"],
                "outcome": (f"{r['outcome_return_pp']}%" if r["outcome_status"] == "RESOLVED" else "pending"),
                "evidence": "EXPLORATORY — forward observation, n small",
            })
        items.append({
            "kind": "audit_finding", "symbols": [], "sectors": [],
            "headline": "Matched-window audit: no consistent filter lift for the frozen lineage; "
                        "old +23.30pp lift claim retired",
            "status": "CODE VERIFIED",
            "evidence": "CODE VERIFIED — audit-2026-10-05",
        })
        return items

def make_server(store: ResearchStore):
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("strategy-factory-research")

    @mcp.tool()
    def brief(interest_profile: dict) -> dict:
        """Interest-ranked research brief. interest_profile: {tickers:[{symbol,weight}], sectors:[{sector,weight}], holdings:[{symbol,weight}]}. Ranking changes what is shown first, never what is true."""
        items = rank_by_profile(store.brief_items(), interest_profile or {})
        return {
            "as_of": datetime.now(timezone.utc).isoformat(),
            "evidence_note": "All items carry evidence labels; rankings are explainable via why_shown.",
            "items": items[:25],
        }

    @mcp.tool()
    def cohort_summary() -> dict:
        """Resolved forward-observation record with sample sizes and caveats."""
        return {
            "hypothesis": HYPOTHESIS,
            "selected": summarize_rows(store.observations()),
            "rejected_cohort": summarize_rows(store.rejected()),
            "caveat": "Forward observations are a research record, not a validated edge. "
                      "Do not present without sample sizes.",
        }

    @mcp.tool()
    def relationship_map() -> dict:
        """Sector clusters, betas, lead-lag linkages. Status: pending data build."""
        return {
            "status": "PLANNED — relationship engine data not yet built",
            "note": "Point-in-time correlations only when built; a decoupling is itself the signal.",
            "clusters": [], "betas": [], "lead_lag": [],
        }

    @mcp.tool()
    def hypothesis_status() -> dict:
        """Forward-test state: rule, bars, progress, next resolution date."""
        obs = store.observations()
        res = [r for r in obs if r.get("outcome_status") == "RESOLVED"]
        return {
            "hypothesis": HYPOTHESIS,
            "rule": "ret_5d > 0 AND close > ma50, complete-series only",
            "status": "EXPLORATORY — forward test in progress",
            "resolved": len(res), "pending": len(obs) - len(res),
            "target": ">=30 resolved across >=3 signal dates",
            "success_bars": "excess vs SPY > 0, hit rate >= 55%, selected > same-date rejected",
            "kill_bars": "excess vs SPY < -2pp or hit rate < 45% at n>=30",
            "signal_dates": sorted({r["signal_date"] for r in obs}),
        }

    @mcp.tool()
    def scan_setups() -> dict:
        """GATED. Returns the gating reason until the hypothesis passes its bars."""
        return {"gated": True, "reason": GATE_REASON, "see": "hypothesis_status"}

    return mcp

def self_test(store: ResearchStore):
    mcp = make_server(store)
    async def run():
        tools = await mcp.list_tools()
        names = [t.name for t in tools]
        print("tools:", names)
        assert {"brief", "cohort_summary", "relationship_map", "hypothesis_status", "scan_setups"} <= set(names)
        # call via direct function test on store logic
        s = store.brief_items()
        ranked = rank_by_profile(s, {"tickers": [{"symbol": "MU", "weight": 0.9}], "holdings": [{"symbol": "SKHY", "weight": 1.0}]})
        print("brief items:", len(ranked), "| top:", ranked[0]["headline"][:80] if ranked else None)
        print("cohort total:", len(store.observations()), "rejected:", len(store.rejected()))
        print("SELF-TEST OK")
    import asyncio
    asyncio.run(run())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forward-dir", type=pathlib.Path, required=True)
    ap.add_argument("--research-root", type=pathlib.Path, required=True)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    store = ResearchStore(args.forward_dir, args.research_root)
    if args.self_test:
        self_test(store)
        return
    make_server(store).run()

if __name__ == "__main__":
    main()
