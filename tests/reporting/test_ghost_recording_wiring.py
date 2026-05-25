"""Tests for ghost recording wiring in observation scripts.

Verifies:
- Rejected rows create GhostRecord entries
- Duplicate runs are idempotent
- Selected observations are unchanged
- No fabricated outcomes
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.reporting.ghost_ledger import (
    _ghost_id_for_rejection,
    _resolve_first_failed_gate,
    load_ghost_ledger,
    record_observation_rejections,
)


# ─── Ghost ID determinism ───


def test_ghost_id_deterministic() -> None:
    """Same inputs produce same ghost ID."""
    id1 = _ghost_id_for_rejection("NVDA", "2026-05-20T04:00:00+00:00", "swing", "ret_20d_rank", "20d_momentum_too_weak")
    id2 = _ghost_id_for_rejection("NVDA", "2026-05-20T04:00:00+00:00", "swing", "ret_20d_rank", "20d_momentum_too_weak")
    assert id1 == id2
    assert len(id1) == 24


def test_ghost_id_different_symbol() -> None:
    """Different symbols produce different ghost IDs."""
    id1 = _ghost_id_for_rejection("AMD", "2026-05-20T04:00:00+00:00", "swing", "ret_20d_rank", "20d_momentum_too_weak")
    id2 = _ghost_id_for_rejection("NVDA", "2026-05-20T04:00:00+00:00", "swing", "ret_20d_rank", "20d_momentum_too_weak")
    assert id1 != id2


def test_ghost_id_not_random_uuid() -> None:
    """Ghost ID is a deterministic hash, not a UUID."""
    id1 = _ghost_id_for_rejection("AAPL", "2026-05-20", "swing", "volume_filter", "volume_not_elevated")
    assert len(id1) == 24
    assert "-" not in id1


# ─── First failed gate resolution ───


def test_resolve_first_failed_gate() -> None:
    """Returns the first gate that fails."""
    gates = [
        ("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return"),
        ("close_above_ma50", lambda v: v > 0.5, "close_above_ma50", "below_50ma"),
    ]
    row = {"ret_5d": -0.02, "close_above_ma50": 1.0}
    result = _resolve_first_failed_gate(row, gates)
    assert result is not None
    gate_name, reason, score = result
    assert gate_name == "ret_5d_positive"
    assert reason == "recent_negative_return"


def test_resolve_all_gates_pass() -> None:
    """Returns None when all gates pass."""
    gates = [
        ("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return"),
        ("close_above_ma50", lambda v: v > 0.5, "close_above_ma50", "below_50ma"),
    ]
    row = {"ret_5d": 0.05, "close_above_ma50": 1.0}
    result = _resolve_first_failed_gate(row, gates)
    assert result is None


def test_resolve_missing_column_skipped() -> None:
    """Missing column is skipped, next gate is checked."""
    gates = [
        ("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return"),
        ("close_above_ma50", lambda v: v > 0.5, "close_above_ma50", "below_50ma"),
    ]
    row = {"ret_5d": 0.05}
    result = _resolve_first_failed_gate(row, gates)
    assert result is None


# ─── record_observation_rejections ───


def test_rejected_rows_create_ghosts(tmp_path: Path) -> None:
    """Non-selected symbols at latest timestamp become ghost records."""
    ghost_path = tmp_path / "ghost.csv"
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-05-20", "2026-05-20"]),
        "symbol": ["AAPL", "MSFT"],
        "close": [150.0, 300.0],
        "selected": [True, False],
        "ret_5d": [0.05, -0.02],
        "close_above_ma50": [1, 1],
    })
    gates = [
        ("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return"),
        ("close_above_ma50", lambda v: v > 0.5, "close_above_ma50", "below_50ma"),
    ]
    count = record_observation_rejections(df, Path("/tmp"), "test_strat", "swing", gates, ghost_path=ghost_path)
    assert count == 1
    rows = load_ghost_ledger(ghost_path)
    assert len(rows) == 1
    assert rows[0]["symbol"] == "MSFT"
    assert rows[0]["rejection_reason"] == "recent_negative_return"


def test_duplicate_run_no_duplicate_ghosts(tmp_path: Path) -> None:
    """Running twice with same universe does not duplicate ghost records."""
    ghost_path = tmp_path / "ghost.csv"
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-05-20"]),
        "symbol": ["REJ"],
        "close": [100.0],
        "selected": [False],
        "ret_5d": [-0.01],
        "close_above_ma50": [1],
    })
    gates = [("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return")]
    count1 = record_observation_rejections(df, Path("/tmp"), "test", "swing", gates, ghost_path=ghost_path)
    count2 = record_observation_rejections(df, Path("/tmp"), "test", "swing", gates, ghost_path=ghost_path)
    assert count1 == 1
    assert count2 == 0
    rows = load_ghost_ledger(ghost_path)
    assert len(rows) == 1


def test_all_selected_rows_no_ghosts(tmp_path: Path) -> None:
    """All-selected universe creates zero ghost records."""
    ghost_path = tmp_path / "ghost.csv"
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-05-20"]),
        "symbol": ["WIN"],
        "close": [100.0],
        "selected": [True],
        "ret_5d": [0.05],
        "close_above_ma50": [1],
    })
    gates = [("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return")]
    count = record_observation_rejections(df, Path("/tmp"), "test", "swing", gates, ghost_path=ghost_path)
    assert count == 0


def test_empty_universe_no_ghosts(tmp_path: Path) -> None:
    """Empty DataFrame produces zero ghost records."""
    count = record_observation_rejections(pd.DataFrame(), Path("/tmp"), "test", "swing", [], ghost_path=tmp_path / "empty.csv")
    assert count == 0


def test_no_selected_column_no_ghosts(tmp_path: Path) -> None:
    """DataFrame without 'selected' column produces zero ghost records."""
    df = pd.DataFrame({"symbol": ["A"], "close": [100.0]})
    count = record_observation_rejections(df, Path("/tmp"), "test", "swing", [], ghost_path=tmp_path / "no_col.csv")
    assert count == 0


def test_multiple_rejection_reasons(tmp_path: Path) -> None:
    """Different rejection reasons are recorded per failed gate."""
    ghost_path = tmp_path / "ghost.csv"
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-05-20", "2026-05-20"]),
        "symbol": ["A", "B"],
        "close": [100.0, 200.0],
        "selected": [False, False],
        "ret_5d": [-0.01, 0.05],
        "close_above_ma50": [0, 0],
    })
    gates = [
        ("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return"),
        ("close_above_ma50", lambda v: v > 0.5, "close_above_ma50", "below_50ma"),
    ]
    count = record_observation_rejections(df, Path("/tmp"), "test", "swing", gates, ghost_path=ghost_path)
    assert count == 2
    rows = load_ghost_ledger(ghost_path)
    reasons = {r["symbol"]: r["rejection_reason"] for r in rows}
    assert reasons["A"] == "recent_negative_return"
    assert reasons["B"] == "below_50ma"


# ─── No fabricated outcomes ───


def test_no_fabricated_outcomes_on_ghost_records(tmp_path: Path) -> None:
    """Ghost records created via record_observation_rejections have empty outcome fields."""
    ghost_path = tmp_path / "ghost.csv"
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-05-20"]),
        "symbol": ["TEST"],
        "close": [100.0],
        "selected": [False],
        "ret_5d": [-0.01],
        "close_above_ma50": [1],
    })
    gates = [("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return")]
    record_observation_rejections(df, Path("/tmp"), "test", "swing", gates, ghost_path=ghost_path)
    rows = load_ghost_ledger(ghost_path)
    assert rows[0]["outcome_5d"] == ""
    assert rows[0]["outcome_10d"] == ""
    assert rows[0]["outcome_20d"] == ""
    assert rows[0]["outcome_30d"] == ""
    assert rows[0]["max_favorable_move"] == ""
    assert rows[0]["max_adverse_move"] == ""
    assert rows[0]["setup_broke"] == ""


def test_ghost_recording_does_not_modify_input(tmp_path: Path) -> None:
    """record_observation_rejections does not modify the input DataFrame."""
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-05-20"]),
        "symbol": ["TEST"],
        "close": [100.0],
        "selected": [True],
        "ret_5d": [0.05],
        "close_above_ma50": [1],
    })
    original = df.copy()
    gates = [("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return")]
    record_observation_rejections(df, Path("/tmp"), "test", "swing", gates, ghost_path=tmp_path / "ghost.csv")
    pd.testing.assert_frame_equal(df, original)


# ─── Gate priority ordering ───


def test_relative_strength_gate_order() -> None:
    """Relative strength gates fail in correct priority order."""
    gates = [
        ("ret_5d", lambda v: v > 0.0, "ret_5d_positive", "recent_negative_return"),
        ("close_above_ma50", lambda v: v > 0.5, "close_above_ma50", "below_50ma"),
        ("ret_20d_rank", lambda v: v >= 0.85, "ret_20d_rank", "20d_momentum_too_weak"),
        ("ret_60d_rank", lambda v: v >= 0.70, "ret_60d_rank", "60d_momentum_too_weak"),
    ]
    r1 = _resolve_first_failed_gate({"ret_5d": -0.01, "close_above_ma50": 1.0, "ret_20d_rank": 0.9, "ret_60d_rank": 0.8}, gates)
    assert r1 is not None and r1[0] == "ret_5d_positive"
    r2 = _resolve_first_failed_gate({"ret_5d": 0.05, "close_above_ma50": 0.0, "ret_20d_rank": 0.9, "ret_60d_rank": 0.8}, gates)
    assert r2 is not None and r2[0] == "close_above_ma50"
    r3 = _resolve_first_failed_gate({"ret_5d": 0.05, "close_above_ma50": 1.0, "ret_20d_rank": 0.5, "ret_60d_rank": 0.8}, gates)
    assert r3 is not None and r3[0] == "ret_20d_rank"
    r4 = _resolve_first_failed_gate({"ret_5d": 0.05, "close_above_ma50": 1.0, "ret_20d_rank": 0.9, "ret_60d_rank": 0.5}, gates)
    assert r4 is not None and r4[0] == "ret_60d_rank"


def test_capitulation_gate_order() -> None:
    """Capitulation gates fail in correct priority order."""
    gates = [
        ("ret_3d_z", lambda v: v <= -1.5, "ret_3d_z_threshold", "pullback_not_deep_enough"),
        ("volume_z_20", lambda v: v >= 1.0, "volume_z_20_threshold", "volume_not_elevated"),
        ("close_location", lambda v: v >= 0.50, "close_location_threshold", "close_too_low_in_range"),
        ("spy_drawdown_60d", lambda v: v <= -0.0146, "spy_drawdown_60d_threshold", "spy_not_in_drawdown"),
    ]
    r1 = _resolve_first_failed_gate({"ret_3d_z": -1.0, "volume_z_20": 2.0, "close_location": 0.7, "spy_drawdown_60d": -0.02}, gates)
    assert r1 is not None and r1[0] == "ret_3d_z_threshold"
    r2 = _resolve_first_failed_gate({"ret_3d_z": -2.0, "volume_z_20": 0.5, "close_location": 0.7, "spy_drawdown_60d": -0.02}, gates)
    assert r2 is not None and r2[0] == "volume_z_20_threshold"
    r3 = _resolve_first_failed_gate({"ret_3d_z": -2.0, "volume_z_20": 2.0, "close_location": 0.7, "spy_drawdown_60d": -0.02}, gates)
    assert r3 is None