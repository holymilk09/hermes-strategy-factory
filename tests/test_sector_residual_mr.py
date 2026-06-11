import numpy as np
import pandas as pd

from src.research.sector_residual.sector_residual_mr import (
    SectorResidualConfig,
    audit_rule,
    classify_sector_residual,
    rolling_sector_residual_features,
    sector_etf_for_symbol,
)


def test_sector_etf_for_symbol():
    etf, source, sector = sector_etf_for_symbol("AAPL")

    assert etf == "XLK"
    assert source == "STATIC_MAP"
    assert sector == "TECH"


def test_sector_etf_fallback():
    etf, source, sector = sector_etf_for_symbol("UNKNOWN")

    assert etf == "SPY"
    assert source == "FALLBACK_SPY"


def test_rolling_sector_residual_features():
    rng = np.random.default_rng(1)

    sector = pd.Series(rng.normal(0, 0.01, 150))
    stock = sector * 1.2 + pd.Series(rng.normal(0, 0.01, 150))

    z, r2 = rolling_sector_residual_features(stock, sector, lookback=60, min_obs=45)

    assert len(z) == 150
    assert len(r2) == 150


def test_audit_rule():
    df = pd.DataFrame(
        {
            "sector_residual_z": [-2.5, -1.0],
            "sector_model_r2": [0.2, 0.2],
            "selected": [True, False],
        }
    )

    result = audit_rule(df, SectorResidualConfig())

    assert result["pass"] is True
    assert result["mismatch_count"] == 0


def test_classify_sector_residual_pass():
    df = pd.DataFrame({"selected": [True] * 200 + [False] * 1000})
    audit = {"pass": True}
    fold_df = pd.DataFrame(
        {
            "selected_rows": [50, 50, 50, 50],
            "selected_mean": [0.01, 0.01, 0.01, 0.01],
            "selected_hit": [0.56, 0.56, 0.56, 0.56],
            "spread": [0.01, 0.01, 0.01, 0.01],
        }
    )
    rand = {"random_percentile": 0.96}

    result = classify_sector_residual(df, audit, fold_df, rand)

    assert result == "TRUE_WALK_FORWARD_PASS"


def test_classify_sector_residual_fail_random():
    df = pd.DataFrame({"selected": [True] * 200 + [False] * 1000})
    audit = {"pass": True}
    fold_df = pd.DataFrame(
        {
            "selected_rows": [50, 50, 50, 50],
            "selected_mean": [0.01, 0.01, 0.01, 0.01],
            "selected_hit": [0.56, 0.56, 0.56, 0.56],
            "spread": [0.01, 0.01, 0.01, 0.01],
        }
    )
    rand = {"random_percentile": 0.80}

    result = classify_sector_residual(df, audit, fold_df, rand)

    assert result == "TRUE_WALK_FORWARD_FAIL"
