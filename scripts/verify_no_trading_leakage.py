from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [ROOT / "data", ROOT / "reports", ROOT / "scripts", ROOT / "src"]

# Active ledgers/reports first (strictest check surface)
PRIORITY_CSVS = [
    ROOT / "data" / "paper_observation" / "relative_strength_continuation_observation_ledger.csv",
    ROOT / "data" / "paper_observation" / "relative_strength_continuation_outcome_ledger.csv",
    ROOT / "reports" / "strategy_factory" / "hypothesis_registry.csv",
]

TRUE_BAD_COLUMNS = {
    "sent_to_broker": True,
    "production_enabled": True,
    "live_enabled": True,
    "broker_execution_enabled": True,
}


def iter_csv_paths() -> Iterable[Path]:
    seen: set[Path] = set()

    for p in PRIORITY_CSVS:
        if p.exists() and p not in seen:
            seen.add(p)
            yield p

    # Secondary scan: only operational CSV directories, not broad historical caches
    secondary_dirs = [
        ROOT / "data" / "paper_observation",
        ROOT / "reports" / "strategy_factory",
        ROOT / "data" / "paper_shadow",
    ]

    max_bytes = 20 * 1024 * 1024
    for base in secondary_dirs:
        if not base.exists():
            continue
        for p in base.rglob("*.csv"):
            if p in seen:
                continue
            try:
                if p.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            seen.add(p)
            yield p


def check_csv(path: Path) -> list[str]:
    issues: list[str] = []

    # Fast header probe first
    try:
        header = pd.read_csv(path, nrows=0)
    except Exception:
        return issues

    cols = [str(c).strip().lower() for c in header.columns]
    target_cols = [c for c in list(TRUE_BAD_COLUMNS.keys()) + ["broker_order_id"] if c in cols]
    if not target_cols:
        return issues

    true_tokens = {"true", "1", "yes", "y", "on"}

    # Chunked scan to avoid loading huge files
    try:
        for chunk in pd.read_csv(path, usecols=target_cols, chunksize=50000):
            chunk.columns = [str(c).strip().lower() for c in chunk.columns]

            for col in TRUE_BAD_COLUMNS:
                if col in chunk.columns:
                    normalized = chunk[col].fillna("").astype(str).str.strip().str.lower()
                    if bool(normalized.isin(true_tokens).any()):
                        issues.append(f"{path}: {col}=true detected")

            if "broker_order_id" in chunk.columns:
                s = chunk["broker_order_id"].fillna("").astype(str).str.strip().str.lower()
                populated = (~s.isin(["", "nan", "none"]))
                if bool(populated.any()):
                    issues.append(f"{path}: broker_order_id populated")

            if issues:
                return issues
    except Exception:
        return issues

    return issues


def main() -> None:
    issues: list[str] = []
    for p in iter_csv_paths():
        issues.extend(check_csv(p))

    if issues:
        print("NO_TRADING_LEAKAGE_FAIL")
        for i in issues:
            print(i)
        raise SystemExit(1)

    print("NO_TRADING_LEAKAGE_PASS")


if __name__ == "__main__":
    main()
