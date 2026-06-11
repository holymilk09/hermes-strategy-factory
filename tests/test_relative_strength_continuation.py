import pandas as pd

from src.research.momentum.relative_strength_continuation import (
    RelativeStrengthConfig,
    audit_rule,
    classify_relative_strength,
)


def test_audit_rule():
    df = pd.DataFrame(
        {
            "ret_20d_rank": [0.90, 0.50],
            "ret_60d_rank": [0.80, 0.80],
            "close_above_ma50": [True, True],
            "ret_5d": [0.01, 0.01],
            "selected": [True, False],
        }
    )

    result = audit_rule(df, RelativeStrengthConfig())

    assert result["pass"] is True
    assert result["mismatch_count"] == 0


def test_classify_relative_strength_pass():
    df = pd.DataFrame({"selected": [True] * 240 + [False] * 1000})
    audit = {"pass": True}
    fold_df = pd.DataFrame(
        {
            "selected_rows": [60, 60, 60, 60],
            "selected_mean": [0.012, 0.012, 0.012, 0.012],
            "selected_hit": [0.56, 0.56, 0.56, 0.56],
            "spread": [0.006, 0.006, 0.006, 0.006],
        }
    )
    rand = {"random_percentile": 0.96}

    result = classify_relative_strength(df, audit, fold_df, rand)

    assert result == "TRUE_WALK_FORWARD_PASS"


def test_classify_relative_strength_fail_random():
    df = pd.DataFrame({"selected": [True] * 240 + [False] * 1000})
    audit = {"pass": True}
    fold_df = pd.DataFrame(
        {
            "selected_rows": [60, 60, 60, 60],
            "selected_mean": [0.012, 0.012, 0.012, 0.012],
            "selected_hit": [0.56, 0.56, 0.56, 0.56],
            "spread": [0.006, 0.006, 0.006, 0.006],
        }
    )
    rand = {"random_percentile": 0.70}

    result = classify_relative_strength(df, audit, fold_df, rand)

    assert result == "TRUE_WALK_FORWARD_FAIL"


def test_classify_relative_strength_inconclusive_count():
    df = pd.DataFrame({"selected": [True] * 100 + [False] * 1000})
    audit = {"pass": True}
    fold_df = pd.DataFrame(
        {
            "selected_rows": [25, 25, 25, 25],
            "selected_mean": [0.012, 0.012, 0.012, 0.012],
            "selected_hit": [0.56, 0.56, 0.56, 0.56],
            "spread": [0.006, 0.006, 0.006, 0.006],
        }
    )
    rand = {"random_percentile": 0.96}

    result = classify_relative_strength(df, audit, fold_df, rand)

    assert result == "TRUE_WALK_FORWARD_INCONCLUSIVE"
