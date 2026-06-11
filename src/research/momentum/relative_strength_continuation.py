from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RelativeStrengthConfig:
    start_date: str = "2024-01-01"
    forward_window: int = 10
    ret_20d_rank_threshold: float = 0.85
    ret_60d_rank_threshold: float = 0.70
    min_selected_total: int = 200
    min_selected_per_fold: int = 40

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

    keep = ["timestamp", "open", "high", "low", "close"]
    if "volume" in df.columns:
        keep.append("volume")

    return df[keep].reset_index(drop=True)


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


def discover_symbol_universe(root: Path) -> list[str]:
    excluded = {
        "SPY", "QQQ", "IWM",
        "XLK", "XLF", "XLV", "XLY", "XLC", "XLI",
        "XLE", "XLP", "XLU", "XLB", "XLRE",
        "SMH", "IBB", "ARKK",
    }

    symbols: list[str] = []

    for d in [root / "data" / "cache" / "ohlcv_1d", root / "data" / "cache", root / "data"]:
        if not d.exists():
            continue

        for p in d.glob("*.csv"):
            symbol = p.stem.upper().replace("_1D", "").replace("_1d", "")
            if symbol not in excluded:
                symbols.append(symbol)

    return sorted(set(symbols))


def build_symbol_momentum_frame(
    root: Path,
    symbol: str,
    config: RelativeStrengthConfig | None = None,
) -> pd.DataFrame:
    config = config or RelativeStrengthConfig()

    path = find_ohlcv_path(root, symbol)
    if path is None:
        raise FileNotFoundError(f"No OHLCV found for {symbol}")

    df = load_ohlcv_csv(path)
    close = df["close"]

    out = pd.DataFrame()
    out["timestamp"] = df["timestamp"]
    out["symbol"] = symbol
    out["close"] = close
    out["ret_5d"] = close / close.shift(5) - 1.0
    out["ret_20d"] = close / close.shift(20) - 1.0
    out["ret_60d"] = close / close.shift(60) - 1.0
    out["ma50"] = close.rolling(50, min_periods=50).mean()
    out["close_above_ma50"] = close > out["ma50"]
    out["forward_return"] = close.shift(-config.forward_window) / close - 1.0

    out = out[out["timestamp"] >= pd.Timestamp(config.start_date, tz="UTC")]

    out = out.dropna(
        subset=[
            "timestamp",
            "symbol",
            "ret_5d",
            "ret_20d",
            "ret_60d",
            "ma50",
            "forward_return",
        ]
    )

    return out.sort_values("timestamp").reset_index(drop=True)


def build_relative_strength_candidate_ledger(
    root: Path,
    config: RelativeStrengthConfig | None = None,
) -> pd.DataFrame:
    config = config or RelativeStrengthConfig()

    symbols = discover_symbol_universe(root)
    frames = []
    failures = []

    for symbol in symbols:
        try:
            frame = build_symbol_momentum_frame(root, symbol, config)
            if not frame.empty:
                frames.append(frame)
        except Exception as exc:
            failures.append((symbol, f"{type(exc).__name__}: {exc}"))

    if not frames:
        raise ValueError(f"No symbol frames built. failures={failures[:10]}")

    ledger = pd.concat(frames, axis=0, ignore_index=True)
    ledger = ledger.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    ledger["ret_20d_rank"] = ledger.groupby("timestamp")["ret_20d"].rank(pct=True)
    ledger["ret_60d_rank"] = ledger.groupby("timestamp")["ret_60d"].rank(pct=True)

    ledger["selected"] = (
        (ledger["ret_20d_rank"] >= config.ret_20d_rank_threshold)
        & (ledger["ret_60d_rank"] >= config.ret_60d_rank_threshold)
        & (ledger["close_above_ma50"].astype(bool))
        & (ledger["ret_5d"] > 0)
    )

    ledger["strategy"] = "relative_strength_continuation"
    ledger["lineage"] = "relative_strength_continuation_phase28a"
    ledger["feature_config_hash"] = config.config_hash

    raw = (
        ledger["timestamp"].astype(str)
        + "|"
        + ledger["symbol"].astype(str)
        + "|relative_strength_continuation"
    )
    ledger["candidate_id"] = raw.map(lambda x: sha256(x.encode("utf-8")).hexdigest()[:24])

    if ledger["candidate_id"].duplicated().any():
        dupes = int(ledger["candidate_id"].duplicated().sum())
        raise ValueError(f"Duplicate candidate_id rows: {dupes}")

    ledger.attrs["failures"] = failures
    return ledger


def audit_rule(
    df: pd.DataFrame, config: RelativeStrengthConfig | None = None
) -> dict[str, Any]:
    config = config or RelativeStrengthConfig()

    expected = (
        (pd.to_numeric(df["ret_20d_rank"], errors="coerce") >= config.ret_20d_rank_threshold)
        & (pd.to_numeric(df["ret_60d_rank"], errors="coerce") >= config.ret_60d_rank_threshold)
        & (df["close_above_ma50"].astype(bool))
        & (pd.to_numeric(df["ret_5d"], errors="coerce") > 0)
    )

    actual = df["selected"].astype(bool)
    mismatch = actual.ne(expected)

    return {
        "rule": (
            f"ret_20d_rank >= {config.ret_20d_rank_threshold} AND "
            f"ret_60d_rank >= {config.ret_60d_rank_threshold} AND "
            "close_above_ma50 == true AND ret_5d > 0"
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
        return {"trades": 0, "mean": None, "hit_rate": None}

    r = pd.to_numeric(df["forward_return"], errors="coerce").dropna()

    if r.empty:
        return {"trades": 0, "mean": None, "hit_rate": None}

    return {
        "trades": int(len(r)),
        "mean": float(r.mean()),
        "hit_rate": float((r > 0).mean()),
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
        "latest_selected_ts": (
            selected["timestamp"].max().isoformat() if not selected.empty else None
        ),
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
        "ret_5d",
        "ret_20d",
        "ret_60d",
        "ret_20d_rank",
        "ret_60d_rank",
        "close_above_ma50",
        "candidate_id",
        "lineage",
        "feature_config_hash",
    ]

    existing = [c for c in keep if c in selected.columns]
    return selected[existing].sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def build_time_folds(df: pd.DataFrame, n_folds: int = 4) -> pd.DataFrame:
    timestamps = sorted(pd.to_datetime(df["timestamp"], utc=True).dropna().unique())
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


def evaluate_folds(df: pd.DataFrame, n_folds: int = 4) -> pd.DataFrame:
    folds = build_time_folds(df, n_folds)
    rows = []

    for _, fold in folds.iterrows():
        part = df[(df["timestamp"] >= fold["start"]) & (df["timestamp"] <= fold["end"])].copy()

        selected = part[part["selected"]].copy()
        rejected = part[~part["selected"]].copy()

        s = summarize_returns(selected)
        r = summarize_returns(rejected)

        spread = None
        if s["mean"] is not None and r["mean"] is not None:
            spread = s["mean"] - r["mean"]

        rows.append(
            {
                "fold": int(fold["fold"]),
                "candidate_rows": int(len(part)),
                "selected_rows": s["trades"],
                "rejected_rows": r["trades"],
                "selected_mean": s["mean"],
                "selected_hit": s["hit_rate"],
                "rejected_mean": r["mean"],
                "rejected_hit": r["hit_rate"],
                "spread": spread,
            }
        )

    return pd.DataFrame(rows)


def random_baseline(
    df: pd.DataFrame,
    n: int = 500,
    seed: int = 42,
) -> dict[str, Any]:
    selected_count = int(df["selected"].sum())

    if selected_count <= 0:
        return {"classification": "NO_SELECTED_ROWS"}

    observed_mean = summarize_returns(df[df["selected"]])["mean"]

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
    elif pct >= 0.90:
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


def classify_relative_strength(
    df: pd.DataFrame,
    rule_audit: dict[str, Any],
    fold_df: pd.DataFrame,
    rand: dict[str, Any],
    config: RelativeStrengthConfig | None = None,
) -> str:
    config = config or RelativeStrengthConfig()

    if not rule_audit.get("pass"):
        return "RULE_AUDIT_FAIL"

    if int(df["selected"].sum()) < config.min_selected_total:
        return "TRUE_WALK_FORWARD_INCONCLUSIVE"

    if (fold_df["selected_rows"] < config.min_selected_per_fold).any():
        return "TRUE_WALK_FORWARD_INCONCLUSIVE"

    selected_means = fold_df["selected_mean"].dropna()
    selected_hits = fold_df["selected_hit"].dropna()
    spreads = fold_df["spread"].dropna()

    if selected_means.empty or selected_hits.empty or spreads.empty:
        return "TRUE_WALK_FORWARD_FAIL"

    avg_mean = float(selected_means.mean())
    avg_hit = float(selected_hits.mean())
    avg_spread = float(spreads.mean())
    positive_spread_rate = float((spreads > 0).mean())

    random_pct = rand.get("random_percentile")

    if avg_mean < 0.010:
        return "TRUE_WALK_FORWARD_FAIL"

    if avg_hit < 0.54:
        return "TRUE_WALK_FORWARD_FAIL"

    if avg_spread < 0.005:
        return "TRUE_WALK_FORWARD_FAIL"

    if positive_spread_rate < 0.75:
        return "TRUE_WALK_FORWARD_FAIL"

    if random_pct is None or random_pct < 0.90:
        return "TRUE_WALK_FORWARD_FAIL"

    if positive_spread_rate >= 1.0 and random_pct >= 0.95:
        return "TRUE_WALK_FORWARD_PASS"

    return "TRUE_WALK_FORWARD_WEAK_PASS"


def write_csv_atomic(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)
