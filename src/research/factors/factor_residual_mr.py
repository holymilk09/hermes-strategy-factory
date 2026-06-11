"""
Phase 24A — Factor-Neutral Residual Mean Reversion.

Builds a multi-factor (ETF) regression model to compute residual returns
and selects candidates with large negative residual z-scores.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FactorResidualConfig:
    start_date: str = "2024-01-01"
    lookback: int = 60
    min_obs: int = 45
    residual_z_threshold: float = -2.0
    min_factor_r2: float = 0.20
    forward_window: int = 5

    factor_symbols: tuple[str, ...] = (
        "SPY",
        "XLK",
        "XLF",
        "XLV",
        "XLY",
        "XLC",
        "XLI",
        "XLE",
        "XLP",
        "XLU",
        "XLB",
        "XLRE",
        "SMH",
        "IBB",
        "ARKK",
    )

    @property
    def config_hash(self) -> str:
        payload = repr(self).encode("utf-8")
        return sha256(payload).hexdigest()[:16]


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
        raise ValueError(f"Missing timestamp/date column: {path}")

    if "close" not in df.columns:
        raise ValueError(f"Missing close column: {path}")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    # Normalize to midnight UTC for date-only alignment
    df["timestamp"] = df["timestamp"].dt.normalize()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    df = df.dropna(subset=["timestamp", "close"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")

    return df[["timestamp", "close"]].reset_index(drop=True)


def find_ohlcv_path(root: Path, symbol: str) -> Path | None:
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

    return None


def discover_symbol_universe(root: Path, excluded: set[str]) -> list[str]:
    candidates = []

    patterns = [
        root / "data" / "cache" / "ohlcv_1d",
        root / "data" / "cache",
        root / "data",
    ]

    for directory in patterns:
        if not directory.exists():
            continue

        for p in directory.glob("*.csv"):
            name = p.stem.upper()
            name = name.replace("_1D", "").replace("_1d", "")
            if name not in excluded:
                candidates.append(name)

    return sorted(set(candidates))


def build_factor_return_matrix(
    root: Path,
    config: FactorResidualConfig,
) -> pd.DataFrame:
    frames = []

    for symbol in config.factor_symbols:
        path = find_ohlcv_path(root, symbol)
        if path is None:
            continue

        df = load_ohlcv_csv(path)
        df[symbol] = df["close"].pct_change()
        frames.append(df[["timestamp", symbol]])

    if not frames:
        raise FileNotFoundError("No factor OHLCV files found")

    out = frames[0]
    for frame in frames[1:]:
        out = pd.merge(out, frame, on="timestamp", how="inner")

    out = out.sort_values("timestamp").reset_index(drop=True)
    return out


def rolling_factor_residual_features(
    symbol_returns: pd.Series,
    factor_returns: pd.DataFrame,
    lookback: int,
    min_obs: int,
) -> tuple[pd.Series, pd.Series]:
    y = pd.to_numeric(symbol_returns, errors="coerce").reset_index(drop=True)
    x = factor_returns.reset_index(drop=True).astype(float)

    residual = pd.Series(np.nan, index=y.index, dtype=float)
    r2 = pd.Series(np.nan, index=y.index, dtype=float)

    for i in range(len(y)):
        start = max(0, i - lookback + 1)
        end = i + 1

        y_win = y.iloc[start:end]
        x_win = x.iloc[start:end]

        valid = y_win.notna()
        for col in x_win.columns:
            valid &= x_win[col].notna()

        if int(valid.sum()) < min_obs:
            continue

        yv = y_win[valid].to_numpy(dtype=float)
        xv = x_win[valid].to_numpy(dtype=float)

        # Add intercept
        X = np.column_stack([np.ones(len(xv)), xv])

        try:
            beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
        except np.linalg.LinAlgError:
            continue

        x_current = x.iloc[i].to_numpy(dtype=float)

        if not np.isfinite(x_current).all() or not np.isfinite(y.iloc[i]):
            continue

        pred = float(np.dot(np.r_[1.0, x_current], beta))
        resid = float(y.iloc[i] - pred)

        y_hat = X @ beta
        ss_res = float(np.sum((yv - y_hat) ** 2))
        ss_tot = float(np.sum((yv - np.mean(yv)) ** 2))

        model_r2 = np.nan if ss_tot == 0 else 1.0 - ss_res / ss_tot

        residual.iloc[i] = resid
        r2.iloc[i] = model_r2

    resid_std = residual.rolling(lookback, min_periods=min_obs).std()
    residual_z = residual / resid_std.replace(0, np.nan)

    return residual_z.rename("factor_residual_z"), r2.rename("factor_model_r2")


def compute_rsi_2(close: pd.Series) -> pd.Series:
    close = pd.to_numeric(close, errors="coerce")
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(2, min_periods=2).mean()
    avg_loss = loss.rolling(2, min_periods=2).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi.fillna(50.0).rename("rsi_2")


def compute_forward_return(close: pd.Series, window: int) -> pd.Series:
    return (close.shift(-window) / close - 1.0).rename("forward_return")


def build_symbol_factor_residual_candidates(
    root: Path,
    symbol: str,
    factor_matrix: pd.DataFrame,
    config: FactorResidualConfig,
) -> pd.DataFrame:
    path = find_ohlcv_path(root, symbol)
    if path is None:
        raise FileNotFoundError(f"No OHLCV found for {symbol}")

    sym = load_ohlcv_csv(path)
    sym["symbol_return"] = sym["close"].pct_change()

    merged = pd.merge(
        sym,
        factor_matrix,
        on="timestamp",
        how="inner",
    )

    factor_cols = [c for c in factor_matrix.columns if c != "timestamp"]

    residual_z, model_r2 = rolling_factor_residual_features(
        symbol_returns=merged["symbol_return"],
        factor_returns=merged[factor_cols],
        lookback=config.lookback,
        min_obs=config.min_obs,
    )

    out = pd.DataFrame()
    out["timestamp"] = merged["timestamp"]
    out["symbol"] = symbol
    out["close"] = merged["close"]
    out["factor_residual_z"] = residual_z
    out["factor_model_r2"] = model_r2
    out["residual_z"] = residual_z
    out["residual_r2"] = model_r2
    out["rsi_2"] = compute_rsi_2(merged["close"])
    out["forward_return"] = compute_forward_return(merged["close"], config.forward_window)

    out["strategy"] = "factor_residual_mr"
    out["selected"] = (
        (out["factor_residual_z"] <= config.residual_z_threshold)
        & (out["factor_model_r2"] >= config.min_factor_r2)
    )

    out["lineage"] = "factor_neutral_residual_mr_phase24a"
    out["feature_config_hash"] = config.config_hash

    out = out[out["timestamp"] >= pd.Timestamp(config.start_date, tz="UTC")]
    out = out.dropna(
        subset=[
            "timestamp",
            "symbol",
            "factor_residual_z",
            "factor_model_r2",
            "forward_return",
        ]
    )

    out = out.sort_values("timestamp").reset_index(drop=True)

    raw = (
        out["timestamp"].astype(str)
        + "|"
        + out["symbol"].astype(str)
        + "|factor_residual_mr"
    )
    out["candidate_id"] = raw.map(lambda x: sha256(x.encode("utf-8")).hexdigest()[:24])

    return out


def build_factor_residual_candidate_ledger(
    root: Path,
    config: FactorResidualConfig | None = None,
) -> pd.DataFrame:
    config = config or FactorResidualConfig()

    factor_matrix = build_factor_return_matrix(root, config)

    excluded = set(config.factor_symbols)
    symbols = discover_symbol_universe(root, excluded=excluded)

    frames = []
    failures = []

    for symbol in symbols:
        try:
            frame = build_symbol_factor_residual_candidates(
                root=root,
                symbol=symbol,
                factor_matrix=factor_matrix,
                config=config,
            )
            if not frame.empty:
                frames.append(frame)
        except Exception as exc:
            failures.append((symbol, f"{type(exc).__name__}: {exc}"))

    if not frames:
        raise ValueError(f"No candidate frames built. failures={failures[:10]}")

    ledger = pd.concat(frames, axis=0, ignore_index=True)
    ledger = ledger.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    if ledger["candidate_id"].duplicated().any():
        dupes = int(ledger["candidate_id"].duplicated().sum())
        raise ValueError(f"Duplicate candidate_id rows: {dupes}")

    ledger.attrs["failures"] = failures
    ledger.attrs["factor_symbols_used"] = [c for c in factor_matrix.columns if c != "timestamp"]

    return ledger


def summarize_ledger(df: pd.DataFrame) -> dict[str, Any]:
    selected = df[df["selected"]].copy()
    rejected = df[~df["selected"]].copy()

    def part_summary(part: pd.DataFrame) -> dict[str, Any]:
        if part.empty:
            return {"rows": 0, "mean": None, "hit": None}

        r = pd.to_numeric(part["forward_return"], errors="coerce").dropna()

        if r.empty:
            return {"rows": 0, "mean": None, "hit": None}

        return {
            "rows": int(len(r)),
            "mean": float(r.mean()),
            "hit": float((r > 0).mean()),
        }

    s = part_summary(selected)
    r = part_summary(rejected)

    spread = None
    if s["mean"] is not None and r["mean"] is not None:
        spread = s["mean"] - r["mean"]

    return {
        "candidate_rows": int(len(df)),
        "selected_rows": int(df["selected"].sum()),
        "rejected_rows": int((~df["selected"]).sum()),
        "latest_candidate_ts": df["timestamp"].max().isoformat(),
        "latest_selected_ts": selected["timestamp"].max().isoformat() if not selected.empty else None,
        "selected": s,
        "rejected": r,
        "spread": spread,
        "factor_symbols_used": df.attrs.get("factor_symbols_used", []),
        "failures": df.attrs.get("failures", []),
    }


def build_trade_ledger(candidate_ledger: pd.DataFrame) -> pd.DataFrame:
    selected = candidate_ledger[candidate_ledger["selected"]].copy()
    selected = selected.rename(columns={"forward_return": "realized_return"})

    keep = [
        "timestamp",
        "symbol",
        "strategy",
        "realized_return",
        "factor_residual_z",
        "factor_model_r2",
        "residual_z",
        "residual_r2",
        "rsi_2",
        "candidate_id",
        "lineage",
        "feature_config_hash",
    ]

    existing = [c for c in keep if c in selected.columns]
    return selected[existing].sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def write_csv_atomic(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)
