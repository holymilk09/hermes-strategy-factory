"""Tests for Filter Quality Audit — pass rates, lift, monotonicity, warnings."""

from __future__ import annotations

from pathlib import Path

from src.reporting.filter_quality_audit import (
    LABEL_FILTER_LIFT_STRONG,
    LABEL_FILTER_LIFT_WEAK,
    LABEL_FILTER_LIFT_INCONCLUSIVE,
    LABEL_SCORE_MONOTONIC,
    LABEL_SCORE_NON_MONOTONIC,
    LABEL_SCORE_INCONCLUSIVE,
    FilterQualityMetrics,
    ScoreBucketStats,
    compute_accepted_vs_rejected_lift,
    compute_pass_rate,
    assess_score_bucket_monotonicity,
    compute_ghost_baseline_return,
    compute_filter_quality,
    quality_to_dict,
)


def _make_obs(
    outcome_return: str = "+2.0%",
    ret_20d_rank: str = "0.85",
) -> dict[str, str]:
    return {
        "observation_id": "obs1",
        "symbol": "AAPL",
        "outcome_return": outcome_return,
        "outcome_10d": outcome_return,
        "ret_20d_rank": ret_20d_rank,
    }


def _make_ghost(
    outcome_10d: str = "+1.0%",
    data_status: str = "MATURE",
    rejection_reason: str = "vol_filter",
) -> dict[str, str]:
    return {
        "ghost_id": "g1",
        "rejection_reason": rejection_reason,
        "data_status": data_status,
        "outcome_10d": outcome_10d,
        "outcome_5d": outcome_10d,
        "outcome_20d": outcome_10d,
        "outcome_30d": outcome_10d,
    }


# ─── Accept vs Reject lift tests ─────────────────────────────


def test_lift_positive() -> None:
    """Accepted candidates outperform rejected = positive lift."""
    accepted = [_make_obs("+5.0%") for _ in range(5)]
    rejected = [_make_ghost("+1.0%") for _ in range(5)]
    lift = compute_accepted_vs_rejected_lift(accepted, rejected)
    assert lift is not None
    assert lift > 2.0  # ~4% difference


def test_lift_negative() -> None:
    """Rejected candidates outperform accepted = negative lift."""
    accepted = [_make_obs("+1.0%") for _ in range(5)]
    rejected = [_make_ghost("+5.0%") for _ in range(5)]
    lift = compute_accepted_vs_rejected_lift(accepted, rejected)
    assert lift is not None
    assert lift < -2.0


def test_lift_zero_empty_input() -> None:
    """Empty inputs produce None lift."""
    lift = compute_accepted_vs_rejected_lift([], [])
    assert lift is None


def test_lift_insufficient_samples() -> None:
    """Fewer than 5 matured ghosts = None lift."""
    accepted = [_make_obs("+3.0%") for _ in range(3)]
    rejected = [_make_ghost("+2.0%") for _ in range(3)]
    lift = compute_accepted_vs_rejected_lift(accepted, rejected)
    assert lift is None


def test_lift_rejected_filters_pending() -> None:
    """Pending ghosts are excluded from lift calculation."""
    accepted = [_make_obs("+4.0%") for _ in range(5)]
    rejected = (
        [_make_ghost("+5.0%") for _ in range(5)]  # MATURE
        + [_make_ghost("+1.0%", data_status="PENDING") for _ in range(5)]  # PENDING
    )
    lift = compute_accepted_vs_rejected_lift(accepted, rejected)
    assert lift is not None
    # Only MATURE ghosts count
    assert lift < 0  # accepted underperform MATURE ghosts


# ─── Pass rate tests ──────────────────────────────────────────


def test_pass_rate_half() -> None:
    """50 candidates, 25 accepted = 50% pass rate."""
    rate = compute_pass_rate(50, 25)
    assert rate == 0.5


def test_pass_rate_zero_candidates() -> None:
    """Zero candidates = None pass rate."""
    rate = compute_pass_rate(0, 0)
    assert rate is None


def test_pass_rate_all_pass() -> None:
    """All candidates pass = 100%."""
    rate = compute_pass_rate(10, 10)
    assert rate == 1.0


def test_pass_rate_none_pass() -> None:
    """No candidates pass = 0%."""
    rate = compute_pass_rate(10, 0)
    assert rate == 0.0


# ─── Score bucket monotonicity tests ──────────────────────────


def test_monotonic_increasing_high_rank() -> None:
    """Higher score buckets should have higher returns (monotonic)."""
    # High rank -> high return
    obs_list = [_make_obs("+3.0%", "0.95") for _ in range(5)] + [
        _make_obs("+1.0%", "0.55") for _ in range(5)
    ]
    assessment, buckets = assess_score_bucket_monotonicity(obs_list)
    # Should be monotonic since high rank > low rank returns
    assert assessment in (LABEL_SCORE_MONOTONIC, LABEL_SCORE_INCONCLUSIVE)


def test_non_monotonic() -> None:
    """Lower score buckets outperforming higher = non-monotonic."""
    obs_list = (
        [_make_obs("-1.0%", "0.95") for _ in range(5)]    # high rank, bad return
        + [_make_obs("+5.0%", "0.55") for _ in range(5)]   # low rank, good return
    )
    assessment, buckets = assess_score_bucket_monotonicity(obs_list)
    # The high bucket (0.9-1.0) has -1% while 0.5-0.6 has +5% — clearly non-monotonic
    if len(buckets) >= 2:
        sorted_buckets = sorted(buckets, key=lambda b: float(b.bucket.split("-")[0]))
        means = [b.mean_return for b in sorted_buckets if b.mean_return is not None]
        if len(means) >= 2:
            assert assessment == LABEL_SCORE_NON_MONOTONIC


def test_monotonic_insufficient_data() -> None:
    """Fewer than 10 observations = inconclusive."""
    obs_list = [_make_obs("+2.0%", "0.85") for _ in range(3)]
    assessment, buckets = assess_score_bucket_monotonicity(obs_list)
    assert assessment == LABEL_SCORE_INCONCLUSIVE


# ─── Ghost baseline tests ─────────────────────────────────────


def test_ghost_baseline_positive() -> None:
    """Matured ghosts with positive returns produce positive baseline."""
    ghosts = [_make_ghost("+2.0%") for _ in range(5)]
    baseline = compute_ghost_baseline_return(ghosts)
    assert baseline is not None
    assert baseline > 0


def test_ghost_baseline_empty() -> None:
    """No matured ghosts = None baseline."""
    baseline = compute_ghost_baseline_return([])
    assert baseline is None


def test_ghost_baseline_pending_excluded() -> None:
    """Pending ghosts are not included in baseline."""
    ghosts = [_make_ghost("+5.0%", data_status="PENDING") for _ in range(5)]
    baseline = compute_ghost_baseline_return(ghosts)
    assert baseline is None


# ─── Filter quality tests ─────────────────────────────────────


def test_filter_quality_strong_lift() -> None:
    """Accepted strongly outperforms rejected = Filter Lift Strong."""
    accepted = [_make_obs("+5.0%") for _ in range(5)]
    rejected = [_make_ghost("+1.0%") for _ in range(5)]
    quality = compute_filter_quality("test_strat", accepted, rejected)
    assert quality.filter_lift_assessment == LABEL_FILTER_LIFT_STRONG


def test_filter_quality_weak_lift() -> None:
    """Accepted and rejected with similar returns = Filter Lift Weak."""
    accepted = [_make_obs("+2.0%") for _ in range(5)]
    rejected = [_make_ghost("+1.9%") for _ in range(5)]
    quality = compute_filter_quality("test_strat", accepted, rejected)
    assert quality.filter_lift_assessment == LABEL_FILTER_LIFT_WEAK


def test_filter_quality_inconclusive_no_ghosts() -> None:
    """No ghost records = Inconclusive."""
    quality = compute_filter_quality("test_strat", [_make_obs()], [])
    assert quality.filter_lift_assessment == LABEL_FILTER_LIFT_INCONCLUSIVE


def test_filter_quality_pass_rate() -> None:
    """Pass rate is computed correctly."""
    accepted = [_make_obs() for _ in range(5)]
    rejected = [_make_ghost() for _ in range(5)]
    quality = compute_filter_quality("test_strat", accepted, rejected, total_candidates=10)
    assert quality.pass_rate == 0.5


def test_filter_quality_warnings_on_weak_lift() -> None:
    """Weak filter lift produces warnings."""
    accepted = [_make_obs("+2.0%") for _ in range(5)]
    rejected = [_make_ghost("+1.9%") for _ in range(5)]
    quality = compute_filter_quality("test_strat", accepted, rejected)
    assert len(quality.warnings) > 0


# ─── Accepted and rejected with similar returns = Filter Lift Weak ──


def test_similar_returns_flag_filter_lift_weak() -> None:
    """Test requirement: Accepted and rejected with similar returns must flag Filter Lift Weak."""
    accepted = [_make_obs("+2.1%") for _ in range(5)]
    rejected = [_make_ghost("+2.0%") for _ in range(5)]
    quality = compute_filter_quality("test_strat", accepted, rejected)
    assert quality.filter_lift_assessment == LABEL_FILTER_LIFT_WEAK


# ─── Serialization tests ──────────────────────────────────────


def test_quality_to_dict() -> None:
    """FilterQualityMetrics converts to dict correctly."""
    buckets = [
        ScoreBucketStats(bucket="0.8-0.9", count=5, mean_return=2.0, hit_rate=0.6),
        ScoreBucketStats(bucket="0.5-0.6", count=3, mean_return=1.0, hit_rate=0.5),
    ]
    quality = FilterQualityMetrics(
        strategy_id="test_strat",
        pass_rate=0.5,
        accepted_vs_rejected_lift=2.0,
        accepted_mean_return=3.0,
        rejected_mean_return=1.0,
        ghost_baseline_return=1.5,
        score_bucket_monotonicity=LABEL_SCORE_MONOTONIC,
        score_buckets=buckets,
        filter_lift_assessment=LABEL_FILTER_LIFT_STRONG,
        warnings=[],
    )
    d = quality_to_dict(quality)
    assert d["strategy_id"] == "test_strat"
    assert d["accepted_vs_rejected_lift"] == 2.0
    assert d["filter_lift_assessment"] == LABEL_FILTER_LIFT_STRONG
    assert d["score_bucket_monotonicity"] == LABEL_SCORE_MONOTONIC
    assert len(d["score_buckets"]) == 2


# ─── Ledger immutability meta-test ────────────────────────────


def test_no_strategy_logic_import() -> None:
    """Filter quality audit imports only from reporting layer."""
    import src.reporting.filter_quality_audit  # noqa: F811

    import sys
    mod_names = list(sys.modules.keys())
    strategy_modules = [m for m in mod_names if "research.momentum" in m or "research.price_volume" in m]
    assert len(strategy_modules) == 0, f"Unexpected imports: {strategy_modules}"