from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ShadowOrderConfig:
    order_type: str = "MARKET_ON_NEXT_OPEN_SHADOW"
    notional_usd: float = 1000.0
    side: str = "BUY"
    tif: str = "DAY"
    execution_mode: str = "SHADOW_ONLY"


def build_shadow_order_id(timestamp: pd.Series, symbol: pd.Series, strategy: pd.Series) -> pd.Series:
    raw = timestamp.astype(str) + "|" + symbol.astype(str) + "|" + strategy.astype(str)
    return raw.map(lambda x: sha256(x.encode("utf-8")).hexdigest()[:24])


def build_shadow_orders(
    candidates: pd.DataFrame,
    config: ShadowOrderConfig | None = None,
) -> pd.DataFrame:
    config = config or ShadowOrderConfig()
    df = candidates.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    required = ["timestamp", "symbol"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Shadow order input missing columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["symbol"] = df["symbol"].astype(str)

    if "strategy" not in df.columns:
        df["strategy"] = "residual_reversion"

    df = df.dropna(subset=["timestamp", "symbol"])

    orders = pd.DataFrame()
    orders["timestamp"] = df["timestamp"]
    orders["symbol"] = df["symbol"]
    orders["strategy"] = df["strategy"]
    orders["side"] = config.side
    orders["order_type"] = config.order_type
    orders["notional_usd"] = config.notional_usd
    orders["tif"] = config.tif
    orders["execution_mode"] = config.execution_mode
    orders["broker_order_id"] = None
    orders["sent_to_broker"] = False
    orders["shadow_order_id"] = build_shadow_order_id(
        orders["timestamp"],
        orders["symbol"],
        orders["strategy"],
    )

    carry_cols = [
        "residual_z",
        "residual_r2",
        "rsi_2",
        "regime_score",
        "forward_return",
        "candidate_id",
        "run_hash",
    ]

    for c in carry_cols:
        if c in df.columns:
            orders[c] = df[c].values

    orders = orders.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    return orders


def append_shadow_orders_atomic(orders: pd.DataFrame, output_path: Path) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        existing = pd.read_csv(output_path)
        combined = pd.concat([existing, orders], axis=0, ignore_index=True)
        combined = combined.drop_duplicates(subset=["shadow_order_id"], keep="last")
    else:
        combined = orders.copy()

    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    combined.to_csv(tmp, index=False)
    tmp.replace(output_path)

    return {
        "output_path": str(output_path),
        "rows_written": int(len(orders)),
        "total_rows": int(len(combined)),
        "sent_to_broker_any": bool(combined["sent_to_broker"].astype(bool).any())
        if "sent_to_broker" in combined.columns
        else False,
    }
