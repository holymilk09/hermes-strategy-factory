from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OBS_LEDGER = ROOT / "data" / "paper_observation" / "relative_strength_continuation_observation_ledger.csv"
OUTCOME_LEDGER = ROOT / "data" / "paper_observation" / "relative_strength_continuation_outcome_ledger.csv"
REGISTRY = ROOT / "reports" / "strategy_factory" / "hypothesis_registry.csv"
ACTIVE_STATUS = ROOT / "reports" / "strategy_factory" / "active_observation_status.md"
NEXT_ACTION = ROOT / "reports" / "strategy_factory" / "next_action_queue.md"
WATCHDOG_JSON = ROOT / "reports" / "strategy_factory" / "relative_strength_maturity_watchdog.json"

OUT_MD = ROOT / "reports" / "strategy_factory" / "feature_factory_state_snapshot.md"
OUT_JSON = ROOT / "reports" / "strategy_factory" / "feature_factory_state_snapshot.json"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if df.empty:
        return df
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def main() -> None:
    obs = load_csv(OBS_LEDGER)
    out = load_csv(OUTCOME_LEDGER)

    symbols: list[str] = []
    latest_signal_ts = None
    sent_to_broker_any = False

    if not obs.empty:
        if "symbol" in obs.columns:
            symbols = sorted(obs["symbol"].astype(str).str.upper().unique().tolist())
        if "signal_timestamp" in obs.columns:
            ts = pd.to_datetime(obs["signal_timestamp"], utc=True, errors="coerce")
            if ts.notna().any():
                latest_signal_ts = ts.max().isoformat()
        if "sent_to_broker" in obs.columns:
            sent_to_broker_any = bool(obs["sent_to_broker"].astype(bool).any())

    resolved = 0
    pending = int(len(obs)) if not obs.empty else 0
    if not out.empty and "outcome_status" in out.columns:
        st = out["outcome_status"].astype(str)
        resolved = int(st.eq("RESOLVED").sum())
        pending = int(len(out) - resolved)

    maturity_classification = "UNKNOWN"
    mature_count = None
    bars_remaining: dict[str, Any] = {}
    next_allowed_action = "CONTINUE_WAITING"

    if WATCHDOG_JSON.exists():
        wd = json.loads(WATCHDOG_JSON.read_text())
        maturity_classification = wd.get("classification", "UNKNOWN")
        mature_count = wd.get("mature_count")
        for r in wd.get("rows", []):
            bars_remaining[r.get("symbol")] = r.get("bars_remaining")
        if maturity_classification == "OUTCOMES_READY":
            next_allowed_action = "RUN_OUTCOME_UPDATE_AND_DRIFT_REPORT"
        elif maturity_classification == "WATCHDOG_HARD_FAIL_BROKER_FLAG":
            next_allowed_action = "HALT_AND_AUDIT"

    snapshot = {
        "active_lineage": "relative_strength_continuation",
        "pending": pending,
        "resolved": resolved,
        "symbols": symbols,
        "latest_signal_timestamp": latest_signal_ts,
        "maturity_classification": maturity_classification,
        "mature_count": mature_count,
        "bars_remaining_per_symbol": bars_remaining,
        "broker_leakage": bool(sent_to_broker_any),
        "production_hard_block": True,
        "live_hard_block": True,
        "shadow_disabled": True,
        "broker_execution_disabled": True,
        "next_allowed_action": next_allowed_action,
        "artifacts_present": {
            "hypothesis_registry": REGISTRY.exists(),
            "active_observation_status": ACTIVE_STATUS.exists(),
            "next_action_queue": NEXT_ACTION.exists(),
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    lines = [
        "# Feature Factory State Snapshot",
        "",
        f"active_lineage: {snapshot['active_lineage']}",
        f"pending: {snapshot['pending']}",
        f"resolved: {snapshot['resolved']}",
        f"symbols: {', '.join(snapshot['symbols']) if snapshot['symbols'] else 'NONE'}",
        f"latest_signal_timestamp: {snapshot['latest_signal_timestamp']}",
        f"maturity_classification: {snapshot['maturity_classification']}",
        f"mature_count: {snapshot['mature_count']}",
        f"bars_remaining_per_symbol: {snapshot['bars_remaining_per_symbol']}",
        f"broker_leakage: {snapshot['broker_leakage']}",
        f"production_hard_block: {snapshot['production_hard_block']}",
        f"live_hard_block: {snapshot['live_hard_block']}",
        f"broker_execution_disabled: {snapshot['broker_execution_disabled']}",
        f"shadow_disabled: {snapshot['shadow_disabled']}",
        f"next_allowed_action: {snapshot['next_allowed_action']}",
        "",
        "Production: BLOCKED",
        "Live: BLOCKED",
        "Broker execution: DISABLED",
        "Shadow orders: DISABLED",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("SNAPSHOT_PASS")
    print(f"Snapshot markdown: {OUT_MD}")
    print(f"Snapshot json: {OUT_JSON}")


if __name__ == "__main__":
    main()
