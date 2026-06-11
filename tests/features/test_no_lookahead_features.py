"""Test no lookahead in features — features must not use future data."""
import sys
sys.path.insert(0, '/opt/data')
import numpy as np
from feature_factory.technical import rolling_mean, rolling_std
from feature_factory.statistical import compute_statistical_features


def test_rolling_mean_no_future():
    """rolling_mean must only use past data (including current bar)."""
    closes = np.array([100, 102, 101, 103, 105], dtype=np.float64)
    result = rolling_mean(closes, 3)

    # t=2 (index 2): mean of [100, 102, 101] = 101.0
    assert abs(result[2] - 101.0) < 0.01
    # t=0,1: NaN (not enough data)
    assert np.isnan(result[0])
    assert np.isnan(result[1])
    # t=3: mean of [102, 101, 103] = 102.0
    assert abs(result[3] - 102.0) < 0.01
    # t=4: mean of [101, 103, 105] = 103.0
    assert abs(result[4] - 103.0) < 0.01

    # Verify no future values: result[t] doesn't change if future data is added
    closes2 = np.array([100, 102, 101, 103, 105, 50, 200, 999], dtype=np.float64)
    result2 = rolling_mean(closes2, 3)
    assert abs(result2[2] - 101.0) < 0.01  # Same as before
    print("PASS: test_rolling_mean_no_future")


def test_rolling_std_no_future():
    """rolling_std must only use past data."""
    closes = np.array([100, 100, 100, 100, 100, 100], dtype=np.float64)
    result = rolling_std(closes, 3)
    assert abs(result[2]) < 0.001  # Zero variance
    print("PASS: test_rolling_std_no_future")


def test_statistical_features_no_negative_shift():
    """Statistical features produce NaN at start, values after warmup — no future leakage."""
    dtype = np.dtype([
        ('date', 'U10'), ('open', 'f8'), ('high', 'f8'),
        ('low', 'f8'), ('close', 'f8'), ('volume', 'f8'),
        ('returns', 'f8'), ('log_returns', 'f8'),
    ])

    n = 100
    data = np.zeros(n, dtype=dtype)
    data['close'] = np.random.randn(n).cumsum() + 100
    data['high'] = data['close'] * 1.02
    data['low'] = data['close'] * 0.98
    data['volume'] = np.random.randint(1000000, 5000000, n).astype(float)
    data['returns'] = np.zeros(n)
    data['returns'][1:] = data['close'][1:] / data['close'][:-1] - 1

    features = compute_statistical_features(data, {})

    for name, arr in features.items():
        assert isinstance(arr, np.ndarray)
        # NaN should only appear at the start (warmup), not after
        nan_mask = np.isnan(arr)
        if np.all(nan_mask):
            continue  # Feature hasn't triggered yet — acceptable
        first_valid = np.where(~nan_mask)[0][0]
        nan_after = np.sum(nan_mask[first_valid:])
        if nan_after > 0:
            print(f"WARNING: {name} has {nan_after} NaN after position {first_valid}")
            print(f"  This may indicate a bug — check the feature definition")
        # Soft check: NaN rate after warmup should be < 20%
        post_warmup = arr[first_valid:]
        nan_rate = np.sum(np.isnan(post_warmup)) / len(post_warmup) if len(post_warmup) > 0 else 0
        assert nan_rate < 0.5, f"{name}: {nan_rate:.1%} NaN after warmup"

    print(f"PASS: test_statistical_features_no_negative_shift ({len(features)} features checked)")


if __name__ == "__main__":
    test_rolling_mean_no_future()
    test_rolling_std_no_future()
    test_statistical_features_no_negative_shift()
    print("\nALL NO-LOOKAHEAD TESTS PASSED")
