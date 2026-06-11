"""
Phase 23A — Phase 12 Formula Forensics.

Reverse-engineer the original Phase 12 feature methodology by comparing
stored old features against multiple plausible formula families.

Uses phase12_etf_inclusive_features as reference cache.
Loads price data from NPZ files (close key) and yfinance for benchmarks.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


OLD_KEYS = [
    "residual_z",
    "residual_r2",
    "rsi_2",
    "regime_score",
]

SECTOR_ETF_CANDIDATES = [
    "XLK", "XLF", "XLV", "XLY", "XLC", "XLI", "XLE",
    "XLP", "XLU", "XLB", "XLRE", "SMH", "IBB", "ARKK",
]

# ---------------------------------------------------------------------------
# Formula candidate definition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FormulaCandidate:
    name: str
    residual_lookback: int
    residual_mode: str
    benchmark_symbol: str
    rsi_mode: str
    regime_mode: str


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_old_cache_npz(path: Path) -> dict[str, np.ndarray]:
    """Load a Phase 12 NPZ file and return arrays keyed by field name."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = np.load(path, allow_pickle=False)
    return {k: data[k].reshape(-1) for k in data.files}


def load_ohlcv_csv(path: Path) -> pd.DataFrame:
    """Load OHLCV CSV with standardised columns."""
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

    if "close" not in df.columns:
        raise ValueError(f"OHLCV missing close column: {path}")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp", "close"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")

    return df[["timestamp", "close"]].reset_index(drop=True)


def load_close_from_npz(path: Path) -> pd.DataFrame:
    """Load close prices from existing Phase 12 NPZ cache.

    This is a fallback when OHLCV CSVs are unavailable.
    The NPZ files contain a 'close' key and a 'timestamp' key.
    """
    if not path.exists():
        raise FileNotFoundError(path)

    data = np.load(path, allow_pickle=False)

    if "close" not in data.files or "timestamp" not in data.files:
        raise ValueError(f"NPZ missing close/timestamp: {path}")

    ts = data["timestamp"].reshape(-1)
    close = data["close"].reshape(-1)

    # Parse timestamp
    numeric = pd.to_numeric(pd.Series(ts), errors="coerce")
    if numeric.max() > 1e17:
        parsed = pd.to_datetime(numeric, unit="ns", utc=True, errors="coerce")
    elif numeric.max() > 1e13:
        parsed = pd.to_datetime(numeric, unit="us", utc=True, errors="coerce")
    else:
        parsed = pd.to_datetime(numeric, unit="s", utc=True, errors="coerce")

    df = pd.DataFrame({"timestamp": parsed, "close": pd.to_numeric(pd.Series(close), errors="coerce")})
    df = df.dropna(subset=["timestamp", "close"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")
    return df.reset_index(drop=True)


def find_ohlcv_path(root: Path, symbol: str) -> Path | None:
    """Find OHLCV data for a symbol, checking CSV paths first, then NPZ caches."""
    # CSV candidates
    candidates = [
        root / "data" / "cache" / "ohlcv_1d" / f"{symbol}_1D.csv",
        root / "data" / "cache" / "ohlcv_1d" / f"{symbol}_1d.csv",
        root / "data" / "cache" / "ohlcv_1d" / f"{symbol}.csv",
        root / "data" / "cache" / f"{symbol}_1D.csv",
        root / "data" / "cache" / f"{symbol}_1d.csv",
        root / "data" / "cache" / f"{symbol}.csv",
        root / "data" / f"{symbol}_1D.csv",
        root / "data" / f"{symbol}.csv",
    ]

    for path in candidates:
        if path.exists():
            return path

    # NPZ fallback: check cached NPZ directories
    npz_dirs = [
        root / "cache" / "phase12_etf_inclusive_features",
        root / "cache" / "phase12_canonical_features",
        root / "cache" / "phase12_rebuilt_features",
    ]

    for npz_dir in npz_dirs:
        npz_path = npz_dir / f"{symbol}.npz"
        if npz_path.exists():
            return npz_path  # Loaded as NPZ later

    return None


def load_symbol_close(path: Path) -> pd.DataFrame:
    """Load close data from either CSV or NPZ path."""
    if path.suffix == ".npz":
        return load_close_from_npz(path)
    return load_ohlcv_csv(path)


def fetch_yfinance_data(symbol: str, start_date: str = "2023-06-01", end_date: str = "2026-05-20") -> pd.DataFrame | None:
    """Fetch OHLCV data for a symbol via yfinance."""
    import yfinance as yf  # noqa: PLC0415

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date, auto_adjust=True)
        if hist.empty:
            return None
        df = hist[["Close"]].copy()
        df.columns = ["close"]
        df.index = pd.to_datetime(df.index, utc=True)
        df.index.name = "timestamp"
        return df.reset_index()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------


def align_symbol_and_benchmark(
    symbol_df: pd.DataFrame,
    bench_df: pd.DataFrame,
) -> pd.DataFrame:
    """Align symbol and benchmark data by date (ignoring intraday timestamps)."""
    sym = symbol_df.copy()
    sym["date"] = pd.to_datetime(sym["timestamp"], utc=True).dt.date

    bench = bench_df.copy()
    bench["date"] = pd.to_datetime(bench["timestamp"], utc=True).dt.date
    bench = bench.drop_duplicates("date")

    merged = pd.merge(
        sym.rename(columns={"close": "symbol_close"}),
        bench[["date", "close"]].rename(columns={"close": "benchmark_close"}),
        on="date",
        how="inner",
    )

    return merged.sort_values("date").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Formula computation
# ---------------------------------------------------------------------------


def safe_corr(a: np.ndarray, b: np.ndarray) -> float | None:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    n = min(len(a), len(b))
    if n <= 30:
        return None

    a = a[:n]
    b = b[:n]

    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 30:
        return None

    if np.nanstd(a[mask]) == 0 or np.nanstd(b[mask]) == 0:
        return None

    return float(np.corrcoef(a[mask], b[mask])[0, 1])


def safe_mae(a: np.ndarray, b: np.ndarray) -> float | None:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    n = min(len(a), len(b))
    if n == 0:
        return None

    a = a[:n]
    b = b[:n]

    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) == 0:
        return None

    return float(np.mean(np.abs(a[mask] - b[mask])))


def simple_rsi(close: pd.Series, window: int = 2) -> pd.Series:
    close = pd.to_numeric(close, errors="coerce")
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window, min_periods=window).mean()
    avg_loss = loss.rolling(window, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def wilder_rsi(close: pd.Series, window: int = 2) -> pd.Series:
    close = pd.to_numeric(close, errors="coerce")
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def rolling_return_residual_z(
    symbol_close: pd.Series,
    bench_close: pd.Series,
    lookback: int,
) -> tuple[pd.Series, pd.Series]:
    close_s = pd.to_numeric(symbol_close, errors="coerce")
    close_b = pd.to_numeric(bench_close, errors="coerce")

    combined = pd.DataFrame({"sym": close_s, "bench": close_b}).dropna()
    if len(combined) < lookback:
        empty = pd.Series(np.nan, index=close_s.index)
        return empty, empty

    sym_ret = combined["sym"].pct_change()
    bench_ret = combined["bench"].pct_change()

    x = bench_ret
    y = sym_ret

    x_mean = x.rolling(lookback, min_periods=lookback).mean()
    y_mean = y.rolling(lookback, min_periods=lookback).mean()

    cov = ((x - x_mean) * (y - y_mean)).rolling(lookback, min_periods=lookback).mean()
    var = ((x - x_mean) ** 2).rolling(lookback, min_periods=lookback).mean()

    beta = cov / var.replace(0, np.nan)
    alpha = y_mean - beta * x_mean

    residual = y - (alpha + beta * x)
    resid_std = residual.rolling(lookback, min_periods=lookback).std()
    residual_z = residual / resid_std.replace(0, np.nan)

    corr = x.rolling(lookback, min_periods=lookback).corr(y)
    r2 = corr ** 2

    return residual_z.reindex(close_s.index), r2.reindex(close_s.index)


def rolling_price_ratio_z(
    symbol_close: pd.Series,
    bench_close: pd.Series,
    lookback: int,
) -> tuple[pd.Series, pd.Series]:
    close_s = pd.to_numeric(symbol_close, errors="coerce")
    close_b = pd.to_numeric(bench_close, errors="coerce")

    combined = pd.DataFrame({"sym": close_s, "bench": close_b}).dropna()
    if len(combined) < lookback:
        empty = pd.Series(np.nan, index=close_s.index)
        return empty, empty

    ratio = combined["sym"] / combined["bench"]

    mean = ratio.rolling(lookback, min_periods=lookback).mean()
    std = ratio.rolling(lookback, min_periods=lookback).std()

    z = (ratio - mean) / std.replace(0, np.nan)

    sym_ret = combined["sym"].pct_change()
    bench_ret = combined["bench"].pct_change()
    corr = sym_ret.rolling(lookback, min_periods=lookback).corr(bench_ret)
    r2 = corr ** 2

    return z.reindex(close_s.index), r2.reindex(close_s.index)


def rolling_close_z(
    symbol_close: pd.Series,
    lookback: int,
) -> tuple[pd.Series, pd.Series]:
    close = pd.to_numeric(symbol_close, errors="coerce")
    ret = close.pct_change()

    mean = ret.rolling(lookback, min_periods=lookback).mean()
    std = ret.rolling(lookback, min_periods=lookback).std()

    z = (ret - mean) / std.replace(0, np.nan)
    r2 = pd.Series(np.nan, index=close.index)

    return z, r2


def regime_proxy(
    close: pd.Series,
    mode: str,
) -> pd.Series:
    close = pd.to_numeric(close, errors="coerce")
    ret = close.pct_change()

    if mode == "vol20_rank252":
        vol = ret.rolling(20, min_periods=20).std()
        return vol.rolling(252, min_periods=60).rank(pct=True)

    if mode == "mom20_rank252":
        mom = close / close.shift(20) - 1
        return mom.rolling(252, min_periods=60).rank(pct=True)

    if mode == "vol_mom_combo":
        vol = ret.rolling(20, min_periods=20).std()
        mom = close / close.shift(20) - 1

        vol_rank = vol.rolling(252, min_periods=60).rank(pct=True)
        mom_rank = mom.rolling(252, min_periods=60).rank(pct=True)

        return (vol_rank + mom_rank) / 2.0

    if mode == "binary_trend":
        ma20 = close.rolling(20, min_periods=20).mean()
        ma50 = close.rolling(50, min_periods=50).mean()
        return (ma20 > ma50).astype(float)

    raise ValueError(f"Unknown regime mode: {mode}")


# ---------------------------------------------------------------------------
# Compute features for a candidate
# ---------------------------------------------------------------------------


def compute_candidate_features(
    merged: pd.DataFrame,
    candidate: FormulaCandidate,
) -> pd.DataFrame:
    """Compute all features for a candidate formula given aligned symbol+benchmark data."""
    close = pd.to_numeric(merged["symbol_close"], errors="coerce")
    bench = pd.to_numeric(merged["benchmark_close"], errors="coerce")

    if candidate.residual_mode == "return_residual":
        residual_z, residual_r2 = rolling_return_residual_z(close, bench, candidate.residual_lookback)
    elif candidate.residual_mode == "price_ratio_z":
        residual_z, residual_r2 = rolling_price_ratio_z(close, bench, candidate.residual_lookback)
    elif candidate.residual_mode == "close_return_z":
        residual_z, residual_r2 = rolling_close_z(close, candidate.residual_lookback)
    else:
        raise ValueError(f"Unknown residual mode: {candidate.residual_mode}")

    if candidate.rsi_mode == "simple":
        rsi_2 = simple_rsi(close, 2)
    elif candidate.rsi_mode == "wilder":
        rsi_2 = wilder_rsi(close, 2)
    else:
        raise ValueError(f"Unknown rsi mode: {candidate.rsi_mode}")

    regime_score = regime_proxy(close, candidate.regime_mode)

    out = pd.DataFrame(
        {
            "residual_z": residual_z,
            "residual_r2": residual_r2,
            "rsi_2": rsi_2,
            "regime_score": regime_score,
        }
    )

    return out


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def compare_candidate_to_old(
    old: dict[str, np.ndarray],
    candidate_features: pd.DataFrame,
    candidate: FormulaCandidate,
) -> dict[str, Any]:
    """Compare candidate-computed features against stored old features.

    Returns per-key correlations, MAE, and a composite score.
    """
    rows = []

    for key in OLD_KEYS:
        if key not in old:
            rows.append({"key": key, "corr": None, "mae": None, "status": "MISSING_IN_OLD"})
            continue

        old_arr = old[key].reshape(-1).astype(float)

        if key not in candidate_features.columns:
            rows.append({"key": key, "corr": None, "mae": None, "status": "MISSING_IN_CANDIDATE"})
            continue

        new_arr = candidate_features[key].to_numpy(dtype=float)

        rows.append(
            {
                "key": key,
                "corr": safe_corr(old_arr, new_arr),
                "mae": safe_mae(old_arr, new_arr),
                "status": "OK",
            }
        )

    residual_z_corr = next((r["corr"] for r in rows if r["key"] == "residual_z"), None)
    residual_r2_corr = next((r["corr"] for r in rows if r["key"] == "residual_r2"), None)
    rsi_corr = next((r["corr"] for r in rows if r["key"] == "rsi_2"), None)
    regime_corr = next((r["corr"] for r in rows if r["key"] == "regime_score"), None)

    score_parts = [
        residual_z_corr or 0.0,
        residual_r2_corr or 0.0,
        rsi_corr or 0.0,
        regime_corr or 0.0,
    ]

    composite_score = float(np.mean(score_parts))

    return {
        "candidate_name": candidate.name,
        "benchmark_symbol": candidate.benchmark_symbol,
        "residual_mode": candidate.residual_mode,
        "residual_lookback": candidate.residual_lookback,
        "rsi_mode": candidate.rsi_mode,
        "regime_mode": candidate.regime_mode,
        "composite_score": composite_score,
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# Candidate generation
# ---------------------------------------------------------------------------


def generate_formula_candidates(available_benchmarks: list[str]) -> list[FormulaCandidate]:
    """Generate all plausible formula candidates from available benchmarks."""
    candidates = []

    lookbacks = [20, 40, 60, 90, 120]
    residual_modes = ["return_residual", "price_ratio_z", "close_return_z"]
    rsi_modes = ["simple", "wilder"]
    regime_modes = ["vol20_rank252", "mom20_rank252", "vol_mom_combo", "binary_trend"]

    for bench in available_benchmarks:
        for lookback in lookbacks:
            for residual_mode in residual_modes:
                for rsi_mode in rsi_modes:
                    for regime_mode in regime_modes:
                        name = f"{bench}_{residual_mode}_{lookback}_{rsi_mode}_{regime_mode}"
                        candidates.append(
                            FormulaCandidate(
                                name=name,
                                residual_lookback=lookback,
                                residual_mode=residual_mode,
                                benchmark_symbol=bench,
                                rsi_mode=rsi_mode,
                                regime_mode=regime_mode,
                            )
                        )

    return candidates


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify_forensic_match(best_score: float | None) -> str:
    if best_score is None:
        return "FORENSICS_NO_MATCH"

    if best_score >= 0.90:
        return "FORENSICS_STRONG_RECONSTRUCTION"

    if best_score >= 0.75:
        return "FORENSICS_PARTIAL_RECONSTRUCTION"

    if best_score >= 0.60:
        return "FORENSICS_WEAK_RECONSTRUCTION"

    return "FORENSICS_NO_MATCH"
