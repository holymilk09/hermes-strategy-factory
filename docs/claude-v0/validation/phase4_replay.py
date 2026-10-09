#!/usr/bin/env python3
"""Phase 4 — replayed output audit (VALIDATION_PLAN.md §6).

Replays the daily brief for 20 consecutive settled sessions and checks, automatically:
  - every number in the text equals a value in that brief's JSON (no invented numbers)
  - zero buy/sell language outside the disclaimer
  - each name's block stays short enough for a phone (<= 8 non-blank lines)
Writes every replayed brief (JSON + markdown) to cache/research_intel/validation/replay/.
"""
from __future__ import annotations

import json
import re
from datetime import date

from common import OUT, ROOT, calendar, store
from src.research_intel.brief import build_brief, render_brief_md
from src.research_intel.data import MemoryProvider
from src.research_intel.events import EventCalendar
from src.research_intel.interest import Profile

FORBIDDEN = ("buy ", "sell ", "strong buy", "guaranteed", "you should", "price target", "load up",
             "take profit", "stop loss")
NUM = re.compile(r"(?<![A-Za-z])[+-]?\d+(?:\.\d+)?")
MAX_LINES = 8


def numeric_leaves(x, acc):
    if isinstance(x, bool):
        return
    if isinstance(x, (int, float)):
        acc.add(float(x))
    elif isinstance(x, dict):
        for v in x.values():
            numeric_leaves(v, acc)
    elif isinstance(x, (list, tuple)):
        for v in x:
            numeric_leaves(v, acc)
    elif isinstance(x, str):
        for m in re.finditer(r"\d{4}-\d{2}-\d{2}", x):
            y, mo, d = m.group(0).split("-")
            acc.update({float(y), float(mo), float(d)})


def allowed(values):
    out = set()
    for v in values:
        for f in ("{:.0f}", "{:.1f}", "{:.2f}", "{:+.1f}", "{:+.2f}", "{:+.0f}"):
            for w in (v, abs(v)):
                out.add(f.format(w).lstrip("+"))
        if float(v).is_integer():
            out.add(str(int(v)))
        out.add(f"{v * 100:.0f}")          # percentages rendered from fractions (weights)
    return out


ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def check_text(text, vals, where, problems):
    ok = allowed(vals)
    for iso in ISO.findall(text):          # an ISO date must itself be a JSON date
        y, mo, d = (float(x) for x in iso.split("-"))
        if not {y, mo, d} <= vals:
            problems.append(f"{where}: date {iso} not traceable to JSON")
    text = ISO.sub(" ", text)
    for m in NUM.finditer(text):
        tok = m.group(0).lstrip("+")
        if tok not in ok and tok.lstrip("-") not in ok:
            problems.append(f"{where}: number {m.group(0)!r} not traceable to JSON in: {text[:120]}")


def main():
    st = store()
    p = MemoryProvider([st.series(s) for s in st.symbols()])
    fwd = EventCalendar.load(ROOT / "cache/research_intel/events/earnings_2026-10-08_31d.json",
                             date(2026, 10, 8), date(2026, 10, 8), date(2026, 11, 7))
    cal = calendar().merged(fwd)
    prof = Profile.from_dict(json.loads((ROOT / "docs/claude-v0/examples/demo_profile.json").read_text())
                             | {"pins": ["JPM", "HON", "MSFT", "UNH"]})
    days = list(st.series("SPY").dates)[-20:]
    rdir = OUT / "replay"
    rdir.mkdir(parents=True, exist_ok=True)
    problems, stats = [], {"briefs": 0, "items": 0, "guidance_lines": 0, "alerts": 0, "flags": 0,
                           "max_item_lines": 0, "headline_kinds": {}}
    for d in days:
        b = build_brief(p, prof, d, cal)
        md = render_brief_md(b)
        (rdir / f"brief_{d}.json").write_text(json.dumps(b, indent=1, default=str))
        (rdir / f"brief_{d}.md").write_text(md)
        stats["briefs"] += 1
        body = md.replace(b["disclaimer"], "").lower()
        for f in FORBIDDEN:
            if f in body:
                problems.append(f"{d}: forbidden phrase {f!r}")
        top_vals = set()
        numeric_leaves({k: v for k, v in b.items() if k not in ("items",)}, top_vals)
        for it in b["items"]:
            stats["items"] += 1
            vals = set(top_vals)
            numeric_leaves(it, vals)
            for g in it["notes"]:
                stats["guidance_lines"] += 1
                check_text(g, vals, f"{d} {it['symbol']}", problems)
            stats["alerts"] += it["move"]["status"] == "ALERT"
            stats["flags"] += len(it["flags"])
        all_vals = set(top_vals)
        for it in b["items"]:
            numeric_leaves(it, all_vals)
        for h in b["headline"]:
            check_text(h, all_vals, f"{d} headline", problems)
            k = h.split(":")[1].split()[0] if ":" in h else h.split()[0]
            stats["headline_kinds"][k] = stats["headline_kinds"].get(k, 0) + 1
        for block in md.split("\n### ")[1:]:
            block = block.split("\n## ")[0].split("\n---")[0]
            n = sum(1 for ln in block.splitlines() if ln.strip())
            stats["max_item_lines"] = max(stats["max_item_lines"], n)
            if n > MAX_LINES:
                problems.append(f"{d}: item {block.splitlines()[0]!r} has {n} lines (> {MAX_LINES})")
        # rendered markdown numbers must also be traceable
        check_text(md.split("## Names")[0].replace(b["disclaimer"], ""), all_vals, f"{d} md-top", problems)
    res = {"sessions": [days[0].isoformat(), days[-1].isoformat()], "stats": stats,
           "problems": problems, "pass": not problems}
    (OUT / "phase4.json").write_text(json.dumps(res, indent=1))
    print("4", "PASS" if not problems else "FAIL", json.dumps(stats))
    for pr in problems[:25]:
        print("  ", pr)


if __name__ == "__main__":
    main()
