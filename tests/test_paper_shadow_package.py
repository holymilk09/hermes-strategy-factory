from pathlib import Path

import pandas as pd
import pytest

from src.paper.risk_gates import PaperRiskConfig, apply_paper_risk_gates
from src.paper.shadow_orders import (
    ShadowOrderConfig,
    append_shadow_orders_atomic,
    build_shadow_orders,
)
from src.paper.strategy_manifest import (
    ResidualStrategyManifest,
    assert_manifest_paper_only,
    write_manifest,
)


def test_manifest_paper_only(tmp_path: Path):
    manifest = ResidualStrategyManifest()
    path = tmp_path / "manifest.json"
    payload = write_manifest(path, manifest)

    assert path.exists()
    assert payload["live_enabled"] is False
    assert payload["broker_execution_enabled"] is False
    assert_manifest_paper_only(payload)


def test_manifest_rejects_live_enabled():
    payload = {
        "mode": "PAPER_SHADOW_ONLY",
        "production_enabled": False,
        "live_enabled": True,
        "broker_execution_enabled": False,
    }

    with pytest.raises(ValueError):
        assert_manifest_paper_only(payload)


def test_risk_gates_apply_rule_and_caps():
    df = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"] * 4,
            "symbol": ["A", "B", "C", "D"],
            "residual_z": [-2.5, -1.0, -3.0, -2.2],
            "residual_r2": [0.30, 0.30, 0.10, 0.50],
        }
    )

    gated, summary = apply_paper_risk_gates(
        df,
        PaperRiskConfig(max_shadow_orders_per_day=10),
    )

    assert len(gated) == 2
    assert set(gated["symbol"]) == {"A", "D"}
    assert summary["final_rows"] == 2


def test_build_shadow_orders_never_sent_to_broker():
    df = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "symbol": ["AAPL"],
            "strategy": ["residual_reversion"],
            "residual_z": [-2.5],
            "residual_r2": [0.30],
        }
    )

    orders = build_shadow_orders(df, ShadowOrderConfig())

    assert len(orders) == 1
    assert bool(orders["sent_to_broker"].iloc[0]) is False
    assert orders["execution_mode"].iloc[0] == "SHADOW_ONLY"
    assert orders["broker_order_id"].isna().all()


def test_append_shadow_orders_atomic_dedupes(tmp_path: Path):
    df = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "symbol": ["AAPL"],
            "strategy": ["residual_reversion"],
        }
    )

    orders = build_shadow_orders(df)
    output = tmp_path / "shadow_orders.csv"

    r1 = append_shadow_orders_atomic(orders, output)
    r2 = append_shadow_orders_atomic(orders, output)

    saved = pd.read_csv(output)

    assert r1["rows_written"] == 1
    assert r2["rows_written"] == 1
    assert len(saved) == 1
