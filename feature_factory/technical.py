"""
Technical Features — price/volume indicators using rolling windows.

All computations are point-in-time: only look backward, never forward.
Each function returns a numpy array of same length as input.
"""
import numpy as np


def rolling_mean(arr: np.ndarray, window: int) -> np.ndarray:
    """Simple moving average with no look-ahead."""
    n = len(arr)
    result = np.full(n, np.nan)
    if n < window:
        return result
    cumsum = np.cumsum(np.nan_to_num(arr, 0))
    result[window - 1] = cumsum[window - 1] / window
    result[window:] = (cumsum[window:] - cumsum[:-window]) / window
    return result


def rolling_std(arr: np.ndarray, window: int) -> np.ndarray:
    """Rolling standard deviation."""
    n = len(arr)
    result = np.full(n, np.nan)
    if n < window:
        return result
    for i in range(window - 1, n):
        result[i] = np.nanstd(arr[i - window + 1:i + 1])
    return result


def rolling_min(arr: np.ndarray, window: int) -> np.ndarray:
    """Rolling minimum."""
    n = len(arr)
    result = np.full(n, np.nan)
    if n < window:
        return result
    for i in range(window - 1, n):
        result[i] = np.nanmin(arr[i - window + 1:i + 1])
    return result


def rolling_max(arr: np.ndarray, window: int) -> np.ndarray:
    """Rolling maximum."""
    n = len(arr)
    result = np.full(n, np.nan)
    if n < window:
        return result
    for i in range(window - 1, n):
        result[i] = np.nanmax(arr[i - window + 1:i + 1])
    return result


def compute_technical_features(df, config: dict) -> dict:
    """
    Compute technical indicator features.

    Returns dict: {feature_name: np.array}
    """
    closes = df['close']
    highs = df['high']
    lows = df['low']
    volumes = df['volume']
    n = len(closes)
    features = {}

    windows = config.get("windows", [5, 10, 20, 50, 200])

    # ── Moving Averages ──
    for w in windows:
        sma = rolling_mean(closes, w)
        features[f"sma_{w}"] = sma

        # Price relative to SMA (normalized)
        with np.errstate(divide='ignore', invalid='ignore'):
            features[f"dist_sma_{w}"] = np.where(sma > 0, (closes - sma) / sma, np.nan)

        # SMA slope (rate of change over 5 days)
        sma_shift = np.roll(sma, 5)
        sma_shift[:5] = np.nan
        with np.errstate(divide='ignore', invalid='ignore'):
            features[f"sma_{w}_slope"] = np.where(sma_shift > 0, (sma - sma_shift) / sma_shift, np.nan)

    # ── Exponential MA ──
    ema_10 = _ema(closes, 10)
    ema_20 = _ema(closes, 20)
    features["ema_10"] = ema_10
    features["ema_20"] = ema_20
    with np.errstate(divide='ignore', invalid='ignore'):
        features["ema_cross"] = np.where(ema_20 > 0, (ema_10 - ema_20) / ema_20, np.nan)

    # ── RSI ──
    for period in config.get("rsi_periods", [2, 7, 14]):
        features[f"rsi_{period}"] = _rsi(closes, period)

    # ── Bollinger Bands ──
    bb_win = config.get("bb_window", 20)
    bb_std = config.get("bb_std", 2.0)
    sma_bb = rolling_mean(closes, bb_win)
    std_bb = rolling_std(closes, bb_win)
    features["bb_upper"] = sma_bb + bb_std * std_bb
    features["bb_lower"] = sma_bb - bb_std * std_bb
    with np.errstate(divide='ignore', invalid='ignore'):
        features["bb_width"] = np.where(sma_bb > 0, (features["bb_upper"] - features["bb_lower"]) / sma_bb, np.nan)
        features["bb_position"] = np.where((features["bb_upper"] - features["bb_lower"]) > 0,
                                           (closes - features["bb_lower"]) / (features["bb_upper"] - features["bb_lower"]),
                                           np.nan)

    # ── ATR (Average True Range) ──
    for period in config.get("atr_periods", [7, 14]):
        features[f"atr_{period}"] = _atr(highs, lows, closes, period)
        with np.errstate(divide='ignore', invalid='ignore'):
            features[f"atr_{period}_pct"] = np.where(closes > 0, features[f"atr_{period}"] / closes, np.nan)

    # ── Volume Features ──
    for w in windows:
        vol_ma = rolling_mean(volumes, w)
        features[f"vol_ma_{w}"] = vol_ma
        with np.errstate(divide='ignore', invalid='ignore'):
            features[f"rvol_{w}"] = np.where(vol_ma > 0, volumes / vol_ma, np.nan)

    # ── MACD ──
    ema_12 = _ema(closes, 12)
    ema_26 = _ema(closes, 26)
    macd_line = ema_12 - ema_26
    signal_line = _ema(macd_line, 9)
    features["macd"] = macd_line
    features["macd_signal"] = signal_line
    features["macd_histogram"] = macd_line - signal_line

    # ── Swing low detection ──
    features["swing_low_5d"] = rolling_min(lows, 5)
    features["swing_high_5d"] = rolling_max(highs, 5)

    # ── Donchian Channels ──
    for w in config.get("donchian_windows", [20, 50]):
        features[f"donchian_high_{w}"] = rolling_max(highs, w)
        features[f"donchian_low_{w}"] = rolling_min(lows, w)
        with np.errstate(divide='ignore', invalid='ignore'):
            dc_range = features[f"donchian_high_{w}"] - features[f"donchian_low_{w}"]
            features[f"donchian_pos_{w}"] = np.where(dc_range > 0,
                                                     (closes - features[f"donchian_low_{w}"]) / dc_range,
                                                     np.nan)

    # ── Hurst Exponent (mean reversion check) ──
    features["hurst_100"] = _hurst(closes, 100)

    return features


# ── Helper functions ──

def _ema(arr: np.ndarray, period: int) -> np.ndarray:
    """Exponential moving average."""
    n = len(arr)
    result = np.full(n, np.nan)
    if n < period:
        return result
    alpha = 2.0 / (period + 1)
    # Seed with SMA for first value
    if period > 0 and n >= period:
        seg = arr[:period]
        seg_clean = seg[~np.isnan(seg)]
        if len(seg_clean) > 0:
            result[period - 1] = np.nanmean(seg_clean)
    for i in range(period, n):
        if not np.isnan(arr[i]):
            result[i] = alpha * arr[i] + (1 - alpha) * result[i - 1]
    return result


def _rsi(closes: np.ndarray, period: int) -> np.ndarray:
    """Relative Strength Index (RSI)."""
    n = len(closes)
    result = np.full(n, np.nan)
    if n < period + 2:
        return result

    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.nanmean(gains[:period])
    avg_loss = np.nanmean(losses[:period])

    for i in range(period, n - 1):
        if avg_loss == 0:
            result[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i] = 100.0 - (100.0 / (1.0 + rs))

        # Wilder's smoothing
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    return result


def _atr(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int) -> np.ndarray:
    """Average True Range."""
    n = len(highs)
    result = np.full(n, np.nan)
    if n < period + 1:
        return result

    tr = np.zeros(n)
    for i in range(1, n):
        tr[i] = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )

    # Wilder's smoothing
    atr_val = np.nanmean(tr[1:period + 1])
    result[period] = atr_val
    for i in range(period + 1, n):
        atr_val = (atr_val * (period - 1) + tr[i]) / period
        result[i] = atr_val

    return result


def _hurst(closes: np.ndarray, lookback: int) -> np.ndarray:
    """Hurst exponent using rescaled range. H<0.5 = mean-reverting, H>0.5 = trending."""
    n = len(closes)
    result = np.full(n, np.nan)
    if n < lookback:
        return result

    for i in range(lookback, n):
        segment = closes[i - lookback:i + 1]
        returns = np.diff(np.log(segment[segment > 0]))
        if len(returns) < 20:
            continue

        n_vals = [10, 20, 40, 60]
        rs_vals = []
        for nv in n_vals:
            if nv > len(returns):
                continue
            rs_list = []
            for start in range(0, len(returns) - nv + 1, nv):
                chunk = returns[start:start + nv]
                mean_r = np.mean(chunk)
                dev = chunk - mean_r
                cumdev = np.cumsum(dev)
                R = np.max(cumdev) - np.min(cumdev)
                S = np.std(chunk) if np.std(chunk) > 0 else 0.001
                rs_list.append(R / S)
            if rs_list:
                rs_vals.append((np.log(nv), np.log(np.mean(rs_list))))

        if len(rs_vals) >= 2:
            x_vals = [v[0] for v in rs_vals]
            y_vals = [v[1] for v in rs_vals]
            mean_x = np.mean(x_vals)
            mean_y = np.mean(y_vals)
            num = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals))
            den = sum((x - mean_x) ** 2 for x in x_vals)
            if den > 0:
                result[i] = max(0.0, min(1.0, num / den))

    return result
