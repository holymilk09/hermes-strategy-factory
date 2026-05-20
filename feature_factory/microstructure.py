"""
Microstructure Features — from daily OHLCV data.

Since we don't have intraday data, we approximate microstructure signals:
  - Signed volume proxy (tick rule)
  - Volume-at-price concentration
  - Spread proxy (high-low range relative to close)
  - VWAP deviation proxy
  - Order flow imbalance proxy
"""
import numpy as np
from feature_factory.technical import rolling_mean, rolling_std


def compute_microstructure_features(df, config: dict) -> dict:
    """
    Compute microstructure approximation features from daily data.

    Returns dict: {feature_name: np.array}
    """
    closes = df['close']
    highs = df['high']
    lows = df['low']
    opens = df['open']
    volumes = df['volume']
    n = len(closes)
    features = {}

    # ── Signed Volume (Tick Rule approximation) ──
    signed_vol = np.full(n, np.nan)
    for i in range(1, n):
        if closes[i] > closes[i - 1]:
            signed_vol[i] = volumes[i]       # Buy volume
        elif closes[i] < closes[i - 1]:
            signed_vol[i] = -volumes[i]       # Sell volume
        else:
            signed_vol[i] = 0

    features["signed_volume"] = signed_vol

    # ── Cumulative signed volume (Kyle's Lambda proxy) ──
    cum_sv = np.cumsum(np.nan_to_num(signed_vol))
    features["cum_signed_volume"] = cum_sv

    # ── Order Flow Imbalance (10-day) ──
    for w in [5, 10, 20]:
        sv_ma = rolling_mean(signed_vol, w)
        vol_ma = rolling_mean(volumes, w)
        with np.errstate(divide='ignore', invalid='ignore'):
            features[f"ofi_{w}d"] = np.where(vol_ma > 0, sv_ma / vol_ma, np.nan)

    # ── VWAP proxy (daily) ──
    # Approximate as (H+L+C)/3 — typical price weighted by volume
    typical_price = (highs + lows + closes) / 3.0
    vwap_proxy = np.full(n, np.nan)
    cum_tp_vol = np.cumsum(np.nan_to_num(typical_price * volumes))
    cum_vol = np.cumsum(np.nan_to_num(volumes))
    with np.errstate(divide='ignore', invalid='ignore'):
        vwap_proxy = np.where(cum_vol > 0, cum_tp_vol / cum_vol, np.nan)
    features["vwap_proxy"] = vwap_proxy
    with np.errstate(divide='ignore', invalid='ignore'):
        features["vwap_deviation"] = np.where(vwap_proxy > 0, (closes - vwap_proxy) / vwap_proxy, np.nan)

    # ── Spread proxy (high-low / close) ──
    with np.errstate(divide='ignore', invalid='ignore'):
        features["spread_proxy"] = np.where(closes > 0, (highs - lows) / closes, np.nan)
        features["spread_proxy_ma20"] = rolling_mean(features["spread_proxy"], 20)

    # ── Volume at close (close location in daily range) ──
    with np.errstate(divide='ignore', invalid='ignore'):
        range_size = highs - lows
        features["close_location"] = np.where(range_size > 0, (closes - lows) / range_size, np.nan)

    # ── Amihud Illiquidity proxy ──
    amihud = np.full(n, np.nan)
    for i in range(1, n):
        if volumes[i] * closes[i] > 0:
            amihud[i] = abs(df['returns'][i]) / (volumes[i] * closes[i])
    features["amihud_illiquidity"] = amihud
    features["amihud_ma20"] = rolling_mean(amihud, 20)

    # ── Volume climax detection ──
    vol_ma20 = rolling_mean(volumes, 20)
    with np.errstate(divide='ignore', invalid='ignore'):
        features["volume_climax"] = np.where(vol_ma20 > 0, volumes / vol_ma20, np.nan)

    # ── Intraday volatility proxy (high-low vs close) ──
    with np.errstate(divide='ignore', invalid='ignore'):
        features["intraday_range_pct"] = np.where(closes > 0, (highs - lows) / closes, np.nan)

    # ── Up/down volume ratio ──
    up_vol = np.full(n, np.nan)
    down_vol = np.full(n, np.nan)
    for i in range(1, n):
        if closes[i] > closes[i - 1]:
            up_vol[i] = volumes[i]
            down_vol[i] = 0
        elif closes[i] < closes[i - 1]:
            up_vol[i] = 0
            down_vol[i] = volumes[i]

    up_vol_sum = rolling_mean(np.nan_to_num(up_vol), 10)
    down_vol_sum = rolling_mean(np.nan_to_num(down_vol), 10)
    with np.errstate(divide='ignore', invalid='ignore'):
        features["up_down_vol_ratio"] = np.where(down_vol_sum > 0, up_vol_sum / down_vol_sum, np.nan)

    # ── Kyle's Lambda (daily approximation) ──
    # Lambda = |return| / dollar_volume — higher lambda = more price impact per dollar
    for i in range(20, n):
        abs_rets = np.abs(df['returns'][i - 19:i + 1])
        dv = volumes[i - 19:i + 1] * closes[i - 19:i + 1]
        mask = (dv > 0) & ~np.isnan(abs_rets)
        if np.sum(mask) > 5:
            features.setdefault("kyles_lambda", np.full(n, np.nan))
            features["kyles_lambda"][i] = np.nanmean(abs_rets[mask] / dv[mask])

    # ── Downward pressure (lower close + above-avg volume) ──
    features["downward_pressure"] = np.where(
        (closes < closes - np.roll(closes, 1)) & (volumes > rolling_mean(volumes, 20)),
        1.0, 0.0
    )
    # Fix first element
    features["downward_pressure"][0] = np.nan

    return features
