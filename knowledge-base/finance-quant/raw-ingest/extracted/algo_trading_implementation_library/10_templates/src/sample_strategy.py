from __future__ import annotations

from datetime import datetime
import pandas as pd
from .contracts import Signal


def prepare_features(bars: pd.DataFrame, fast_ma: int, slow_ma: int, pullback_window: int) -> pd.DataFrame:
    '''Prepare simple trend + pullback features.

    bars columns: timestamp, symbol, open, high, low, close, volume
    '''
    df = bars.sort_values(["symbol", "timestamp"]).copy()
    g = df.groupby("symbol", group_keys=False)
    df["fast_ma"] = g["close"].transform(lambda s: s.rolling(fast_ma).mean())
    df["slow_ma"] = g["close"].transform(lambda s: s.rolling(slow_ma).mean())
    df["pullback"] = g["close"].transform(lambda s: s / s.rolling(pullback_window).max() - 1)
    df["trend_positive"] = df["fast_ma"] > df["slow_ma"]
    return df


def generate_signals(features: pd.DataFrame, run_id: str, strategy_id: str, min_score: float) -> list[Signal]:
    signals: list[Signal] = []
    latest = features.sort_values("timestamp").groupby("symbol").tail(1)
    for row in latest.itertuples(index=False):
        if pd.isna(row.fast_ma) or pd.isna(row.slow_ma):
            continue
        score = 0.0
        reasons = []
        if row.trend_positive:
            score += 0.3
            reasons.append("trend_positive")
        if row.pullback < -0.01:
            score += 0.2
            reasons.append("short_pullback")
        direction = "long" if score >= min_score else "flat"
        signals.append(Signal(
            run_id=run_id,
            strategy_id=strategy_id,
            symbol=row.symbol,
            timestamp=pd.Timestamp(row.timestamp).to_pydatetime(),
            direction=direction,
            score=score,
            confidence=min(1.0, max(0.0, score)),
            horizon="5 bars",
            reason_codes=reasons,
        ))
    return signals
