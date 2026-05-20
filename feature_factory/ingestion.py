"""
Data Ingestion — fetch OHLCV from Alpaca, build point-in-time DataFrames.

Standard library for API (urllib+json), pandas/numpy for computation.
"""
import json
import os
import urllib.request
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

import numpy as np


def _load_alpaca_creds():
    """Load Alpaca API credentials from /opt/data/.env."""
    env = {}
    env_path = "/opt/data/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env[k.strip()] = v.strip()
    return env.get("ALPACA_API_KEY", ""), env.get("ALPACA_SECRET_KEY", "")


def fetch_ohlcv(
    symbol: str,
    start_date: str,
    end_date: str,
    warmup_days: int = 365,
) -> List[Tuple]:
    """
    Fetch OHLCV bars from Alpaca.
    Returns list of (timestamp, open, high, low, close, volume).
    """
    api_key, api_secret = _load_alpaca_creds()
    if not api_key:
        print(f"Ingestion: No Alpaca API key for {symbol}")
        return []

    start_dt = datetime.strptime(start_date[:10], "%Y-%m-%d") - timedelta(days=warmup_days)
    start_utc = start_dt.strftime("%Y-%m-%dT00:00:00Z")
    end_utc = f"{end_date[:10]}T23:59:59Z"

    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Accept": "application/json",
    }

    url = (f"https://data.alpaca.markets/v2/stocks/{symbol}/bars"
           f"?timeframe=1Day&start={start_utc}&end={end_utc}&limit=10000")

    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode())
        bars = data.get("bars", [])
        ohlcv = [(b["t"], b["o"], b["h"], b["l"], b["c"], b["v"]) for b in bars]
        return ohlcv
    except Exception as e:
        print(f"Ingestion: Failed to fetch {symbol} — {e}")
        return []


def build_price_df(
    symbol: str,
    start_date: str,
    end_date: str,
    config: dict,
) -> Optional[np.ndarray]:
    """
    Build structured price array from Alpaca data.

    Returns structured numpy array with fields:
      date (str), open, high, low, close, volume, returns, log_returns

    Returns None if no data or insufficient bars.
    """
    warmup = config.get("warmup_days", 365)
    ohlcv = fetch_ohlcv(symbol, start_date, end_date, warmup_days=warmup)

    if not ohlcv or len(ohlcv) < 60:
        return None

    # Convert to structured array
    n = len(ohlcv)
    dates = [b[0][:10] for b in ohlcv]
    opens = np.array([b[1] for b in ohlcv], dtype=np.float64)
    highs = np.array([b[2] for b in ohlcv], dtype=np.float64)
    lows = np.array([b[3] for b in ohlcv], dtype=np.float64)
    closes = np.array([b[4] for b in ohlcv], dtype=np.float64)
    volumes = np.array([b[5] for b in ohlcv], dtype=np.float64)

    # Compute returns
    returns = np.zeros(n)
    returns[1:] = (closes[1:] / closes[:-1]) - 1
    log_returns = np.zeros(n)
    log_returns[1:] = np.log(closes[1:] / closes[:-1])

    dtype = np.dtype([
        ('date', 'U10'),
        ('open', 'f8'),
        ('high', 'f8'),
        ('low', 'f8'),
        ('close', 'f8'),
        ('volume', 'f8'),
        ('returns', 'f8'),
        ('log_returns', 'f8'),
    ])

    arr = np.zeros(n, dtype=dtype)
    arr['date'] = dates
    arr['open'] = opens
    arr['high'] = highs
    arr['low'] = lows
    arr['close'] = closes
    arr['volume'] = volumes
    arr['returns'] = returns
    arr['log_returns'] = log_returns

    return arr


def build_multi_symbol_dataset(
    symbols: List[str],
    start_date: str,
    end_date: str,
    config: dict,
) -> dict:
    """Fetch and build DataFrames for multiple symbols. Returns {symbol: structured_array}."""
    data = {}
    for i, sym in enumerate(symbols):
        df = build_price_df(sym, start_date, end_date, config)
        if df is not None:
            data[sym] = df
        if (i + 1) % 20 == 0:
            print(f"Ingestion: {i + 1}/{len(symbols)} symbols loaded...")
    print(f"Ingestion: Complete — {len(data)}/{len(symbols)} symbols with valid data")
    return data
