"""Test feature store API methods exist and are importable."""
import sys
sys.path.insert(0, '/opt/data')

def test_store_import():
    from feature_factory.store import FeatureStore
    store = FeatureStore("/tmp/test_feature_store_api")
    assert store is not None
    print("PASS: FeatureStore imports and initializes")

def test_store_api_methods_exist():
    from feature_factory.store import FeatureStore
    store = FeatureStore("/tmp/test_feature_store_api")
    methods = ["write", "read", "get_features", "get_feature_matrix",
               "get_labels", "get_metadata", "summary", "list_versions"]
    for m in methods:
        assert hasattr(store, m), f"Missing method: {m}"
    print(f"PASS: all {len(methods)} API methods present")

def test_label_factory_import():
    from feature_factory.label_factory import LabelFactory
    lf = LabelFactory()
    assert lf is not None
    print("PASS: LabelFactory imports")

def test_importance_runner_import():
    from feature_factory.feature_importance_runner import FeatureImportanceRunner
    fir = FeatureImportanceRunner()
    assert fir is not None
    print("PASS: FeatureImportanceRunner imports")

def test_redundancy_analyzer_import():
    from feature_factory.redundancy_analyzer import RedundancyAnalyzer
    ra = RedundancyAnalyzer()
    assert ra is not None
    print("PASS: RedundancyAnalyzer imports")

def test_leakage_audit_import():
    from feature_factory.leakage_audit import LeakageAudit
    la = LeakageAudit()
    assert la is not None
    print("PASS: LeakageAudit imports")

def test_validation_report_import():
    from feature_factory.feature_validation_report import ValidationReport
    vr = ValidationReport("/tmp/test_reports")
    assert vr is not None
    print("PASS: ValidationReport imports")

if __name__ == "__main__":
    test_store_import()
    test_store_api_methods_exist()
    test_label_factory_import()
    test_importance_runner_import()
    test_redundancy_analyzer_import()
    test_leakage_audit_import()
    test_validation_report_import()
    print("\nALL STORE API TESTS PASSED")
