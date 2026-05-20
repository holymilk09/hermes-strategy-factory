"""
Residual Features — factor residual dislocation (Avellaneda & Lee framework).

Regress stock returns on sector ETF returns to extract idiosyncratic residual.
Then compute residual z-score, cumulative residual, half-life, etc.

Point-in-time: regression uses only past data in rolling windows.
"""
import numpy as np
from feature_factory.technical import rolling_mean, rolling_std


def compute_residual_features(df, etf_df, config: dict, benchmark_type: str = "sector") -> dict:
    """
    Compute residual features by regressing stock returns on sector ETF returns.

    df: structured array for the stock
    etf_df: structured array for the sector ETF (or None)

    Returns dict: {feature_name: np.array}
    """
    n = len(df['close'])
    features = {
        "residual_z": np.full(n, np.nan),
        "residual_beta": np.full(n, np.nan),
        "residual_alpha": np.full(n, np.nan),
        "cumulative_residual": np.full(n, np.nan),
        "residual_half_life": np.full(n, np.nan),
        "residual_r2": np.full(n, np.nan),
        "residual_return": np.full(n, np.nan),
    }

    if etf_df is None or len(etf_df) < 60:
        return features

    window = config.get("regression_window", 60)
    z_window = config.get("zscore_window", 20)

    stock_rets = df['returns']
    etf_rets = etf_df['returns']

    # Align lengths — use shorter
    min_len = min(n, len(etf_rets))
    if min_len < window:
        return features

    for i in range(window, min_len):
        s = stock_rets[i - window + 1:i + 1]
        e = etf_rets[i - window + 1:i + 1]

        # Remove NaN pairs
        mask = ~np.isnan(s) & ~np.isnan(e)
        s_clean = s[mask]
        e_clean = e[mask]

        if len(s_clean) < 20:
            continue

        # Linear regression: s = alpha + beta * e + epsilon
        mean_s = np.mean(s_clean)
        mean_e = np.mean(e_clean)

        num = np.sum((s_clean - mean_s) * (e_clean - mean_e))
        den = np.sum((e_clean - mean_e) ** 2)

        if den == 0:
            continue

        beta = num / den
        alpha = mean_s - beta * mean_e

        # Residuals
        residuals = s_clean - (alpha + beta * e_clean)

        # R-squared
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((s_clean - mean_s) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Cumulative residual over z_window
        cum_res = np.sum(residuals[-z_window:]) if len(residuals) >= z_window else np.sum(residuals)

        # z-score
        mean_res = np.mean(residuals)
        std_res = np.std(residuals)
        if std_res > 0:
            features["residual_z"][i] = (cum_res - (mean_res * min(z_window, len(residuals)))) / (std_res * np.sqrt(min(z_window, len(residuals))))
        else:
            features["residual_z"][i] = 0.0

        features["residual_beta"][i] = beta
        features["residual_alpha"][i] = alpha
        features["cumulative_residual"][i] = cum_res
        features["residual_r2"][i] = r2

        # Current period residual return
        if not np.isnan(stock_rets[i]) and not np.isnan(etf_rets[i]):
            features["residual_return"][i] = stock_rets[i] - (alpha + beta * etf_rets[i])

        # Half-life estimation (Ornstein-Uhlenbeck)
        if len(residuals) > 10:
            features["residual_half_life"][i] = _estimate_half_life(residuals)

    return features


def _estimate_half_life(residuals: np.ndarray) -> float:
    """
    Estimate half-life of mean reversion for an OU process.
    Half-life = ln(2) / theta where theta is the speed of mean reversion.

    Uses regression: residual(t) - residual(t-1) = a + b * residual(t-1) + e
    Then half-life = -ln(2) / b
    """
    n = len(residuals)
    if n < 10:
        return np.nan

    # Cumulative residuals
    cum_res = np.cumsum(residuals)

    y = np.diff(cum_res)
    x = cum_res[:-1]

    mask = ~np.isnan(x) & ~np.isnan(y)
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 5:
        return np.nan

    # Simple regression
    mean_x = np.mean(x_clean)
    mean_y = np.mean(y_clean)
    num = np.sum((x_clean - mean_x) * (y_clean - mean_y))
    den = np.sum((x_clean - mean_x) ** 2)

    if den == 0:
        return np.nan

    b = num / den  # theta (negative for mean-reverting)
    if b >= 0:
        return np.inf  # Not mean-reverting
    return -np.log(2) / b
