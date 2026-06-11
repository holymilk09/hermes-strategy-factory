from pathlib import Path

import pandas as pd

from src.research.validation.artifact_reconstruction import (
    ArtifactRole,
    ReconstructionClass,
    build_artifact_manifest,
    classify_role,
    normalize_existing_feature_ledger,
)


def test_classify_trade_ledger_by_columns(tmp_path: Path):
    path = tmp_path / "residual_reversion_trade_ledger.csv"
    columns = ["symbol", "timestamp", "realized_return"]

    role = classify_role(path, columns, "csv_read_ok")

    assert role == ArtifactRole.TRADE_LEDGER.value


def test_classify_candidate_feature_ledger_by_columns(tmp_path: Path):
    path = tmp_path / "residual_candidate_feature_ledger.csv"
    columns = ["symbol", "timestamp", "score", "residual", "forward_return"]

    role = classify_role(path, columns, "csv_read_ok")

    assert role == ArtifactRole.CANDIDATE_FEATURE_LEDGER.value


def test_build_manifest_ledger_only(tmp_path: Path):
    report_dir = tmp_path / "reports" / "strategy_factory"
    report_dir.mkdir(parents=True)

    df = pd.DataFrame(
        {
            "symbol": ["AAPL"],
            "timestamp": ["2024-01-01"],
            "realized_return": [0.01],
        }
    )
    df.to_csv(report_dir / "residual_reversion_trade_ledger.csv", index=False)

    manifest = build_artifact_manifest(tmp_path)

    assert manifest["has_trade_ledger"] is True
    assert manifest["reconstruction_class"] == ReconstructionClass.LEDGER_ONLY.value


def test_build_manifest_true_ready(tmp_path: Path):
    report_dir = tmp_path / "reports" / "strategy_factory"
    report_dir.mkdir(parents=True)

    feature_df = pd.DataFrame(
        {
            "symbol": ["AAPL"],
            "timestamp": ["2024-01-01"],
            "score": [1.2],
            "forward_return": [0.01],
        }
    )
    feature_df.to_csv(report_dir / "residual_candidate_feature_ledger.csv", index=False)

    config_path = report_dir / "residual_selection_config.json"
    config_path.write_text('{"threshold": 1.0, "top_n": 50}', encoding="utf-8")

    manifest = build_artifact_manifest(tmp_path)

    assert manifest["has_candidate_feature_ledger"] is True
    assert manifest["has_selection_config"] is True
    assert manifest["reconstruction_class"] == ReconstructionClass.TRUE_WALK_FORWARD_READY.value


def test_normalize_existing_feature_ledger(tmp_path: Path):
    source = tmp_path / "features.csv"
    output = tmp_path / "normalized.csv"

    df = pd.DataFrame(
        {
            "Symbol": ["AAPL"],
            "Date": ["2024-01-01"],
            "Score": [1.5],
            "Forward_Return": [0.02],
        }
    )
    df.to_csv(source, index=False)

    result = normalize_existing_feature_ledger(source, output)

    assert output.exists()
    assert result["rows"] == 1
    assert "score" in result["score_columns"]
