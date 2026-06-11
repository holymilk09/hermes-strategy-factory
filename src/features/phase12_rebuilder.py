from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Phase12FeatureConfig:
    start_date: str = "2024-01-01"
    residual_lookback: int = 60
    rsi_window: int = 2
    regime_window: int = 20
    forward_windows: tuple[int, ...] = (5, 10, 20)


def load_ohlcv_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]

    time_col = None
    for c in ["timestamp", "date", "datetime", "time"]:
        if c in df.columns:
            time_col = c
            break

    if time_col is None:
        raise ValueError(f"OHLCV missing timestamp/date column: {path}")

    required = ["open", "high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"OHLCV missing columns {missing}: {path}")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")
    keep = ["timestamp", "open", "high", "low", "close"]
    if "volume" in df.columns:
        keep.append("volume")

    return df[keep].reset_index(drop=True)


def compute_rsi(close: pd.Series, window: int = 2) -> pd.Series:
    close = pd.to_numeric(close, errors="coerce")
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))

    rsi = rsi.fillna(50.0)
    return rsi.rename(f"rsi_{window}")


def compute_forward_returns(close: pd.Series, windows: tuple[int, ...]) -> pd.DataFrame:
    out = pd.DataFrame(index=close.index)

    for w in windows:
        out[f"forward_return_{w}d"] = close.shift(-w) / close - 1.0

    return out


def rolling_beta_residual(
    symbol_ret: pd.Series,
    market_ret: pd.Series,
    lookback: int,
) -> tuple[pd.Series, pd.Series]:
    x = pd.to_numeric(market_ret, errors="coerce")
    y = pd.to_numeric(symbol_ret, errors="coerce")

    x_mean = x.rolling(lookback, min_periods=lookback).mean()
    y_mean = y.rolling(lookback, min_periods=lookback).mean()

    cov = ((x - x_mean) * (y - y_mean)).rolling(lookback, min_periods=lookback).mean()
    var = ((x - x_mean) ** 2).rolling(lookback, min_periods=lookback).mean()

    beta = cov / var.replace(0, np.nan)
    alpha = y_mean - beta * x_mean

    fitted = alpha + beta * x
    residual = y - fitted

    rolling_resid_std = residual.rolling(lookback, min_periods=lookback).std()
    residual_z = residual / rolling_resid_std.replace(0, np.nan)

    corr = x.rolling(lookback, min_periods=lookback).corr(y)
    residual_r2 = corr ** 2

    return residual_z.rename("residual_z"), residual_r2.rename("residual_r2")


def compute_regime_score(close: pd.Series, window: int = 20) -> pd.Series:
    ret = close.pct_change()
    vol = ret.rolling(window, min_periods=window).std()
    momentum = close / close.shift(window) - 1.0

    vol_rank = vol.rolling(252, min_periods=60).rank(pct=True)
    mom_rank = momentum.rolling(252, min_periods=60).rank(pct=True)

    regime_score = (vol_rank + mom_rank) / 2.0
    return regime_score.rename("regime_score")


def build_symbol_features(
    symbol_ohlcv: pd.DataFrame,
    market_ohlcv: pd.DataFrame,
    config: Phase12FeatureConfig | None = None,
) -> pd.DataFrame:
    config = config or Phase12FeatureConfig()

    sym = symbol_ohlcv.copy()
    mkt = market_ohlcv.copy()

    sym["timestamp"] = pd.to_datetime(sym["timestamp"], utc=True)
    mkt["timestamp"] = pd.to_datetime(mkt["timestamp"], utc=True)

    merged = pd.merge(
        sym,
        mkt[["timestamp", "close"]].rename(columns={"close": "market_close"}),
        on="timestamp",
        how="inner",
    )

    merged = merged.sort_values("timestamp").reset_index(drop=True)

    close = pd.to_numeric(merged["close"], errors="coerce")
    market_close = pd.to_numeric(merged["market_close"], errors="coerce")

    symbol_ret = close.pct_change()
    market_ret = market_close.pct_change()

    residual_z, residual_r2 = rolling_beta_residual(
        symbol_ret=symbol_ret,
        market_ret=market_ret,
        lookback=config.residual_lookback,
    )

    out = pd.DataFrame()
    out["timestamp"] = merged["timestamp"]
    out["close"] = close
    out["residual_z"] = residual_z
    out["residual_r2"] = residual_r2
    out["rsi_2"] = compute_rsi(close, window=config.rsi_window)
    out["regime_score"] = compute_regime_score(close, window=config.regime_window)

    fwd = compute_forward_returns(close, config.forward_windows)
    out = pd.concat([out, fwd], axis=1)

    out = out[out["timestamp"] >= pd.Timestamp(config.start_date, tz="UTC")]
    out = out.reset_index(drop=True)

    return out


def save_symbol_npz(features: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {}
    payload["timestamp"] = features["timestamp"].astype("int64").to_numpy()

    for c in features.columns:
        if c == "timestamp":
            continue
        payload[c] = pd.to_numeric(features[c], errors="coerce").to_numpy(dtype=float)

    np.savez_compressed(output_path, **payload)


def load_old_npz(path: Path) -> dict[str, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(path)

    data = np.load(path, allow_pickle=False)
    return {k: data[k] for k in data.files}
