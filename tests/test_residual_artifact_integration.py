from pathlib import Path

import pandas as pd
import pytest

from src.research.artifacts.candidate_recorder import CandidateArtifactConfig
from src.research.artifacts.residual_integration import (
    ResidualArtifactPaths,
    build_default_residual_selection_rule,
    infer_residual_score_column,
    normalize_residual_candidate_columns,
    record_residual_preselection_artifacts,
    validate_recorded_artifact_has_rejected_candidates,
)


def test_normalize_residual_candidate_columns():
    raw = pd.DataFrame(
        {
            "Date": ["2024-01-01"],
            "Symbol": ["AAPL"],
            "Residual_Z": [1.5],
        }
    )

    out = normalize_residual_candidate_columns(raw)

    assert "timestamp" in out.columns
    assert "symbol" in out.columns
    assert "strategy" in out.columns
    assert out["strategy"].iloc[0] == "residual_reversion"


def test_infer_residual_score_column():
    df = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "symbol": ["AAPL"],
            "residual_z": [1.5],
        }
    )

    assert infer_residual_score_column(df) == "residual_z"


def test_build_default_rule_requires_threshold_or_top_n():
    df = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "symbol": ["AAPL"],
            "residual_z": [1.5],
        }
    )

    with pytest.raises(ValueError):
        build_default_residual_selection_rule(df)


def test_record_residual_preselection_artifacts(tmp_path: Path):
    candidates = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=5, freq="D"),
            "symbol": ["A", "B", "C", "D", "E"],
            "residual_z": [0.1, 1.2, 2.0, 0.4, 3.0],
        }
    )

    selected = candidates[candidates["residual_z"] >= 1.5].copy()

    rule = build_default_residual_selection_rule(
        candidates,
        threshold=1.5,
        score_column="residual_z",
    )

    config = CandidateArtifactConfig(
        strategy_name="residual_reversion",
        universe_name="TEST",
        timeframe="1D",
        feature_config_hash="feature_hash",
        selection_config_hash=rule.rule_hash,
        code_version="test",
    )

    paths = ResidualArtifactPaths(
        candidate_feature_ledger=tmp_path / "residual_candidate_feature_ledger.csv",
        selection_event_ledger=tmp_path / "residual_selection_event_ledger.csv",
    )

    result = record_residual_preselection_artifacts(
        candidates_preselection=candidates,
        selected_frame=selected,
        artifact_config=config,
        selection_rule=rule,
        paths=paths,
    )

    assert result.status == "SUCCESS"
    assert result.candidate_rows == 5
    assert result.selected_rows == 2
    assert paths.candidate_feature_ledger.exists()
    assert paths.selection_event_ledger.exists()

    stats = validate_recorded_artifact_has_rejected_candidates(paths.candidate_feature_ledger)

    assert stats["rows"] == 5
    assert stats["selected"] == 2
    assert stats["rejected"] == 3
    assert stats["has_rejected_candidates"] is True
