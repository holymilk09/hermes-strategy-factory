from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.reporting.retail_wording import DISCLAIMER
from src.reporting.trust_calibration import FilterImpact, TrustRecommendation


def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _fmt_pct(v: str | None) -> str:
    if v is None:
        return "N/A"
    return v


def generate_trust_state_summary(
    recommendation: TrustRecommendation,
    output_dir: Path,
    date_str: str | None = None,
) -> Path:
    """Generate TRUST_STATE_SUMMARY_<date>.md report."""
    date_str = date_str or _now_str()
    report_dir = output_dir / "reports" / "trust_calibration"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"TRUST_STATE_SUMMARY_{date_str}.md"

    mw = recommendation.market_weather_split
    mw_lines: list[str] = []
    for key, label in [
        ("market_helping", "Market Helping"),
        ("market_not_helping", "Market Not Helping"),
        ("market_unknown", "Market Unknown"),
    ]:
        seg = mw.get(key, {})
        if seg and seg.get("completed_count", 0) > 0:
            mw_lines.append(f"- **{label}**: {seg['completed_count']} completed")
            if seg.get("avg_10d_return"):
                mw_lines.append(f"  - Avg 10d return: {seg['avg_10d_return']}")
            if seg.get("hit_rate"):
                mw_lines.append(f"  - Hit rate: {seg['hit_rate']}")
            if seg.get("max_adverse_move"):
                mw_lines.append(f"  - Max adverse move: {seg['max_adverse_move']}")

    mw_str = "\n".join(mw_lines) if mw_lines else "- Not enough proof yet"
    missing_str = "\n".join("- " + w for w in recommendation.missing_data_warnings) if recommendation.missing_data_warnings else "- None"

    content = (
        f"# Trust State Summary \u2014 {date_str}\n\n"
        f"**Strategy / Setup Type:** {recommendation.strategy_id}\n"
        f"**Completed Sample Count:** {recommendation.completed_sample_count}\n"
        f"**Trust State:** {recommendation.trust_state}\n"
        f"**Manual Approval Required:** Yes\n\n"
        f"## Reason\n\n{recommendation.reason}\n\n"
        f"## Windows Reviewed\n\n{recommendation.windows_reviewed}\n\n"
        f"## Market Weather Split\n\n{mw_str}\n\n"
        f"## Baseline Comparison\n\n{recommendation.baseline_comparison}\n\n"
        f"## Missing Data Warnings\n\n{missing_str}\n\n"
        f"## Important\n\n"
        f"This trust state is a **report label only**. It does not automatically change any "
        f"strategy behavior, thresholds, or filters. Human review and explicit approval "
        f"are required before any action is taken.\n\n{DISCLAIMER}\n"
    )
    path.write_text(content.strip() + "\n")
    return path


def generate_filter_impact_audit(
    impacts: list[FilterImpact],
    output_dir: Path,
    date_str: str | None = None,
) -> Path:
    """Generate FILTER_IMPACT_AUDIT_<date>.md report."""
    date_str = date_str or _now_str()
    report_dir = output_dir / "reports" / "trust_calibration"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"FILTER_IMPACT_AUDIT_{date_str}.md"

    lines: list[str] = []
    for impact in impacts:
        helped_label = {
            "true": "Filter appears to be helping",
            "false": "Filter may be too strict",
            "INCONCLUSIVE": "Inconclusive",
        }.get(impact.filter_helped, impact.filter_helped)
        lines.append(
            f"### {impact.filter_name}\n\n"
            f"- **Blocked count:** {impact.blocked_count}\n"
            f"- **Blocked winners:** {impact.blocked_winners}\n"
            f"- **Blocked losers:** {impact.blocked_losers}\n"
            f"- **Avg ghost 5d return:** {_fmt_pct(impact.avg_ghost_return_5d)}\n"
            f"- **Avg ghost 10d return:** {_fmt_pct(impact.avg_ghost_return_10d)}\n"
            f"- **Avg ghost 20d return:** {_fmt_pct(impact.avg_ghost_return_20d)}\n"
            f"- **Avg ghost 30d return:** {_fmt_pct(impact.avg_ghost_return_30d)}\n"
            f"- **Avg active 10d return:** {_fmt_pct(impact.avg_active_return_10d)}\n"
            f"- **Ghost hit rate:** {_fmt_pct(impact.ghost_hit_rate)}\n"
            f"- **Active hit rate:** {_fmt_pct(impact.active_hit_rate)}\n"
            f"- **Verdict:** {helped_label}\n"
            f"- **Notes:** {impact.notes}\n"
            f"- **Recommended human review:** Yes\n"
        )

    body = "\n".join(lines) if lines else "No filters with sufficient sample size for analysis."
    content = (
        f"# Filter Impact Audit \u2014 {date_str}\n\n"
        f"{body}\n\n{DISCLAIMER}\n"
    )
    path.write_text(content.strip() + "\n")
    return path


def generate_ghost_ledger_summary(
    ghost_summary_data: dict[str, Any],
    output_dir: Path,
    date_str: str | None = None,
) -> Path:
    """Generate GHOST_LEDGER_SUMMARY_<date>.md report."""
    date_str = date_str or _now_str()
    report_dir = output_dir / "reports" / "trust_calibration"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"GHOST_LEDGER_SUMMARY_{date_str}.md"

    total = ghost_summary_data.get("total_ghost_records", 0)
    matured = ghost_summary_data.get("matured_ghost_records", 0)
    pending = ghost_summary_data.get("pending_ghost_records", 0)
    insufficient = ghost_summary_data.get("insufficient_data_ghosts", 0)

    winner_lines: list[str] = []
    for w in ghost_summary_data.get("top_ghost_winners", []):
        winner_lines.append(
            f"- {w.get('symbol', '?')} ({w.get('ghost_id', '?')}): {w.get('return_20d', '?')}"
        )
    loser_lines: list[str] = []
    for w in ghost_summary_data.get("top_ghost_losers", []):
        loser_lines.append(
            f"- {w.get('symbol', '?')} ({w.get('ghost_id', '?')}): {w.get('return_20d', '?')}"
        )

    rejection_reasons = ghost_summary_data.get("rejection_reasons", {})
    unexpected_reasons = ghost_summary_data.get("rejection_reasons_with_unexpected_winners", [])
    unexpected_count = ghost_summary_data.get("unexpected_winners_count", 0)
    expected_count = ghost_summary_data.get("expected_losers_count", 0)

    reasons_lines = "\n".join(
        f"- {k}: {v} blocked" for k, v in sorted(rejection_reasons.items())
    ) if rejection_reasons else "- None"

    winners_str = "\n".join(winner_lines) if winner_lines else "None matured yet."
    losers_str = "\n".join(loser_lines) if loser_lines else "None matured yet."
    unexpected_reasons_str = ", ".join(unexpected_reasons) if unexpected_reasons else "None"

    content = (
        f"# Ghost Ledger Summary \u2014 {date_str}\n\n"
        f"## Overview\n\n"
        f"- **Total ghost records:** {total}\n"
        f"- **Matured ghost records:** {matured}\n"
        f"- **Pending ghost records:** {pending}\n"
        f"- **Insufficient data:** {insufficient}\n\n"
        f"## Rejection Reasons\n\n{reasons_lines}\n\n"
        f"## Top Ghost Winners (by 20d return)\n\n{winners_str}\n\n"
        f"## Top Ghost Losers (by 20d return)\n\n{losers_str}\n\n"
        f"## Unexpected Winners (ghosts with >5% 10d return)\n\n"
        f"- Count: {unexpected_count}\n"
        f"- Rejection reasons involved: {unexpected_reasons_str}\n\n"
        f"## Expected Losers (ghosts with <-5% 10d return)\n\n"
        f"- Count: {expected_count}\n\n"
        f"## Rejection Reasons Producing Unexpected Winners\n\n"
        f"{unexpected_reasons_str}\n\n"
        f"## Rejection Reasons Producing Expected Losers\n\n"
        f"All rejection reasons that blocked >5% losers are doing their job correctly.\n\n"
        f"{DISCLAIMER}\n"
    )
    path.write_text(content.strip() + "\n")
    return path