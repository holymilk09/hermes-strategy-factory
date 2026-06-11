from __future__ import annotations

"""Filter Quality Audit — evaluate filter tightness, pass rates, score monotonicity.

Pure audit layer. Never modifies strategy behavior, thresholds, scoring, or ledgers.
Produces additive audit labels only.
"""

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


# ─── Labels ───────────────────────────────────────────────────

LABEL_FILTER_LIFT_WEAK = "Filter Lift Weak"
LABEL_FILTER_LIFT_STRONG = "Filter Lift Strong"
LABEL_FILTER_LIFT_INCONCLUSIVE = "Filter Lift Inconclusive"
LABEL_SCORE_MONOTONIC = "Score Monotonic"
LABEL_SCORE_NON_MONOTONIC = "Score Non-Monotonic"
LABEL_SCORE_INCONCLUSIVE = "Score Inconclusive"
LABEL_PASS = "Pass"

MIN_OBSERVATIONS_FOR_LIFT = 5
MIN_OBSERVATIONS_FOR_MONOTONIC = 10
LIFT_SIGNIFICANCE_THRESHOLD = 0.5  # percentage points


# ─── Dataclasses ──────────────────────────────────────────────


@dataclass(frozen=True)
class ScoreBucketStats:
    """Aggregate stats for a single score bucket."""

    bucket: str
    count: int
    mean_return: float | None
    hit_rate: float | None


@dataclass(frozen=True)
class FilterQualityMetrics:
    """Filter quality audit results for a strategy/system."""

    strategy_id: str
    pass_rate: float | None
    accepted_vs_rejected_lift: float | None  # accepted_mean - rejected_mean
    accepted_mean_return: float | None
    rejected_mean_return: float | None
    ghost_baseline_return: float | None
    score_bucket_monotonicity: str  # Score Monotonic / Score Non-Monotonic / Score Inconclusive
    score_buckets: list[ScoreBucketStats]
    filter_lift_assessment: str  # Filter Lift Weak / Filter Lift Strong / Filter Lift Inconclusive
    warnings: list[str]


@dataclass(frozen=True)
class RejectionReasonStats:
    """Stats per rejection reason (filter gate)."""

    reason: str
    count: int
    matured_count: int
    mean_return: float | None
    hit_rate: float | None


# ─── Helpers ──────────────────────────────────────────────────


def _parse_pct(s: str) -> float | None:
    if not s or s.strip() == "":
        return None
    try:
        return float(s.replace("%", "").replace("+", ""))
    except (ValueError, TypeError):
        return None


def _parse_float(s: str) -> float | None:
    if not s or s.strip() == "":
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


# ─── Core audit functions ─────────────────────────────────────


def compute_accepted_vs_rejected_lift(
    accepted_observations: list[dict[str, str]],
    ghost_records: list[dict[str, str]],
    return_key: str = "outcome_return",
) -> float | None:
    """Compute lift: mean accepted return minus mean rejected (ghost) return.

    Positive lift means filters are selecting better candidates.
    Near-zero or negative lift means filters are not adding value.
    """
    accepted_returns: list[float] = []
    for obs in accepted_observations:
        raw = obs.get(return_key) or obs.get("outcome_10d", "") or ""
        v = _parse_pct(raw)
        if v is not None:
            accepted_returns.append(v)

    rejected_returns: list[float] = []
    for ghost in ghost_records:
        if ghost.get("data_status", "").upper() != "MATURE":
            continue
        raw = ghost.get("outcome_10d", "") or ""
        v = _parse_pct(raw)
        if v is not None:
            rejected_returns.append(v)

    if len(accepted_returns) < MIN_OBSERVATIONS_FOR_LIFT or len(rejected_returns) < MIN_OBSERVATIONS_FOR_LIFT:
        return None

    mean_accepted = sum(accepted_returns) / len(accepted_returns)
    mean_rejected = sum(rejected_returns) / len(rejected_returns)

    return round(mean_accepted - mean_rejected, 4)


def compute_pass_rate(
    total_candidates: int,
    accepted_count: int,
) -> float | None:
    """Compute the fraction of candidates that pass the filter."""
    if total_candidates <= 0:
        return None
    return round(accepted_count / total_candidates, 4)


def assess_score_bucket_monotonicity(
    observations: list[dict[str, str]],
    score_key: str = "ret_20d_rank",
    return_key: str = "outcome_return",
) -> tuple[str, list[ScoreBucketStats]]:
    """Check if higher score buckets produce higher returns.

    Returns (assessment, bucket_stats).
    """
    # Bucket by decile
    buckets: dict[str, list[float]] = {}
    for obs in observations:
        score_raw = obs.get(score_key, "")
        score = _parse_float(score_raw)
        if score is None:
            continue
        ret_raw = obs.get(return_key) or obs.get("outcome_10d", "") or ""
        ret = _parse_pct(ret_raw)
        if ret is None:
            continue

        # Assign to decile bucket
        if score >= 0.9:
            bucket = "0.9-1.0"
        elif score >= 0.8:
            bucket = "0.8-0.9"
        elif score >= 0.7:
            bucket = "0.7-0.8"
        elif score >= 0.6:
            bucket = "0.6-0.7"
        elif score >= 0.5:
            bucket = "0.5-0.6"
        elif score >= 0.4:
            bucket = "0.4-0.5"
        elif score >= 0.3:
            bucket = "0.3-0.4"
        elif score >= 0.2:
            bucket = "0.2-0.3"
        elif score >= 0.1:
            bucket = "0.1-0.2"
        else:
            bucket = "0.0-0.1"

        if bucket not in buckets:
            buckets[bucket] = []
        buckets[bucket].append(ret)

    if not buckets:
        return LABEL_SCORE_INCONCLUSIVE, []

    # Build stats
    bucket_stats: list[ScoreBucketStats] = []
    for bucket_label in sorted(buckets.keys()):
        returns = buckets[bucket_label]
        mean_ret = sum(returns) / len(returns) if returns else None
        hits = sum(1 for r in returns if r > 0)
        hit_rate = hits / len(returns) if returns else None
        bucket_stats.append(ScoreBucketStats(
            bucket=bucket_label,
            count=len(returns),
            mean_return=mean_ret,
            hit_rate=hit_rate,
        ))

    total_obs = sum(bs.count for bs in bucket_stats)
    if total_obs < MIN_OBSERVATIONS_FOR_MONOTONIC:
        return LABEL_SCORE_INCONCLUSIVE, bucket_stats

    # Check monotonicity: mean_return should be non-decreasing as bucket increases
    sorted_stats = sorted(bucket_stats, key=lambda x: float(x.bucket.split("-")[0]))
    means = [s.mean_return for s in sorted_stats if s.mean_return is not None]

    if len(means) < 2:
        return LABEL_SCORE_INCONCLUSIVE, bucket_stats

    violations = 0
    for i in range(1, len(means)):
        if means[i] is not None and means[i - 1] is not None:
            if means[i] < means[i - 1]:
                violations += 1

    violation_rate = violations / (len(means) - 1)

    if violation_rate <= 0.2:
        return LABEL_SCORE_MONOTONIC, bucket_stats
    else:
        return LABEL_SCORE_NON_MONOTONIC, bucket_stats


def compute_ghost_baseline_return(
    ghost_records: list[dict[str, str]],
    return_key: str = "outcome_10d",
) -> float | None:
    """Compute the mean return of all matured ghost records.

    This represents the baseline return of rejected/filtered-out setups.
    """
    returns: list[float] = []
    for ghost in ghost_records:
        if ghost.get("data_status", "").upper() != "MATURE":
            continue
        raw = ghost.get(return_key, "") or ""
        v = _parse_pct(raw)
        if v is not None:
            returns.append(v)

    if not returns:
        return None

    return round(sum(returns) / len(returns), 4)


def compute_filter_quality(
    strategy_id: str,
    accepted_observations: list[dict[str, str]],
    ghost_records: list[dict[str, str]],
    total_candidates: int | None = None,
) -> FilterQualityMetrics:
    """Compute filter quality metrics for a strategy.

    Pure audit — never modifies strategy behavior or data.
    """
    warnings: list[str] = []

    # Pass rate
    total = total_candidates if total_candidates is not None else (
        len(accepted_observations) + len(
            [g for g in ghost_records if g.get("data_status", "").upper() != "PENDING"]
        )
    )
    pass_rate = compute_pass_rate(total, len(accepted_observations)) if total > 0 else None

    # Accepted vs rejected lift
    lift = compute_accepted_vs_rejected_lift(accepted_observations, ghost_records)

    # Mean returns
    accepted_returns: list[float] = []
    for obs in accepted_observations:
        raw = obs.get("outcome_return") or obs.get("outcome_10d", "") or ""
        v = _parse_pct(raw)
        if v is not None:
            accepted_returns.append(v)
    accepted_mean = round(sum(accepted_returns) / len(accepted_returns), 4) if accepted_returns else None

    rejected_returns: list[float] = []
    for ghost in ghost_records:
        if ghost.get("data_status", "").upper() != "MATURE":
            continue
        raw = ghost.get("outcome_10d", "") or ""
        v = _parse_pct(raw)
        if v is not None:
            rejected_returns.append(v)
    rejected_mean = round(sum(rejected_returns) / len(rejected_returns), 4) if rejected_returns else None

    # Ghost baseline return
    ghost_baseline = compute_ghost_baseline_return(ghost_records)

    # Score bucket monotonicity
    monotonicity, buckets = assess_score_bucket_monotonicity(accepted_observations)

    # Filter lift assessment
    lift_assessment = LABEL_FILTER_LIFT_INCONCLUSIVE
    if lift is not None:
        if lift > LIFT_SIGNIFICANCE_THRESHOLD:
            lift_assessment = LABEL_FILTER_LIFT_STRONG
        elif lift < -LIFT_SIGNIFICANCE_THRESHOLD:
            lift_assessment = LABEL_FILTER_LIFT_WEAK
            warnings.append(
                f"Accepted candidates underperform rejected by {abs(lift):.2f}pp. "
                f"Filters may be selecting worse candidates."
            )
        else:
            lift_assessment = LABEL_FILTER_LIFT_WEAK
            warnings.append(
                f"Accepted vs rejected lift is {lift:.2f}pp. "
                f"Near-zero/negative lift indicates filters are not separating effectively."
            )

    # Score bucket warnings
    if monotonicity == LABEL_SCORE_NON_MONOTONIC:
        warnings.append("Score buckets are not monotonically increasing. Higher scores do not consistently produce higher returns.")

    return FilterQualityMetrics(
        strategy_id=strategy_id,
        pass_rate=pass_rate,
        accepted_vs_rejected_lift=lift,
        accepted_mean_return=accepted_mean,
        rejected_mean_return=rejected_mean,
        ghost_baseline_return=ghost_baseline,
        score_bucket_monotonicity=monotonicity,
        score_buckets=buckets,
        filter_lift_assessment=lift_assessment,
        warnings=warnings,
    )


def quality_to_dict(metrics: FilterQualityMetrics) -> dict[str, Any]:
    """Convert FilterQualityMetrics to a JSON-serializable dict."""
    return {
        "strategy_id": metrics.strategy_id,
        "pass_rate": metrics.pass_rate,
        "accepted_vs_rejected_lift": metrics.accepted_vs_rejected_lift,
        "accepted_mean_return": metrics.accepted_mean_return,
        "rejected_mean_return": metrics.rejected_mean_return,
        "ghost_baseline_return": metrics.ghost_baseline_return,
        "score_bucket_monotonicity": metrics.score_bucket_monotonicity,
        "score_buckets": [
            {
                "bucket": b.bucket,
                "count": b.count,
                "mean_return": b.mean_return,
                "hit_rate": b.hit_rate,
            }
            for b in metrics.score_buckets
        ],
        "filter_lift_assessment": metrics.filter_lift_assessment,
        "warnings": metrics.warnings,
    }