"""Tests for Phase 23A — Phase 12 Formula Forensics."""

import numpy as np
import pandas as pd

from src.features.forensics.phase12_formula_forensics import (
    FormulaCandidate,
    align_symbol_and_benchmark,
    classify_forensic_match,
    compare_candidate_to_old,
    compute_candidate_features,
    generate_formula_candidates,
    safe_corr,
    simple_rsi,
    wilder_rsi,
)


def test_safe_corr():
    a = np.arange(100, dtype=float)
    b = a.copy()
    assert safe_corr(a, b) > 0.99


def test_simple_and_wilder_rsi():
    close = pd.Series([10, 9, 8, 9, 10, 11, 10, 9], dtype=float)
    s = simple_rsi(close, 2)
    w = wilder_rsi(close, 2)
    assert len(s) == len(close)
    assert len(w) == len(close)
    assert s.notna().all()
    assert w.notna().all()


def test_compute_candidate_features():
    ts = pd.date_range("2024-01-01", periods=200, freq="D", tz="UTC")
    merged = pd.DataFrame(
        {
            "timestamp": ts,
            "symbol_close": np.linspace(100, 150, 200),
            "benchmark_close": np.linspace(400, 500, 200),
        }
    )

    candidate = FormulaCandidate(
        name="test",
        residual_lookback=20,
        residual_mode="price_ratio_z",
        benchmark_symbol="SPY",
        rsi_mode="simple",
        regime_mode="vol_mom_combo",
    )

    out = compute_candidate_features(merged, candidate)
    assert "residual_z" in out.columns
    assert "residual_r2" in out.columns
    assert "rsi_2" in out.columns
    assert "regime_score" in out.columns


def test_compare_candidate_to_old():
    ts = pd.date_range("2024-01-01", periods=200, freq="D", tz="UTC")
    features = pd.DataFrame(
        {
            "residual_z": np.linspace(-2, 2, 200),
            "residual_r2": np.linspace(0, 1, 200),
            "rsi_2": np.linspace(10, 90, 200),
            "regime_score": np.linspace(0, 1, 200),
        }
    )

    old = {
        "residual_z": features["residual_z"].to_numpy(),
        "residual_r2": features["residual_r2"].to_numpy(),
        "rsi_2": features["rsi_2"].to_numpy(),
        "regime_score": features["regime_score"].to_numpy(),
    }

    candidate = FormulaCandidate(
        name="test",
        residual_lookback=20,
        residual_mode="price_ratio_z",
        benchmark_symbol="SPY",
        rsi_mode="simple",
        regime_mode="vol_mom_combo",
    )

    result = compare_candidate_to_old(old, features, candidate)
    assert result["composite_score"] > 0.99


def test_generate_formula_candidates():
    candidates = generate_formula_candidates(["SPY", "XLK"])
    assert len(candidates) > 0
    assert any(c.benchmark_symbol == "XLK" for c in candidates)


def test_classify_forensic_match():
    assert classify_forensic_match(0.95) == "FORENSICS_STRONG_RECONSTRUCTION"
    assert classify_forensic_match(0.80) == "FORENSICS_PARTIAL_RECONSTRUCTION"
    assert classify_forensic_match(0.65) == "FORENSICS_WEAK_RECONSTRUCTION"
    assert classify_forensic_match(0.30) == "FORENSICS_NO_MATCH"
