from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class BacktestBenchmark:
    lineage: str = "relative_strength_continuation"
    phase: str = "28A"
    historical_mean: float = 0.03261
    historical_hit_rate: float = 0.5574
    historical_selected_count: int = 3687
    historical_spread_vs_rejected: float = 0.02085
    historical_random_percentile: float = 1.000
    historical_classification: str = "TRUE_WALK_FORWARD_WEAK_PASS"


@dataclass(frozen=True)
class DriftThresholds:
    min_resolved_for_classification: int = 6
    confirmed_mean: float = 0.020
    confirmed_hit: float = 0.50
    mixed_mean: float = 0.0
    mixed_hit: float = 0.40


def load_observation_ledger(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    if df.empty:
        return df

    df.columns = [str(c).strip().lower() for c in df.columns]

    if "signal_timestamp" in df.columns:
        df["signal_timestamp"] = pd.to_datetime(df["signal_timestamp"], utc=True, errors="coerce")

    if "sent_to_broker" in df.columns:
        df["sent_to_broker"] = df["sent_to_broker"].astype(bool)

    return df


def load_outcome_ledger(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    if df.empty:
        return df

    df.columns = [str(c).strip().lower() for c in df.columns]

    if "signal_timestamp" in df.columns:
        df["signal_timestamp"] = pd.to_datetime(df["signal_timestamp"], utc=True, errors="coerce")

    if "outcome_timestamp" in df.columns:
        df["outcome_timestamp"] = pd.to_datetime(df["outcome_timestamp"], utc=True, errors="coerce")

    if "outcome_return" in df.columns:
        df["outcome_return"] = pd.to_numeric(df["outcome_return"], errors="coerce")

    if "sent_to_broker" in df.columns:
        df["sent_to_broker"] = df["sent_to_broker"].astype(bool)

    return df


def summarize_observation_state(
    observation_df: pd.DataFrame,
    outcome_df: pd.DataFrame,
) -> dict[str, Any]:
    observations_total = int(len(observation_df)) if observation_df is not None else 0

    sent_to_broker_any = False
    latest_signal_ts = None

    if observation_df is not None and not observation_df.empty:
        if "sent_to_broker" in observation_df.columns:
            sent_to_broker_any = bool(observation_df["sent_to_broker"].astype(bool).any())

        if "signal_timestamp" in observation_df.columns:
            ts = pd.to_datetime(observation_df["signal_timestamp"], utc=True, errors="coerce")
            if ts.notna().any():
                latest_signal_ts = ts.max().isoformat()

    if outcome_df is None or outcome_df.empty or "outcome_status" not in outcome_df.columns:
        return {
            "observations_total": observations_total,
            "outcomes_total": 0,
            "resolved": 0,
            "pending": observations_total,
            "latest_signal_ts": latest_signal_ts,
            "sent_to_broker_any": sent_to_broker_any,
        }

    statuses = outcome_df["outcome_status"].astype(str)
    resolved = int(statuses.eq("RESOLVED").sum())
    pending = int(len(outcome_df) - resolved)

    if "sent_to_broker" in outcome_df.columns:
        sent_to_broker_any = bool(
            sent_to_broker_any or outcome_df["sent_to_broker"].astype(bool).any()
        )

    return {
        "observations_total": observations_total,
        "outcomes_total": int(len(outcome_df)),
        "resolved": resolved,
        "pending": pending,
        "latest_signal_ts": latest_signal_ts,
        "sent_to_broker_any": sent_to_broker_any,
    }


def summarize_resolved_outcomes(outcome_df: pd.DataFrame) -> dict[str, Any]:
    if outcome_df is None or outcome_df.empty or "outcome_status" not in outcome_df.columns:
        return {
            "resolved_count": 0,
            "mean_return": None,
            "median_return": None,
            "hit_rate": None,
            "best_return": None,
            "worst_return": None,
        }

    resolved = outcome_df[outcome_df["outcome_status"].astype(str).eq("RESOLVED")].copy()

    if resolved.empty or "outcome_return" not in resolved.columns:
        return {
            "resolved_count": 0,
            "mean_return": None,
            "median_return": None,
            "hit_rate": None,
            "best_return": None,
            "worst_return": None,
        }

    r = pd.to_numeric(resolved["outcome_return"], errors="coerce").dropna()

    if r.empty:
        return {
            "resolved_count": 0,
            "mean_return": None,
            "median_return": None,
            "hit_rate": None,
            "best_return": None,
            "worst_return": None,
        }

    return {
        "resolved_count": int(len(r)),
        "mean_return": float(r.mean()),
        "median_return": float(r.median()),
        "hit_rate": float((r > 0).mean()),
        "best_return": float(r.max()),
        "worst_return": float(r.min()),
    }


def classify_observation_drift(
    observation_state: dict[str, Any],
    outcome_summary: dict[str, Any],
    thresholds: DriftThresholds | None = None,
) -> str:
    thresholds = thresholds or DriftThresholds()

    if observation_state.get("sent_to_broker_any"):
        return "OBSERVATION_DRIFT_HARD_FAIL_BROKER_FLAG"

    resolved = int(outcome_summary.get("resolved_count") or 0)

    if resolved < thresholds.min_resolved_for_classification:
        return "OBSERVATION_DRIFT_PENDING"

    mean_return = outcome_summary.get("mean_return")
    hit_rate = outcome_summary.get("hit_rate")

    if mean_return is None or hit_rate is None:
        return "OBSERVATION_DRIFT_PENDING"

    if mean_return >= thresholds.confirmed_mean and hit_rate >= thresholds.confirmed_hit:
        return "FORWARD_OBSERVATION_CONFIRMED_EARLY"

    if mean_return > thresholds.mixed_mean and hit_rate >= thresholds.mixed_hit:
        return "FORWARD_OBSERVATION_MIXED"

    return "FORWARD_OBSERVATION_WEAK"


def compare_to_benchmark(
    outcome_summary: dict[str, Any],
    benchmark: BacktestBenchmark | None = None,
) -> dict[str, Any]:
    benchmark = benchmark or BacktestBenchmark()

    mean_return = outcome_summary.get("mean_return")
    hit_rate = outcome_summary.get("hit_rate")

    if mean_return is None:
        mean_delta = None
        mean_capture = None
    else:
        mean_delta = float(mean_return - benchmark.historical_mean)
        mean_capture = (
            float(mean_return / benchmark.historical_mean)
            if benchmark.historical_mean != 0
            else None
        )

    if hit_rate is None:
        hit_delta = None
    else:
        hit_delta = float(hit_rate - benchmark.historical_hit_rate)

    return {
        "lineage": benchmark.lineage,
        "phase": benchmark.phase,
        "resolved_count": outcome_summary.get("resolved_count"),
        "forward_mean": mean_return,
        "historical_mean": benchmark.historical_mean,
        "mean_delta": mean_delta,
        "mean_capture_ratio": mean_capture,
        "forward_hit_rate": hit_rate,
        "historical_hit_rate": benchmark.historical_hit_rate,
        "hit_delta": hit_delta,
        "historical_selected_count": benchmark.historical_selected_count,
        "historical_spread_vs_rejected": benchmark.historical_spread_vs_rejected,
        "historical_random_percentile": benchmark.historical_random_percentile,
        "historical_classification": benchmark.historical_classification,
    }


def next_action_from_classification(classification: str) -> str:
    if classification == "OBSERVATION_DRIFT_PENDING":
        return "WAIT_FOR_OUTCOMES"

    if classification == "FORWARD_OBSERVATION_CONFIRMED_EARLY":
        return "CONTINUE_FORWARD_OBSERVATION"

    if classification == "FORWARD_OBSERVATION_MIXED":
        return "CONTINUE_FORWARD_OBSERVATION"

    if classification == "FORWARD_OBSERVATION_WEAK":
        return "PAUSE_ESCALATION_CONTINUE_OBSERVATION_ONLY"

    if classification == "OBSERVATION_DRIFT_HARD_FAIL_BROKER_FLAG":
        return "HALT_AND_AUDIT_BROKER_FLAGS"

    return "NO_ACTION"


def write_comparison_csv(path: Path, comparison: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([comparison]).to_csv(path, index=False)


def write_markdown(path: Path, title: str, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", ""]
    lines.extend(rows)
    path.write_text("\n".join(lines), encoding="utf-8")
