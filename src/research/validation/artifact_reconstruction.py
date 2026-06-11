from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class ArtifactRole(str, Enum):
    TRADE_LEDGER = "TRADE_LEDGER"
    CANDIDATE_FEATURE_LEDGER = "CANDIDATE_FEATURE_LEDGER"
    SELECTION_CONFIG = "SELECTION_CONFIG"
    RAW_SIGNAL_CACHE = "RAW_SIGNAL_CACHE"
    UNKNOWN = "UNKNOWN"


class ReconstructionClass(str, Enum):
    TRUE_WALK_FORWARD_READY = "TRUE_WALK_FORWARD_READY"
    PARTIAL_RECONSTRUCTION = "PARTIAL_RECONSTRUCTION"
    LEDGER_ONLY = "LEDGER_ONLY"
    INSUFFICIENT_ARTIFACTS = "INSUFFICIENT_ARTIFACTS"


@dataclass(frozen=True)
class ArtifactRecord:
    path: str
    exists: bool
    role: str
    suffix: str
    size_bytes: int | None
    sha256_16: str | None
    columns: list[str] | None
    rows: int | None
    notes: str


CANDIDATE_PATTERNS = [
    "reports/strategy_factory/*.csv",
    "reports/strategy_factory/*.json",
    "reports/strategy_factory/*.yaml",
    "reports/strategy_factory/*.yml",
    "data/research/*.csv",
    "data/research/*.json",
    "data/research/*.npz",
    "data/cache/*.npz",
    "data/cache/*.csv",
    "config/*.yaml",
    "config/*.yml",
    "config/*.json",
    "scripts/*residual*.py",
    "src/**/*residual*.py",
    "src/**/*strategy*.py",
]


TRADE_LEDGER_HINTS = {
    "symbol",
    "entry_time",
    "timestamp",
    "date",
    "datetime",
    "return",
    "realized_return",
    "ret",
    "pnl_pct",
    "forward_return",
}


FEATURE_LEDGER_HINTS = {
    "symbol",
    "timestamp",
    "entry_time",
    "score",
    "signal",
    "rank",
    "residual",
    "zscore",
    "z_score",
    "feature",
    "forward_return",
    "realized_return",
}


SELECTION_CONFIG_HINTS = {
    "threshold",
    "lookback",
    "rank",
    "top_n",
    "min_score",
    "max_candidates",
    "strategy",
    "residual",
    "mean_reversion",
    "structural_mr",
}


def file_sha256_16(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def discover_artifacts(root: Path) -> list[Path]:
    paths: list[Path] = []

    for pattern in CANDIDATE_PATTERNS:
        paths.extend(root.glob(pattern))

    unique = sorted(set(p for p in paths if p.is_file()))
    return unique


def inspect_csv(path: Path) -> tuple[list[str] | None, int | None, str]:
    try:
        df = pd.read_csv(path, nrows=2000)
        return list(df.columns), int(len(df)), "csv_read_ok"
    except Exception as exc:
        return None, None, f"csv_read_failed: {type(exc).__name__}: {exc}"


def inspect_json_or_yaml_text(path: Path) -> tuple[list[str] | None, int | None, str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        keys = []
        lowered = text.lower()
        for hint in sorted(SELECTION_CONFIG_HINTS):
            if hint.lower() in lowered:
                keys.append(hint)
        return keys, None, "text_scan_ok"
    except Exception as exc:
        return None, None, f"text_scan_failed: {type(exc).__name__}: {exc}"


def inspect_npz(path: Path) -> tuple[list[str] | None, int | None, str]:
    try:
        data = np.load(path, allow_pickle=False)
        keys = list(data.files)
        rows = None
        for key in keys:
            arr = data[key]
            if hasattr(arr, "shape") and len(arr.shape) >= 1:
                rows = int(arr.shape[0])
                break
        return keys, rows, "npz_read_ok"
    except Exception as exc:
        return None, None, f"npz_read_failed: {type(exc).__name__}: {exc}"


def classify_role(path: Path, columns: list[str] | None, notes: str) -> str:
    name = path.name.lower()
    text = " ".join(columns or []).lower()

    if "trade_ledger" in name or "trades" in name:
        return ArtifactRole.TRADE_LEDGER.value

    if "selection" in name or "config" in name or path.suffix.lower() in {".yaml", ".yml", ".json"}:
        if any(h in text or h in name for h in SELECTION_CONFIG_HINTS):
            return ArtifactRole.SELECTION_CONFIG.value

    if "candidate" in name or "feature" in name or "signal" in name:
        if columns and {"symbol"}.issubset(set(c.lower() for c in columns)):
            return ArtifactRole.CANDIDATE_FEATURE_LEDGER.value

    if path.suffix.lower() == ".npz":
        if "residual" in name or "candidate" in name or "signal" in name:
            return ArtifactRole.RAW_SIGNAL_CACHE.value

    if columns:
        colset = set(c.lower() for c in columns)
        has_trade_time = bool(colset & {"entry_time", "timestamp", "date", "datetime"})
        has_return = bool(colset & {"return", "realized_return", "ret", "pnl_pct", "forward_return"})
        has_symbol = "symbol" in colset

        if has_symbol and has_trade_time and has_return:
            if colset & {"score", "signal", "rank", "residual", "zscore", "z_score"}:
                return ArtifactRole.CANDIDATE_FEATURE_LEDGER.value
            return ArtifactRole.TRADE_LEDGER.value

    return ArtifactRole.UNKNOWN.value


def inspect_artifact(path: Path) -> ArtifactRecord:
    suffix = path.suffix.lower()
    columns: list[str] | None = None
    rows: int | None = None
    notes = "not_inspected"

    if suffix == ".csv":
        columns, rows, notes = inspect_csv(path)
    elif suffix in {".json", ".yaml", ".yml", ".py", ".md"}:
        columns, rows, notes = inspect_json_or_yaml_text(path)
    elif suffix == ".npz":
        columns, rows, notes = inspect_npz(path)

    role = classify_role(path, columns, notes)

    return ArtifactRecord(
        path=str(path),
        exists=path.exists(),
        role=role,
        suffix=suffix,
        size_bytes=path.stat().st_size if path.exists() else None,
        sha256_16=file_sha256_16(path) if path.exists() else None,
        columns=columns,
        rows=rows,
        notes=notes,
    )


def build_artifact_manifest(root: Path) -> dict[str, Any]:
    paths = discover_artifacts(root)
    records = [inspect_artifact(p) for p in paths]

    role_counts: dict[str, int] = {}
    for r in records:
        role_counts[r.role] = role_counts.get(r.role, 0) + 1

    has_trade_ledger = role_counts.get(ArtifactRole.TRADE_LEDGER.value, 0) > 0
    has_candidate_feature_ledger = role_counts.get(ArtifactRole.CANDIDATE_FEATURE_LEDGER.value, 0) > 0
    has_selection_config = role_counts.get(ArtifactRole.SELECTION_CONFIG.value, 0) > 0
    has_raw_signal_cache = role_counts.get(ArtifactRole.RAW_SIGNAL_CACHE.value, 0) > 0

    if has_candidate_feature_ledger and has_selection_config:
        reconstruction_class = ReconstructionClass.TRUE_WALK_FORWARD_READY.value
    elif has_raw_signal_cache and has_trade_ledger:
        reconstruction_class = ReconstructionClass.PARTIAL_RECONSTRUCTION.value
    elif has_trade_ledger:
        reconstruction_class = ReconstructionClass.LEDGER_ONLY.value
    else:
        reconstruction_class = ReconstructionClass.INSUFFICIENT_ARTIFACTS.value

    return {
        "reconstruction_class": reconstruction_class,
        "role_counts": role_counts,
        "has_trade_ledger": has_trade_ledger,
        "has_candidate_feature_ledger": has_candidate_feature_ledger,
        "has_selection_config": has_selection_config,
        "has_raw_signal_cache": has_raw_signal_cache,
        "records": [asdict(r) for r in records],
    }


def select_best_record(manifest: dict[str, Any], role: ArtifactRole) -> dict[str, Any] | None:
    records = [r for r in manifest["records"] if r["role"] == role.value]
    if not records:
        return None

    records = sorted(
        records,
        key=lambda r: (
            r["rows"] or 0,
            r["size_bytes"] or 0,
        ),
        reverse=True,
    )
    return records[0]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str), encoding="utf-8")


def normalize_existing_feature_ledger(source_path: Path, output_path: Path) -> dict[str, Any]:
    df = pd.read_csv(source_path)

    lower_map = {c: c.lower() for c in df.columns}
    df = df.rename(columns=lower_map)

    if "timestamp" not in df.columns:
        for c in ["entry_time", "date", "datetime"]:
            if c in df.columns:
                df["timestamp"] = pd.to_datetime(df[c], utc=True, errors="coerce")
                break
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    if "symbol" not in df.columns:
        raise ValueError("Candidate feature ledger missing symbol")

    if "timestamp" not in df.columns:
        raise ValueError("Candidate feature ledger missing timestamp")

    score_cols = [c for c in df.columns if c in {"score", "signal", "rank", "residual", "zscore", "z_score"}]

    if not score_cols:
        raise ValueError("Candidate feature ledger has no score/signal/rank/residual column")

    df = df.dropna(subset=["timestamp", "symbol"])
    df = df.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return {
        "source_path": str(source_path),
        "output_path": str(output_path),
        "rows": int(len(df)),
        "columns": list(df.columns),
        "score_columns": score_cols,
    }


def build_feasibility_report(manifest: dict[str, Any]) -> str:
    lines = []
    lines.append("# Residual True Walk-Forward Feasibility")
    lines.append("")
    lines.append(f"reconstruction_class: {manifest['reconstruction_class']}")
    lines.append("")
    lines.append("## Role Counts")
    lines.append("")
    for role, count in sorted(manifest["role_counts"].items()):
        lines.append(f"- {role}: {count}")

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")

    cls = manifest["reconstruction_class"]

    if cls == ReconstructionClass.TRUE_WALK_FORWARD_READY.value:
        lines.append("TRUE_WALK_FORWARD may be possible. Candidate feature ledger and selection config both exist.")
    elif cls == ReconstructionClass.PARTIAL_RECONSTRUCTION.value:
        lines.append("Partial reconstruction possible. Raw signal cache exists, but candidate feature ledger or explicit selection config may be missing.")
    elif cls == ReconstructionClass.LEDGER_ONLY.value:
        lines.append("Only trade ledger exists. True walk-forward cannot be proven from current artifacts.")
    else:
        lines.append("Insufficient artifacts. Cannot validate residual selection.")

    lines.append("")
    lines.append("## Strict Rule")
    lines.append("")
    lines.append("Do not upgrade Phase 17 validation level unless candidate features and selection logic are genuinely reconstructable.")

    return "\n".join(lines)
