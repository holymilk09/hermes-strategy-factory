import pandas as pd

from src.research.robustness.residual_edge_audit import (
    bootstrap_mean_returns,
    classify_edge_robustness,
    contribution_concentration,
    chronological_split_summary,
    grouped_summary,
    normalize_trade_ledger,
    summarize_returns,
)


def test_normalize_trade_ledger():
    raw = pd.DataFrame(
        {
            "symbol": ["AAPL", "MSFT"],
            "entry_time": ["2024-01-01", "2024-01-02"],
            "return": [0.01, -0.02],
        }
    )

    out = normalize_trade_ledger(raw)

    assert "timestamp" in out.columns
    assert "realized_return" in out.columns
    assert "strategy" in out.columns
    assert "side" in out.columns
    assert len(out) == 2


def test_summarize_returns():
    df = pd.DataFrame({"realized_return": [0.01, -0.01, 0.03]})

    s = summarize_returns(df)

    assert s["trades"] == 3
    assert s["hit_rate"] == 2 / 3
    assert s["mean"] > 0


def test_grouped_summary():
    df = pd.DataFrame(
        {
            "symbol": ["A", "A", "B"],
            "realized_return": [0.01, 0.02, -0.01],
        }
    )

    out = grouped_summary(df, "symbol")

    assert set(out["symbol"]) == {"A", "B"}


def test_contribution_concentration():
    df = pd.DataFrame(
        {
            "symbol": ["A", "A", "B"],
            "realized_return": [1.0, 1.0, 1.0],
        }
    )

    out = contribution_concentration(df, "symbol")

    assert out["top_group"] == "A"
    assert out["top_abs_contribution_share"] == 2 / 3


def test_bootstrap_mean_returns():
    df = pd.DataFrame({"realized_return": [0.01, 0.02, 0.03, -0.01]})

    out = bootstrap_mean_returns(df, n=50, seed=1)

    assert out["runs"] == 50
    assert out["positive_rate"] is not None


def test_chronological_split_summary():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=8, freq="D"),
            "realized_return": [0.01] * 8,
        }
    )

    out = chronological_split_summary(df, splits=4)

    assert len(out) == 4
    assert all(out["trades"] == 2)


def test_classify_edge_robustness_no_edge():
    baseline = {"trades": 200, "mean": 0.001, "hit_rate": 0.51}
    symbol_concentration = {"top_abs_contribution_share": 0.10}
    month_concentration = {"top_abs_contribution_share": 0.10}
    bootstrap = {"positive_rate": 0.90}
    splits = pd.DataFrame({"mean": [0.01, 0.01, 0.01, 0.01]})

    result = classify_edge_robustness(
        baseline,
        symbol_concentration,
        month_concentration,
        bootstrap,
        splits,
    )

    assert result == "NO_EDGE"


def test_classify_edge_robustness_candidate():
    baseline = {"trades": 200, "mean": 0.01, "hit_rate": 0.56}
    symbol_concentration = {"top_abs_contribution_share": 0.10}
    month_concentration = {"top_abs_contribution_share": 0.10}
    bootstrap = {"positive_rate": 0.90}
    splits = pd.DataFrame({"mean": [0.01, -0.005, 0.02, 0.01]})

    result = classify_edge_robustness(
        baseline,
        symbol_concentration,
        month_concentration,
        bootstrap,
        splits,
    )

    assert result == "ROBUST_EDGE_CANDIDATE"
