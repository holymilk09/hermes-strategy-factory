"""Tests for Phase 25A — Regime Contingency Forensics."""

import pandas as pd

from src.research.regime_forensics.fold_regime_diagnostics import (
    build_diagnostic_decision,
    build_time_folds,
    classify_regime_contingency,
    compute_universe_breadth,
    summarize_selected_vs_rejected,
)


def test_build_time_folds():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=100, tz="UTC"),
        }
    )

    folds = build_time_folds(df, 4)

    assert len(folds) == 4


def test_summarize_selected_vs_rejected():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=100, tz="UTC"),
            "symbol": ["A"] * 100,
            "selected": [True, False] * 50,
            "forward_return": [0.02, 0.0] * 50,
            "family": ["x"] * 100,
        }
    )

    folds = build_time_folds(df, 4)
    out = summarize_selected_vs_rejected(df, folds)

    assert len(out) == 4
    assert out["spread"].mean() > 0


def test_compute_universe_breadth():
    df = pd.DataFrame(
        {
            "timestamp": ["2026-01-01", "2026-01-01"],
            "selected": [True, False],
            "forward_return": [0.01, -0.01],
        }
    )

    out = compute_universe_breadth(df)

    assert len(out) == 1
    assert out["candidate_count"].iloc[0] == 2


def test_classify_regime_dependency_plausible():
    family_summary = pd.DataFrame(
        {
            "fold": [1, 2, 3, 4],
            "spread": [-0.01, 0.0, 0.03, -0.01],
        }
    )

    regime_summary = pd.DataFrame(
        {
            "fold": [1, 2, 3, 4],
            "universe_forward_mean": [0.0, 0.0, 0.02, 0.0],
            "spy_position_60d_mean": [0.3, 0.4, 0.8, 0.3],
            "spy_above_ma50_rate": [0.2, 0.3, 0.9, 0.2],
        }
    )

    result = classify_regime_contingency(family_summary, regime_summary)

    assert result == "REGIME_DEPENDENCY_PLAUSIBLE"


def test_decision_text():
    decision = build_diagnostic_decision("REGIME_DEPENDENCY_PLAUSIBLE")

    assert "pre-registered" in decision
