from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class SelectionRule:
    rule_name: str
    strategy: str
    score_column: str
    threshold: float | None
    rank_column: str | None
    top_n: int | None
    direction: str

    @property
    def rule_hash(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True).encode("utf-8")
        return sha256(payload).hexdigest()[:16]


def validate_selection_rule(rule: SelectionRule) -> None:
    if rule.direction not in {"higher_is_better", "lower_is_better"}:
        raise ValueError("direction must be higher_is_better or lower_is_better")

    if rule.threshold is None and rule.top_n is None:
        raise ValueError("selection rule must define threshold or top_n")

    if rule.threshold is not None and rule.top_n is not None:
        raise ValueError("selection rule cannot define both threshold and top_n")


def apply_selection_rule(
    candidates: pd.DataFrame,
    rule: SelectionRule,
) -> pd.DataFrame:
    validate_selection_rule(rule)

    df = candidates.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    score_col = rule.score_column.lower()

    if score_col not in df.columns:
        raise ValueError(f"Missing score column: {score_col}")

    df[score_col] = pd.to_numeric(df[score_col], errors="coerce")
    df["selected"] = False

    if rule.threshold is not None:
        if rule.direction == "higher_is_better":
            df["selected"] = df[score_col] >= rule.threshold
        else:
            df["selected"] = df[score_col] <= rule.threshold

    if rule.top_n is not None:
        ascending = rule.direction == "lower_is_better"
        df = df.sort_values(score_col, ascending=ascending).reset_index(drop=True)
        df.loc[df.index[: rule.top_n], "selected"] = True

    df["selection_rule_hash"] = rule.rule_hash
    df["selection_rule_name"] = rule.rule_name
    return df


def record_selection_event(
    selected_frame: pd.DataFrame,
    rule: SelectionRule,
    output_path: Path,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "rule_name": rule.rule_name,
        "rule_hash": rule.rule_hash,
        "strategy": rule.strategy,
        "score_column": rule.score_column,
        "threshold": rule.threshold,
        "rank_column": rule.rank_column,
        "top_n": rule.top_n,
        "direction": rule.direction,
        "candidate_count": int(len(selected_frame)),
        "selected_count": int(selected_frame["selected"].sum()),
        "timestamp_min": str(pd.to_datetime(selected_frame["timestamp"]).min())
        if "timestamp" in selected_frame.columns
        else None,
        "timestamp_max": str(pd.to_datetime(selected_frame["timestamp"]).max())
        if "timestamp" in selected_frame.columns
        else None,
    }

    row = pd.DataFrame([event])

    if output_path.exists():
        existing = pd.read_csv(output_path)
        combined = pd.concat([existing, row], axis=0, ignore_index=True)
        combined = combined.drop_duplicates(subset=["rule_hash", "timestamp_min", "timestamp_max"], keep="last")
    else:
        combined = row

    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    combined.to_csv(tmp, index=False)
    tmp.replace(output_path)

    return event
