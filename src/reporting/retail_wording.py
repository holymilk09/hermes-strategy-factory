from __future__ import annotations

from dataclasses import dataclass

DISCLAIMER = (
    "Research-only: This report is for research tracking and education only. "
    "It is not investment advice. No live trading. No broker execution. "
    "No production activation."
)

TIME_RANGE_SHORT = "Short-Term Setup: 1–5 trading days"
TIME_RANGE_SWING = "Swing Setup: 5–30 trading days"
TIME_RANGE_LONG = "Long-Term Trend View: 1–6 months+"


@dataclass(frozen=True)
class RetailWordingCard:
    main_view: str
    time_range: str
    price_area_that_matters: str
    setup_breaks_below: str
    setup_breaks_above: str
    why_it_looks_strong_or_weak: str
    main_risk: str
    what_changed: str
    plain_english: str
    disclaimer: str


def _main_view(outcome_status: str, ret_5d: float) -> str:
    status = (outcome_status or "").upper().strip()
    if status == "PENDING":
        if ret_5d >= 0.15:
            return "Waiting for Pullback"
        return "Waiting for Stronger Proof"
    if ret_5d <= -0.08:
        return "Weakening"
    return "Bullish Swing Setup"


def _risk_label(ret_5d: float) -> str:
    if ret_5d >= 0.15:
        return "Too Stretched"
    if ret_5d <= -0.05:
        return "Weakening"
    return "High Risk Setup"


def _changed_text(ret_5d: float, pending: bool) -> str:
    if ret_5d >= 0.15:
        return "Large short-term move increased pullback risk."
    if ret_5d <= -0.05:
        return "Recent pullback reduced confidence in follow-through."
    if pending:
        return "Setup structure is mostly unchanged; proof window is still open."
    return "Setup stayed within expected range during the latest period."


def _time_range_for_view(main_view: str) -> str:
    # Deterministic mapping; default per requirement is swing.
    if main_view in {"Waiting for Breakout Confirmation", "Waiting for Pullback"}:
        return TIME_RANGE_SHORT
    if main_view in {"No Edge", "No Reliable Rating Yet"}:
        return TIME_RANGE_LONG
    return TIME_RANGE_SWING


def build_retail_wording(
    *,
    outcome_status: str,
    signal_close: float,
    ret_5d: float,
    ret_20d_rank: float,
    ret_60d_rank: float,
    progress_text: str,
) -> RetailWordingCard:
    main_view = _main_view(outcome_status, ret_5d)
    risk = _risk_label(ret_5d)

    area_low = round(signal_close * 0.97, 2)
    area_high = round(signal_close * 1.03, 2)
    breaks_below = round(signal_close * 0.96, 2)
    improves_above = round(signal_close * 1.02, 2)

    pending = (outcome_status or "").upper().strip() == "PENDING"
    why = (
        f"Relative strength ranks remain elevated "
        f"(20d {ret_20d_rank:.2f}, 60d {ret_60d_rank:.2f}); {progress_text}"
    )

    plain_english = (
        f"This setup currently maps to '{main_view}'. "
        f"Price area that matters is {area_low} to {area_high}. "
        f"Setup breaks below {breaks_below}. Setup improves if {improves_above}."
    )

    return RetailWordingCard(
        main_view=main_view,
        time_range=_time_range_for_view(main_view),
        price_area_that_matters=f"{area_low} to {area_high}",
        setup_breaks_below=f"{breaks_below}",
        setup_breaks_above=f"{improves_above}",
        why_it_looks_strong_or_weak=why,
        main_risk=risk,
        what_changed=_changed_text(ret_5d, pending),
        plain_english=plain_english,
        disclaimer=DISCLAIMER,
    )
