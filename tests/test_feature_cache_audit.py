from pathlib import Path

import numpy as np
import pandas as pd

from src.data.feature_cache_audit import (
    audit_feature_cache,
    discover_feature_cache_files,
    find_phase12_builder_candidates,
    inspect_npz_feature_file,
    parse_timestamp_array,
)


def test_parse_timestamp_array_strings():
    arr = np.array(["2026-05-01", "2026-05-02"])
    parsed = parse_timestamp_array(arr)

    assert parsed.notna().sum() == 2
    assert parsed.max() == pd.Timestamp("2026-05-02", tz="UTC")


def test_discover_feature_cache_files(tmp_path: Path):
    cache_dir = tmp_path / "cache" / "phase12_etf_inclusive_features"
    cache_dir.mkdir(parents=True)

    np.savez(cache_dir / "AAPL.npz", timestamp=np.array(["2026-05-01"]), residual_z=np.array([1.0]))

    files = discover_feature_cache_files(tmp_path)

    assert len(files) == 1
    assert files[0].name == "AAPL.npz"


def test_inspect_npz_feature_file(tmp_path: Path):
    path = tmp_path / "AAPL.npz"

    np.savez(
        path,
        timestamp=np.array(["2026-05-01", "2026-05-02"]),
        residual_z=np.array([1.0, 2.0]),
    )

    result = inspect_npz_feature_file(path)

    assert result["status"] == "OK"
    assert result["row_count"] == 2
    assert result["latest_ts"].startswith("2026-05-02")


def test_audit_feature_cache_fresh(tmp_path: Path):
    cache_dir = tmp_path / "cache" / "phase12_etf_inclusive_features"
    cache_dir.mkdir(parents=True)

    np.savez(
        cache_dir / "AAPL.npz",
        timestamp=np.array(["2026-05-08", "2026-05-09"]),
        residual_z=np.array([1.0, 2.0]),
    )

    audit = audit_feature_cache(
        tmp_path,
        as_of=pd.Timestamp("2026-05-10", tz="UTC"),
    )

    assert audit["file_count"] == 1
    assert audit["fresh"] is True


def test_audit_feature_cache_stale(tmp_path: Path):
    cache_dir = tmp_path / "cache" / "phase12_etf_inclusive_features"
    cache_dir.mkdir(parents=True)

    np.savez(
        cache_dir / "AAPL.npz",
        timestamp=np.array(["2026-04-01"]),
        residual_z=np.array([1.0]),
    )

    audit = audit_feature_cache(
        tmp_path,
        as_of=pd.Timestamp("2026-05-10", tz="UTC"),
    )

    assert audit["fresh"] is False


def test_find_phase12_builder_candidates(tmp_path: Path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()

    path = scripts / "build_phase12_features.py"
    path.write_text(
        "np.savez_compressed('cache/phase12_etf_inclusive_features/AAPL.npz', residual_z=x)",
        encoding="utf-8",
    )

    hits = find_phase12_builder_candidates(tmp_path)

    assert len(hits) == 1
    assert hits[0]["score"] >= 2
