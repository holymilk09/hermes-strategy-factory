from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.reporting.ghost_ledger import load_ghost_ledger

# ──────────────────────────────────────────────
# Trust state constants
# ──────────────────────────────────────────────

TRUST_ACTIVE = "ACTIVE"
TRUST_STILL_MATURING = "STILL_MATURING"
TRUST_CAUTION = "CAUTION"
TRUST_UNDER_REVIEW = "UNDER_REVIEW"
TRUST_QUARANTINE_REVIEW = "QUARANTINE_REVIEW"
TRUST_RETIRE_REVIEW = "RETIRE_REVIEW"

TRUST_STATES = [
    TRUST_ACTIVE,
    TRUST_STILL_MATURING,
    TRUST_CAUTION,
    TRUST_UNDER_REVIEW,
    TRUST_QUARANTINE_REVIEW,
    TRUST_RETIRE_REVIEW,
]

# ──────────────────────────────────────────────
# Sample size gates
# ──────────────────────────────────────────────

MINIMUM_MATURING = 30       # Under 30: only STILL_MATURING
MINIMUM_CAUTION = 30        # 30–49: CAUTION eligible
MINIMUM_UNDER_REVIEW = 50   # 50–99: UNDER_REVIEW eligible
MINIMUM_NEGATIVE_REVIEW = 100  # 100+: QUARANTINE/RETIRE eligible


def trust_state_for_sample_count(completed_count: int) -> str:
    """Return the maximum trust state allowed given sample count."""
    if completed_count < MINIMUM_MATURING:
        return TRUST_STILL_MATURING
    if completed_count < MINIMUM_UNDER_REVIEW:
        return TRUST_CAUTION
    if completed_count < MINIMUM_NEGATIVE_REVIEW:
        return TRUST_UNDER_REVIEW
    return TRUST_ACTIVE  # Eligible for any state; further analysis required


def can_reach_negative_trust(completed_count: int) -> bool:
    """True if QUARANTINE_REVIEW or RETIRE_REVIEW is even eligible."""
    return completed_count >= MINIMUM_NEGATIVE_REVIEW


# ──────────────────────────────────────────────
# Baseline comparison helpers
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class BaselineReturns:
    spy_5d: float | None = None
    spy_10d: float | None = None
    spy_20d: float | None = None
    spy_30d: float | None = None
    qqq_5d: float | None = None
    qqq_10d: float | None = None
    qqq_20d: float | None = None
    qqq_30d: float | None = None
    sector_5d: float | None = None
    sector_10d: float | None = None
    sector_20d: float | None = None
    sector_30d: float | None = None
    baseline_status: str = "BASELINE_UNAVAILABLE"


def _parse_pct(s: str) -> float | None:
    if not s or s.strip() == "":
        return None
    try:
        return float(s.replace("%", "").replace("+", ""))
    except Exception:
        return None


def compute_baseline_returns(
    root: Path,
    signal_date: str,
    symbol: str = "",
    sector_etf: str = "",
) -> BaselineReturns:
    """Compute baseline ETF returns from signal_date over 5/10/20/30 day windows.

    Uses cached OHLCV data for SPY, QQQ, and optional sector ETF.
    """
    from src.reporting.maturity_scoreboard import checkpoint_result, load_ohlcv_rows
    from src.paper.maturity_watchdog import find_symbol_ohlcv_path

    if not signal_date:
        return BaselineReturns()

    try:
        signal_dt = datetime.fromisoformat(signal_date.replace("Z", "+00:00"))
    except Exception:
        return BaselineReturns()

    def _returns_for(ticker: str) -> dict[str, float | None]:
        path = find_symbol_ohlcv_path(root, ticker)
        if path is None:
            return {}
        rows = load_ohlcv_rows(path)
        if not rows:
            return {}
        future = [r for r in rows if r["dt"] > signal_dt]
        if not future:
            return {}
        initial = future[0]["close"]
        days = len(future)
        out: dict[str, float | None] = {}
        for n in (5, 10, 20, 30):
            if days >= n:
                r = checkpoint_result(initial, future, n)
                out[f"_{n}d"] = _parse_pct(r or "")
            else:
                out[f"_{n}d"] = None
        return out

    spy = _returns_for("SPY")
    qqq = _returns_for("QQQ")
    sector = _returns_for(sector_etf) if sector_etf else {}

    has_any = any(v is not None for v in list(spy.values()) + list(qqq.values()) + list(sector.values()))

    return BaselineReturns(
        spy_5d=spy.get("_5d"),
        spy_10d=spy.get("_10d"),
        spy_20d=spy.get("_20d"),
        spy_30d=spy.get("_30d"),
        qqq_5d=qqq.get("_5d"),
        qqq_10d=qqq.get("_10d"),
        qqq_20d=qqq.get("_20d"),
        qqq_30d=qqq.get("_30d"),
        sector_5d=sector.get("_5d"),
        sector_10d=sector.get("_10d"),
        sector_20d=sector.get("_20d"),
        sector_30d=sector.get("_30d"),
        baseline_status="BASELINE_AVAILABLE" if has_any else "BASELINE_UNAVAILABLE",
    )


# ──────────────────────────────────────────────
# Raw return and excess return calculation
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class ComputedOutcome:
    raw_return_5d: float | None = None
    raw_return_10d: float | None = None
    raw_return_20d: float | None = None
    raw_return_30d: float | None = None
    spy_excess_5d: float | None = None
    spy_excess_10d: float | None = None
    spy_excess_20d: float | None = None
    spy_excess_30d: float | None = None
    qqq_excess_5d: float | None = None
    qqq_excess_10d: float | None = None
    qqq_excess_20d: float | None = None
    qqq_excess_30d: float | None = None
    sector_excess_5d: float | None = None
    sector_excess_10d: float | None = None
    sector_excess_20d: float | None = None
    sector_excess_30d: float | None = None
    baseline_status: str = "BASELINE_UNAVAILABLE"


def compute_outcome_returns(
    raw_return_str: str,
    baseline: BaselineReturns,
    window: int = 10,
) -> ComputedOutcome:
    """Compute raw and excess returns given a raw return string and baseline context."""
    raw = _parse_pct(raw_return_str)
    if raw is None:
        return ComputedOutcome()

    spy_ret = getattr(baseline, f"spy_{window}d", None)
    qqq_ret = getattr(baseline, f"qqq_{window}d", None)
    sector_ret = getattr(baseline, f"sector_{window}d", None)

    spy_ex = raw - spy_ret if spy_ret is not None else None
    qqq_ex = raw - qqq_ret if qqq_ret is not None else None
    sector_ex = raw - sector_ret if sector_ret is not None else None

    return ComputedOutcome(
        raw_return_5d=raw if window == 5 else None,
        raw_return_10d=raw if window == 10 else None,
        raw_return_20d=raw if window == 20 else None,
        raw_return_30d=raw if window == 30 else None,
        spy_excess_5d=spy_ex if window == 5 else None,
        spy_excess_10d=spy_ex if window == 10 else None,
        spy_excess_20d=spy_ex if window == 20 else None,
        spy_excess_30d=spy_ex if window == 30 else None,
        qqq_excess_5d=qqq_ex if window == 5 else None,
        qqq_excess_10d=qqq_ex if window == 10 else None,
        qqq_excess_20d=qqq_ex if window == 20 else None,
        qqq_excess_30d=qqq_ex if window == 30 else None,
        sector_excess_5d=sector_ex if window == 5 else None,
        sector_excess_10d=sector_ex if window == 10 else None,
        sector_excess_20d=sector_ex if window == 20 else None,
        sector_excess_30d=sector_ex if window == 30 else None,
        baseline_status=baseline.baseline_status,
    )


# ──────────────────────────────────────────────
# Market weather segmentation
# ──────────────────────────────────────────────

def segment_by_market_weather(
    records: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Separate completed outcomes into market-helping and market-not-helping groups."""
    helping: list[dict[str, Any]] = []
    not_helping: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []

    for r in records:
        weather = (r.get("market_weather") or "").strip().lower()
        if not weather or weather in ("", "unknown", "not enough proof yet"):
            unknown.append(r)
        elif weather in ("helping", "bullish", "uptrend", "trending up", "strong market"):
            helping.append(r)
        else:
            not_helping.append(r)

    def _segment_stats(group: list[dict[str, Any]]) -> dict[str, Any]:
        if not group:
            return {"completed_count": 0}
        returns_10d = []
        for r in group:
            o = _parse_pct(r.get("outcome_10d", ""))
            if o is not None:
                returns_10d.append(o)
        count = len(returns_10d)
        avg_ret = sum(returns_10d) / count if count > 0 else None
        hits = sum(1 for v in returns_10d if v > 0)
        hit_rate = hits / count if count > 0 else None
        max_adv = min(returns_10d) if returns_10d else None
        return {
            "completed_count": count,
            "avg_10d_return": f"{avg_ret:.2f}%" if avg_ret is not None else None,
            "hit_rate": f"{hit_rate:.1%}" if hit_rate is not None else None,
            "max_adverse_move": f"{max_adv:.2f}%" if max_adv is not None else None,
        }

    return {
        "market_helping": _segment_stats(helping),
        "market_not_helping": _segment_stats(not_helping),
        "market_unknown": _segment_stats(unknown),
    }


# ──────────────────────────────────────────────
# Filter impact audit
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class FilterImpact:
    filter_name: str
    blocked_count: int
    blocked_winners: int
    blocked_losers: int
    avg_ghost_return_5d: str | None = None
    avg_ghost_return_10d: str | None = None
    avg_ghost_return_20d: str | None = None
    avg_ghost_return_30d: str | None = None
    avg_active_return_5d: str | None = None
    avg_active_return_10d: str | None = None
    avg_active_return_20d: str | None = None
    avg_active_return_30d: str | None = None
    ghost_hit_rate: str | None = None
    active_hit_rate: str | None = None
    filter_helped: str = "INCONCLUSIVE"
    notes: str = ""


def compute_filter_impact(
    filter_name: str,
    ghost_records: list[dict[str, str]],
    active_records: list[dict[str, str]],
) -> FilterImpact:
    """Compare ghost (filtered-out) outcomes vs active (published) outcomes for one filter.

    filter_helped:
      - true if ghost outcomes are poor relative to active
      - false if ghost outcomes are strong
      - INCONCLUSIVE if sample size too small
    """
    matching_ghosts = [r for r in ghost_records if r.get("rejection_reason", "") == filter_name]
    blocked = len(matching_ghosts)

    if blocked == 0:
        return FilterImpact(filter_name=filter_name, blocked_count=0, blocked_winners=0, blocked_losers=0)

    # Filter to matured ghosts only
    matured = [r for r in matching_ghosts if r.get("data_status", "").upper() == "MATURE"]

    if len(matured) < 5:
        return FilterImpact(
            filter_name=filter_name,
            blocked_count=blocked,
            blocked_winners=0,
            blocked_losers=0,
            filter_helped="INCONCLUSIVE",
            notes="Fewer than 5 matured ghost records for this filter.",
        )

    def _avg_return(records: list[dict[str, str]], outcome_key: str) -> str | None:
        vals = []
        for r in records:
            v = _parse_pct(r.get(outcome_key, ""))
            if v is not None:
                vals.append(v)
        if not vals:
            return None
        avg = sum(vals) / len(vals)
        return f"{avg:.2f}%"

    def _hit_rate(records: list[dict[str, str]], outcome_key: str) -> str | None:
        vals = []
        for r in records:
            v = _parse_pct(r.get(outcome_key, ""))
            if v is not None:
                vals.append(v)
        if not vals:
            return None
        hits = sum(1 for v in vals if v > 0)
        return f"{hits / len(vals):.1%}"

    def _winners(records: list[dict[str, str]]) -> int:
        return sum(1 for r in records if (_parse_pct(r.get("outcome_10d", "")) or 0) > 0)

    def _losers(records: list[dict[str, str]]) -> int:
        return sum(1 for r in records if (_parse_pct(r.get("outcome_10d", "")) or 0) < 0)

    blocked_winners = _winners(matured)
    blocked_losers = _losers(matured)

    # Active (published) stats
    active_matured = [r for r in active_records if r.get("outcome_status", "").upper() not in ("PENDING", "")]
    active_matured = [r for r in active_matured if _parse_pct(r.get("outcome_return", "")) is not None]

    avg_ghost_10d = _avg_return(matured, "outcome_10d")
    avg_active_10d = _avg_return(active_matured, "outcome_return") if active_matured else None
    ghost_hit = _hit_rate(matured, "outcome_10d")
    active_hit = _hit_rate(active_matured, "outcome_return") if active_matured else None

    # Decision logic
    ghost_avg_val = _parse_pct(avg_ghost_10d or "0")
    active_avg_val = _parse_pct(avg_active_10d or "0")
    ghost_hit_val = float(ghost_hit.replace("%", "")) / 100 if ghost_hit else 0
    active_hit_val = float(active_hit.replace("%", "")) / 100 if active_hit else 0

    if ghost_avg_val is not None and active_avg_val is not None:
        if ghost_avg_val < active_avg_val and ghost_hit_val < active_hit_val:
            filter_helped = "true"
            notes = "Ghost outcomes are weaker than active. Filter appears to be helping."
        elif ghost_avg_val >= active_avg_val and ghost_hit_val >= active_hit_val and blocked >= 10:
            filter_helped = "false"
            notes = "Ghost outcomes are as strong or stronger than active. Filter may be too strict."
        else:
            filter_helped = "INCONCLUSIVE"
            notes = "Evidence is mixed. Manual review recommended."
    else:
        filter_helped = "INCONCLUSIVE"
        notes = "Sample size too small for reliable conclusion."

    return FilterImpact(
        filter_name=filter_name,
        blocked_count=blocked,
        blocked_winners=blocked_winners,
        blocked_losers=blocked_losers,
        avg_ghost_return_5d=_avg_return(matured, "outcome_5d"),
        avg_ghost_return_10d=avg_ghost_10d,
        avg_ghost_return_20d=_avg_return(matured, "outcome_20d"),
        avg_ghost_return_30d=_avg_return(matured, "outcome_30d"),
        avg_active_return_5d=_avg_return(active_matured, "outcome_return") if active_matured else None,
        avg_active_return_10d=avg_active_10d,
        avg_active_return_20d=_avg_return(active_matured, "outcome_return") if active_matured else None,
        avg_active_return_30d=_avg_return(active_matured, "outcome_return") if active_matured else None,
        ghost_hit_rate=ghost_hit,
        active_hit_rate=active_hit,
        filter_helped=filter_helped,
        notes=notes,
    )


# ──────────────────────────────────────────────
# Trust state recommendation
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class TrustRecommendation:
    strategy_id: str
    completed_sample_count: int
    trust_state: str
    reason: str
    windows_reviewed: str
    market_weather_split: dict[str, Any]
    baseline_comparison: str
    missing_data_warnings: list[str]
    manual_approval_required: bool = True


def recommend_trust_state(
    strategy_id: str,
    completed_outcomes: list[dict[str, Any]],
    ghost_records: list[dict[str, str]] | None = None,
    root: Path | None = None,
) -> TrustRecommendation:
    """Produce a trust state recommendation for a strategy based on its completed outcomes.

    This function NEVER changes strategy behavior. It only produces a report label.
    """
    count = len(completed_outcomes)
    max_state = trust_state_for_sample_count(count)
    warnings: list[str] = []

    # Determine base state by sample count alone
    if count == 0:
        return TrustRecommendation(
            strategy_id=strategy_id,
            completed_sample_count=0,
            trust_state=TRUST_STILL_MATURING,
            reason="No completed outcomes yet. Still maturing.",
            windows_reviewed="N/A",
            market_weather_split={},
            baseline_comparison="N/A",
            missing_data_warnings=["Zero completed outcomes."],
        )

    # Compute aggregate stats
    returns_10d = []
    returns_20d = []
    hit_10d = 0
    for r in completed_outcomes:
        ret_raw = r.get("outcome_return") or r.get("outcome_10d") or ""
        v = _parse_pct(ret_raw)
        if v is not None:
            returns_10d.append(v)
            if v > 0:
                hit_10d += 1
        v20 = _parse_pct(r.get("outcome_20d", ""))
        if v20 is not None:
            returns_20d.append(v20)

    if not returns_10d:
        return TrustRecommendation(
            strategy_id=strategy_id,
            completed_sample_count=count,
            trust_state=TRUST_STILL_MATURING,
            reason="None of the outcomes have computable returns yet.",
            windows_reviewed="5d, 10d, 20d, 30d",
            market_weather_split={},
            baseline_comparison="N/A",
            missing_data_warnings=["No computable returns found."],
        )

    avg_10d = sum(returns_10d) / len(returns_10d)
    hit_rate = hit_10d / len(returns_10d)

    # Baseline comparison
    baseline_str = "N/A"
    if root:
        for r in completed_outcomes:
            bl = compute_baseline_returns(root, r.get("signal_timestamp") or r.get("signal_date", ""))
            if bl.baseline_status == "BASELINE_AVAILABLE":
                baseline_str = f"Baseline available for some records (status: {bl.baseline_status})"
                break

    # Market weather split
    weather_split = segment_by_market_weather(completed_outcomes)

    # Build reason
    reason_parts = []
    if max_state == TRUST_STILL_MATURING:
        reason_parts.append(f"Only {count} completed outcomes. Minimum {MINIMUM_MATURING} required for CAUTION.")
    elif max_state == TRUST_CAUTION:
        reason_parts.append(f"{count} completed outcomes. CAUTION eligible.")
        if avg_10d < 0:
            reason_parts.append(f"Average 10d return is negative ({avg_10d:.2f}%). Recommend monitoring.")
        if hit_rate < 0.4:
            reason_parts.append(f"Hit rate is {hit_rate:.1%}. Below 40% threshold.")
    elif max_state == TRUST_UNDER_REVIEW:
        reason_parts.append(f"{count} completed outcomes. UNDER_REVIEW eligible.")
        if avg_10d < -2.0:
            reason_parts.append(f"Average 10d return is poor ({avg_10d:.2f}%).")
    elif max_state == TRUST_ACTIVE:
        if count >= MINIMUM_NEGATIVE_REVIEW:
            # Check for broad persistent weakness
            avg_20d = sum(returns_20d) / len(returns_20d) if returns_20d else avg_10d
            if avg_10d < -2.0 and avg_20d < -2.0 and hit_rate < 0.35:
                would_be = TRUST_QUARANTINE_REVIEW
                reason_parts.append(
                    f"{count} completed outcomes. Weakness is broad and persistent "
                    f"across windows (10d avg: {avg_10d:.2f}%, 20d avg: {avg_20d:.2f}%, hit: {hit_rate:.1%}). "
                    f"Would be {would_be} but manual approval required."
                )
            else:
                reason_parts.append(f"{count} completed outcomes. No broad persistent weakness detected.")
        else:
            reason_parts.append(f"{count} completed outcomes. Active.")

    reason = " ".join(reason_parts) if reason_parts else f"{count} completed outcomes."

    # Negative trust states only if evidence is broad AND persistent AND sample size sufficient
    trust_state = TRUST_ACTIVE
    if max_state == TRUST_STILL_MATURING:
        trust_state = TRUST_STILL_MATURING
    elif max_state == TRUST_CAUTION:
        trust_state = TRUST_CAUTION
    elif max_state == TRUST_UNDER_REVIEW:
        trust_state = TRUST_UNDER_REVIEW
    else:
        # max_state is ACTIVE (eligible for any)
        if count >= MINIMUM_NEGATIVE_REVIEW and avg_10d < -3.0 and hit_rate < 0.3:
            trust_state = TRUST_QUARANTINE_REVIEW
        else:
            trust_state = TRUST_ACTIVE

    return TrustRecommendation(
        strategy_id=strategy_id,
        completed_sample_count=count,
        trust_state=trust_state,
        reason=reason,
        windows_reviewed="5d, 10d, 20d, 30d",
        market_weather_split=weather_split,
        baseline_comparison=baseline_str,
        missing_data_warnings=warnings,
        manual_approval_required=True,
    )


# ──────────────────────────────────────────────
# Filter audit from ghost ledger
# ──────────────────────────────────────────────

def audit_all_filters(
    ghost_records: list[dict[str, str]],
    active_records: list[dict[str, str]],
) -> list[FilterImpact]:
    """Run filter impact audit for every rejection reason found in the ghost ledger."""
    reasons = set(r.get("rejection_reason", "") for r in ghost_records if r.get("rejection_reason"))
    impacts: list[FilterImpact] = []
    for reason in sorted(reasons):
        impact = compute_filter_impact(reason, ghost_records, active_records)
        impacts.append(impact)
    return impacts