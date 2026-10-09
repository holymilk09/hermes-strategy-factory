from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.research_intel.data import INSUFFICIENT_DATA, OK, MemoryProvider
from src.research_intel.interest import Profile
from src.research_intel.relationships import ClusterMap
from src.research_intel.risk import risk_panel
from src.research_intel.scoreboard import score, scoreboard
from tests.research_intel.conftest import business_days, series_from_returns

N = 300


def _world(calendar, rng):
    from datetime import date
    days = business_days(date(2025, 6, 2), N + 1)      # the shared fixture is too short for a 250+20 lookback
    n = N
    m = rng.normal(0.0004, 0.01, n)
    s = {"SPY": m, "QQQ": 1.1 * m, "AAA": 1.5 * m + rng.normal(0, 0.01, n), "BBB": 0.5 * m + rng.normal(0, 0.006, n),
         "CCC": rng.normal(0, 0.02, n)}
    prov = MemoryProvider([series_from_returns(k, days, v) for k, v in s.items()])
    return prov, days, {k: np.array(v) for k, v in s.items()}


def test_risk_panel_matches_pandas(calendar, rng):
    p, days, rets = _world(calendar, rng)
    prof = Profile.from_dict({"holdings": [{"symbol": "AAA", "weight": 0.5}, {"symbol": "BBB", "weight": 0.3},
                                           {"symbol": "CCC", "weight": 0.2}]})
    rp = risk_panel(p, ClusterMap({}), prof, days[-1], window=250, floor=60)
    assert rp.status == OK and rp.window_n == 250 and rp.sample == "FULL"
    w = {"AAA": 0.5, "BBB": 0.3, "CCC": 0.2}
    df = pd.DataFrame({k: rets[k][-250:] for k in ("AAA", "BBB", "CCC", "SPY", "QQQ")})
    book = sum(w[k] * df[k] for k in w)
    assert rp.vol_60d_ann_pp == pytest.approx(book[-60:].std(ddof=1) * np.sqrt(252) * 100, rel=1e-9)
    assert rp.vol_20d_ann_pp == pytest.approx(book[-20:].std(ddof=1) * np.sqrt(252) * 100, rel=1e-9)
    b = np.polyfit(df["SPY"][-60:], book[-60:], 1)[0]
    assert rp.beta_spy_60d == pytest.approx(b, abs=1e-9)
    assert rp.hhi == pytest.approx(0.25 + 0.09 + 0.04) and rp.effective_n == pytest.approx(1 / 0.38, abs=1e-3)
    c = df[["AAA", "BBB", "CCC"]][-60:].corr().values
    assert rp.avg_pairwise_corr_60d == pytest.approx((c[0, 1] + c[0, 2] + c[1, 2]) / 3, abs=1e-3)
    losses = -book
    assert rp.var_95_pp == pytest.approx(np.quantile(losses, 0.95) * 100, abs=1e-3)
    assert rp.var_99_pp == pytest.approx(np.quantile(losses, 0.99) * 100, abs=1e-3)
    level = (1 + book).cumprod()
    assert rp.max_drawdown_pp == pytest.approx((level / level.cummax() - 1).min() * 100, abs=1e-3)
    assert sum(rp.risk_contribution.values()) == pytest.approx(1.0, abs=1e-6)
    assert rp.worst_day_pp == pytest.approx(book.min() * 100, abs=1e-3)


def test_risk_panel_excludes_short_history_name(calendar, rng):
    p, days, _ = _world(calendar, rng)
    short = series_from_returns("NEW", days[-30:], [0.001] * 29)
    p2 = MemoryProvider([p.series(s) for s in p.symbols()] + [short])
    prof = Profile.from_dict({"holdings": [{"symbol": "AAA", "weight": 0.5}, {"symbol": "NEW", "weight": 0.5}]})
    rp = risk_panel(p2, ClusterMap({}), prof, days[-1])
    assert rp.status == OK and "NEW" in rp.excluded and rp.weights == {"AAA": 1.0}
    assert rp.weight_covered == pytest.approx(0.5)


def test_risk_panel_empty_and_insufficient(calendar, rng):
    p, days, _ = _world(calendar, rng)
    assert risk_panel(p, ClusterMap({}), Profile(), days[-1]).status == INSUFFICIENT_DATA
    prof = Profile.from_dict({"holdings": [{"symbol": "ZZZ", "weight": 1.0}]})
    assert risk_panel(p, ClusterMap({}), prof, days[-1]).status == INSUFFICIENT_DATA


def test_scoreboard_matches_pandas(calendar, rng):
    p, days, rets = _world(calendar, rng)
    r = score(p, "AAA", days[-1])
    assert r.status == OK and r.history_n == 270
    a, m = pd.Series(rets["AAA"][-270:]), pd.Series(rets["SPY"][-270:])
    assert r.ret_20_pp == pytest.approx(((1 + a[-20:]).prod() - 1) * 100, abs=1e-3)
    assert r.excess_60_pp == pytest.approx((((1 + a[-60:]).prod() - 1) - ((1 + m[-60:]).prod() - 1)) * 100, abs=1e-3)
    assert r.vol_20d_ann_pp == pytest.approx(a[-20:].std(ddof=1) * np.sqrt(252) * 100, abs=1e-3)
    rets20 = (1 + a).rolling(20).apply(np.prod, raw=True).dropna() - 1
    hist = rets20[:-1]
    assert r.ext_z == pytest.approx((rets20.iloc[-1] - hist.mean()) / hist.std(ddof=1), abs=1e-3)
    assert r.relative_strength in ("LEADING", "LAGGING", "MIXED")
    assert r.extension in ("NORMAL", "STRETCHED_UP", "STRETCHED_DOWN")
    sb = scoreboard(p, ["AAA", "BBB", "CCC", "ZZZ"], days[-1])
    assert [x["symbol"] for x in sb["rows"]][-1] == "ZZZ" and sb["rows"][-1]["status"] == INSUFFICIENT_DATA
    ex = [x["excess_60_pp"] for x in sb["rows"][:-1]]
    assert ex == sorted(ex, reverse=True)


def test_scoreboard_short_history_has_no_percentiles(calendar, rng):
    p, days, _ = _world(calendar, rng)
    r = score(p, "AAA", days[150])
    assert r.status == OK and r.ext_z is None and r.extension == "NOT_AVAILABLE"
