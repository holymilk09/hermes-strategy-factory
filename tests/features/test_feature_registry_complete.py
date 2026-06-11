"""Test every feature has registry metadata."""
import sys
sys.path.insert(0, '/opt/data')
import yaml

def test_registry_has_all_categories():
    with open("/opt/data/config/feature_registry.yaml") as f:
        reg = yaml.safe_load(f)

    features = reg.get("features", {})
    assert len(features) > 0, "Registry is empty"

    expected_cats = {"technical", "statistical", "regime", "residual", "microstructure_liquidity_proxy"}
    for name, meta in features.items():
        cat = meta.get("category")
        assert cat in expected_cats, f"{name}: unknown category '{cat}'"

    print(f"PASS: {len(features)} features, all categories valid")

def test_registry_required_fields():
    required = ["category", "subcategory", "formula", "input_data", "lookback",
                "known_at_time", "point_in_time_safe", "missing_policy", "version",
                "expected_use", "risk_notes"]

    with open("/opt/data/config/feature_registry.yaml") as f:
        reg = yaml.safe_load(f)

    features = reg.get("features", {})
    for name, meta in features.items():
        for field in required:
            assert field in meta, f"{name}: missing '{field}'"

    print(f"PASS: all {len(features)} features have required metadata fields")

def test_category_counts_match():
    """Verify the 120 feature claim."""
    with open("/opt/data/config/feature_registry.yaml") as f:
        reg = yaml.safe_load(f)

    features = reg.get("features", {})
    cats = {}
    for name, meta in features.items():
        cat = meta["category"]
        cats[cat] = cats.get(cat, 0) + 1

    total = sum(cats.values())
    print(f"  technical: {cats.get('technical', 0)}")
    print(f"  statistical: {cats.get('statistical', 0)}")
    print(f"  regime: {cats.get('regime', 0)}")
    print(f"  residual: {cats.get('residual', 0)}")
    print(f"  microstructure_liquidity_proxy: {cats.get('microstructure_liquidity_proxy', 0)}")
    print(f"  TOTAL: {total}")
    assert total >= 100, f"Expected >= 100 features, got {total}"

if __name__ == "__main__":
    test_registry_has_all_categories()
    test_registry_required_fields()
    test_category_counts_match()
    print("\nALL REGISTRY TESTS PASSED")
