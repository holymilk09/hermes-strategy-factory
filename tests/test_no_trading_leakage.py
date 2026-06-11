from pathlib import Path

import pandas as pd

from scripts.verify_no_trading_leakage import check_csv


def _write(path: Path, df: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def test_sent_to_broker_false_passes(tmp_path: Path):
    p = _write(tmp_path / "a.csv", pd.DataFrame({"sent_to_broker": [False, False]}))
    assert check_csv(p) == []


def test_sent_to_broker_true_fails(tmp_path: Path):
    p = _write(tmp_path / "a.csv", pd.DataFrame({"sent_to_broker": [False, True]}))
    issues = check_csv(p)
    assert any("sent_to_broker=true" in i for i in issues)


def test_broker_order_id_empty_passes(tmp_path: Path):
    p = _write(tmp_path / "a.csv", pd.DataFrame({"broker_order_id": ["", None]}))
    assert check_csv(p) == []


def test_broker_order_id_populated_fails(tmp_path: Path):
    p = _write(tmp_path / "a.csv", pd.DataFrame({"broker_order_id": ["abc123"]}))
    issues = check_csv(p)
    assert any("broker_order_id populated" in i for i in issues)


def test_production_enabled_false_passes(tmp_path: Path):
    p = _write(tmp_path / "a.csv", pd.DataFrame({"production_enabled": [False]}))
    assert check_csv(p) == []


def test_production_enabled_true_fails(tmp_path: Path):
    p = _write(tmp_path / "a.csv", pd.DataFrame({"production_enabled": [True]}))
    issues = check_csv(p)
    assert any("production_enabled=true" in i for i in issues)
