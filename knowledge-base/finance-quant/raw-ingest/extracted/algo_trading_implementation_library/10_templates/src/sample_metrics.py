from __future__ import annotations

import math
import numpy as np
import pandas as pd


def equity_to_returns(equity: pd.Series) -> pd.Series:
    return equity.pct_change().dropna()


def max_drawdown(equity: pd.Series) -> float:
    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    return float(drawdown.min())


def time_under_water(equity: pd.Series) -> float:
    running_max = equity.cummax()
    return float((equity < running_max).mean())


def annualized_volatility(returns: pd.Series, annualization: int = 252) -> float:
    return float(returns.std(ddof=1) * math.sqrt(annualization))


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, annualization: int = 252) -> float:
    if returns.empty:
        return float("nan")
    excess = returns - risk_free_rate / annualization
    vol = excess.std(ddof=1)
    if vol == 0 or np.isnan(vol):
        return float("nan")
    return float(excess.mean() / vol * math.sqrt(annualization))


def sortino_ratio(returns: pd.Series, threshold: float = 0.0, annualization: int = 252) -> float:
    downside = returns[returns < threshold] - threshold
    dd = downside.std(ddof=1)
    if dd == 0 or np.isnan(dd):
        return float("nan")
    return float((returns.mean() - threshold) / dd * math.sqrt(annualization))


def profit_factor(trades: pd.DataFrame) -> float:
    gross_profit = trades.loc[trades["pnl"] > 0, "pnl"].sum()
    gross_loss = trades.loc[trades["pnl"] < 0, "pnl"].sum()
    if gross_loss == 0:
        return float("inf")
    return float(gross_profit / abs(gross_loss))


def expectancy(trades: pd.DataFrame) -> float:
    if trades.empty:
        return float("nan")
    return float(trades["pnl"].mean())


def metric_pack(equity_df: pd.DataFrame, trades_df: pd.DataFrame) -> dict:
    equity = equity_df["equity"]
    returns = equity_to_returns(equity)
    years = max(len(returns) / 252, 1e-9)
    total_return = equity.iloc[-1] / equity.iloc[0] - 1
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1
    return {
        "total_return": float(total_return),
        "cagr": float(cagr),
        "annualized_volatility": annualized_volatility(returns),
        "sharpe": sharpe_ratio(returns),
        "sortino": sortino_ratio(returns),
        "max_drawdown": max_drawdown(equity),
        "time_under_water": time_under_water(equity),
        "trade_count": int(len(trades_df)),
        "profit_factor": profit_factor(trades_df),
        "expectancy": expectancy(trades_df),
    }
