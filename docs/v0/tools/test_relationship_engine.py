#!/usr/bin/env python3
"""
Tests for massive_data.py and relationship_engine.py (built 2026-10-17).
Software-correctness fixtures only — market conclusions come from real data
(the engine's output on the real Massive cache was additionally verified
against an independent numpy/pandas computation, 2026-10-17).

Run:  python -m pytest docs/v0/tools/test_relationship_engine.py -q
"""
from __future__ import annotations

import csv
import importlib.util
import math
import pathlib

HERE = pathlib.Path(__file__).parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


md = _load("massive_data", "massive_data.py")
eng = _load("relationship_engine", "relationship_engine.py")


def test_bar_date_is_eastern_session_date():
    # Timestamp returned by Massive for the Fri 2026-10-16 SPY bar (prev call).
    assert md.bar_date(1792180800000) == "2026-10-16"


def _write(cache: pathlib.Path, sym: str, dates: list[str], closes: list[float]):
    cache.mkdir(parents=True, exist_ok=True)
    with open(cache / f"{sym}.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        for d, c in zip(dates, closes):
            w.writerow([d, c, c, c, c, 1000])


def _dates(n: int) -> list[str]:
    # business days from 2026-01-05 (a Monday); holidays irrelevant for fixtures
    out, d = [], __import__("datetime").date(2026, 1, 5)
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += __import__("datetime").timedelta(days=1)
    return out


def test_beta_of_doubled_benchmark_is_two(tmp_path):
    dates = _dates(90)
    bench = [100.0]
    for i in range(1, 90):
        bench.append(bench[-1] * math.exp(0.001 * math.sin(i * 1.7) + 0.0005))
    asset = [100.0]
    for i in range(1, 90):
        r_b = math.log(bench[i] / bench[i - 1])
        asset.append(asset[-1] * math.exp(2.0 * r_b))
    _write(tmp_path, "SPY", dates, bench)
    _write(tmp_path, "QQQ", dates, bench)
    _write(tmp_path, "AAA", dates, asset)
    m = eng.build(tmp_path, as_of=dates[-1], windows=(60,))
    b = m["betas"]["AAA"]["spy_60d"]
    assert abs(b["beta"] - 2.0) < 0.01
    assert b["r2"] > 0.999


def test_lead_lag_detects_one_session_lead(tmp_path):
    dates = _dates(90)
    base = [100.0]
    for i in range(1, 90):
        base.append(base[-1] * math.exp(0.01 * math.sin(i * 2.3)))
    follower = [100.0, 100.0]  # follower repeats leader's previous return
    for i in range(2, 90):
        follower.append(follower[-1] * (base[i - 1] / base[i - 2]))
    _write(tmp_path, "SPY", dates, base)
    _write(tmp_path, "QQQ", dates, base)
    _write(tmp_path, "LEAD", dates, base)
    _write(tmp_path, "FOLL", dates, follower)
    m = eng.build(tmp_path, as_of=dates[-1], windows=(60,))
    links = {(l["from"], l["to"]): l for l in m["lead_lag_links"]}
    assert ("LEAD", "FOLL") in links
    assert links[("LEAD", "FOLL")]["lag_sessions"] == 1
    assert links[("LEAD", "FOLL")]["corr"] > 0.99


def test_point_in_time_cutoff(tmp_path):
    dates = _dates(90)
    calm = [100.0 + 0.01 * i for i in range(90)]
    wild = list(calm)
    for i in range(70, 90):  # chaos only after the cutoff
        wild[i] = wild[i - 1] * (1.5 if i % 2 else 0.6)
    _write(tmp_path, "SPY", dates, calm)
    _write(tmp_path, "QQQ", dates, calm)
    _write(tmp_path, "AAA", dates, wild)
    early = eng.build(tmp_path, as_of=dates[60], windows=(60,))
    # with data through dates[60] only, AAA tracks SPY almost perfectly
    assert early["betas"]["AAA"]["spy_60d"]["r2"] > 0.99


# --- massive_data pull retry (F6 fix, 2026-11-02) ---

class _Args:
    symbols = ["AAA", "BBB"]
    universe_file = None
    from_date = "2026-01-01"
    to_date = "2026-01-31"
    out = "."


def _no_sleep(_s):
    pass


def test_pull_retries_transient_failure(monkeypatch):
    calls = {"AAA": 0}
    def flaky(sym, _f, _t):
        if sym == "AAA":
            calls["AAA"] += 1
            if calls["AAA"] < 3:
                raise RuntimeError("connection reset")
            return [{"x": 1}]
        return [{"x": 1}]
    monkeypatch.setattr(md, "fetch_aggs", flaky)
    monkeypatch.setattr(md, "write_cache", lambda *_a: 1)
    monkeypatch.setattr(md.time, "sleep", _no_sleep)
    assert md.cmd_pull(_Args()) == 0
    assert calls["AAA"] == 3


def test_pull_never_retries_429_and_stops(monkeypatch):
    seen = []
    def limited(sym, _f, _t):
        seen.append(sym)
        raise RuntimeError("HTTP 429 too many requests")
    monkeypatch.setattr(md, "fetch_aggs", limited)
    monkeypatch.setattr(md, "write_cache", lambda *_a: 1)
    monkeypatch.setattr(md.time, "sleep", _no_sleep)
    assert md.cmd_pull(_Args()) == 1
    assert seen == ["AAA"]  # one attempt only, run stops before BBB
