"""Operator CLI for the research-intel products. Read-only over prices and ledgers.

  python -m src.research_intel.cli brief  --profile P.json [--events E.json --events-date D]
                                          [--as-of D] [--ledger-frozen F.csv]
                                          [--ledger-hyp S.csv --ledger-hyp-rejected R.csv] [--out DIR]
  python -m src.research_intel.cli alerts --profile P.json [--as-of D]
  python -m src.research_intel.cli weekly --profile P.json [--previous W.json] [--as-of D] [--out DIR]
  python -m src.research_intel.cli record [--ledger-frozen F.csv] [--ledger-hyp S.csv ...]
  python -m src.research_intel.cli report --profile P.json [--events ...] [--out DIR]   # brief + attribution + risk + scoreboard, md + html

--as-of defaults to the last settled SPY session in the cache.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import asdict
from datetime import date

from .brief import build_brief, render_brief_md
from .report import build_report, render_report_html, render_report_md
from .data import DEFAULT_REFERENCE, CacheStore
from .events import EventCalendar
from .interest import Profile, ranked_watchlist
from .moves import move_alerts
from .research_record import FROZEN_LINEAGE, HYPOTHESIS_V1, hypothesis_status, summarize
from .weekly import render_weekly_md, weekly_map

DEFAULT_CACHE = "cache/research_intel/ohlcv_v2"


def _records(a, as_of):
    out = [summarize(a.ledger_frozen, FROZEN_LINEAGE).to_dict(),
           summarize(a.ledger_hyp, HYPOTHESIS_V1).to_dict()]
    hs = asdict(hypothesis_status(a.ledger_hyp, a.ledger_hyp_rejected, as_of))
    return out, hs


def _write(out_dir, stem, payload, md):
    d = pathlib.Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{stem}.json").write_text(json.dumps(payload, indent=1, default=str) + "\n")
    (d / f"{stem}.md").write_text(md)
    print(f"wrote {d / (stem + '.json')} and {d / (stem + '.md')}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="research_intel")
    ap.add_argument("cmd", choices=["brief", "alerts", "weekly", "record", "report"])
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--profile")
    ap.add_argument("--as-of", type=date.fromisoformat)
    ap.add_argument("--events", action="append",
                    help="FILE:START:END — saved earnings calendar JSON and the date range it was "
                         "queried for (YYYY-MM-DD); repeatable")
    ap.add_argument("--events-date", type=date.fromisoformat)
    ap.add_argument("--previous")
    ap.add_argument("--ledger-frozen")
    ap.add_argument("--ledger-hyp")
    ap.add_argument("--ledger-hyp-rejected")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    store = CacheStore(a.cache)
    try:
        ref = store.series(DEFAULT_REFERENCE)
    except (FileNotFoundError, ValueError) as e:
        ap.error(f"cache {a.cache!r} has no usable {DEFAULT_REFERENCE} series ({e}); import data first")
    as_of = a.as_of or ref.last_date
    if as_of not in set(ref.dates):
        prior = ref.upto(as_of).last_date
        ap.error(f"{as_of} is not a settled trading session in the cache"
                 + (f"; the last one on or before it is {prior}" if prior else ""))
    for spec in a.events or []:
        if spec.count(":") < 2:
            ap.error(f"--events expects FILE:START:END, got {spec!r}")
    if a.profile and not pathlib.Path(a.profile).exists():
        ap.error(f"profile file not found: {a.profile}")

    if a.cmd == "record":
        recs, hs = _records(a, as_of)
        json.dump({"records": recs, "hypothesis": hs}, sys.stdout, indent=1, default=str)
        print()
        return 0
    if not a.profile:
        ap.error("--profile is required for " + a.cmd)
    profile = Profile.load(a.profile)

    if a.cmd == "alerts":
        syms = [w.symbol for w in ranked_watchlist(profile, as_of)]
        al = move_alerts(store, syms, as_of)
        json.dump([m.to_dict() for m in al], sys.stdout, indent=1)
        print()
        return 0
    if a.cmd == "brief":
        cal = None
        for spec in a.events or []:
            fp, start, end = spec.rsplit(":", 2)
            c = EventCalendar.load(fp, a.events_date or as_of,
                                   date.fromisoformat(start), date.fromisoformat(end))
            cal = c if cal is None else cal.merged(c)
        recs, _ = _records(a, as_of)
        b = build_brief(store, profile, as_of, cal, record=recs)
        md = render_brief_md(b)
        if a.out:
            _write(a.out, f"brief_{as_of.isoformat()}", b, md)
        else:
            sys.stdout.write(md)
        return 0
    if a.cmd == "report":
        cal = None
        for spec in a.events or []:
            fp, start, end = spec.rsplit(":", 2)
            c = EventCalendar.load(fp, a.events_date or as_of, date.fromisoformat(start), date.fromisoformat(end))
            cal = c if cal is None else cal.merged(c)
        recs, _ = _records(a, as_of)
        r = build_report(store, profile, as_of, cal, record=recs)
        md = render_report_md(r)
        if a.out:
            _write(a.out, f"report_{as_of.isoformat()}", r, md)
            pathlib.Path(a.out, f"report_{as_of.isoformat()}.html").write_text(render_report_html(r))
            print(f"wrote {pathlib.Path(a.out, f'report_{as_of.isoformat()}.html')}")
        else:
            sys.stdout.write(md)
        return 0
    if a.cmd == "weekly":
        prev = json.loads(pathlib.Path(a.previous).read_text()) if a.previous else None
        m = weekly_map(store, profile, as_of, prev)
        md = render_weekly_md(m)
        if a.out:
            _write(a.out, f"weekly_{as_of.isoformat()}", m, md)
        else:
            sys.stdout.write(md)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
