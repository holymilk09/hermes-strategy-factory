import pandas as pd

from src.research.validation.true_walk_forward import (
    ResidualSelectionRule,
    audit_selected_flag_matches_rule,
    classify_true_walk_forward,
    evaluate_true_walk_forward_folds,
    normalize_candidate_ledger,
    random_selection_baseline,
    summarize_returns,
)


def test_normalize_candidate_ledger():
    raw = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "symbol": ["AAPL"],
            "selected": [True],
            "residual_z": [-2.5],
            "residual_r2": [0.30],
            "forward_return": [0.02],
        }
    )

    out = normalize_candidate_ledger(raw)

    assert len(out) == 1
    assert bool(out["selected"].iloc[0]) is True


def test_rule_audit_pass():
    raw = pd.DataFrame(
        {
            "timestamp": ["2024-01-01", "2024-01-02"],
            "symbol": ["AAPL", "MSFT"],
            "selected": [True, False],
            "residual_z": [-2.5, -1.0],
            "residual_r2": [0.30, 0.30],
            "forward_return": [0.02, -0.01],
        }
    )
    df = normalize_candidate_ledger(raw)

    result = audit_selected_flag_matches_rule(df, ResidualSelectionRule())

    assert result["pass"] is True
    assert result["mismatch_count"] == 0


def test_rule_audit_fail():
    raw = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "symbol": ["AAPL"],
            "selected": [False],
            "residual_z": [-2.5],
            "residual_r2": [0.30],
            "forward_return": [0.02],
        }
    )
    df = normalize_candidate_ledger(raw)

    result = audit_selected_flag_matches_rule(df, ResidualSelectionRule())

    assert result["pass"] is False
    assert result["mismatch_count"] == 1


def test_summarize_returns():
    df = pd.DataFrame({"forward_return": [0.01, -0.01, 0.03]})

    s = summarize_returns(df)

    assert s["trades"] == 3
    assert s["hit_rate"] == 2 / 3
    assert s["mean"] > 0


def test_evaluate_true_walk_forward_folds():
    rows = []
    for i in range(100):
        rows.append(
            {
                "timestamp": pd.Timestamp("2024-01-01") + pd.Timedelta(days=i),
                "symbol": f"S{i}",
                "selected": i % 5 == 0,
                "residual_z": -2.5 if i % 5 == 0 else -1.0,
                "residual_r2": 0.30,
                "forward_return": 0.02 if i % 5 == 0 else 0.0,
            }
        )

    df = normalize_candidate_ledger(pd.DataFrame(rows))
    folds = evaluate_true_walk_forward_folds(df, n_folds=4)

    assert len(folds) == 4
    assert folds["selected_rows"].sum() == 20


def test_random_selection_baseline():
    rows = []
    for i in range(100):
        rows.append(
            {
                "timestamp": pd.Timestamp("2024-01-01") + pd.Timedelta(days=i),
                "symbol": f"S{i}",
                "selected": i < 10,
                "residual_z": -2.5 if i < 10 else -1.0,
                "residual_r2": 0.30,
                "forward_return": 0.05 if i < 10 else 0.0,
            }
        )

    df = normalize_candidate_ledger(pd.DataFrame(rows))
    result = random_selection_baseline(df, n=50, seed=1)

    assert result["runs"] == 50
    assert result["observed_mean"] > result["random_mean_avg"]


def test_classify_true_walk_forward_pass():
    rule_audit = {"pass": True}

    fold_df = pd.DataFrame(
        {
            "selected_rows": [30, 30, 30, 30],
            "selected_mean": [0.01, 0.01, 0.01, 0.01],
            "selected_hit": [0.55, 0.55, 0.55, 0.55],
            "selected_vs_rejected_spread": [0.01, 0.01, 0.01, 0.01],
        }
    )

    random_baseline = {"random_percentile": 0.99}

    result = classify_true_walk_forward(
        candidate_count=5000,
        selected_count=120,
        rule_audit=rule_audit,
        fold_df=fold_df,
        random_baseline=random_baseline,
    )

    assert result == "TRUE_WALK_FORWARD_PASS"


def test_classify_true_walk_forward_rule_fail():
    rule_audit = {"pass": False}
    fold_df = pd.DataFrame()
    random_baseline = {"random_percentile": 0.99}

    result = classify_true_walk_forward(
        candidate_count=5000,
        selected_count=120,
        rule_audit=rule_audit,
        fold_df=fold_df,
        random_baseline=random_baseline,
    )

    assert result == "RULE_AUDIT_FAIL"
