"""
Regime Features — market state detection for gating strategies.

Produces features that classify the current regime:
  - Trend regime (bull/bear/sideways)
  - Volatility regime (low/normal/high/crash)
  - Breadth / participation
  - Momentum regime
"""
import numpy as np
from feature_factory.technical import rolling_mean, rolling_std, rolling_min, rolling_max


def compute_regime_features(df, config: dict) -> dict:
    """
    Compute regime classification features.

    Returns dict: {feature_name: np.array}
    """
    closes = df['close']
    returns = df['returns']
    highs = df['high']
    lows = df['low']
    n = len(closes)
    features = {}

    # ── SMA Alignment ──
    sma20 = rolling_mean(closes, 20)
    sma50 = rolling_mean(closes, 50)
    sma200 = rolling_mean(closes, 200)

    features["sma20_50_alignment"] = np.where((sma20 > sma50) & (sma50 > sma200) & (closes > sma20), 3,
                                       np.where((sma20 > sma50) & (closes > sma20), 2,
                                       np.where(closes > sma200, 1, 0)))

    # ── Trend Strength ──
    # Slope of 50-day SMA
    sma50_shift = np.roll(sma50, 10)
    sma50_shift[:10] = np.nan
    with np.errstate(divide='ignore', invalid='ignore'):
        features["trend_strength"] = np.where(sma50_shift > 0, (sma50 - sma50_shift) / sma50_shift, np.nan)

    # ── Regime Score (0-3) ──
    # Factor 1: Price above 50 SMA
    f1 = np.where(closes > sma50, 1.0, 0.0)
    # Factor 2: Price above 200 SMA
    f2 = np.where(closes > sma200, 1.0, 0.0)
    # Factor 3: Low vol (vol < 2.5% daily)
    vol20 = np.full(n, np.nan)
    for i in range(20, n):
        vol20[i] = np.nanstd(returns[i - 19:i + 1])
    f3 = np.where(vol20 < 0.025, 1.0, 0.0)

    features["regime_score"] = f1 + f2 + f3
    features["vol_regime"] = np.where(vol20 < 0.01, "low",
                                np.where(vol20 < 0.025, "normal",
                                np.where(vol20 < 0.04, "high", "crash")))

    # ── Breadth proxy: consecutive closes above 20 SMA ──
    above_sma20 = np.where(closes > sma20, 1, 0)
    features["breadth_sma20"] = _rolling_sum(above_sma20.astype(float), 10)

    # ── Higher Highs / Lower Lows ──
    features["hh_ll_20d"] = _hh_ll(highs, lows, 20)

    # ── ADX proxy (trend vs range) ──
    features["adx_proxy_14"] = _adx_proxy(highs, lows, closes, 14)

    # ── Volatility expansion ──
    # Ratio of current vol to 3-month average vol
    for i in range(60, n):
        if vol20[i] > 0:
            features.setdefault("vol_expansion", np.full(n, np.nan))
            avg_vol_3m = np.nanmean(vol20[max(0, i - 60):i + 1])
            if avg_vol_3m > 0:
                features["vol_expansion"][i] = vol20[i] / avg_vol_3m

    # ── Distance from 52-week high / low ──
    for i in range(252, n):
        high_52w = np.nanmax(highs[max(0, i - 252):i + 1])
        low_52w = np.nanmin(lows[max(0, i - 252):i + 1])
        features.setdefault("dist_52w_high", np.full(n, np.nan))
        features.setdefault("dist_52w_low", np.full(n, np.nan))
        if high_52w > 0:
            features["dist_52w_high"][i] = closes[i] / high_52w
        if low_52w > 0:
            features["dist_52w_low"][i] = closes[i] / low_52w

    return features


def _rolling_sum(arr: np.ndarray, window: int) -> np.ndarray:
    n = len(arr)
    result = np.full(n, np.nan)
    if n < window:
        return result
    cumsum = np.cumsum(np.nan_to_num(arr, 0))
    result[window - 1] = cumsum[window - 1]
    result[window:] = cumsum[window:] - cumsum[:-window]
    return result


def _hh_ll(highs: np.ndarray, lows: np.ndarray, window: int) -> np.ndarray:
    """HH/LL score: 2=HH+HL, 1=HH or HL, 0=neither, -1=LL, -2=LH+LL."""
    n = len(highs)
    result = np.full(n, np.nan)
    if n < window + 1:
        return result

    for i in range(window, n):
        prev_high = np.nanmax(highs[i - window:i])
        prev_low = np.nanmin(lows[i - window:i])
        score = 0
        if highs[i] > prev_high:
            score += 1
        if lows[i] > prev_low:
            score += 1
        if highs[i] < prev_high:
            score -= 1
        if lows[i] < prev_low:
            score -= 1
        result[i] = score
    return result


def _adx_proxy(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int) -> np.ndarray:
    """Simplified ADX proxy: measures trend strength."""
    n = len(highs)
    result = np.full(n, np.nan)
    if n < period + 1:
        return result

    tr = np.zeros(n)
    plus_dm = np.zeros(n)
    minus_dm = np.zeros(n)
    for i in range(1, n):
        tr[i] = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        up = highs[i] - highs[i - 1]
        down = lows[i - 1] - lows[i]
        plus_dm[i] = up if up > down and up > 0 else 0
        minus_dm[i] = down if down > up and down > 0 else 0

    atr = np.full(n, np.nan)
    atr[period] = np.nanmean(tr[1:period + 1])
    for i in range(period + 1, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period

    di_plus = np.full(n, np.nan)
    di_minus = np.full(n, np.nan)
    for i in range(period, n):
        avg_pdm = np.nanmean(plus_dm[i - period + 1:i + 1])
        avg_mdm = np.nanmean(minus_dm[i - period + 1:i + 1])
        if atr[i] > 0:
            di_plus[i] = (avg_pdm / atr[i]) * 100
            di_minus[i] = (avg_mdm / atr[i]) * 100
        if (di_plus[i] + di_minus[i]) > 0:
            result[i] = abs(di_plus[i] - di_minus[i]) / (di_plus[i] + di_minus[i]) * 100

    return result
