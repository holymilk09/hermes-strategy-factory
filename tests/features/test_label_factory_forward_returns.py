"""Test label factory — forward returns compute correctly."""
import sys
sys.path.insert(0, '/opt/data')
import numpy as np
from feature_factory.label_factory import LabelFactory, _forward_return, _triple_barrier_label


def test_forward_return_5d():
    """forward_return_5d = close[t+5] / close[t] - 1"""
    closes = np.array([100, 102, 101, 103, 105, 108, 106, 110], dtype=np.float64)
    result = _forward_return(closes, 5)

    assert len(result) == 8
    # t=0: close[5]=108, 108/100 - 1 = 0.08
    assert abs(result[0] - 0.08) < 0.001
    # t=1: close[6]=106, 106/102 - 1 = 0.0392
    assert abs(result[1] - 0.0392) < 0.01
    # t=2: close[7]=110, 110/101 - 1 = 0.0891
    assert abs(result[2] - 0.0891) < 0.01
    # t=3+: NaN (out of bounds)
    assert np.isnan(result[3])
    assert np.isnan(result[7])
    print("PASS: test_forward_return_5d")


def test_forward_return_10d():
    """forward_return_10d with short array — all NaN after horizon."""
    closes = np.array([100, 101, 102, 103, 104, 105], dtype=np.float64)
    result = _forward_return(closes, 10)
    assert np.all(np.isnan(result))
    print("PASS: test_forward_return_10d")


def test_triple_barrier_profit():
    """Triple barrier hits profit first."""
    highs = np.array([100, 102, 105, 107, 108, 107])
    lows = np.array([99, 100, 101, 103, 104, 105])
    closes = np.array([100, 101, 103, 105, 106, 106])

    result = _triple_barrier_label(highs, lows, closes, 0.05, 0.03, 5)
    # t=0: entry=100, profit=105, stop=97, high reaches 105 at t=2 → +1
    assert result[0] == 1.0
    print("PASS: test_triple_barrier_profit")


def test_triple_barrier_stop():
    """Triple barrier hits stop first."""
    highs = np.array([100, 101, 101, 102])
    lows = np.array([99, 96, 95, 94])
    closes = np.array([100, 98, 97, 96])

    result = _triple_barrier_label(highs, lows, closes, 0.10, 0.03, 5)
    # t=0: entry=100, profit=110, stop=97, low hits 96 at t=1 → -1
    assert result[0] == -1.0
    print("PASS: test_triple_barrier_stop")


def test_triple_barrier_time():
    """Triple barrier expires — no barrier hit."""
    highs = np.array([100, 101, 102, 101, 102])
    lows = np.array([99, 99, 100, 99, 100])
    closes = np.array([100, 100, 101, 100, 101])

    result = _triple_barrier_label(highs, lows, closes, 0.10, 0.10, 3)
    # t=0: entry=100, profit=110, stop=90 — neither hit within 3 days → 0
    assert result[0] == 0.0
    print("PASS: test_triple_barrier_time")


def test_label_factory_builds_all_labels():
    """LabelFactory produces all expected label types."""
    # Minimal test data
    closes = np.array([
        ('2024-01-01', 100, 102, 98, 100, 1000000, 0.0, 0.0),
        ('2024-01-02', 101, 103, 99, 101, 1200000, 0.01, 0.01),
        ('2024-01-03', 102, 104, 100, 102, 1100000, 0.0099, 0.0099),
        ('2024-01-04', 103, 105, 101, 103, 900000, 0.0098, 0.0098),
        ('2024-01-05', 104, 106, 102, 104, 1000000, 0.0097, 0.0097),
        ('2024-01-08', 105, 107, 103, 105, 1100000, 0.0096, 0.0096),
        ('2024-01-09', 106, 108, 104, 106, 1200000, 0.0095, 0.0095),
        ('2024-01-10', 107, 109, 105, 107, 800000, 0.0094, 0.0094),
        ('2024-01-11', 108, 110, 106, 108, 1000000, 0.0093, 0.0093),
        ('2024-01-12', 109, 111, 107, 109, 1100000, 0.0093, 0.0093),
        ('2024-01-15', 110, 112, 108, 110, 1200000, 0.0092, 0.0092),
        ('2024-01-16', 111, 113, 109, 111, 1000000, 0.0091, 0.0091),
    ], dtype=[('date', 'U10'), ('open', 'f8'), ('high', 'f8'),
              ('low', 'f8'), ('close', 'f8'), ('volume', 'f8'),
              ('returns', 'f8'), ('log_returns', 'f8')])

    factory = LabelFactory({"horizons": [1, 5]})
    labels = factory.build_labels({"TEST": closes})

    assert "TEST" in labels
    assert "forward_return_1d" in labels["TEST"]
    assert "forward_return_5d" in labels["TEST"]
    assert "triple_barrier" in labels["TEST"]

    # forward_return_1d at t=0 should be first non-NaN
    result_1d = labels["TEST"]["forward_return_1d"]
    assert not np.isnan(result_1d[0])
    assert abs(result_1d[0] - 0.01) < 0.001  # 101/100 - 1

    print("PASS: test_label_factory_builds_all_labels")


if __name__ == "__main__":
    test_forward_return_5d()
    test_forward_return_10d()
    test_triple_barrier_profit()
    test_triple_barrier_stop()
    test_triple_barrier_time()
    test_label_factory_builds_all_labels()
    print("\nALL TESTS PASSED")
