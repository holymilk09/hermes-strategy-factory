from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def load_ohlcv(path: Path) -> pd.DataFrame:
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
        raise ValueError(f"Missing timestamp/date: {path}")

    required = ["open", "high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLC columns {missing}: {path}")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")

    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")

    return df.reset_index(drop=True)


def load_candidate_ledger(path: Path, family: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]

    required = ["timestamp", "symbol", "selected", "forward_return"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{family} missing columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["selected"] = df["selected"].astype(bool)
    df["forward_return"] = pd.to_numeric(df["forward_return"], errors="coerce")
    df["family"] = family

    df = df.dropna(subset=["timestamp", "symbol", "selected", "forward_return"])
    df = df.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    return df


def discover_symbol_ohlcv_paths(root: Path) -> dict[str, Path]:
    dirs = [
        root / "data" / "cache" / "ohlcv_1d",
        root / "data" / "cache",
        root / "data",
    ]

    out: dict[str, Path] = {}

    for d in dirs:
        if not d.exists():
            continue

        for p in d.glob("*.csv"):
            symbol = p.stem.upper()
            symbol = symbol.replace("_1D", "").replace("_1d", "")

            if symbol not in out:
                out[symbol] = p

    return out


def compute_spy_pit_features(spy: pd.DataFrame) -> pd.DataFrame:
    out = spy.copy()
    close = out["close"]
    ret = close.pct_change()

    out["spy_ret_5d_trailing"] = close / close.shift(5) - 1.0
    out["spy_ret_20d_trailing"] = close / close.shift(20) - 1.0
    out["spy_ret_60d_trailing"] = close / close.shift(60) - 1.0

    out["spy_vol_20d_trailing"] = ret.rolling(20, min_periods=20).std()
    out["spy_vol_60d_trailing"] = ret.rolling(60, min_periods=60).std()

    out["spy_vol_20d_pct252"] = (
        out["spy_vol_20d_trailing"]
        .rolling(252, min_periods=60)
        .rank(pct=True)
    )

    out["spy_ma20"] = close.rolling(20, min_periods=20).mean()
    out["spy_ma50"] = close.rolling(50, min_periods=50).mean()
    out["spy_ma200"] = close.rolling(200, min_periods=100).mean()

    out["spy_above_ma20"] = close > out["spy_ma20"]
    out["spy_above_ma50"] = close > out["spy_ma50"]
    out["spy_above_ma200"] = close > out["spy_ma200"]

    high60 = close.rolling(60, min_periods=20).max()
    low60 = close.rolling(60, min_periods=20).min()

    out["spy_drawdown_60d"] = close / high60 - 1.0
    out["spy_position_60d"] = (close - low60) / (high60 - low60).replace(0, np.nan)

    keep = [
        "timestamp",
        "spy_ret_5d_trailing",
        "spy_ret_20d_trailing",
        "spy_ret_60d_trailing",
        "spy_vol_20d_trailing",
        "spy_vol_60d_trailing",
        "spy_vol_20d_pct252",
        "spy_above_ma20",
        "spy_above_ma50",
        "spy_above_ma200",
        "spy_drawdown_60d",
        "spy_position_60d",
    ]

    return out[keep].sort_values("timestamp").reset_index(drop=True)


def compute_symbol_pit_frame(symbol: str, path: Path) -> pd.DataFrame:
    df = load_ohlcv(path)

    close = df["close"]
    volume = df["volume"] if "volume" in df.columns else pd.Series(np.nan, index=df.index)

    out = pd.DataFrame()
    out["timestamp"] = df["timestamp"]
    out["symbol"] = symbol
    out["ret_5d_trailing"] = close / close.shift(5) - 1.0
    out["ret_20d_trailing"] = close / close.shift(20) - 1.0
    out["above_ma20"] = close > close.rolling(20, min_periods=20).mean()
    out["above_ma50"] = close > close.rolling(50, min_periods=50).mean()

    vol_mean = volume.rolling(20, min_periods=20).mean()
    vol_std = volume.rolling(20, min_periods=20).std()
    out["volume_z_20"] = (volume - vol_mean) / vol_std.replace(0, np.nan)

    return out.dropna(subset=["timestamp"]).reset_index(drop=True)


def compute_universe_pit_features(root: Path) -> pd.DataFrame:
    paths = discover_symbol_ohlcv_paths(root)

    excluded = {
        "SPY", "QQQ", "IWM",
        "XLK", "XLF", "XLV", "XLY", "XLC", "XLI",
        "XLE", "XLP", "XLU", "XLB", "XLRE",
        "SMH", "IBB", "ARKK",
    }

    frames = []

    for symbol, path in paths.items():
        if symbol in excluded:
            continue

        try:
            frame = compute_symbol_pit_frame(symbol, path)
            if not frame.empty:
                frames.append(frame)
        except Exception:
            continue

    if not frames:
        raise ValueError("No universe PIT frames built")

    all_symbols = pd.concat(frames, axis=0, ignore_index=True)

    rows = []

    for ts, group in all_symbols.groupby("timestamp"):
        rows.append(
            {
                "timestamp": ts,
                "universe_ret_5d_median_trailing": float(group["ret_5d_trailing"].median()),
                "universe_ret_20d_median_trailing": float(group["ret_20d_trailing"].median()),
                "universe_ret_5d_dispersion": float(group["ret_5d_trailing"].std()),
                "universe_ret_20d_dispersion": float(group["ret_20d_trailing"].std()),
                "universe_above_ma20_rate": float(group["above_ma20"].mean()),
                "universe_above_ma50_rate": float(group["above_ma50"].mean()),
                "universe_positive_20d_rate": float((group["ret_20d_trailing"] > 0).mean()),
                "universe_volume_z20_median": float(group["volume_z_20"].median()),
                "symbol_count": int(len(group)),
            }
        )

    return pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)


def merge_pit_regime_features(
    candidates: pd.DataFrame,
    spy_features: pd.DataFrame,
    universe_features: pd.DataFrame,
) -> pd.DataFrame:
    base = candidates.sort_values("timestamp").copy()

    merged = pd.merge_asof(
        base,
        spy_features.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
        allow_exact_matches=True,
    )

    merged = pd.merge_asof(
        merged.sort_values("timestamp"),
        universe_features.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
        allow_exact_matches=True,
    )

    return merged


def build_time_folds(df: pd.DataFrame, n_folds: int = 4) -> pd.DataFrame:
    timestamps = sorted(df["timestamp"].dropna().unique())
    chunks = np.array_split(np.array(timestamps), n_folds)

    rows = []
    for i, chunk in enumerate(chunks, start=1):
        rows.append(
            {
                "fold": i,
                "start": pd.Timestamp(chunk[0]),
                "end": pd.Timestamp(chunk[-1]),
            }
        )

    return pd.DataFrame(rows)


def summarize_pit_features_by_fold(
    merged: pd.DataFrame,
    folds: pd.DataFrame,
) -> pd.DataFrame:
    numeric_cols = [
        "spy_ret_5d_trailing",
        "spy_ret_20d_trailing",
        "spy_ret_60d_trailing",
        "spy_vol_20d_trailing",
        "spy_vol_60d_trailing",
        "spy_vol_20d_pct252",
        "spy_drawdown_60d",
        "spy_position_60d",
        "universe_ret_5d_median_trailing",
        "universe_ret_20d_median_trailing",
        "universe_ret_5d_dispersion",
        "universe_ret_20d_dispersion",
        "universe_above_ma20_rate",
        "universe_above_ma50_rate",
        "universe_positive_20d_rate",
        "universe_volume_z20_median",
    ]

    bool_cols = [
        "spy_above_ma20",
        "spy_above_ma50",
        "spy_above_ma200",
    ]

    rows = []

    for _, fold in folds.iterrows():
        part = merged[
            (merged["timestamp"] >= fold["start"])
            & (merged["timestamp"] <= fold["end"])
        ].copy()

        row = {
            "fold": int(fold["fold"]),
            "start": fold["start"],
            "end": fold["end"],
            "rows": int(len(part)),
        }

        for c in numeric_cols:
            if c in part.columns:
                row[f"{c}_mean"] = float(pd.to_numeric(part[c], errors="coerce").mean())

        for c in bool_cols:
            if c in part.columns:
                row[f"{c}_rate"] = float(part[c].astype(bool).mean())

        rows.append(row)

    return pd.DataFrame(rows)


def summarize_selected_performance_by_pit_bucket(
    merged: pd.DataFrame,
    feature: str,
    quantiles: int = 3,
) -> pd.DataFrame:
    df = merged.copy()

    if feature not in df.columns:
        return pd.DataFrame()

    x = pd.to_numeric(df[feature], errors="coerce")
    valid = df[x.notna()].copy()

    if valid.empty or valid[feature].nunique() < quantiles:
        return pd.DataFrame()

    try:
        valid["bucket"] = pd.qcut(valid[feature], q=quantiles, duplicates="drop")
    except ValueError:
        return pd.DataFrame()

    rows = []

    for bucket, group in valid.groupby("bucket", observed=True):
        selected = group[group["selected"]].copy()
        rejected = group[~group["selected"]].copy()

        def mean_hit(part: pd.DataFrame) -> tuple[int, float | None, float | None]:
            if part.empty:
                return 0, None, None
            r = pd.to_numeric(part["forward_return"], errors="coerce").dropna()
            if r.empty:
                return 0, None, None
            return int(len(r)), float(r.mean()), float((r > 0).mean())

        sn, sm, sh = mean_hit(selected)
        rn, rm, rh = mean_hit(rejected)

        spread = None
        if sm is not None and rm is not None:
            spread = sm - rm

        rows.append(
            {
                "feature": feature,
                "bucket": str(bucket),
                "candidate_rows": int(len(group)),
                "selected_rows": sn,
                "rejected_rows": rn,
                "selected_mean": sm,
                "selected_hit": sh,
                "rejected_mean": rm,
                "rejected_hit": rh,
                "spread": spread,
            }
        )

    return pd.DataFrame(rows)


def evaluate_proxy_candidates(merged: pd.DataFrame) -> pd.DataFrame:
    features = [
        "spy_ret_20d_trailing",
        "spy_ret_60d_trailing",
        "spy_vol_20d_pct252",
        "spy_drawdown_60d",
        "spy_position_60d",
        "universe_ret_20d_median_trailing",
        "universe_above_ma20_rate",
        "universe_above_ma50_rate",
        "universe_positive_20d_rate",
        "universe_ret_20d_dispersion",
        "universe_volume_z20_median",
    ]

    frames = []

    for feature in features:
        b = summarize_selected_performance_by_pit_bucket(merged, feature, quantiles=3)
        if not b.empty:
            frames.append(b)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, axis=0, ignore_index=True)


def classify_pit_proxy_result(bucket_summary: pd.DataFrame) -> str:
    if bucket_summary.empty:
        return "PIT_PROXY_INCONCLUSIVE"

    candidates = bucket_summary.dropna(subset=["spread", "selected_rows"]).copy()

    if candidates.empty:
        return "PIT_PROXY_INCONCLUSIVE"

    candidates = candidates[candidates["selected_rows"] >= 30]

    if candidates.empty:
        return "PIT_PROXY_INCONCLUSIVE"

    best = candidates.sort_values("spread", ascending=False).iloc[0]

    if best["spread"] >= 0.01 and best["selected_mean"] >= 0.01:
        return "PIT_PROXY_CANDIDATE_FOUND"

    if best["spread"] >= 0.005:
        return "PIT_PROXY_WEAK_CANDIDATE"

    return "PIT_PROXY_NO_EDGE_BUCKET"


def build_pit_proxy_decision(classification: str) -> str:
    if classification == "PIT_PROXY_CANDIDATE_FOUND":
        return (
            "A PIT-safe regime proxy candidate exists. Next phase may define exactly one "
            "pre-registered regime-conditioned strategy using a holdout validation."
        )

    if classification == "PIT_PROXY_WEAK_CANDIDATE":
        return (
            "A weak PIT proxy exists but is insufficient for shadow. Require stronger holdout validation."
        )

    if classification == "PIT_PROXY_NO_EDGE_BUCKET":
        return (
            "PIT-safe proxies do not explain the fold-3 edge. Move to a new orthogonal feature family."
        )

    return (
        "PIT proxy diagnostics inconclusive. Do not create a trading rule."
    )
