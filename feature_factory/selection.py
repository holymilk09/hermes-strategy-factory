"""
Feature Selection — rank features by predictive power, stability, and uniqueness.

Methods:
  1. Mutual information (non-linear relationship with forward returns)
  2. Stability score (how consistent across time periods)
  3. Redundancy detection (correlation between features)
  4. Composite ranking across all metrics
"""
import numpy as np


def mutual_information(x: np.ndarray, y: np.ndarray, n_bins: int = 20) -> float:
    """
    Mutual information between feature x and target y.
    Uses histogram-based estimation.
    """
    mask = ~np.isnan(x) & ~np.isnan(y)
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 50:
        return 0.0

    # Bin the data
    x_bins = np.percentile(x_clean, np.linspace(0, 100, n_bins + 1))
    x_bins = np.unique(x_bins)
    y_bins = np.percentile(y_clean, np.linspace(0, 100, n_bins + 1))
    y_bins = np.unique(y_bins)

    x_digit = np.digitize(x_clean, x_bins) - 1
    y_digit = np.digitize(y_clean, y_bins) - 1
    x_digit = np.clip(x_digit, 0, len(x_bins) - 1)
    y_digit = np.clip(y_digit, 0, len(y_bins) - 1)

    # Joint histogram
    joint = np.zeros((len(x_bins), len(y_bins)))
    for i in range(len(x_clean)):
        joint[x_digit[i], y_digit[i]] += 1
    joint /= len(x_clean)

    # Marginals
    px = np.sum(joint, axis=1)
    py = np.sum(joint, axis=0)

    # Mutual information
    mi = 0.0
    for i in range(len(x_bins)):
        for j in range(len(y_bins)):
            if joint[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += joint[i, j] * np.log(joint[i, j] / (px[i] * py[j]))

    return mi


def stability_score(feature_values: np.ndarray, n_splits: int = 3) -> float:
    """
    Measure how stable a feature's statistical properties are across time.
    High stability = low variance in mean/std across time segments.
    """
    mask = ~np.isnan(feature_values)
    clean = feature_values[mask]
    if len(clean) < n_splits * 20:
        return 0.0

    split_size = len(clean) // n_splits
    means = []
    stds = []
    for i in range(n_splits):
        seg = clean[i * split_size:(i + 1) * split_size]
        if len(seg) > 10:
            means.append(np.mean(seg))
            stds.append(np.std(seg))

    if not means:
        return 0.0

    # Lower variance in mean/std = higher stability
    mean_cv = np.std(means) / (abs(np.mean(means)) + 1e-10)
    std_cv = np.std(stds) / (abs(np.mean(stds)) + 1e-10)

    # Invert so higher = more stable
    stability = 1.0 / (1.0 + mean_cv + std_cv)
    return min(stability, 1.0)


def redundancy_check(feature_matrix: np.ndarray, feature_names: list) -> dict:
    """
    Detect highly correlated features (potential redundancy).
    Returns dict of {feature_name: correlated_alternatives}
    """
    threshold = 0.85
    redundant = {}

    for i, name_i in enumerate(feature_names):
        corr_alt = []
        for j, name_j in enumerate(feature_names):
            if i >= j:
                continue
            mask = ~np.isnan(feature_matrix[:, i]) & ~np.isnan(feature_matrix[:, j])
            if np.sum(mask) < 20:
                continue
            corr_val = np.abs(np.corrcoef(
                feature_matrix[mask, i],
                feature_matrix[mask, j]
            )[0, 1])
            if corr_val > threshold:
                corr_alt.append(name_j)
        if corr_alt:
            redundant[name_i] = corr_alt

    return redundant


def rank_features(
    features: dict,
    forward_returns: np.ndarray,
    n_top: int = 20,
) -> dict:
    """
    Rank features by composite score: MI score + stability - redundancy.

    features: {feature_name: np.array}
    forward_returns: np.array of same length (target to predict)

    Returns sorted list of {name, mi_score, stability, composite}
    """
    rankings = []

    for name, values in features.items():
        if not isinstance(values, np.ndarray):
            continue
        if len(values) < 100:
            continue

        mi = mutual_information(values, forward_returns)
        stab = stability_score(values)

        # Composite: weight MI higher than stability
        composite = mi * 0.7 + stab * 0.3

        rankings.append({
            "name": name,
            "mi_score": round(mi, 4),
            "stability": round(stab, 4),
            "composite": round(composite, 4),
            "n_nan": int(np.sum(np.isnan(values))),
            "mean": round(float(np.nanmean(values)), 4),
            "std": round(float(np.nanstd(values)), 4),
        })

    rankings.sort(key=lambda x: x["composite"], reverse=True)
    return rankings[:n_top]
