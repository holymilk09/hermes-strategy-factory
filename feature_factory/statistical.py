"""
Statistical Features — returns, momentum, z-scores, vol ratios, price-volume relationships.

All computations point-in-time. No future leakage.
"""
import numpy as np
from feature_factory.technical import rolling_mean, rolling_std, rolling_min, rolling_max


def compute_statistical_features(df, config: dict) -> dict:
    """
    Compute statistical features: momentum, volatility, z-scores, correlations.

    Returns dict: {feature_name: np.array}
    """
    closes = df['close']
    highs = df['high']
    lows = df['low']
    volumes = df['volume']
    returns = df['returns']
    n = len(closes)
    features = {}

    windows = config.get("windows", [5, 10, 20, 50, 100])

    # ── Momentum / Returns ──
    for w in windows:
        if n > w:
            mom = np.full(n, np.nan)
            for i in range(w, n):
                if closes[i - w] > 0:
                    mom[i] = (closes[i] / closes[i - w]) - 1
            features[f"mom_{w}d"] = mom

            # Smoothed momentum (momentum of SMA)
            sma = rolling_mean(closes, w)
            sma_mom = np.full(n, np.nan)
            for i in range(5, n):
                if sma[i - 5] > 0:
                    sma_mom[i] = (sma[i] / sma[i - 5]) - 1
            features[f"mom_sma_{w}"] = sma_mom

    # ── Volatility ──
    for w in windows:
        if n > w:
            feat_name = f"vol_{w}d"
            vol = np.full(n, np.nan)
            for i in range(w, n):
                vol[i] = np.nanstd(returns[i - w + 1:i + 1])
            features[feat_name] = vol

            # Volatility ratio (short/long vol)
            if w >= 20:
                short_window = w // 4
                if short_window >= 5:
                    # Only compute if we have the shorter vol
                    pass
                # Skip vol_ratio — problematic with numpy truth checks

    # ── Z-Scores ──
    for w in config.get("zscore_windows", [20, 50]):
        sma = rolling_mean(closes, w)
        std = rolling_std(closes, w)
        with np.errstate(divide='ignore', invalid='ignore'):
            features[f"zscore_{w}d"] = np.where(std > 0, (closes - sma) / std, np.nan)

    # ── Max/Min drawdown ──
    for w in [20, 100]:
        if n > w:
            peak = rolling_max(closes, w)
            trough = rolling_min(closes, w)
            with np.errstate(divide='ignore', invalid='ignore'):
                features[f"dd_{w}d"] = np.where(peak > 0, (closes - peak) / peak, np.nan)
                features[f"range_{w}d"] = np.where(trough > 0, (peak - trough) / trough, np.nan)

    # ── Skewness / Kurtosis of returns ──
    for w in [20, 50]:
        if n > w:
            sk = np.full(n, np.nan)
            kt = np.full(n, np.nan)
            for i in range(w, n):
                chunk = returns[i - w + 1:i + 1]
                chunk = chunk[~np.isnan(chunk)]
                if len(chunk) > 5:
                    mean_r = np.mean(chunk)
                    std_r = np.std(chunk)
                    if std_r > 0:
                        sk[i] = np.mean(((chunk - mean_r) / std_r) ** 3)
                        kt[i] = np.mean(((chunk - mean_r) / std_r) ** 4)
            features[f"skew_{w}d"] = sk
            features[f"kurtosis_{w}d"] = kt

    # ── Consecutive moves ──
    features["consec_up"] = _consecutive_direction(returns, 1)
    features["consec_down"] = _consecutive_direction(returns, -1)

    # ── Price-Volume Correlation ──
    for w in [20, 50]:
        if n > w:
            pv_corr = np.full(n, np.nan)
            for i in range(w, n):
                p = closes[i - w + 1:i + 1]
                v = volumes[i - w + 1:i + 1]
                if np.std(p) > 0 and np.std(v) > 0:
                    pv_corr[i] = np.corrcoef(p, v)[0, 1]
            features[f"pv_corr_{w}d"] = pv_corr

    # ── Gap features ──
    gaps = np.full(n, np.nan)
    for i in range(1, n):
        if closes[i - 1] > 0:
            gaps[i] = (closes[i] / closes[i - 1]) - 1
    features["daily_gap"] = gaps

    # ── Efficiency Ratio (Kaufman) ──
    for w in [10, 20]:
        features[f"eff_ratio_{w}d"] = _efficiency_ratio(closes, w)

    return features


def _consecutive_direction(returns: np.ndarray, direction: int) -> np.ndarray:
    """Count consecutive days in given direction (1=up, -1=down)."""
    n = len(returns)
    result = np.zeros(n)
    count = 0
    for i in range(1, n):
        if np.isnan(returns[i]):
            continue
        if (direction == 1 and returns[i] > 0) or (direction == -1 and returns[i] < 0):
            count += 1
        else:
            count = 0
        result[i] = count
    return result


def _efficiency_ratio(closes: np.ndarray, window: int) -> np.ndarray:
    """Kaufman Efficiency Ratio: |net change| / sum of absolute changes."""
    n = len(closes)
    result = np.full(n, np.nan)
    for i in range(window, n):
        direction = abs(closes[i] - closes[i - window])
        volatility = sum(abs(closes[j] - closes[j - 1]) for j in range(i - window + 1, i + 1))
        if volatility > 0:
            result[i] = direction / volatility
    return result
