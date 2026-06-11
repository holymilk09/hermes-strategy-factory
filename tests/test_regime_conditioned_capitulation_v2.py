import pandas as pd

from src.research.regime_conditioned.capitulation_v2_drawdown import (
    RegimeConditionedConfig,
    apply_regime_conditioned_rule,
    audit_rule,
    classify_holdout,
)


def test_apply_regime_conditioned_rule():
    df = pd.DataFrame(
        {
            "ret_3d_z": [-2.0, -1.0],
            "volume_z_20": [1.5, 1.5],
            "close_location": [0.7, 0.7],
            "spy_drawdown_60d": [-0.05, -0.05],
        }
    )

    selected = apply_regime_conditioned_rule(df, RegimeConditionedConfig())

    assert selected.tolist() == [True, False]


def test_audit_rule():
    df = pd.DataFrame(
        {
            "ret_3d_z": [-2.0, -1.0],
            "volume_z_20": [1.5, 1.5],
            "close_location": [0.7, 0.7],
            "spy_drawdown_60d": [-0.05, -0.05],
            "selected": [True, False],
        }
    )

    audit = audit_rule(df, RegimeConditionedConfig())

    assert audit["pass"] is True
    assert audit["mismatch_count"] == 0


def test_classify_holdout_pass():
    df = pd.DataFrame({"selected": [True] * 100 + [False] * 1000})
    audit = {"pass": True}

    fold_df = pd.DataFrame(
        {
            "fold": [1, 2, 3, 4],
            "is_holdout": [False, False, True, True],
            "selected_rows": [10, 10, 40, 40],
            "selected_mean": [0.0, 0.0, 0.02, 0.02],
            "selected_hit": [0.5, 0.5, 0.60, 0.60],
            "spread": [0.0, 0.0, 0.01, 0.01],
        }
    )

    random_baseline = {"random_percentile": 0.96}

    result = classify_holdout(df, audit, fold_df, random_baseline, RegimeConditionedConfig())

    assert result == "REGIME_HOLDOUT_PASS_RESEARCH_ONLY"


def test_classify_holdout_fail_random():
    df = pd.DataFrame({"selected": [True] * 100 + [False] * 1000})
    audit = {"pass": True}

    fold_df = pd.DataFrame(
        {
            "fold": [1, 2, 3, 4],
            "is_holdout": [False, False, True, True],
            "selected_rows": [10, 10, 40, 40],
            "selected_mean": [0.0, 0.0, 0.02, 0.02],
            "selected_hit": [0.5, 0.5, 0.60, 0.60],
            "spread": [0.0, 0.0, 0.01, 0.01],
        }
    )

    random_baseline = {"random_percentile": 0.80}

    result = classify_holdout(df, audit, fold_df, random_baseline, RegimeConditionedConfig())

    assert result == "REGIME_HOLDOUT_FAIL"
