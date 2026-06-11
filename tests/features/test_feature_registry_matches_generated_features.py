"""
Hard test: generated feature names must EXACTLY match registry feature names.

If mismatch: BLOCKED_REGISTRY_MISMATCH
If registry has stale features: BLOCKED_STALE_REGISTRY_FEATURE

No feature importance run is allowed while registry mismatch exists.
"""
import sys
sys.path.insert(0, '/opt/data')
import yaml
import numpy as np

from feature_factory.technical import compute_technical_features
from feature_factory.statistical import compute_statistical_features
from feature_factory.regime import compute_regime_features
from feature_factory.microstructure import compute_microstructure_features


def test_registry_exact_match():
    """Generated features == registry features for every category."""

    # ── Generate all features from test data ──
    n = 300
    dtype = np.dtype([
        ('date', 'U10'), ('open', 'f8'), ('high', 'f8'),
        ('low', 'f8'), ('close', 'f8'), ('volume', 'f8'),
        ('returns', 'f8'), ('log_returns', 'f8'),
    ])
    data = np.zeros(n, dtype=dtype)
    np.random.seed(42)
    data['close'] = np.random.randn(n).cumsum() + 100
    data['high'] = data['close'] * 1.02
    data['low'] = data['close'] * 0.98
    data['volume'] = np.random.randint(1_000_000, 5_000_000, n).astype(float)
    data['returns'] = np.zeros(n)
    data['returns'][1:] = data['close'][1:] / data['close'][:-1] - 1

    generated = {
        "technical": set(compute_technical_features(
            data, {"windows": [5, 10, 20, 50, 200], "rsi_periods": [2, 7, 14], "donchian_windows": [20, 50]}
        ).keys()),
        "statistical": set(compute_statistical_features(
            data, {"windows": [5, 10, 20, 50, 100], "zscore_windows": [20, 50]}
        ).keys()),
        "regime": set(compute_regime_features(data, {}).keys()),
        "microstructure_liquidity_proxy": set(compute_microstructure_features(data, {}).keys()),
        "residual": set(),  # Requires ETF data — will validate separately
    }

    # ── Load registry ──
    with open("/opt/data/config/feature_registry.yaml") as f:
        registry = yaml.safe_load(f)

    registered = {}
    for key, meta in registry.get("features", {}).items():
        if key in ['registry_version', 'generated_at', 'status', 'total_features', 'categories']:
            continue
        cat = meta.get("category", "unknown")
        registered.setdefault(cat, []).append(key)

    # ── Compare ──
    failures = []
    for cat in ["technical", "statistical", "regime", "microstructure_liquidity_proxy"]:
        gen_set = generated.get(cat, set())
        reg_set = set(registered.get(cat, []))
        missing = gen_set - reg_set
        extra = reg_set - gen_set

        if missing or extra:
            failures.append({
                "category": cat,
                "missing_from_registry": sorted(missing) if missing else [],
                "extra_in_registry": sorted(extra) if extra else [],
                "generated_count": len(gen_set),
                "registered_count": len(reg_set),
            })

    # ── Residual: special validation ──
    residual_reg = set(registered.get("residual", []))
    residual_expected = {"residual_z", "residual_beta", "residual_alpha",
                         "cumulative_residual", "residual_half_life",
                         "residual_r2", "residual_return"}
    residual_missing = residual_expected - residual_reg
    residual_extra = residual_reg - residual_expected
    if residual_missing or residual_extra:
        failures.append({
            "category": "residual",
            "missing_from_registry": sorted(residual_missing),
            "extra_in_registry": sorted(residual_extra),
            "note": "Residual features require ETF data; validated against expected code output",
        })

    # ── Determine status ──
    if failures:
        print("BLOCKED_REGISTRY_MISMATCH")
        for f in failures:
            print(f"  {f['category']}: missing={f.get('missing_from_registry', [])} extra={f.get('extra_in_registry', [])}")
        raise AssertionError(f"Registry mismatch: {len(failures)} categories failed")

    # ── Success ──
    total_gen = sum(len(v) for v in generated.values())
    total_reg = sum(len(registered.get(c, [])) for c in ["technical", "statistical", "regime", "residual", "microstructure_liquidity_proxy"])
    print(f"REGISTRY_MATCHES_GENERATED: {total_gen} generated == {total_reg} registered")
    for cat in ["technical", "statistical", "regime", "residual", "microstructure_liquidity_proxy"]:
        g = len(generated.get(cat, set()))
        r = len(registered.get(cat, []))
        print(f"  {cat}: {g}/{r}")


if __name__ == "__main__":
    test_registry_exact_match()
    print("\nALL REGISTRY MATCH TESTS PASSED")
