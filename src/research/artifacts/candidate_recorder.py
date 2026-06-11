from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_CANDIDATE_COLUMNS = [
    "timestamp",
    "symbol",
    "strategy",
    "candidate_id",
    "selected",
]


@dataclass(frozen=True)
class CandidateArtifactConfig:
    strategy_name: str
    universe_name: str
    timeframe: str
    feature_config_hash: str
    selection_config_hash: str
    code_version: str

    @property
    def run_hash(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True).encode("utf-8")
        return sha256(payload).hexdigest()[:16]


def ensure_timestamp_utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def build_candidate_id(timestamp: pd.Series, symbol: pd.Series, strategy: pd.Series) -> pd.Series:
    raw = (
        timestamp.astype(str)
        + "|"
        + symbol.astype(str)
        + "|"
        + strategy.astype(str)
    )
    return raw.map(lambda x: sha256(x.encode("utf-8")).hexdigest()[:24])


def validate_candidate_ledger(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_CANDIDATE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Candidate ledger missing columns: {missing}")

    if df["candidate_id"].duplicated().any():
        dupes = int(df["candidate_id"].duplicated().sum())
        raise ValueError(f"Duplicate candidate_id rows: {dupes}")

    if df["timestamp"].isna().any():
        raise ValueError("Candidate ledger contains null timestamps")

    if df["symbol"].isna().any():
        raise ValueError("Candidate ledger contains null symbols")

    if df["selected"].isna().any():
        raise ValueError("Candidate ledger contains null selected flags")


def normalize_candidate_frame(
    raw: pd.DataFrame,
    config: CandidateArtifactConfig,
) -> pd.DataFrame:
    df = raw.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "timestamp" not in df.columns:
        for alt in ["entry_time", "date", "datetime", "time"]:
            if alt in df.columns:
                df["timestamp"] = df[alt]
                break

    if "timestamp" not in df.columns:
        raise ValueError("Candidate frame missing timestamp")

    if "symbol" not in df.columns:
        raise ValueError("Candidate frame missing symbol")

    if "strategy" not in df.columns:
        df["strategy"] = config.strategy_name

    if "selected" not in df.columns:
        df["selected"] = False

    df["timestamp"] = ensure_timestamp_utc(df["timestamp"])
    df["symbol"] = df["symbol"].astype(str)
    df["strategy"] = df["strategy"].astype(str)
    df["selected"] = df["selected"].astype(bool)

    if "candidate_id" not in df.columns:
        df["candidate_id"] = build_candidate_id(
            df["timestamp"],
            df["symbol"],
            df["strategy"],
        )

    df["run_hash"] = config.run_hash
    df["universe_name"] = config.universe_name
    df["timeframe"] = config.timeframe
    df["feature_config_hash"] = config.feature_config_hash
    df["selection_config_hash"] = config.selection_config_hash
    df["code_version"] = config.code_version

    df = df.dropna(subset=["timestamp", "symbol"])
    df = df.sort_values(["timestamp", "symbol", "strategy"]).reset_index(drop=True)

    validate_candidate_ledger(df)
    return df


def append_csv_atomic(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        existing = pd.read_csv(output_path)
        combined = pd.concat([existing, df], axis=0, ignore_index=True)
        combined = combined.drop_duplicates(subset=["candidate_id"], keep="last")
    else:
        combined = df.copy()

    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    combined.to_csv(tmp, index=False)
    tmp.replace(output_path)


def record_candidate_feature_ledger(
    candidates: pd.DataFrame,
    config: CandidateArtifactConfig,
    output_path: Path,
) -> dict[str, Any]:
    normalized = normalize_candidate_frame(candidates, config)
    append_csv_atomic(normalized, output_path)

    return {
        "output_path": str(output_path),
        "rows_written": int(len(normalized)),
        "selected_rows": int(normalized["selected"].sum()),
        "run_hash": config.run_hash,
        "columns": list(normalized.columns),
    }
