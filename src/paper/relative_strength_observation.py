from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RelativeStrengthObservationConfig:
    ret_20d_rank_threshold: float = 0.85
    ret_60d_rank_threshold: float = 0.70
    outcome_window: int = 10
    max_stale_calendar_days: int = 5

    strategy: str = "relative_strength_continuation"
    lineage: str = "relative_strength_continuation_phase28a_weak_pass"

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


def discover_symbol_paths(root: Path) -> dict[str, Path]:
    excluded = {
        "SPY", "QQQ", "IWM",
        "XLK", "XLF", "XLV", "XLY", "XLC", "XLI",
        "XLE", "XLP", "XLU", "XLB", "XLRE",
        "SMH", "IBB", "ARKK",
    }

    out: dict[str, Path] = {}

    dirs = [
        root / "data" / "cache" / "ohlcv_1d",
        root / "data" / "cache",
        root / "data",
    ]

    for d in dirs:
        if not d.exists():
            continue

        for p in d.glob("*.csv"):
            symbol = p.stem.upper().replace("_1D", "").replace("_1d", "")
            if symbol not in excluded and symbol not in out:
                out[symbol] = p

    return out


def build_symbol_feature_frame(symbol: str, path: Path) -> pd.DataFrame:
    df = load_ohlcv(path)
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

    out = out.dropna(
        subset=[
            "timestamp",
            "symbol",
            "close",
            "ret_5d",
            "ret_20d",
            "ret_60d",
            "ma50",
        ]
    )

    return out.sort_values("timestamp").reset_index(drop=True)


def build_current_relative_strength_universe(
    root: Path,
    config: RelativeStrengthObservationConfig | None = None,
) -> pd.DataFrame:
    config = config or RelativeStrengthObservationConfig()

    paths = discover_symbol_paths(root)

    frames = []
    failures = []

    for symbol, path in paths.items():
        try:
            frame = build_symbol_feature_frame(symbol, path)
            if not frame.empty:
                frames.append(frame)
        except Exception as exc:
            failures.append((symbol, f"{type(exc).__name__}: {exc}"))

    if not frames:
        raise ValueError(f"No relative strength frames built. failures={failures[:10]}")

    universe = pd.concat(frames, axis=0, ignore_index=True)
    universe = universe.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    universe["ret_20d_rank"] = universe.groupby("timestamp")["ret_20d"].rank(pct=True)
    universe["ret_60d_rank"] = universe.groupby("timestamp")["ret_60d"].rank(pct=True)

    universe["selected"] = (
        (universe["ret_20d_rank"] >= config.ret_20d_rank_threshold)
        & (universe["ret_60d_rank"] >= config.ret_60d_rank_threshold)
        & (universe["close_above_ma50"].astype(bool))
        & (universe["ret_5d"] > 0)
    )

    universe["strategy"] = config.strategy
    universe["lineage"] = config.lineage
    universe["feature_config_hash"] = config.config_hash
    universe.attrs["failures"] = failures

    return universe.sort_values(["timestamp", "symbol"]).reset_index(drop=True)


def latest_fresh_signals(
    universe: pd.DataFrame,
    as_of: pd.Timestamp | None = None,
    config: RelativeStrengthObservationConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    config = config or RelativeStrengthObservationConfig()

    df = universe.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])

    if df.empty:
        raise ValueError("Signal universe is empty")

    if as_of is None:
        as_of = pd.Timestamp.now("UTC")

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
    config: RelativeStrengthObservationConfig | None = None,
) -> pd.DataFrame:
    config = config or RelativeStrengthObservationConfig()

    columns = [
        "observation_id",
        "signal_timestamp",
        "symbol",
        "strategy",
        "lineage",
        "signal_close",
        "ret_5d",
        "ret_20d",
        "ret_60d",
        "ret_20d_rank",
        "ret_60d_rank",
        "close_above_ma50",
        "outcome_window",
        "outcome_status",
        "outcome_return",
        "outcome_timestamp",
        "created_at",
        "sent_to_broker",
        "broker_order_id",
    ]

    if selected.empty:
        return pd.DataFrame(columns=columns)

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
    obs["ret_5d"] = df["ret_5d"]
    obs["ret_20d"] = df["ret_20d"]
    obs["ret_60d"] = df["ret_60d"]
    obs["ret_20d_rank"] = df["ret_20d_rank"]
    obs["ret_60d_rank"] = df["ret_60d_rank"]
    obs["close_above_ma50"] = df["close_above_ma50"]
    obs["outcome_window"] = config.outcome_window
    obs["outcome_status"] = "PENDING"
    obs["outcome_return"] = np.nan
    obs["outcome_timestamp"] = pd.NaT
    obs["created_at"] = pd.Timestamp.now("UTC").isoformat()
    obs["sent_to_broker"] = False
    obs["broker_order_id"] = None

    return obs[columns].sort_values(["signal_timestamp", "symbol"]).reset_index(drop=True)


def append_observations_atomic(
    observations: pd.DataFrame, output_path: Path
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        existing = pd.read_csv(output_path)
        combined = pd.concat([existing, observations], axis=0, ignore_index=True)
        if "observation_id" in combined.columns:
            combined = combined.drop_duplicates(subset=["observation_id"], keep="last")
    else:
        combined = observations.copy()

    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    combined.to_csv(tmp, index=False)
    tmp.replace(output_path)

    sent_any = False
    if "sent_to_broker" in combined.columns and not combined.empty:
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
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame().to_csv(output_path, index=False)
        return {
            "resolved": 0,
            "pending": 0,
            "total": 0,
            "output_path": str(output_path),
        }

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

    obs["signal_timestamp"] = pd.to_datetime(
        obs["signal_timestamp"], utc=True, errors="coerce"
    )
    obs["signal_close"] = pd.to_numeric(obs["signal_close"], errors="coerce")
    obs["outcome_window"] = (
        pd.to_numeric(obs["outcome_window"], errors="coerce").fillna(10).astype(int)
    )

    symbol_paths = discover_symbol_paths(root)
    rows = []

    for _, row in obs.iterrows():
        out = row.to_dict()

        if str(row.get("outcome_status", "PENDING")) == "RESOLVED":
            rows.append(out)
            continue

        symbol = str(row["symbol"])
        path = symbol_paths.get(symbol)

        if path is None:
            out["outcome_status"] = "PENDING_NO_OHLCV"
            rows.append(out)
            continue

        try:
            prices = load_ohlcv(path)
        except Exception:
            out["outcome_status"] = "PENDING_OHLCV_ERROR"
            rows.append(out)
            continue

        prices = prices[prices["timestamp"] > row["signal_timestamp"]].copy()

        if len(prices) < int(row["outcome_window"]):
            out["outcome_status"] = "PENDING"
            rows.append(out)
            continue

        outcome = prices.iloc[int(row["outcome_window"]) - 1]
        outcome_close = float(outcome["close"])

        out["outcome_timestamp"] = outcome["timestamp"]
        out["outcome_close"] = outcome_close
        out["outcome_return"] = outcome_close / float(row["signal_close"]) - 1.0
        out["outcome_status"] = "RESOLVED"

        rows.append(out)

    result = pd.DataFrame(rows)

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

    resolved = df[df["outcome_status"].astype(str).eq("RESOLVED")].copy()
    r = pd.to_numeric(resolved.get("outcome_return"), errors="coerce").dropna()

    return {
        "total": int(len(df)),
        "resolved": int(len(resolved)),
        "pending": int(len(df) - len(resolved)),
        "mean": float(r.mean()) if not r.empty else None,
        "hit_rate": float((r > 0).mean()) if not r.empty else None,
    }
