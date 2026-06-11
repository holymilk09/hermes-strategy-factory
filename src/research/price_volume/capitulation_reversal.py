"""
Phase 24B — Price-Volume Capitulation Reversal.

Selects stocks with sharp downside moves (ret_3d_z <= -2.0),
abnormal volume expansion (volume_z_20 >= 1.5), and close in
the upper 60% of the daily range (close_location >= 0.60).
Tests 5-day forward mean reversion.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CapitulationConfig:
    start_date: str = "2024-01-01"
    ret_window: int = 3
    ret_z_lookback: int = 60
    volume_z_lookback: int = 20
    forward_window: int = 5

    ret_3d_z_threshold: float = -2.0
    volume_z_threshold: float = 1.5
    close_location_threshold: float = 0.60

    min_selected_total: int = 100
    min_selected_per_fold: int = 20

    @property
    def config_hash(self) -> str:
        return sha256(repr(self).encode("utf-8")).hexdigest()[:16]


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

    required = ["open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns {missing}: {path}")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    # Normalize to midnight UTC for date-only alignment
    df["timestamp"] = df["timestamp"].dt.normalize()

    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["timestamp", "open", "high", "low", "close", "volume"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")

    return df[["timestamp", "open", "high", "low", "close", "volume"]].reset_index(drop=True)


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

    for p in candidates:
        if p.exists():
            return p

    return None


def discover_symbol_universe(root: Path, excluded: set[str] | None = None) -> list[str]:
    excluded = excluded or set()
    symbols: list[str] = []

    dirs = [
        root / "data" / "cache" / "ohlcv_1d",
        root / "data" / "cache",
        root / "data",
    ]

    for d in dirs:
        if not d.exists():
            continue

        for p in d.glob("*.csv"):
            name = p.stem.upper()
            name = name.replace("_1D", "").replace("_1d", "")
            if name not in excluded:
                symbols.append(name)

    return sorted(set(symbols))


def zscore_trailing(series: pd.Series, lookback: int) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce")
    mean = x.rolling(lookback, min_periods=lookback).mean()
    std = x.rolling(lookback, min_periods=lookback).std()
    return (x - mean) / std.replace(0, np.nan)


def compute_close_location(df: pd.DataFrame) -> pd.Series:
    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")
    close = pd.to_numeric(df["close"], errors="coerce")

    rng = high - low
    loc = (close - low) / rng.replace(0, np.nan)

    return loc.fillna(0.5).clip(0.0, 1.0)


def build_symbol_capitulation_candidates(
    root: Path,
    symbol: str,
    config: CapitulationConfig | None = None,
) -> pd.DataFrame:
    config = config or CapitulationConfig()

    path = find_ohlcv_path(root, symbol)
    if path is None:
        raise FileNotFoundError(f"No OHLCV found for {symbol}")

    df = load_ohlcv_csv(path)

    close = df["close"]
    volume = df["volume"]

    ret_1d = close.pct_change()
    ret_3d = close / close.shift(config.ret_window) - 1.0

    ret_3d_z = zscore_trailing(ret_3d, config.ret_z_lookback)
    volume_z_20 = zscore_trailing(volume, config.volume_z_lookback)
    close_location = compute_close_location(df)

    forward_return = close.shift(-config.forward_window) / close - 1.0

    out = pd.DataFrame()
    out["timestamp"] = df["timestamp"]
    out["symbol"] = symbol
    out["close"] = close
    out["ret_1d"] = ret_1d
    out["ret_3d"] = ret_3d
    out["ret_3d_z"] = ret_3d_z
    out["volume_z_20"] = volume_z_20
    out["close_location"] = close_location
    out["forward_return"] = forward_return
    out["strategy"] = "price_volume_capitulation"
    out["lineage"] = "price_volume_capitulation_phase24b"
    out["feature_config_hash"] = config.config_hash

    out["selected"] = (
        (out["ret_3d_z"] <= config.ret_3d_z_threshold)
        & (out["volume_z_20"] >= config.volume_z_threshold)
        & (out["close_location"] >= config.close_location_threshold)
    )

    out = out[out["timestamp"] >= pd.Timestamp(config.start_date, tz="UTC")]

    out = out.dropna(
        subset=[
            "timestamp",
            "symbol",
            "ret_3d_z",
            "volume_z_20",
            "close_location",
            "forward_return",
        ]
    )

    out = out.sort_values("timestamp").reset_index(drop=True)

    raw = (
        out["timestamp"].astype(str)
        + "|"
        + out["symbol"].astype(str)
        + "|price_volume_capitulation"
    )
    out["candidate_id"] = raw.map(lambda x: sha256(x.encode("utf-8")).hexdigest()[:24])

    return out


def build_capitulation_candidate_ledger(
    root: Path,
    config: CapitulationConfig | None = None,
) -> pd.DataFrame:
    config = config or CapitulationConfig()

    excluded = {
        "SPY", "QQQ", "IWM",
        "XLK", "XLF", "XLV", "XLY", "XLC", "XLI",
        "XLE", "XLP", "XLU", "XLB", "XLRE",
        "SMH", "IBB", "ARKK",
    }

    symbols = discover_symbol_universe(root, excluded=excluded)

    frames = []
    failures = []

    for symbol in symbols:
        try:
            frame = build_symbol_capitulation_candidates(root, symbol, config)
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
    return ledger


def audit_selection_rule(
    df: pd.DataFrame,
    config: CapitulationConfig | None = None,
) -> dict[str, Any]:
    config = config or CapitulationConfig()

    expected = (
        (pd.to_numeric(df["ret_3d_z"], errors="coerce") <= config.ret_3d_z_threshold)
        & (pd.to_numeric(df["volume_z_20"], errors="coerce") >= config.volume_z_threshold)
        & (pd.to_numeric(df["close_location"], errors="coerce") >= config.close_location_threshold)
    )

    actual = df["selected"].astype(bool)
    mismatch = actual.ne(expected)

    return {
        "rule": (
            f"ret_3d_z <= {config.ret_3d_z_threshold} "
            f"AND volume_z_20 >= {config.volume_z_threshold} "
            f"AND close_location >= {config.close_location_threshold}"
        ),
        "rows": int(len(df)),
        "selected_actual": int(actual.sum()),
        "selected_expected": int(expected.sum()),
        "mismatch_count": int(mismatch.sum()),
        "mismatch_rate": float(mismatch.mean()) if len(df) else None,
        "pass": int(mismatch.sum()) == 0,
    }


def summarize_returns(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "trades": 0,
            "mean": None,
            "median": None,
            "hit_rate": None,
            "sum_return": 0.0,
            "std": None,
            "sharpe_proxy": None,
        }

    r = pd.to_numeric(df["forward_return"], errors="coerce").dropna()

    if r.empty:
        return {
            "trades": 0,
            "mean": None,
            "median": None,
            "hit_rate": None,
            "sum_return": 0.0,
            "std": None,
            "sharpe_proxy": None,
        }

    std = float(r.std(ddof=1)) if len(r) > 1 else 0.0

    return {
        "trades": int(len(r)),
        "mean": float(r.mean()),
        "median": float(r.median()),
        "hit_rate": float((r > 0).mean()),
        "sum_return": float(r.sum()),
        "std": std,
        "sharpe_proxy": None if std == 0 else float(r.mean() / std),
    }


def summarize_ledger(df: pd.DataFrame) -> dict[str, Any]:
    selected = df[df["selected"]].copy()
    rejected = df[~df["selected"]].copy()

    s = summarize_returns(selected)
    r = summarize_returns(rejected)

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
        "ret_3d_z",
        "volume_z_20",
        "close_location",
        "ret_3d",
        "ret_1d",
        "candidate_id",
        "lineage",
        "feature_config_hash",
    ]

    existing = [c for c in keep if c in selected.columns]
    return selected[existing].sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def build_time_folds(df: pd.DataFrame, n_folds: int = 4) -> list[tuple[int, pd.Timestamp, pd.Timestamp]]:
    timestamps = sorted(pd.to_datetime(df["timestamp"], utc=True).dropna().unique())

    if len(timestamps) < n_folds:
        raise ValueError("Not enough unique timestamps for folds")

    chunks = np.array_split(np.array(timestamps), n_folds)

    folds = []
    for i, chunk in enumerate(chunks, start=1):
        folds.append((i, pd.Timestamp(chunk[0]), pd.Timestamp(chunk[-1])))

    return folds


def evaluate_folds(df: pd.DataFrame, n_folds: int = 4) -> pd.DataFrame:
    rows = []

    for fold, start, end in build_time_folds(df, n_folds):
        part = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].copy()

        selected = part[part["selected"]].copy()
        rejected = part[~part["selected"]].copy()

        s = summarize_returns(selected)
        r = summarize_returns(rejected)

        spread = None
        if s["mean"] is not None and r["mean"] is not None:
            spread = s["mean"] - r["mean"]

        rows.append(
            {
                "fold": fold,
                "test_start": start,
                "test_end": end,
                "candidate_rows": int(len(part)),
                "selected_rows": int(len(selected)),
                "rejected_rows": int(len(rejected)),
                "selected_mean": s["mean"],
                "selected_hit": s["hit_rate"],
                "rejected_mean": r["mean"],
                "rejected_hit": r["hit_rate"],
                "selected_vs_rejected_spread": spread,
            }
        )

    return pd.DataFrame(rows)


def random_selection_baseline(
    df: pd.DataFrame,
    n: int = 500,
    seed: int = 42,
) -> dict[str, Any]:
    selected_count = int(df["selected"].sum())

    if selected_count <= 0:
        return {
            "runs": 0,
            "observed_mean": None,
            "random_mean_avg": None,
            "random_percentile": None,
            "classification": "NO_SELECTED_ROWS",
        }

    observed_mean = summarize_returns(df[df["selected"]])["mean"]

    if observed_mean is None:
        return {
            "runs": 0,
            "observed_mean": None,
            "random_mean_avg": None,
            "random_percentile": None,
            "classification": "NO_OBSERVED_MEAN",
        }

    rng = np.random.default_rng(seed)
    returns = pd.to_numeric(df["forward_return"], errors="coerce").fillna(0.0).to_numpy()
    idx_all = np.arange(len(df))

    means = []
    for _ in range(n):
        idx = rng.choice(idx_all, size=selected_count, replace=False)
        means.append(float(np.mean(returns[idx])))

    arr = np.array(means)
    pct = float(np.mean(arr <= observed_mean))

    if pct >= 0.95:
        cls = "STRONG_VS_RANDOM"
    elif pct >= 0.75:
        cls = "OK_VS_RANDOM"
    else:
        cls = "WEAK_VS_RANDOM"

    return {
        "runs": int(n),
        "selected_count": selected_count,
        "observed_mean": float(observed_mean),
        "random_mean_avg": float(arr.mean()),
        "random_p05": float(np.percentile(arr, 5)),
        "random_p50": float(np.percentile(arr, 50)),
        "random_p95": float(np.percentile(arr, 95)),
        "random_percentile": pct,
        "classification": cls,
    }


def classify_capitulation_result(
    df: pd.DataFrame,
    rule_audit: dict[str, Any],
    fold_df: pd.DataFrame,
    random_baseline: dict[str, Any],
    config: CapitulationConfig | None = None,
) -> str:
    config = config or CapitulationConfig()

    if not rule_audit.get("pass"):
        return "RULE_AUDIT_FAIL"

    selected_count = int(df["selected"].sum())
    if selected_count < config.min_selected_total:
        return "TRUE_WALK_FORWARD_INCONCLUSIVE"

    if fold_df.empty:
        return "TRUE_WALK_FORWARD_INCONCLUSIVE"

    if (fold_df["selected_rows"] < config.min_selected_per_fold).any():
        return "TRUE_WALK_FORWARD_INCONCLUSIVE"

    selected_means = fold_df["selected_mean"].dropna()
    selected_hits = fold_df["selected_hit"].dropna()
    spreads = fold_df["selected_vs_rejected_spread"].dropna()

    if selected_means.empty or selected_hits.empty or spreads.empty:
        return "TRUE_WALK_FORWARD_FAIL"

    positive_mean_rate = float((selected_means > 0).mean())
    positive_spread_rate = float((spreads > 0).mean())
    avg_mean = float(selected_means.mean())
    avg_hit = float(selected_hits.mean())
    avg_spread = float(spreads.mean())

    random_pct = random_baseline.get("random_percentile")

    if avg_mean < 0.005:
        return "TRUE_WALK_FORWARD_FAIL"

    if avg_hit < 0.52:
        return "TRUE_WALK_FORWARD_FAIL"

    if avg_spread < 0.005:
        return "TRUE_WALK_FORWARD_FAIL"

    if positive_mean_rate < 0.75:
        return "TRUE_WALK_FORWARD_FAIL"

    if positive_spread_rate < 0.75:
        return "TRUE_WALK_FORWARD_FAIL"

    if random_pct is None or random_pct < 0.75:
        return "TRUE_WALK_FORWARD_FAIL"

    if positive_mean_rate >= 1.0 and positive_spread_rate >= 1.0 and random_pct >= 0.95:
        return "TRUE_WALK_FORWARD_PASS"

    return "TRUE_WALK_FORWARD_WEAK_PASS"


def write_csv_atomic(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)
