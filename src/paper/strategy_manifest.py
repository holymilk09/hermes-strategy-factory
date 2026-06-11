from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ResidualStrategyManifest:
    strategy_name: str = "residual_reversion"
    validation_classification: str = "TRUE_WALK_FORWARD_PASS"
    mode: str = "PAPER_SHADOW_ONLY"

    residual_z_threshold: float = -2.0
    residual_r2_threshold: float = 0.20

    direction: str = "long_only"
    timeframe: str = "1D"

    candidate_ledger_path: str = "data/research/candidate_artifacts/residual_candidate_feature_ledger.csv"
    rule_description: str = "residual_z <= -2.0 AND residual_r2 >= 0.20"

    selected_mean: float = 0.0175219969726388
    selected_hit_rate: float = 0.5663430420711975
    rejected_mean: float = 0.0037
    selected_vs_rejected_spread: float = 0.0138
    random_percentile: float = 0.97

    production_enabled: bool = False
    live_enabled: bool = False
    broker_execution_enabled: bool = False

    code_version: str = "phase19"

    @property
    def manifest_hash(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True).encode("utf-8")
        return sha256(payload).hexdigest()[:16]


def write_manifest(path: Path, manifest: ResidualStrategyManifest) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = asdict(manifest)
    payload["manifest_hash"] = manifest.manifest_hash

    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return payload


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)

    return json.loads(path.read_text(encoding="utf-8"))


def assert_manifest_paper_only(manifest: dict[str, Any]) -> None:
    if manifest.get("mode") != "PAPER_SHADOW_ONLY":
        raise ValueError("Manifest mode must be PAPER_SHADOW_ONLY")

    forbidden_true = [
        "production_enabled",
        "live_enabled",
        "broker_execution_enabled",
    ]

    for key in forbidden_true:
        if bool(manifest.get(key)) is True:
            raise ValueError(f"Manifest violates paper-only rule: {key}=True")
