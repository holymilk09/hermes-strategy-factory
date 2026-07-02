#!/usr/bin/env python3
"""Run Edge Audit — economic sanity + drift attribution + filter quality audit.

Produces:
  - reports/edge_audit/YYYY-MM-DD_edge_audit.md
  - reports/edge_audit/YYYY-MM-DD_edge_audit.json

Hard constraints:
  - Never modifies strategy behavior, thresholds, scoring, or ledgers.
  - Never modifies observation, outcome, or ghost ledgers.
  - Creates additive audit outputs only.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("/opt/data")
REPORT_DIR = ROOT / "reports" / "edge_audit"


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def _load_observation_ledgers() -> list[dict[str, str]]:
    """Load all observation ledgers."""
    from src.research.meta.observation_status import OBSERVATION_SYSTEMS

    all_obs: list[dict[str, str]] = []
    for system in OBSERVATION_SYSTEMS:
        path = ROOT / system["observation_ledger"]
        rows = _load_csv(path)
        for r in rows:
            r["_source_system"] = system["name"]
            all_obs.append(r)
    return all_obs


def _load_outcome_ledgers() -> list[dict[str, str]]:
    """Load all outcome ledgers (same as observation ledgers but resolved)."""
    from src.research.meta.observation_status import OBSERVATION_SYSTEMS

    all_out: list[dict[str, str]] = []
    for system in OBSERVATION_SYSTEMS:
        path = ROOT / system["outcome_ledger"]
        rows = _load_csv(path)
        for r in rows:
            r["_source_system"] = system["name"]
            all_out.append(r)
    return all_out


def _load_ghost_ledger() -> list[dict[str, str]]:
    from src.reporting.ghost_ledger import load_ghost_ledger, GHOST_LEDGER_PATH

    return load_ghost_ledger(ROOT / GHOST_LEDGER_PATH)


def _load_sector_etf_map() -> dict[str, str]:
    """Load sector ETF mapping. For now uses default from drift_attribution."""
    from src.reporting.drift_attribution import DEFAULT_SECTOR_ETFS

    return dict(DEFAULT_SECTOR_ETFS)


# ─── Audit runner ─────────────────────────────────────────────


def run_edge_audit() -> dict[str, Any]:
    """Run the full edge audit cycle.

    Returns a dict with all audit results.
    """
    from src.reporting.economic_sanity import compute_batch_sanity, report_to_dict as sanity_to_dict
    from src.reporting.drift_attribution import (
        compute_batch_drift,
        report_to_dict as drift_to_dict,
    )
    from src.reporting.filter_quality_audit import (
        compute_filter_quality,
        quality_to_dict,
    )

    # Load data
    observations = _load_observation_ledgers()
    outcomes = _load_outcome_ledgers()
    ghost_records = _load_ghost_ledger()
    sector_map = _load_sector_etf_map()

    # Sector ETF freshness (Phase 7C) — required for full Independent Strength
    from src.reporting.drift_attribution import validate_sector_freshness
    sector_freshness = validate_sector_freshness(ROOT)

    # Ghost status counts (Phase 7C)
    ghost_status_counts = {"PENDING": 0, "MATURE": 0, "INSUFFICIENT_DATA": 0}
    for g in ghost_records:
        s = g.get("data_status", "").upper()
        if s in ghost_status_counts:
            ghost_status_counts[s] += 1
        else:
            ghost_status_counts[s or "UNKNOWN"] = ghost_status_counts.get(s or "UNKNOWN", 0) + 1

    # 1. Economic sanity
    sanity_report = compute_batch_sanity(observations, ROOT)
    sanity_dict = sanity_to_dict(sanity_report)

    # 2. Drift attribution
    drift_report = compute_batch_drift(observations, ROOT, sector_etf_map=sector_map)
    drift_dict = drift_to_dict(drift_report)

    # 3. Filter quality audit
    # Group by strategy
    strategies = set()
    for obs in observations:
        s = obs.get("strategy", obs.get("_source_system", "unknown"))
        strategies.add(s)

    # Merge outcome_return from outcome ledger into observation rows so
    # filter quality audit can compute accepted_vs_rejected_lift.
    # The observation ledger stores outcome_return as empty; the outcome
    # ledger has the resolved values. (Phase 7C audit-repair.)
    outcome_by_id = {o.get("observation_id", ""): o for o in outcomes}

    filter_quality_results: dict[str, Any] = {}
    for strat in sorted(strategies):
        strat_obs = [o for o in observations if o.get("strategy", o.get("_source_system", "")) == strat]
        # Enrich with outcome_return from the outcome ledger
        for o in strat_obs:
            oid = o.get("observation_id", "")
            if oid in outcome_by_id:
                ret = outcome_by_id[oid].get("outcome_return", "")
                if ret and not o.get("outcome_return"):
                    o["outcome_return"] = ret
        # Ghosts are system-wide; filter quality looks at accepted vs rejected across all
        # For strategy-specific audit, filter ghosts by strategy
        strat_ghosts = [g for g in ghost_records if g.get("strategy_id", "") == strat]
        quality = compute_filter_quality(strat, strat_obs, strat_ghosts, total_candidates=len(strat_obs) + len(strat_ghosts))
        filter_quality_results[strat] = quality_to_dict(quality)

    # Build aggregate result
    result: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_date": _today(),
        "summary": {
            "total_observations": len(observations),
            "total_outcomes": len(outcomes),
            "total_ghost_records": len(ghost_records),
            "ghost_status_counts": ghost_status_counts,
            "strategies_audited": len(strategies),
        },
        "sector_etf_freshness": sector_freshness,
        "economic_sanity": sanity_dict,
        "drift_attribution": drift_dict,
        "filter_quality": filter_quality_results,
        "warnings": _collect_warnings(sanity_dict, drift_dict, filter_quality_results,
                                      sector_freshness=sector_freshness),
    }

    return result


def _collect_warnings(
    sanity: dict[str, Any],
    drift: dict[str, Any],
    filter_quality: dict[str, Any],
    sector_freshness: dict[str, Any] | None = None,
) -> list[str]:
    """Collect warning flags across all audit modules."""
    warnings: list[str] = []

    # Sector freshness warnings (Phase 7C)
    if sector_freshness:
        for etf, info in sector_freshness.items():
            if not info.get("fresh"):
                warnings.append(
                    f"Sector ETF {etf} data missing/stale "
                    f"(latest={info.get('latest_date')}) — "
                    f"full Independent Strength labels are blocked for symbols mapped to {etf}"
                )

    # Sanity warnings
    if sanity.get("cost_fragile_count", 0) > 0:
        warnings.append(
            f"{sanity['cost_fragile_count']} observations are Cost Fragile "
            f"(cost-adjusted return below minimum)"
        )
    if sanity.get("insufficient_data_count", 0) > 0:
        warnings.append(
            f"{sanity['insufficient_data_count']} observations have insufficient data for assessment"
        )
    if sanity.get("compounding_artifact_count", 0) > 0:
        warnings.append(
            f"{sanity['compounding_artifact_count']} symbols have compounding artifact warnings"
        )
    if sanity.get("concurrent_exposure_count", 0) > 0:
        warnings.append("Concurrent exposure detected — many signals within a short time window")

    # Drift warnings
    drift_counts = drift.get("label_counts", {})
    mhs = drift_counts.get("Market Helped Setup", 0)
    sd = drift_counts.get("Sector Drift", 0)
    bd = drift_counts.get("Beta Drift", 0)
    td = drift_counts.get("Ticker Drift", 0)
    fe = drift_counts.get("Failed Edge", 0)

    if mhs > 0:
        warnings.append(f"{mhs} observations are Market Helped Setup (return explained by market rise)")
    if sd > 0:
        warnings.append(f"{sd} observations show Sector Drift (sector explains returns)")
    if bd > 0:
        warnings.append(f"{bd} observations show Beta Drift")
    if td > 0:
        warnings.append(f"{td} observations show Ticker Drift")
    if fe > 0:
        warnings.append(f"{fe} observations have Failed Edge (negative/flat returns)")

    # Filter quality warnings
    for strat, quality in filter_quality.items():
        q_warnings = quality.get("warnings", [])
        for w in q_warnings:
            warnings.append(f"[{strat}] {w}")

    return warnings


def _render_markdown(result: dict[str, Any]) -> str:
    """Render audit result as markdown report."""
    lines: list[str] = []
    lines.append(f"# Edge Audit Report — {result['report_date']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Observations audited:** {result['summary']['total_observations']}")
    lines.append(f"- **Ghost records:** {result['summary']['total_ghost_records']}")
    lines.append(f"- **Strategies audited:** {result['summary']['strategies_audited']}")
    lines.append("")

    # Economic sanity
    sanity = result["economic_sanity"]
    lines.append("## Economic Sanity")
    lines.append("")
    lines.append(f"- **Total assessed:** {sanity['assessed_observations']}")
    lines.append(f"- **Pass:** {sanity['pass_count']}")
    lines.append(f"- **Cost Fragile:** {sanity['cost_fragile_count']}")
    lines.append(f"- **Insufficient Data:** {sanity['insufficient_data_count']}")
    lines.append(f"- **Compounding artifacts:** {sanity['compounding_artifact_count']} symbols")
    lines.append(f"- **Concurrent exposure:** {'Yes' if sanity['concurrent_exposure_count'] > 0 else 'No'}")
    if sanity.get("mean_cost_adjusted_return") is not None:
        lines.append(f"- **Mean cost-adjusted return:** {sanity['mean_cost_adjusted_return']:.2f}%")
    if sanity.get("mean_delay_adjusted_return") is not None:
        lines.append(f"- **Mean delay-adjusted return:** {sanity['mean_delay_adjusted_return']:.2f}%")
    lines.append("")

    # Drift attribution
    drift = result["drift_attribution"]
    lines.append("## Drift Attribution")
    lines.append("")
    lines.append(f"- **Labeled observations:** {drift['labeled_observations']}")
    lines.append("")
    lines.append("### Label Counts")
    lines.append("")
    label_counts = drift.get("label_counts", {})
    for label in ["Independent Strength",
                    "Independent Strength vs SPY/QQQ; sector verification pending",
                    "Market Helped Setup", "Sector Drift",
                    "Beta Drift", "Ticker Drift", "No Confirmed Edge",
                    "Failed Edge", "Compounding Risk", "Cost Fragile",
                    "Insufficient Data"]:
        count = label_counts.get(label, 0)
        lines.append(f"- **{label}:** {count}")
    lines.append("")

    # Sector ETF freshness (Phase 7C)
    sector_freshness = result.get("sector_etf_freshness", {})
    if sector_freshness:
        lines.append("### Sector ETF Freshness")
        lines.append("")
        for etf, info in sector_freshness.items():
            status = "FRESH" if info.get("fresh") else "STALE/MISSING"
            lines.append(f"- **{etf}:** {status} (latest={info.get('latest_date')})")
        lines.append("")

    # Ghost status counts (Phase 7C)
    gsc = result["summary"].get("ghost_status_counts", {})
    if gsc:
        lines.append("### Ghost Ledger Status")
        lines.append("")
        for k in ["PENDING", "MATURE", "INSUFFICIENT_DATA"]:
            lines.append(f"- **{k}:** {gsc.get(k, 0)}")
        lines.append("")

    # Filter quality
    lines.append("## Filter Quality Audit")
    lines.append("")
    for strat, quality in result.get("filter_quality", {}).items():
        lines.append(f"### Strategy: {strat}")
        lines.append("")
        if quality.get("pass_rate") is not None:
            lines.append(f"- **Pass rate:** {quality['pass_rate']:.2%}")
        if quality.get("accepted_vs_rejected_lift") is not None:
            lines.append(f"- **Accepted vs rejected lift:** {quality['accepted_vs_rejected_lift']:.2f}pp")
        if quality.get("accepted_mean_return") is not None:
            lines.append(f"- **Accepted mean return:** {quality['accepted_mean_return']:.2f}%")
        if quality.get("rejected_mean_return") is not None:
            lines.append(f"- **Rejected mean return:** {quality['rejected_mean_return']:.2f}%")
        if quality.get("ghost_baseline_return") is not None:
            lines.append(f"- **Ghost baseline return:** {quality['ghost_baseline_return']:.2f}%")
        lines.append(f"- **Filter lift:** {quality.get('filter_lift_assessment', 'N/A')}")
        lines.append(f"- **Score monotonicity:** {quality.get('score_bucket_monotonicity', 'N/A')}")
        if quality.get("warnings"):
            lines.append(f"- **Warnings:** {len(quality['warnings'])}")
            for w in quality["warnings"]:
                lines.append(f"  - {w}")
        lines.append("")

    # Warnings
    if result.get("warnings"):
        lines.append("## Warnings")
        lines.append("")
        for w in result["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## Safety Confirmation")
    lines.append("")
    lines.append("- **Strategy behavior changed:** NO")
    lines.append("- **Thresholds changed:** NO")
    lines.append("- **Scoring changed:** NO")
    lines.append("- **Observation selection changed:** NO")
    lines.append("- **Ledgers mutated:** NO")
    lines.append("- **Additive audit only:** YES")

    return "\n".join(lines)


def main() -> int:
    """Run the edge audit and write reports."""
    report_dir = REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)

    result = run_edge_audit()

    date_str = _today()

    # Write JSON
    json_path = report_dir / f"{date_str}_edge_audit.json"
    with json_path.open("w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Written: {json_path}")

    # Write MD
    md_path = report_dir / f"{date_str}_edge_audit.md"
    md_content = _render_markdown(result)
    md_path.write_text(md_content)
    print(f"Written: {md_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())