import pandas as pd

from src.research.regime_forensics.pit_regime_proxy import (
    build_pit_proxy_decision,
    classify_pit_proxy_result,
    compute_spy_pit_features,
    evaluate_proxy_candidates,
    merge_pit_regime_features,
    summarize_selected_performance_by_pit_bucket,
)


def test_compute_spy_pit_features():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=300, tz="UTC"),
            "open": range(300),
            "high": range(1, 301),
            "low": range(300),
            "close": range(1, 301),
        }
    )

    out = compute_spy_pit_features(df)

    assert "spy_ret_20d_trailing" in out.columns
    assert "spy_position_60d" in out.columns


def test_merge_pit_regime_features():
    candidates = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=3, tz="UTC"),
            "symbol": ["A", "B", "C"],
            "selected": [True, False, True],
            "forward_return": [0.01, -0.01, 0.02],
        }
    )

    spy = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=3, tz="UTC"),
            "spy_ret_20d_trailing": [0.1, 0.2, 0.3],
        }
    )

    universe = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=3, tz="UTC"),
            "universe_positive_20d_rate": [0.4, 0.5, 0.6],
        }
    )

    out = merge_pit_regime_features(candidates, spy, universe)

    assert "spy_ret_20d_trailing" in out.columns
    assert "universe_positive_20d_rate" in out.columns


def test_summarize_selected_performance_by_pit_bucket():
    rows = []
    for i in range(90):
        rows.append(
            {
                "timestamp": pd.Timestamp("2026-01-01", tz="UTC"),
                "selected": i % 3 == 0,
                "forward_return": 0.02 if i > 60 and i % 3 == 0 else 0.0,
                "feature_x": i,
            }
        )

    df = pd.DataFrame(rows)
    out = summarize_selected_performance_by_pit_bucket(df, "feature_x", quantiles=3)

    assert len(out) == 3
    assert "spread" in out.columns


def test_evaluate_proxy_candidates():
    rows = []
    for i in range(120):
        rows.append(
            {
                "timestamp": pd.Timestamp("2026-01-01", tz="UTC"),
                "selected": i % 4 == 0,
                "forward_return": 0.02 if i > 80 and i % 4 == 0 else 0.0,
                "spy_ret_20d_trailing": i,
                "spy_ret_60d_trailing": i,
                "spy_vol_20d_pct252": i,
                "spy_drawdown_60d": i,
                "spy_position_60d": i,
                "universe_ret_20d_median_trailing": i,
                "universe_above_ma20_rate": i,
                "universe_above_ma50_rate": i,
                "universe_positive_20d_rate": i,
                "universe_ret_20d_dispersion": i,
                "universe_volume_z20_median": i,
            }
        )

    out = evaluate_proxy_candidates(pd.DataFrame(rows))

    assert not out.empty


def test_classify_pit_proxy_result():
    bucket_summary = pd.DataFrame(
        {
            "selected_rows": [50],
            "spread": [0.02],
            "selected_mean": [0.02],
        }
    )

    result = classify_pit_proxy_result(bucket_summary)

    assert result == "PIT_PROXY_CANDIDATE_FOUND"


def test_decision_text():
    decision = build_pit_proxy_decision("PIT_PROXY_CANDIDATE_FOUND")

    assert "pre-registered" in decision
