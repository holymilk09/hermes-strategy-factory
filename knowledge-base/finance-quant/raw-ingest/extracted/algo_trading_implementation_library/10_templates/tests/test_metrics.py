import pandas as pd
from src.sample_metrics import max_drawdown, sharpe_ratio, profit_factor, expectancy


def test_max_drawdown_known_path():
    equity = pd.Series([100, 110, 105, 120, 90, 95])
    assert round(max_drawdown(equity), 4) == -0.25


def test_profit_factor():
    trades = pd.DataFrame({"pnl": [10, -5, 20, -5]})
    assert profit_factor(trades) == 3.0


def test_expectancy():
    trades = pd.DataFrame({"pnl": [10, -5, 20, -5]})
    assert expectancy(trades) == 5.0
