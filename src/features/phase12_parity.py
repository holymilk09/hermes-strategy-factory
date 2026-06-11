from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PARITY_KEYS = [
    "residual_z",
    "residual_r2",
    "rsi_2",
    "regime_score",
    "forward_return_5d",
    "forward_return_10d",
    "forward_return_20d",
]


def safe_corr(a: np.ndarray, b: np.ndarray) -> float | None:
    mask = np.isfinite(a) & np.isfinite(b)

    if mask.sum() < 30:
        return None

    if np.nanstd(a[mask]) == 0 or np.nanstd(b[mask]) == 0:
        return None

    return float(np.corrcoef(a[mask], b[mask])[0, 1])


def compare_npz_features(
    old_path: Path,
    new_path: Path,
    keys: list[str] | None = None,
) -> dict[str, Any]:
    keys = keys or PARITY_KEYS

    old = np.load(old_path, allow_pickle=False)
    new = np.load(new_path, allow_pickle=False)

    rows = []

    for key in keys:
        if key not in old.files or key not in new.files:
            rows.append(
                {
                    "key": key,
                    "status": "MISSING",
                    "old_rows": int(old[key].shape[0]) if key in old.files else None,
                    "new_rows": int(new[key].shape[0]) if key in new.files else None,
                    "corr": None,
                    "mae": None,
                    "overlap_rows": 0,
                }
            )
            continue

        old_arr = old[key].reshape(-1)
        new_arr = new[key].reshape(-1)

        n = min(len(old_arr), len(new_arr))
        old_slice = old_arr[:n].astype(float)
        new_slice = new_arr[:n].astype(float)

        mask = np.isfinite(old_slice) & np.isfinite(new_slice)

        corr = safe_corr(old_slice, new_slice)

        if mask.sum() > 0:
            mae = float(np.mean(np.abs(old_slice[mask] - new_slice[mask])))
        else:
            mae = None

        rows.append(
            {
                "key": key,
                "status": "OK",
                "old_rows": int(len(old_arr)),
                "new_rows": int(len(new_arr)),
                "corr": corr,
                "mae": mae,
                "overlap_rows": int(mask.sum()),
            }
        )

    return {
        "old_path": str(old_path),
        "new_path": str(new_path),
        "rows": rows,
    }


def classify_parity(comparison: dict[str, Any]) -> str:
    rows = comparison["rows"]

    required = [r for r in rows if r["key"] in {"residual_z", "residual_r2", "rsi_2"}]

    if any(r["status"] != "OK" for r in required):
        return "PARITY_FAIL_MISSING_KEYS"

    residual_z = next(r for r in rows if r["key"] == "residual_z")
    residual_r2 = next(r for r in rows if r["key"] == "residual_r2")
    rsi_2 = next(r for r in rows if r["key"] == "rsi_2")

    if residual_z["corr"] is None or residual_z["corr"] < 0.70:
        return "PARITY_FAIL_RESIDUAL_Z"

    if residual_r2["corr"] is None or residual_r2["corr"] < 0.50:
        return "PARITY_FAIL_RESIDUAL_R2"

    if rsi_2["corr"] is None or rsi_2["corr"] < 0.90:
        return "PARITY_FAIL_RSI"

    return "PARITY_DIRECTIONAL_PASS"


def aggregate_parity_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    classifications = {}

    for result in results:
        cls = classify_parity(result)
        classifications[cls] = classifications.get(cls, 0) + 1

    total = len(results)
    directional_pass = classifications.get("PARITY_DIRECTIONAL_PASS", 0)

    pass_rate = directional_pass / total if total else 0.0

    if total == 0:
        final = "PARITY_NO_RESULTS"
    elif pass_rate >= 0.80:
        final = "PARITY_PASS"
    elif pass_rate >= 0.50:
        final = "PARITY_WEAK_PASS"
    else:
        final = "PARITY_FAIL"

    return {
        "total_symbols": total,
        "directional_pass": directional_pass,
        "pass_rate": pass_rate,
        "classifications": classifications,
        "final": final,
    }
