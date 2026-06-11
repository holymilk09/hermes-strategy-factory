from pathlib import Path

import pandas as pd
import pytest

from src.research.artifacts.candidate_recorder import (
    CandidateArtifactConfig,
    normalize_candidate_frame,
    record_candidate_feature_ledger,
)
from src.research.artifacts.selection_audit import (
    SelectionRule,
    apply_selection_rule,
    validate_selection_rule,
)


def test_normalize_candidate_frame_adds_required_fields():
    raw = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "symbol": ["AAPL"],
            "residual_z": [1.5],
        }
    )

    config = CandidateArtifactConfig(
        strategy_name="mean_reversion",
        universe_name="test",
        timeframe="1D",
        feature_config_hash="abc",
        selection_config_hash="def",
        code_version="test",
    )

    out = normalize_candidate_frame(raw, config)

    assert "candidate_id" in out.columns
    assert "selected" in out.columns
    assert "run_hash" in out.columns
    assert out["strategy"].iloc[0] == "mean_reversion"


def test_record_candidate_feature_ledger(tmp_path: Path):
    raw = pd.DataFrame(
        {
            "timestamp": ["2024-01-01", "2024-01-02"],
            "symbol": ["AAPL", "MSFT"],
            "selected": [True, False],
            "residual_z": [1.5, 0.5],
        }
    )

    config = CandidateArtifactConfig(
        strategy_name="mean_reversion",
        universe_name="test",
        timeframe="1D",
        feature_config_hash="abc",
        selection_config_hash="def",
        code_version="test",
    )

    output = tmp_path / "candidate_feature_ledger.csv"
    result = record_candidate_feature_ledger(raw, config, output)

    assert output.exists()
    assert result["rows_written"] == 2
    assert result["selected_rows"] == 1


def test_selection_rule_threshold():
    df = pd.DataFrame(
        {
            "timestamp": ["2024-01-01", "2024-01-02"],
            "symbol": ["AAPL", "MSFT"],
            "residual_z": [1.5, 0.5],
        }
    )

    rule = SelectionRule(
        rule_name="test",
        strategy="mean_reversion",
        score_column="residual_z",
        threshold=1.0,
        rank_column=None,
        top_n=None,
        direction="higher_is_better",
    )

    out = apply_selection_rule(df, rule)

    assert out["selected"].tolist() == [True, False]
    assert "selection_rule_hash" in out.columns


def test_selection_rule_top_n():
    df = pd.DataFrame(
        {
            "timestamp": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "symbol": ["AAPL", "MSFT", "NVDA"],
            "score": [0.2, 0.9, 0.5],
        }
    )

    rule = SelectionRule(
        rule_name="test_top_n",
        strategy="mean_reversion",
        score_column="score",
        threshold=None,
        rank_column=None,
        top_n=2,
        direction="higher_is_better",
    )

    out = apply_selection_rule(df, rule)

    assert int(out["selected"].sum()) == 2


def test_selection_rule_rejects_no_threshold_or_top_n():
    rule = SelectionRule(
        rule_name="bad",
        strategy="mean_reversion",
        score_column="score",
        threshold=None,
        rank_column=None,
        top_n=None,
        direction="higher_is_better",
    )

    with pytest.raises(ValueError):
        validate_selection_rule(rule)
