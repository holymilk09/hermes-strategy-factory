from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LINEAGE_DEFINITIONS: list[dict[str, Any]] = [
    {
        "lineage": "relative_strength_continuation",
        "phase": "28A",
        "family": "momentum",
        "thesis": "Cross-sectional relative strength continuation: stocks with strong trend persistence continue to outperform",
        "fixed_rule": "ret_20d_rank >= 0.85 & ret_60d_rank >= 0.70 & close_above_ma50 & ret_5d > 0",
        "decision_file": "relative_strength_continuation_decision.md",
    },
    {
        "lineage": "regime_conditioned_capitulation_v2",
        "phase": "25C",
        "family": "capitulation",
        "thesis": "Price-volume capitulation plus SPY drawdown regime filter",
        "fixed_rule": "ret_3d_z <= -1.5 & volume_z_20 >= 1.0 & close_location >= 0.50 & spy_drawdown_60d <= -0.0146",
        "decision_file": "regime_conditioned_capitulation_v2_decision.md",
    },
    {
        "lineage": "sector_residual_mr",
        "phase": "27A",
        "family": "residual",
        "thesis": "Sector ETF residual mean reversion: extreme idiosyncratic residual vs sector ETF mean-reverts",
        "fixed_rule": "sector_residual_z <= -2.0 & sector_model_r2 >= 0.15",
        "decision_file": "sector_residual_mr_decision.md",
    },
    {
        "lineage": "price_volume_capitulation_v2",
        "phase": "24B",
        "family": "capitulation",
        "thesis": "Price-volume capitulation event: extreme 3d return + volume spike + intraday weakness",
        "fixed_rule": "ret_3d_z <= -1.5 & volume_z_20 >= 1.0 & close_location >= 0.50",
        "decision_file": "price_volume_capitulation_v2_decision.md",
    },
    {
        "lineage": "price_volume_capitulation_v1",
        "phase": "24A",
        "family": "capitulation",
        "thesis": "Factor residual shock + long-only threshold (earlier broad multi-factor approach, not proper A&L)",
        "fixed_rule": "factor_residual_z <= -2.0 (broad multi-factor OLS, not sector ETF)",
        "decision_file": "canonical_lineage_decision.md",
    },
    {
        "lineage": "canonical_spy_residual",
        "phase": "22B",
        "family": "residual",
        "thesis": "SPY-based rolling OLS residual mean reversion",
        "fixed_rule": "residual_z <= -2.0 & residual_r2 >= 0.20",
        "decision_file": "canonical_lineage_decision.md",
    },
    {
        "lineage": "factor_residual_mr",
        "phase": "24A",
        "family": "residual",
        "thesis": "Factor residual mean reversion (broad multi-factor OLS, not proper A&L sector ETF)",
        "fixed_rule": "factor_residual_z <= -2.0 & factor_residual_r2 >= 0.20",
        "decision_file": "factor_residual_mr_decision.md",
    },
]


@dataclass(frozen=True)
class HypothesisRecord:
    lineage: str
    phase: str
    family: str
    thesis: str
    fixed_rule: str
    classification: str
    decision: str
    grade: str
    status: str
    decision_source: str


def parse_value_field(text: str, key: str) -> str | None:
    """Parse 'key: value' lines from decision files."""
    pattern = rf"^{re.escape(key)}:\s*(.+?)$"
    for line in text.split("\n"):
        m = re.match(pattern, line.strip())
        if m:
            return m.group(1).strip()
    return None


def grade_from_classification(cls: str) -> str:
    """Map classification to letter grade."""
    cls_upper = cls.upper()

    if "WEAK_PASS" in cls_upper and "FORWARD" in cls_upper:
        return "B"
    if "WEAK_PASS" in cls_upper:
        return "B"
    if "PASS" in cls_upper and "HOLDOUT" in cls_upper:
        return "C+"
    if "PASS" in cls_upper and "RESEARCH" in cls_upper:
        return "C+"
    if "PASS" in cls_upper:
        return "B"
    if "INCONCLUSIVE" in cls_upper:
        return "D"
    if "FAIL" in cls_upper:
        return "F"

    return "U"


def status_from_classification(cls: str) -> str:
    """Map classification to status string."""
    cls_upper = cls.upper()

    if "WEAK_PASS" in cls_upper:
        return "Active observation"
    if "HOLDOUT" in cls_upper:
        return "Research-only"
    if "PASS" in cls_upper and "RESEARCH" in cls_upper:
        return "Research-only"
    if "PASS" in cls_upper and "FORWARD" in cls_upper:
        return "Validated"
    if "PASS" in cls_upper:
        return "Research-only"
    if "INCONCLUSIVE" in cls_upper:
        return "Archived low-power"
    if "FAIL" in cls_upper:
        return "Archived"

    return "Unknown"


def read_decision_file(path: Path) -> dict[str, Any]:
    """Read a decision file and extract classification and decision."""
    text = path.read_text(encoding="utf-8")

    cls = parse_value_field(text, "final_classification")
    decision = parse_value_field(text, "decision")

    if cls is None:
        cls = "UNKNOWN"
    if decision is None:
        decision = "No decision text found"

    return {"classification": cls, "decision": decision, "source": str(path)}


def build_hypothesis_registry(root: Path) -> list[HypothesisRecord]:
    """Build hypothesis registry from decision files on disk."""
    decision_dir = root / "reports" / "strategy_factory"
    graveyard_files = {
        p.stem for p in (root / "filter_graveyard").glob("*.md")
    }

    records: list[HypothesisRecord] = []

    for lineage_def in LINEAGE_DEFINITIONS:
        lineage = lineage_def["lineage"]
        file_name = lineage_def["decision_file"]
        decision_path = decision_dir / file_name

        if decision_path.exists():
            parsed = read_decision_file(decision_path)
            cls = parsed["classification"]
            decision = parsed["decision"]
        else:
            cls = "NO_DECISION_FILE"
            decision = f"Decision file not found: {decision_path}"

        # Check graveyard
        graveyard_name = lineage.replace("_v", "_v").rsplit("_", 1)[0] if "_v" in lineage else lineage
        in_graveyard = graveyard_name in graveyard_files

        # Adjust status for graveyard entries
        status = status_from_classification(cls)
        if in_graveyard and status != "Active observation":
            status = "Archived"

        # Special case: old Phase 12 is non-operational
        if lineage == "old_phase12_residual":
            status = "Non-operational"

        grade = grade_from_classification(cls)

        records.append(
            HypothesisRecord(
                lineage=lineage,
                phase=lineage_def["phase"],
                family=lineage_def["family"],
                thesis=lineage_def["thesis"],
                fixed_rule=lineage_def["fixed_rule"],
                classification=cls,
                decision=decision,
                grade=grade,
                status=status,
                decision_source=str(decision_path),
            )
        )

    return records


def hypothesis_registry_to_dict(records: list[HypothesisRecord]) -> list[dict[str, Any]]:
    return [
        {
            "lineage": r.lineage,
            "phase": r.phase,
            "family": r.family,
            "classification": r.classification,
            "grade": r.grade,
            "status": r.status,
            "decision": r.decision,
        }
        for r in records
    ]
