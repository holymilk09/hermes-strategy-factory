from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.research.artifacts.candidate_recorder import (
    CandidateArtifactConfig,
    record_candidate_feature_ledger,
)
from src.research.artifacts.selection_audit import (
    SelectionRule,
    apply_selection_rule,
    record_selection_event,
)


RESIDUAL_FEATURE_HINTS = [
    "residual_z",
    "residual_r2",
    "rsi_2",
    "regime_score",
    "score",
    "signal",
    "rank",
    "forward_return",
    "realized_return",
]


REQUIRED_RESIDUAL_CANDIDATE_COLUMNS = [
    "timestamp",
    "symbol",
]


@dataclass(frozen=True)
class ResidualArtifactPaths:
    candidate_feature_ledger: Path
    selection_event_ledger: Path


@dataclass(frozen=True)
class ResidualIntegrationResult:
    status: str
    candidate_rows: int
    selected_rows: int
    candidate_feature_ledger: str
    selection_event_ledger: str
    selection_rule_hash: str | None
    notes: str


def normalize_residual_candidate_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]

    if "timestamp" not in out.columns:
        for alt in ["entry_time", "date", "datetime", "time"]:
            if alt in out.columns:
                out["timestamp"] = out[alt]
                break

    missing = [c for c in REQUIRED_RESIDUAL_CANDIDATE_COLUMNS if c not in out.columns]
    if missing:
        raise ValueError(f"Residual candidate frame missing columns: {missing}")

    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    out["symbol"] = out["symbol"].astype(str)

    if "strategy" not in out.columns:
        out["strategy"] = "residual_reversion"

    out = out.dropna(subset=["timestamp", "symbol"])
    out = out.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    if out.empty:
        raise ValueError("Residual candidate frame normalized to zero rows")

    return out


def infer_residual_score_column(df: pd.DataFrame) -> str:
    cols = set(str(c).lower() for c in df.columns)

    priority = [
        "residual_z",
        "regime_score",
        "score",
        "signal",
        "rank",
    ]

    for c in priority:
        if c in cols:
            return c

    raise ValueError(
        "Could not infer residual score column. Expected one of: "
        "residual_z, regime_score, score, signal, rank"
    )


def build_default_residual_selection_rule(
    candidates: pd.DataFrame,
    threshold: float | None = None,
    top_n: int | None = None,
    score_column: str | None = None,
    strategy: str = "residual_reversion",
) -> SelectionRule:
    """
    Build an explicit auditable rule.

    This must mirror the real strategy logic.
    If the real pipeline has its own threshold/top_n, pass those values in.
    Do not invent optimized values.
    """

    normalized = normalize_residual_candidate_columns(candidates)
    score_col = score_column or infer_residual_score_column(normalized)

    if threshold is None and top_n is None:
        raise ValueError(
            "Must pass real strategy threshold or top_n. "
            "Do not fabricate selection logic."
        )

    return SelectionRule(
        rule_name=f"{strategy}_{score_col}_selection",
        strategy=strategy,
        score_column=score_col,
        threshold=threshold,
        rank_column=None,
        top_n=top_n,
        direction="higher_is_better",
    )


def record_residual_preselection_artifacts(
    candidates_preselection: pd.DataFrame,
    selected_frame: pd.DataFrame | None,
    artifact_config: CandidateArtifactConfig,
    selection_rule: SelectionRule,
    paths: ResidualArtifactPaths,
) -> ResidualIntegrationResult:
    """
    Records full pre-selection candidate universe.

    candidates_preselection:
        Full candidate frame before final selection.

    selected_frame:
        Optional already-selected frame from the real pipeline.
        Used only to map selected flags without changing strategy logic.

    selection_rule:
        Auditable rule matching the real strategy logic.

    Important:
        This function must not change trading output.
    """

    candidates = normalize_residual_candidate_columns(candidates_preselection)

    if selected_frame is not None and not selected_frame.empty:
        selected = normalize_residual_candidate_columns(selected_frame)

        selected_keys = set(
            zip(
                selected["timestamp"].astype(str),
                selected["symbol"].astype(str),
                selected["strategy"].astype(str),
            )
        )

        candidates["selected"] = [
            (
                str(row.timestamp),
                str(row.symbol),
                str(row.strategy),
            )
            in selected_keys
            for row in candidates.itertuples(index=False)
        ]
    else:
        selected_by_rule = apply_selection_rule(candidates, selection_rule)
        candidates["selected"] = selected_by_rule["selected"].astype(bool).to_numpy()

    feature_result = record_candidate_feature_ledger(
        candidates=candidates,
        config=artifact_config,
        output_path=paths.candidate_feature_ledger,
    )

    event_result = record_selection_event(
        selected_frame=candidates,
        rule=selection_rule,
        output_path=paths.selection_event_ledger,
    )

    return ResidualIntegrationResult(
        status="SUCCESS",
        candidate_rows=int(len(candidates)),
        selected_rows=int(candidates["selected"].sum()),
        candidate_feature_ledger=str(paths.candidate_feature_ledger),
        selection_event_ledger=str(paths.selection_event_ledger),
        selection_rule_hash=event_result["rule_hash"],
        notes="Recorded full residual pre-selection candidate universe.",
    )


def validate_recorded_artifact_has_rejected_candidates(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path)

    if "selected" not in df.columns:
        raise ValueError("Recorded candidate ledger missing selected column")

    selected_count = int(df["selected"].astype(bool).sum())
    total = int(len(df))
    rejected_count = total - selected_count

    return {
        "path": str(path),
        "rows": total,
        "selected": selected_count,
        "rejected": rejected_count,
        "has_rejected_candidates": rejected_count > 0,
        "columns": list(df.columns),
    }
