import pandas as pd
from src.sample_data_pipeline import validate_bars, normalize_bars


def test_validate_bars_accepts_valid_rows():
    df = pd.DataFrame({
        "timestamp": ["2026-01-01"],
        "symbol": ["spy"],
        "open": [100], "high": [101], "low": [99], "close": [100.5], "volume": [1000]
    })
    validate_bars(df)


def test_normalize_uppercases_symbol():
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-01-01"]),
        "symbol": [" spy "],
        "open": [100], "high": [101], "low": [99], "close": [100.5], "volume": [1000]
    })
    out = normalize_bars(df)
    assert out.loc[0, "symbol"] == "SPY"
