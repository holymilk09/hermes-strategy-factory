from __future__ import annotations

import json
from datetime import date

import pytest

from src.research_intel.data import (
    INSUFFICIENT_DATA,
    OK,
    CacheStore,
    MemoryProvider,
    Series,
    aligned_returns,
    build_series,
    parse_robinhood_historicals,
)
from tests.research_intel.conftest import series_from_returns


# Shape copied from a real get_equity_historicals response (2026-10-08), values trimmed.
RH_PAYLOAD = {
    "data": {
        "results": [
            {
                "symbol": "MU",
                "interval": "day",
                "bounds": "regular",
                "bars": [
                    {"begins_at": "2026-10-05T00:00:00Z", "close_price": "1063.960000", "session": "reg"},
                    {"begins_at": "2026-10-06T00:00:00Z", "close_price": "1045.560000", "session": "reg"},
                    {"begins_at": "2026-10-06T00:00:00Z", "close_price": "1045.560000", "session": "reg"},
                    {"begins_at": "2026-10-07T00:00:00Z", "close_price": "1088.000000", "session": "reg",
                     "interpolated": True},
                    {"begins_at": "2026-10-08T00:00:00Z", "close_price": "1090.000000", "session": "reg"},
                ],
            }
        ]
    }
}


def test_robinhood_import_drops_interpolated_and_unsettled():
    [s] = parse_robinhood_historicals(RH_PAYLOAD, settled_through=date(2026, 10, 7))
    assert s.symbol == "MU"
    assert s.source == "robinhood:split"
    # 10-07 is interpolated (dropped), 10-08 is after settled_through (dropped), dup 10-06 collapsed
    assert s.dates == (date(2026, 10, 5), date(2026, 10, 6))
    assert s.closes == (1063.96, 1045.56)


def test_robinhood_import_accepts_json_string():
    [s] = parse_robinhood_historicals(json.dumps(RH_PAYLOAD), settled_through=date(2026, 10, 8))
    assert s.last_date == date(2026, 10, 8)


def test_robinhood_import_rejects_intraday():
    bad = {"data": {"results": [{"symbol": "MU", "interval": "hour", "bars": []}]}}
    with pytest.raises(ValueError, match="daily"):
        parse_robinhood_historicals(bad, settled_through=date(2026, 10, 8))


def test_build_series_rejects_conflicting_duplicates():
    with pytest.raises(ValueError, match="conflicting"):
        build_series("X", [(date(2026, 1, 5), 1.0), (date(2026, 1, 5), 2.0)], "t")


def test_series_rejects_nonpositive_close():
    with pytest.raises(ValueError):
        Series("X", (date(2026, 1, 5),), (0.0,))


def test_cache_roundtrip_and_refuses_history_rewrite(tmp_path):
    store = CacheStore(tmp_path)
    s = build_series("AAA", [(date(2026, 1, 5), 10.0), (date(2026, 1, 6), 11.0)], "t")
    store.write(s)
    assert store.series("AAA").closes == (10.0, 11.0)
    # appending new history is fine
    store.write(build_series("AAA", [(date(2026, 1, 7), 12.0)], "t"))
    assert store.series("AAA").closes == (10.0, 11.0, 12.0)
    # changing a settled close is refused
    with pytest.raises(ValueError, match="refusing"):
        store.write(build_series("AAA", [(date(2026, 1, 6), 11.5)], "t"))
    assert store.symbols() == ["AAA"]


def _provider(calendar, drop=None):
    n = 30
    days = calendar[: n + 1]
    spy = series_from_returns("SPY", days, [0.001] * n)
    aaa_days = [d for d in days if d not in (drop or [])]
    aaa = Series("AAA", tuple(aaa_days), tuple(100.0 + i for i in range(len(aaa_days))), "t")
    return MemoryProvider([spy, aaa]), days


def test_aligned_returns_ok(calendar):
    p, days = _provider(calendar)
    w = aligned_returns(p, ["AAA", "SPY"], days[-1], 20)
    assert w.status == OK
    assert w.n == 20
    assert len(w.returns["AAA"]) == 20
    assert w.sessions[-1] == days[-1]


def test_gap_blocks_instead_of_sliding(calendar):
    p, days = _provider(calendar, drop=[calendar[25]])
    w = aligned_returns(p, ["AAA"], days[-1], 20)
    assert w.status == INSUFFICIENT_DATA
    assert w.missing["AAA"] == (calendar[25],)
    assert "AAA" not in w.returns


def test_gap_outside_window_is_fine(calendar):
    p, days = _provider(calendar, drop=[calendar[2]])
    w = aligned_returns(p, ["AAA"], days[-1], 20)
    assert w.status == OK


def test_as_of_must_be_a_reference_session(calendar):
    p, days = _provider(calendar)
    saturday = date(2026, 1, 10)
    assert saturday.weekday() == 5
    w = aligned_returns(p, ["AAA"], saturday, 3)
    assert w.status == INSUFFICIENT_DATA
    assert "not a reference session" in w.reason


def test_unknown_symbol_is_insufficient(calendar):
    p, days = _provider(calendar)
    w = aligned_returns(p, ["ZZZ"], days[-1], 5)
    assert w.status == INSUFFICIENT_DATA
    assert "ZZZ" in w.missing


def test_point_in_time_ignores_future_bars(calendar):
    p, days = _provider(calendar)
    as_of = days[20]
    w = aligned_returns(p, ["AAA"], as_of, 10)
    assert w.status == OK
    assert max(w.sessions) == as_of


def _quote(sym, d, price, adj=None, interp=False):
    return {"quote": {"symbol": sym, "previous_close": str(price), "adjusted_previous_close": str(adj or price)},
            "close": {"symbol": sym, "date": d, "price": str(price), "interpolated": interp}}


def test_quotes_parser_accepts_only_clean_settled_closes():
    from src.research_intel.data import parse_robinhood_quotes
    ok = {"data": {"results": [_quote("SPY", "2026-10-08", 773.93)]}}
    assert parse_robinhood_quotes(ok, date(2026, 10, 8)) == [("SPY", date(2026, 10, 8), 773.93)]
    for bad in (_quote("SPY", "2026-10-07", 1.0), _quote("SPY", "2026-10-08", 1.0, adj=0.5),
                _quote("SPY", "2026-10-08", 1.0, interp=True)):
        with pytest.raises(ValueError):
            parse_robinhood_quotes({"data": {"results": [bad]}}, date(2026, 10, 8))
