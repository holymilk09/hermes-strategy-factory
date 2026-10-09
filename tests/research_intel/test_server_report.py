"""Report renderers and the MCP server, exercised through a real stdio client."""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from src.research_intel.compliance import lint
from src.research_intel.data import CacheStore
from src.research_intel.interest import Profile
from src.research_intel.report import build_report, render_report_html, render_report_md
from src.research_intel.relationships import ClusterMap
from tests.research_intel.conftest import business_days, series_from_returns

ROOT = Path(__file__).resolve().parents[2]
N = 300


def _cache(tmp_path) -> tuple[CacheStore, list]:
    rng = np.random.default_rng(7)
    days = business_days(date(2025, 6, 2), N + 1)
    m = rng.normal(0.0004, 0.01, N)
    sx = rng.normal(0, 0.006, N)
    st = CacheStore(tmp_path / "cache")
    for sym, r in {"SPY": m, "QQQ": 1.1 * m, "XLK": 1.05 * m + sx, "SMH": 1.3 * m + 1.4 * sx,
                   "MU": 1.2 * m + 1.5 * sx + rng.normal(0, 0.01, N), "NVDA": 1.3 * m + sx + rng.normal(0, 0.012, N),
                   "LLY": 0.3 * m + rng.normal(0, 0.012, N), "JPM": 0.9 * m + rng.normal(0, 0.008, N)}.items():
        st.write(series_from_returns(sym, days, r, start_price=100.0))
    return st, days


PROFILE = {"holdings": [{"symbol": "MU", "shares": 10}, {"symbol": "LLY", "shares": 5}], "pins": ["JPM", "NVDA"]}


def test_report_md_and_html_render_clean(tmp_path):
    st, days = _cache(tmp_path)
    r = build_report(st, Profile.from_dict(PROFILE), days[-1])
    md = render_report_md(r)
    assert "## Book attribution" in md and "## Book risk" in md and "## Scoreboard" in md
    assert lint(md) == []
    page = render_report_html(r)
    assert page.startswith("<!doctype html>") and "viewport" in page and "<script" not in page
    assert lint(page) == []
    json.dumps(r)


async def _call(server_env, calls):
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client
    params = StdioServerParameters(command=sys.executable, args=["-m", "src.research_intel.server"],
                                   env={**os.environ, **server_env}, cwd=str(ROOT))
    out = []
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            out.append(sorted(t.name for t in tools.tools))
            for name, args in calls:
                res = await session.call_tool(name, args)
                if res.is_error:
                    payload = {"error": res.content[0].text}
                else:
                    payload = res.structured_content if getattr(res, "structured_content", None) else json.loads(res.content[0].text)
                out.append((name, res.is_error, payload))
    return out


def test_mcp_server_end_to_end(tmp_path):
    st, days = _cache(tmp_path)
    env = {"SF_CACHE": str(st.root), "SF_MODE": "self"}
    calls = [("data_status", {}), ("brief", {"profile": PROFILE}), ("report", {"profile": PROFILE}),
             ("attribution", {"profile": PROFILE}), ("risk", {"profile": PROFILE}),
             ("scoreboard", {"symbols": ["MU", "NVDA", "ZZZ"]}), ("relationship_map", {"symbols": ["MU", "NVDA"]}),
             ("hypothesis_status", {}), ("cohort_summary", {}), ("brief", {"profile": PROFILE, "as_of": "2020-01-04"})]
    out = asyncio.run(asyncio.wait_for(_call(env, calls), 120))
    names = out[0]
    assert {"brief", "report", "attribution", "risk", "scoreboard", "relationship_map",
            "hypothesis_status", "cohort_summary", "data_status"} <= set(names)
    results = {}
    for name, is_err, payload in out[1:]:
        results.setdefault(name, []).append((is_err, payload))
    ds = results["data_status"][0][1]
    assert ds["settled_through"] == days[-1].isoformat() and ds["mode"] == "self" and ds["sent_to_broker"] is False
    b = results["brief"][0][1]
    assert b["as_of"] == days[-1].isoformat() and "disclosure" in b and "data_provenance" in b
    assert "markdown" in results["report"][0][1]
    assert results["attribution"][0][1]["totals_pp"] and results["risk"][0][1]["status"] == "OK"
    assert results["scoreboard"][0][1]["rows"][-1]["symbol"] == "ZZZ"
    assert results["hypothesis_status"][0][1]["verdict"].startswith("PENDING")
    assert results["cohort_summary"][0][1]["records"][0]["status"] == "NOT_LOADED"
    is_err, payload = results["brief"][1]
    assert is_err and "not a settled session" in json.dumps(payload)


def test_customer_mode_refuses_personal_use_data(tmp_path):
    st, days = _cache(tmp_path)
    # relabel the synthetic data as Robinhood-sourced
    for p in st.root.glob("*_1D.csv"):
        p.write_text(p.read_text().replace(",synthetic", ",robinhood:split"))
    r = subprocess.run([sys.executable, "-m", "src.research_intel.server"], cwd=ROOT, capture_output=True, text=True,
                       env={**os.environ, "SF_CACHE": str(st.root), "SF_MODE": "customer"}, timeout=60)
    assert r.returncode == 2 and "may not be distributed to customers" in r.stderr


def test_customer_mode_requires_disclosure(tmp_path):
    st, days = _cache(tmp_path)        # synthetic = redistributable, but disclosure is unconfigured
    r = subprocess.run([sys.executable, "-m", "src.research_intel.server"], cwd=ROOT, capture_output=True, text=True,
                       env={**os.environ, "SF_CACHE": str(st.root), "SF_MODE": "customer"}, timeout=60)
    assert r.returncode == 2 and "operator disclosure" in r.stderr
