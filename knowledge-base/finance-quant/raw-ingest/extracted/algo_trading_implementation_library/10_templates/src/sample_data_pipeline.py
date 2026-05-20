from __future__ import annotations

import pandas as pd

REQUIRED_BAR_COLUMNS = {"timestamp", "symbol", "open", "high", "low", "close", "volume"}


def load_bars_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    validate_bars(df)
    return normalize_bars(df)


def validate_bars(df: pd.DataFrame) -> None:
    missing = REQUIRED_BAR_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    bad_ohlc = (df["low"] > df["open"]) | (df["open"] > df["high"]) | (df["low"] > df["close"]) | (df["close"] > df["high"])
    if bad_ohlc.any():
        raise ValueError(f"Invalid OHLC rows: {int(bad_ohlc.sum())}")
    if (df["volume"] < 0).any():
        raise ValueError("Negative volume detected")


def normalize_bars(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["symbol"] = out["symbol"].str.upper().str.strip()
    out = out.sort_values(["symbol", "timestamp"]).drop_duplicates(["symbol", "timestamp"], keep="last")
    return out.reset_index(drop=True)
