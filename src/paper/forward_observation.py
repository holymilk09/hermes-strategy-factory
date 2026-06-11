from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ForwardObservationConfig:
    ret_3d_z_threshold: float = -1.5
    volume_z_threshold: float = 1.0
    close_location_threshold: float = 0.50
    spy_drawdown_60d_threshold: float = -0.0146
    outcome_window: int = 5
    max_stale_calendar_days: int = 5

    strategy: str = "regime_conditioned_capitulation_v2"
    lineage: str = "regime_conditioned_capitulation_v2_phase25c_holdout_pass"

    @property
    def config_hash(self) -> str:
        return sha256(repr(self).encode("utf-8")).hexdigest()[:16]


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
        raise ValueError(f"Missing timestamp/date column: {path}")

    required = ["open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns {missing}: {path}")

    df["timestamp"] = pd.to_datetime(df[time_col], utc=True, errors="coerce")

    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["timestamp", "open", "high", "low", "close", "volume"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")

    return df[["timestamp", "open", "high", "low", "close", "volume"]].reset_index(drop=True)


def discover_symbol_paths(root: Path) -> dict[str, Path]:
    dirs = [
        root / "data" / "cache" / "ohlcv_1d",
        root / "data" / "cache",
        root / "data",
    ]

    excluded = {
        "SPY", "QQQ", "IWM",
        "XLK", "XLF", "XLV", "XLY", "XLC", "XLI",
        "XLE", "XLP", "XLU", "XLB", "XLRE",
        "SMH", "IBB", "ARKK",
    }

    out: dict[str, Path] = {}

    for d in dirs:
        if not d.exists():
            continue

        for p in d.glob("*.csv"):
            symbol = p.stem.upper().replace("_1D", "").replace("_1d", "")
            if symbol not in excluded and symbol not in out:
                out[symbol] = p

    return out


def compute_spy_drawdown_60d(spy: pd.DataFrame) -> pd.DataFrame:
    close = spy["close"]
    high60 = close.rolling(60, min_periods=20).max()

    out = pd.DataFrame()
    out["timestamp"] = spy["timestamp"]
    out["spy_drawdown_60d"] = close / high60 - 1.0

    return out.dropna().reset_index(drop=True)


def zscore_trailing(series: pd.Series, lookback: int) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce")
    mean = x.rolling(lookback, min_periods=lookback).mean()
    std = x.rolling(lookback, min_periods=lookback).std()
    return (x - mean) / std.replace(0, np.nan)


def close_location(df: pd.DataFrame) -> pd.Series:
    rng = df["high"] - df["low"]
    loc = (df["close"] - df["low"]) / rng.replace(0, np.nan)
    return loc.fillna(0.5).clip(0.0, 1.0)


def build_symbol_signal_frame(
    symbol: str,
    path: Path,
    config: ForwardObservationConfig,
) -> pd.DataFrame:
    df = load_ohlcv(path)

    close = df["close"]
    volume = df["volume"]

    out = pd.DataFrame()
    out["timestamp"] = df["timestamp"]
    out["symbol"] = symbol
    out["close"] = close
    out["ret_3d"] = close / close.shift(3) - 1.0
    out["ret_3d_z"] = zscore_trailing(out["ret_3d"], 60)
    out["volume_z_20"] = zscore_trailing(volume, 20)
    out["close_location"] = close_location(df)

    out = out.dropna(
        subset=[
            "timestamp",
            "symbol",
            "close",
            "ret_3d_z",
            "volume_z_20",
            "close_location",
        ]
    )

    return out.sort_values("timestamp").reset_index(drop=True)


def build_current_signal_universe(
    root: Path,
    spy_path: Path,
    config: ForwardObservationConfig | None = None,
) -> pd.DataFrame:
    config = config or ForwardObservationConfig()

    spy = load_ohlcv(spy_path)
    spy_drawdown = compute_spy_drawdown_60d(spy)

    symbol_paths = discover_symbol_paths(root)

    frames = []
    failures = []

    for symbol, path in symbol_paths.items():
        try:
            frame = build_symbol_signal_frame(symbol, path, config)
            if not frame.empty:
                frames.append(frame)
        except Exception as exc:
            failures.append((symbol, f"{type(exc).__name__}: {exc}"))

    if not frames:
        raise ValueError(f"No symbol signal frames built. failures={failures[:10]}")

    universe = pd.concat(frames, axis=0, ignore_index=True)

    universe = pd.merge_asof(
        universe.sort_values("timestamp"),
        spy_drawdown.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
        allow_exact_matches=True,
    )

    universe = universe.dropna(subset=["spy_drawdown_60d"]).reset_index(drop=True)

    universe["selected"] = (
        (universe["ret_3d_z"] <= config.ret_3d_z_threshold)
        & (universe["volume_z_20"] >= config.volume_z_threshold)
        & (universe["close_location"] >= config.close_location_threshold)
        & (universe["spy_drawdown_60d"] <= config.spy_drawdown_60d_threshold)
    )

    universe["strategy"] = config.strategy
    universe["lineage"] = config.lineage
    universe["feature_config_hash"] = config.config_hash
    universe.attrs["failures"] = failures

    return universe.sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def latest_fresh_signals(
    universe: pd.DataFrame,
    as_of: pd.Timestamp | None = None,
    config: ForwardObservationConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    config = config or ForwardObservationConfig()

    df = universe.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])

    if df.empty:
        raise ValueError("Signal universe is empty")

    if as_of is None:
        as_of = pd.Timestamp.utcnow()

    as_of = pd.Timestamp(as_of)

    if as_of.tzinfo is None:
        as_of = as_of.tz_localize("UTC")
    else:
        as_of = as_of.tz_convert("UTC")

    latest_ts = df["timestamp"].max()
    age_days = (as_of - latest_ts).total_seconds() / 86400.0
    fresh = age_days <= config.max_stale_calendar_days

    latest = df[df["timestamp"] == latest_ts].copy()
    selected = latest[latest["selected"]].copy()

    freshness = {
        "as_of": as_of.isoformat(),
        "latest_signal_ts": latest_ts.isoformat(),
        "signal_age_days": float(age_days),
        "fresh": bool(fresh),
        "latest_universe_rows": int(len(latest)),
        "latest_selected_rows": int(len(selected)),
        "reason": "FRESH" if fresh else "STALE_SIGNAL_SOURCE",
    }

    if not fresh:
        return selected.iloc[0:0].copy(), freshness

    return selected.sort_values("symbol").reset_index(drop=True), freshness


def build_observation_rows(
    selected: pd.DataFrame,
    config: ForwardObservationConfig | None = None,
) -> pd.DataFrame:
    config = config or ForwardObservationConfig()

    if selected.empty:
        return pd.DataFrame(
            columns=[
                "observation_id",
                "signal_timestamp",
                "symbol",
                "strategy",
                "lineage",
                "signal_close",
                "ret_3d_z",
                "volume_z_20",
                "close_location",
                "spy_drawdown_60d",
                "outcome_window",
                "outcome_status",
                "outcome_return",
                "outcome_timestamp",
                "created_at",
                "sent_to_broker",
                "broker_order_id",
            ]
        )

    df = selected.copy()

    raw = (
        df["timestamp"].astype(str)
        + "|"
        + df["symbol"].astype(str)
        + "|"
        + config.strategy
        + "|forward_observation"
    )

    obs = pd.DataFrame()
    obs["observation_id"] = raw.map(lambda x: sha256(x.encode("utf-8")).hexdigest()[:24])
    obs["signal_timestamp"] = df["timestamp"]
    obs["symbol"] = df["symbol"]
    obs["strategy"] = config.strategy
    obs["lineage"] = config.lineage
    obs["signal_close"] = df["close"]
    obs["ret_3d_z"] = df["ret_3d_z"]
    obs["volume_z_20"] = df["volume_z_20"]
    obs["close_location"] = df["close_location"]
    obs["spy_drawdown_60d"] = df["spy_drawdown_60d"]
    obs["outcome_window"] = config.outcome_window
    obs["outcome_status"] = "PENDING"
    obs["outcome_return"] = np.nan
    obs["outcome_timestamp"] = pd.NaT
    obs["created_at"] = pd.Timestamp.utcnow().isoformat()
    obs["sent_to_broker"] = False
    obs["broker_order_id"] = None

    return obs.sort_values(["signal_timestamp", "symbol"]).reset_index(drop=True)


def append_observations_atomic(observations: pd.DataFrame, output_path: Path) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        existing = pd.read_csv(output_path)
        combined = pd.concat([existing, observations], axis=0, ignore_index=True)
        combined = combined.drop_duplicates(subset=["observation_id"], keep="last")
    else:
        combined = observations.copy()

    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    combined.to_csv(tmp, index=False)
    tmp.replace(output_path)

    sent_any = False
    if "sent_to_broker" in combined.columns:
        sent_any = bool(combined["sent_to_broker"].astype(bool).any())

    return {
        "output_path": str(output_path),
        "rows_written": int(len(observations)),
        "total_rows": int(len(combined)),
        "sent_to_broker_any": sent_any,
    }


def resolve_observation_outcomes(
    observation_path: Path,
    root: Path,
    output_path: Path,
) -> dict[str, Any]:
    if not observation_path.exists():
        raise FileNotFoundError(observation_path)

    obs = pd.read_csv(observation_path)
    obs.columns = [str(c).strip().lower() for c in obs.columns]

    if obs.empty:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        obs.to_csv(output_path, index=False)
        return {
            "resolved": 0,
            "pending": 0,
            "total": 0,
            "output_path": str(output_path),
        }

    obs["signal_timestamp"] = pd.to_datetime(obs["signal_timestamp"], utc=True, errors="coerce")
    obs["signal_close"] = pd.to_numeric(obs["signal_close"], errors="coerce")
    obs["outcome_window"] = pd.to_numeric(obs["outcome_window"], errors="coerce").fillna(5).astype(int)

    symbol_paths = discover_symbol_paths(root)

    resolved_rows = []

    for _, row in obs.iterrows():
        status = row.get("outcome_status", "PENDING")

        if status == "RESOLVED":
            resolved_rows.append(row.to_dict())
            continue

        symbol = str(row["symbol"])
        path = symbol_paths.get(symbol)

        out = row.to_dict()

        if path is None:
            out["outcome_status"] = "PENDING_NO_OHLCV"
            resolved_rows.append(out)
            continue

        try:
            prices = load_ohlcv(path)
        except Exception:
            out["outcome_status"] = "PENDING_OHLCV_ERROR"
            resolved_rows.append(out)
            continue

        prices = prices[prices["timestamp"] > row["signal_timestamp"]].copy()

        if len(prices) < int(row["outcome_window"]):
            out["outcome_status"] = "PENDING"
            resolved_rows.append(out)
            continue

        outcome_row = prices.iloc[int(row["outcome_window"]) - 1]
        outcome_close = float(outcome_row["close"])

        out["outcome_timestamp"] = outcome_row["timestamp"]
        out["outcome_close"] = outcome_close
        out["outcome_return"] = outcome_close / float(row["signal_close"]) - 1.0
        out["outcome_status"] = "RESOLVED"

        resolved_rows.append(out)

    result = pd.DataFrame(resolved_rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    result.to_csv(tmp, index=False)
    tmp.replace(output_path)

    return {
        "resolved": int(result["outcome_status"].eq("RESOLVED").sum()),
        "pending": int((~result["outcome_status"].eq("RESOLVED")).sum()),
        "total": int(len(result)),
        "output_path": str(output_path),
    }


def summarize_outcomes(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "total": 0,
            "resolved": 0,
            "pending": 0,
            "mean": None,
            "hit_rate": None,
        }

    df = pd.read_csv(path)

    if df.empty or "outcome_status" not in df.columns:
        return {
            "total": 0,
            "resolved": 0,
            "pending": 0,
            "mean": None,
            "hit_rate": None,
        }

    resolved = df[df["outcome_status"].eq("RESOLVED")].copy()
    r = pd.to_numeric(resolved.get("outcome_return"), errors="coerce").dropna()

    return {
        "total": int(len(df)),
        "resolved": int(len(resolved)),
        "pending": int(len(df) - len(resolved)),
        "mean": float(r.mean()) if not r.empty else None,
        "hit_rate": float((r > 0).mean()) if not r.empty else None,
    }
