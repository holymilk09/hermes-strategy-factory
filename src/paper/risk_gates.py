from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class PaperRiskConfig:
    max_shadow_orders_per_day: int = 10
    max_symbol_orders_per_day: int = 1
    min_residual_r2: float = 0.20
    max_residual_z: float = -2.0
    allow_short: bool = False


def apply_paper_risk_gates(
    candidates: pd.DataFrame,
    config: PaperRiskConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    config = config or PaperRiskConfig()

    df = candidates.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    required = ["timestamp", "symbol", "residual_z", "residual_r2"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Risk gate input missing columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["symbol"] = df["symbol"].astype(str)
    df["residual_z"] = pd.to_numeric(df["residual_z"], errors="coerce")
    df["residual_r2"] = pd.to_numeric(df["residual_r2"], errors="coerce")

    df = df.dropna(subset=["timestamp", "symbol", "residual_z", "residual_r2"])
    df = df.sort_values(["timestamp", "residual_z"], ascending=[True, True])

    df["risk_pass"] = True
    df["risk_reject_reason"] = ""

    bad_rule = ~(
        (df["residual_z"] <= config.max_residual_z)
        & (df["residual_r2"] >= config.min_residual_r2)
    )

    df.loc[bad_rule, "risk_pass"] = False
    df.loc[bad_rule, "risk_reject_reason"] = "RULE_FAIL"

    if not config.allow_short and "side" in df.columns:
        short_mask = df["side"].astype(str).str.lower().eq("short")
        df.loc[short_mask, "risk_pass"] = False
        df.loc[short_mask, "risk_reject_reason"] = "SHORT_BLOCKED"

    passing = df[df["risk_pass"]].copy()

    if passing.empty:
        summary = {
            "input_rows": int(len(df)),
            "passing_rows": 0,
            "rejected_rows": int(len(df)),
            "final_rows": 0,
        }
        return passing, summary

    passing["trade_date"] = passing["timestamp"].dt.strftime("%Y-%m-%d")

    passing = (
        passing.sort_values(["trade_date", "symbol", "residual_z"])
        .groupby(["trade_date", "symbol"], as_index=False)
        .head(config.max_symbol_orders_per_day)
    )

    passing = (
        passing.sort_values(["trade_date", "residual_z"])
        .groupby("trade_date", as_index=False)
        .head(config.max_shadow_orders_per_day)
    )

    summary = {
        "input_rows": int(len(df)),
        "passing_rows_before_caps": int(df["risk_pass"].sum()),
        "final_rows": int(len(passing)),
        "rejected_rows": int(len(df) - len(passing)),
        "max_shadow_orders_per_day": config.max_shadow_orders_per_day,
        "max_symbol_orders_per_day": config.max_symbol_orders_per_day,
    }

    return passing.reset_index(drop=True), summary
