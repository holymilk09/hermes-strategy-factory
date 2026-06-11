from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SECTOR_ETFS = {
    "TECH": "XLK",
    "FINANCIALS": "XLF",
    "HEALTHCARE": "XLV",
    "CONSUMER_DISCRETIONARY": "XLY",
    "COMMUNICATIONS": "XLC",
    "INDUSTRIALS": "XLI",
    "ENERGY": "XLE",
    "CONSUMER_STAPLES": "XLP",
    "UTILITIES": "XLU",
    "MATERIALS": "XLB",
    "REAL_ESTATE": "XLRE",
    "SEMIS": "SMH",
    "BIOTECH": "IBB",
    "INNOVATION": "ARKK",
}


SYMBOL_SECTOR_HINTS = {
    "AAPL": "TECH",
    "MSFT": "TECH",
    "ADBE": "TECH",
    "CRM": "TECH",
    "ORCL": "TECH",
    "NOW": "TECH",
    "PANW": "TECH",
    "AMD": "SEMIS",
    "NVDA": "SEMIS",
    "AVGO": "SEMIS",
    "TSM": "SEMIS",
    "MU": "SEMIS",
    "QCOM": "SEMIS",
    "INTC": "SEMIS",
    "JPM": "FINANCIALS",
    "BAC": "FINANCIALS",
    "GS": "FINANCIALS",
    "MS": "FINANCIALS",
    "V": "FINANCIALS",
    "MA": "FINANCIALS",
    "UNH": "HEALTHCARE",
    "LLY": "HEALTHCARE",
    "MRK": "HEALTHCARE",
    "ABBV": "HEALTHCARE",
    "PFE": "HEALTHCARE",
    "AMGN": "BIOTECH",
    "GILD": "BIOTECH",
    "REGN": "BIOTECH",
    "TSLA": "CONSUMER_DISCRETIONARY",
    "AMZN": "CONSUMER_DISCRETIONARY",
    "HD": "CONSUMER_DISCRETIONARY",
    "NKE": "CONSUMER_DISCRETIONARY",
    "META": "COMMUNICATIONS",
    "GOOGL": "COMMUNICATIONS",
    "GOOG": "COMMUNICATIONS",
    "NFLX": "COMMUNICATIONS",
    "DIS": "COMMUNICATIONS",
    "CAT": "INDUSTRIALS",
    "GE": "INDUSTRIALS",
    "HON": "INDUSTRIALS",
    "BA": "INDUSTRIALS",
    "XOM": "ENERGY",
    "CVX": "ENERGY",
    "COP": "ENERGY",
    "SLB": "ENERGY",
    "PG": "CONSUMER_STAPLES",
    "KO": "CONSUMER_STAPLES",
    "PEP": "CONSUMER_STAPLES",
    "COST": "CONSUMER_STAPLES",
    "NEE": "UTILITIES",
    "DUK": "UTILITIES",
    "SO": "UTILITIES",
    "LIN": "MATERIALS",
    "SHW": "MATERIALS",
    "FCX": "MATERIALS",
    "PLD": "REAL_ESTATE",
    "AMT": "REAL_ESTATE",
    "EQIX": "REAL_ESTATE",
}


@dataclass(frozen=True)
class SectorResidualConfig:
    start_date: str = "2024-01-01"
    lookback: int = 60
    min_obs: int = 45
    residual_z_threshold: float = -2.0
    min_model_r2: float = 0.15
    forward_window: int = 5

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

    if "close" not in df.columns:
        raise ValueError(f"Missing close column: {path}")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
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

    for p in candidates:
        if p.exists():
            return p

    return None


def discover_symbol_universe(root: Path) -> list[str]:
    excluded = set(SECTOR_ETFS.values()) | {"SPY", "QQQ", "IWM"}

    symbols = []

    for d in [root / "data" / "cache" / "ohlcv_1d", root / "data" / "cache", root / "data"]:
        if not d.exists():
            continue

        for p in d.glob("*.csv"):
            symbol = p.stem.upper().replace("_1D", "").replace("_1d", "")
            if symbol not in excluded:
                symbols.append(symbol)

    return sorted(set(symbols))


def sector_etf_for_symbol(symbol: str) -> tuple[str, str, str]:
    sector = SYMBOL_SECTOR_HINTS.get(symbol.upper())

    if sector is None:
        return "SPY", "FALLBACK_SPY", "UNKNOWN"

    return SECTOR_ETFS[sector], "STATIC_MAP", sector


def rolling_sector_residual_features(
    stock_ret: pd.Series,
    sector_ret: pd.Series,
    lookback: int,
    min_obs: int,
) -> tuple[pd.Series, pd.Series]:
    y = pd.to_numeric(stock_ret, errors="coerce").reset_index(drop=True)
    x = pd.to_numeric(sector_ret, errors="coerce").reset_index(drop=True)

    residual = pd.Series(np.nan, index=y.index, dtype=float)
    model_r2 = pd.Series(np.nan, index=y.index, dtype=float)

    for i in range(len(y)):
        start = max(0, i - lookback + 1)
        end = i + 1

        y_win = y.iloc[start:end]
        x_win = x.iloc[start:end]

        valid = y_win.notna() & x_win.notna()

        if int(valid.sum()) < min_obs:
            continue

        yv = y_win[valid].to_numpy(dtype=float)
        xv = x_win[valid].to_numpy(dtype=float)

        X = np.column_stack([np.ones(len(xv)), xv])

        try:
            beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
        except np.linalg.LinAlgError:
            continue

        if not np.isfinite(x.iloc[i]) or not np.isfinite(y.iloc[i]):
            continue

        pred = float(beta[0] + beta[1] * x.iloc[i])
        resid = float(y.iloc[i] - pred)

        y_hat = X @ beta
        ss_res = float(np.sum((yv - y_hat) ** 2))
        ss_tot = float(np.sum((yv - np.mean(yv)) ** 2))
        r2 = np.nan if ss_tot == 0 else 1.0 - ss_res / ss_tot

        residual.iloc[i] = resid
        model_r2.iloc[i] = r2

    resid_std = residual.rolling(lookback, min_periods=min_obs).std()
    residual_z = residual / resid_std.replace(0, np.nan)

    return residual_z.rename("sector_residual_z"), model_r2.rename("sector_model_r2")


def build_symbol_sector_residual_candidates(
    root: Path,
    symbol: str,
    config: SectorResidualConfig | None = None,
) -> pd.DataFrame:
    config = config or SectorResidualConfig()

    stock_path = find_ohlcv_path(root, symbol)
    if stock_path is None:
        raise FileNotFoundError(f"No OHLCV found for {symbol}")

    sector_etf, sector_source, sector_name = sector_etf_for_symbol(symbol)

    sector_path = find_ohlcv_path(root, sector_etf)
    if sector_path is None:
        sector_etf = "SPY"
        sector_source = "FALLBACK_SPY_NO_SECTOR_ETF"
        sector_name = "UNKNOWN"
        sector_path = find_ohlcv_path(root, "SPY")

    if sector_path is None:
        raise FileNotFoundError(f"No sector ETF or SPY OHLCV found for {symbol}")

    stock = load_ohlcv_csv(stock_path)
    sector = load_ohlcv_csv(sector_path)

    merged = (
        pd.merge(
            stock.rename(columns={"close": "stock_close"}),
            sector.rename(columns={"close": "sector_close"}),
            on="timestamp",
            how="inner",
        )
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    stock_ret = merged["stock_close"].pct_change()
    sector_ret = merged["sector_close"].pct_change()

    residual_z, model_r2 = rolling_sector_residual_features(
        stock_ret=stock_ret,
        sector_ret=sector_ret,
        lookback=config.lookback,
        min_obs=config.min_obs,
    )

    forward_return = (
        merged["stock_close"].shift(-config.forward_window) / merged["stock_close"] - 1.0
    )

    out = pd.DataFrame()
    out["timestamp"] = merged["timestamp"]
    out["symbol"] = symbol
    out["sector_etf"] = sector_etf
    out["sector_source"] = sector_source
    out["sector_name"] = sector_name
    out["stock_close"] = merged["stock_close"]
    out["sector_close"] = merged["sector_close"]
    out["sector_residual_z"] = residual_z
    out["sector_model_r2"] = model_r2
    out["residual_z"] = residual_z
    out["residual_r2"] = model_r2
    out["forward_return"] = forward_return
    out["strategy"] = "sector_residual_mr"
    out["lineage"] = "sector_residual_mr_phase27a"
    out["feature_config_hash"] = config.config_hash

    out["selected"] = (
        (out["sector_residual_z"] <= config.residual_z_threshold)
        & (out["sector_model_r2"] >= config.min_model_r2)
    )

    out = out[out["timestamp"] >= pd.Timestamp(config.start_date, tz="UTC")]
    out = out.dropna(
        subset=[
            "timestamp",
            "symbol",
            "sector_residual_z",
            "sector_model_r2",
            "forward_return",
        ]
    )

    raw = (
        out["timestamp"].astype(str)
        + "|"
        + out["symbol"].astype(str)
        + "|sector_residual_mr"
    )
    out["candidate_id"] = raw.map(lambda x: sha256(x.encode("utf-8")).hexdigest()[:24])

    return out.sort_values("timestamp").reset_index(drop=True)


def build_sector_residual_candidate_ledger(
    root: Path,
    config: SectorResidualConfig | None = None,
) -> pd.DataFrame:
    config = config or SectorResidualConfig()

    symbols = discover_symbol_universe(root)

    frames = []
    failures = []

    for symbol in symbols:
        try:
            frame = build_symbol_sector_residual_candidates(root, symbol, config)
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
        "sector_source_counts": (
            df["sector_source"].value_counts().to_dict()
            if "sector_source" in df.columns
            else {}
        ),
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
        "sector_etf",
        "sector_source",
        "sector_name",
        "sector_residual_z",
        "sector_model_r2",
        "residual_z",
        "residual_r2",
        "candidate_id",
        "lineage",
        "feature_config_hash",
    ]

    existing = [c for c in keep if c in selected.columns]
    return selected[existing].sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def audit_rule(
    df: pd.DataFrame, config: SectorResidualConfig | None = None
) -> dict[str, Any]:
    config = config or SectorResidualConfig()

    expected = (
        (pd.to_numeric(df["sector_residual_z"], errors="coerce") <= config.residual_z_threshold)
        & (pd.to_numeric(df["sector_model_r2"], errors="coerce") >= config.min_model_r2)
    )

    actual = df["selected"].astype(bool)
    mismatch = actual.ne(expected)

    return {
        "rule": (
            f"sector_residual_z <= {config.residual_z_threshold} "
            f"AND sector_model_r2 >= {config.min_model_r2}"
        ),
        "rows": int(len(df)),
        "selected_actual": int(actual.sum()),
        "selected_expected": int(expected.sum()),
        "mismatch_count": int(mismatch.sum()),
        "mismatch_rate": float(mismatch.mean()) if len(df) else None,
        "pass": int(mismatch.sum()) == 0,
    }


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

    selected_mean = summarize_returns(df[df["selected"]])["mean"]

    rng = np.random.default_rng(seed)
    returns = pd.to_numeric(df["forward_return"], errors="coerce").fillna(0.0).to_numpy()
    idx_all = np.arange(len(df))

    means = []
    for _ in range(n):
        idx = rng.choice(idx_all, size=selected_count, replace=False)
        means.append(float(np.mean(returns[idx])))

    arr = np.array(means)
    pct = float(np.mean(arr <= selected_mean))

    if pct >= 0.95:
        cls = "STRONG_VS_RANDOM"
    elif pct >= 0.90:
        cls = "OK_VS_RANDOM"
    else:
        cls = "WEAK_VS_RANDOM"

    return {
        "runs": int(n),
        "selected_count": selected_count,
        "observed_mean": float(selected_mean),
        "random_mean_avg": float(arr.mean()),
        "random_p05": float(np.percentile(arr, 5)),
        "random_p50": float(np.percentile(arr, 50)),
        "random_p95": float(np.percentile(arr, 95)),
        "random_percentile": pct,
        "classification": cls,
    }


def classify_sector_residual(
    df: pd.DataFrame,
    rule_audit: dict[str, Any],
    fold_df: pd.DataFrame,
    rand: dict[str, Any],
) -> str:
    if not rule_audit.get("pass"):
        return "RULE_AUDIT_FAIL"

    if int(df["selected"].sum()) < 150:
        return "TRUE_WALK_FORWARD_INCONCLUSIVE"

    if (fold_df["selected_rows"] < 30).any():
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

    if avg_mean < 0.0075:
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
