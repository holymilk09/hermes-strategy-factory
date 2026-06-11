"""Tests for Phase 24C — Price-Volume Capitulation V2."""

import pandas as pd

from scripts.validate_price_volume_capitulation_v2 import classify_v2


def test_classify_v2_pass():
    df = pd.DataFrame({"selected": [True] * 200 + [False] * 1000})

    rule_audit = {"pass": True}

    fold_df = pd.DataFrame(
        {
            "selected_rows": [50, 50, 50, 50],
            "selected_mean": [0.01, 0.01, 0.01, 0.01],
            "selected_hit": [0.56, 0.56, 0.56, 0.56],
            "selected_vs_rejected_spread": [0.01, 0.01, 0.01, 0.01],
        }
    )

    random_baseline = {"random_percentile": 0.96}

    result = classify_v2(df, rule_audit, fold_df, random_baseline)

    assert result == "TRUE_WALK_FORWARD_PASS"


def test_classify_v2_weak_pass():
    df = pd.DataFrame({"selected": [True] * 200 + [False] * 1000})

    rule_audit = {"pass": True}

    fold_df = pd.DataFrame(
        {
            "selected_rows": [50, 50, 50, 50],
            "selected_mean": [0.01, 0.01, 0.01, 0.01],
            "selected_hit": [0.56, 0.56, 0.56, 0.56],
            "selected_vs_rejected_spread": [0.01, 0.01, 0.01, 0.008],
        }
    )

    random_baseline = {"random_percentile": 0.91}

    result = classify_v2(df, rule_audit, fold_df, random_baseline)

    assert result == "TRUE_WALK_FORWARD_WEAK_PASS"


def test_classify_v2_inconclusive_low_count():
    df = pd.DataFrame({"selected": [True] * 100 + [False] * 1000})

    rule_audit = {"pass": True}

    fold_df = pd.DataFrame(
        {
            "selected_rows": [25, 25, 25, 25],
            "selected_mean": [0.01, 0.01, 0.01, 0.01],
            "selected_hit": [0.56, 0.56, 0.56, 0.56],
            "selected_vs_rejected_spread": [0.01, 0.01, 0.01, 0.01],
        }
    )

    random_baseline = {"random_percentile": 0.96}

    result = classify_v2(df, rule_audit, fold_df, random_baseline)

    assert result == "TRUE_WALK_FORWARD_INCONCLUSIVE"


def test_classify_v2_fail_random():
    df = pd.DataFrame({"selected": [True] * 200 + [False] * 1000})

    rule_audit = {"pass": True}

    fold_df = pd.DataFrame(
        {
            "selected_rows": [50, 50, 50, 50],
            "selected_mean": [0.01, 0.01, 0.01, 0.01],
            "selected_hit": [0.56, 0.56, 0.56, 0.56],
            "selected_vs_rejected_spread": [0.01, 0.01, 0.01, 0.01],
        }
    )

    random_baseline = {"random_percentile": 0.80}

    result = classify_v2(df, rule_audit, fold_df, random_baseline)

    assert result == "TRUE_WALK_FORWARD_FAIL"
