"""Test purged/embargo CV — verify no label overlap, chronological order, no shuffle."""
import sys, json, os
sys.path.insert(0, '/opt/data')
import numpy as np
from feature_factory.purged_cv import PurgedCV


def test_no_overlap_20d():
    """With 20-day horizon, train and test label windows must not overlap."""
    cv = PurgedCV(n_splits=3, label_horizon=20, purge_window=20, embargo_window=20)
    splits = cv.split(500)

    assert len(splits) > 0, "No splits generated"

    overlap = cv.verify_no_overlap()
    assert overlap["status"] == "PASS_NO_OVERLAP", f"Overlap violations: {overlap.get('n_violations', '?')}"

    # Check each split manually too
    for train_idx, test_idx in splits:
        assert np.max(train_idx) < np.min(test_idx), "Train after test"
        for t_train in train_idx[:10]:  # Sample check
            label_end = t_train + 20
            for t_test in test_idx:
                assert label_end <= t_test, f"Train label ends at {label_end}, test starts at {t_test}"

    print("PASS: test_no_overlap_20d")


def test_no_overlap_5d():
    """5-day horizon also must not overlap."""
    cv = PurgedCV(n_splits=5, label_horizon=5)
    splits = cv.split(300)

    assert len(splits) >= 2

    overlap = cv.verify_no_overlap()
    assert overlap["status"] == "PASS_NO_OVERLAP"

    print("PASS: test_no_overlap_5d")


def test_chronological_order():
    """All splits must be chronological: train before test, no shuffle."""
    cv = PurgedCV(n_splits=4, label_horizon=10)
    splits = cv.split(400)

    assert len(splits) >= 2

    chronological = cv.verify_chronological()
    assert chronological["status"] == "PASS_CHRONOLOGICAL"

    # Verify train indices increase across splits
    for i in range(len(splits) - 1):
        assert np.max(splits[i][1]) <= np.min(splits[i + 1][1]), \
            f"Split {i} test after split {i+1} test"

    assert not cv.random_shuffle_used, "Random shuffle must be forbidden"

    print("PASS: test_chronological_order")


def test_multi_horizon():
    """Multi-horizon CV factory creates valid CVs for each horizon."""
    cvs = PurgedCV.make_multi_horizon(1000, horizons=[5, 10, 20])

    assert len(cvs) == 3
    for h, cv in cvs.items():
        assert cv.label_horizon == h
        assert cv.purge_window == h
        assert cv.embargo_window == h
        assert len(cv.splits) > 0

        overlap = cv.verify_no_overlap()
        assert overlap["status"] == "PASS_NO_OVERLAP", f"Horizon {h}: overlap found"

    print("PASS: test_multi_horizon")


def test_report_generation():
    """Report contains all required fields."""
    cv = PurgedCV(n_splits=3, label_horizon=10)
    cv.split(300)

    report = cv.generate_report()
    required_fields = ["run_id", "split_method", "n_splits", "label_horizon",
                       "purge_window", "embargo_window", "overlap_check",
                       "chronological_check", "random_shuffle_used", "status"]
    for field in required_fields:
        assert field in report, f"Missing: {field}"

    assert report["random_shuffle_used"] == False
    print("PASS: test_report_generation")


def test_small_data_handling():
    """Too-small data should raise ValueError or produce empty splits."""
    cv = PurgedCV(n_splits=3, label_horizon=20)
    try:
        splits = cv.split(10)
        assert len(splits) == 0
    except ValueError:
        pass  # Expected
    print("PASS: test_small_data_handling")


if __name__ == "__main__":
    test_no_overlap_20d()
    test_no_overlap_5d()
    test_chronological_order()
    test_multi_horizon()
    test_report_generation()
    test_small_data_handling()

    # Save report
    cv = PurgedCV(n_splits=5, label_horizon=20)
    cv.split(500)
    report = cv.generate_report()

    os.makedirs("reports/feature_factory", exist_ok=True)
    with open("reports/feature_factory/purged_cv_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print("\nALL PURGED CV TESTS PASSED")
    print(f"Report saved: reports/feature_factory/purged_cv_report.json")
