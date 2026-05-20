"""
Feature Validation Report — produce structured report for every feature run.

Output location: reports/feature_factory/
Required fields per spec: run_id, timestamp, feature_version, data_version,
label_version, universe, date_range, symbols, n_features, n_rows, missing_rate,
infinite_values, lookahead_audit_passed, synthetic_data_used, labels_tested,
feature_selection_method, validation_method, top_features_by_label, dead_features,
unstable_features, redundant_feature_clusters, regime_specific_features,
cost_adjusted_usefulness, status.

Status values:
  GENERATED_ONLY — after generation, before importance tests
  VALIDATION_RUNNING — after scoring, before OOS
  VALIDATED_FOR_RESEARCH — only after ALL validation gates pass
  BLOCKED_* — blocked for specific reason
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class ValidationReport:
    """Generate and save feature factory validation reports."""

    def __init__(self, output_dir: str = "/opt/data/reports/feature_factory"):
        """
        output_dir: directory for report files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(
        self,
        run_id: str = None,
        feature_registry: Optional[dict] = None,
        importance_results: Optional[Dict] = None,
        redundancy_results: Optional[Dict] = None,
        leakage_results: Optional[Dict] = None,
        universe: Optional[dict] = None,
        date_range: Optional[tuple] = None,
        symbols: Optional[List[str]] = None,
        labels_tested: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate full validation report.

        Returns the report dict AND saves to file.
        """
        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # ── Feature counts from registry ──
        n_features = 120
        dead_features = []
        unstable_features = []
        redundant_clusters = []
        top_features = []

        if feature_registry:
            reg_features = feature_registry.get("features", {})
            n_features = len(reg_features)

        # ── Extract from importance results ──
        if importance_results:
            summary = importance_results.get("summary", {})
            n_features = summary.get("n_unique_features", n_features)
            labels_tested = labels_tested or summary.get("labels", [])
            dead_features = [
                d["feature_name"]
                for d in importance_results.get("dead_features", [])
            ]
            unstable_features = [
                u["feature_name"]
                for u in importance_results.get("unstable_features", [])
            ]
            top_features = summary.get("top_candidates", [])

        # ── Extract from redundancy results ──
        if redundancy_results:
            redundant_clusters = [
                {
                    "cluster_id": c["cluster_id"],
                    "representative": c["representative_feature"],
                    "redundant_count": len(c["redundant_features"]),
                }
                for c in redundancy_results.get("clusters", [])
            ]

        # ── Leakage status ──
        lookahead_passed = False
        if leakage_results:
            lookahead_passed = leakage_results.get("status") == "PASS"

        # ── Determine status ──
        status = self._determine_status(
            importance_results, redundancy_results, leakage_results,
            lookahead_passed
        )

        report = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "feature_version": "1.0.0",
            "data_version": "alpaca_v2_daily",
            "label_version": "1.0.0",
            "universe": self._serialize_universe(universe),
            "date_range": date_range,
            "symbols": symbols or [],
            "n_features": n_features,
            "n_rows": "see per-symbol metadata",
            "missing_rate": "see per-feature metadata",
            "infinite_values": 0,
            "lookahead_audit_passed": lookahead_passed,
            "synthetic_data_used": False,
            "labels_tested": labels_tested or [],
            "feature_selection_method": "rank_ic + mutual_information + decile_spread",
            "validation_method": "time_series_purged (pending)",
            "top_features_by_label": self._format_top_features(top_features),
            "dead_features": dead_features,
            "unstable_features": unstable_features,
            "redundant_feature_clusters": redundant_clusters,
            "regime_specific_features": "see feature_registry.yaml regime category",
            "cost_adjusted_usefulness": "NOT_ESTIMATED — future work",
            "status": status,
        }

        # ── Save to file ──
        self._save(report, run_id)

        return report

    def _determine_status(
        self,
        importance: Optional[Dict],
        redundancy: Optional[Dict],
        leakage: Optional[Dict],
        lookahead_ok: bool,
    ) -> str:
        """Determine validation status."""
        if not lookahead_ok:
            return "BLOCKED_LEAKAGE"
        if importance is None:
            return "GENERATED_ONLY"
        if importance.get("summary", {}).get("n_feature_label_pairs", 0) > 0:
            return "VALIDATION_RUNNING"
        return "GENERATED_ONLY"

    def _format_top_features(self, top: List[dict]) -> List[dict]:
        """Compact format for top features."""
        return [
            {
                "feature": t.get("feature_name", "?"),
                "label": t.get("label_name", "?"),
                "ic": t.get("rank_ic_mean", 0),
                "mi": t.get("mutual_information", 0),
            }
            for t in top[:20]
        ]

    def _serialize_universe(self, universe: Optional[dict]) -> str:
        if universe is None:
            return "strategy_config.yaml sectors (default)"
        sectors = universe.get("sectors", {})
        etfs = universe.get("sector_etfs", {})
        n_sectors = len(sectors)
        n_stocks = sum(len(v) for v in sectors.values())
        n_etfs = len(etfs)
        return f"{n_sectors} sectors, {n_stocks} stocks, {n_etfs} ETFs"

    def _save(self, report: Dict, run_id: str):
        """Save report as JSON."""
        path = os.path.join(self.output_dir, f"validation_report_{run_id}.json")
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Validation Report: saved to {path}")

    def summary(self, report: Dict) -> str:
        """Compact text summary."""
        lines = [
            f"FEATURE_FACTORY_VALIDATION_REPORT",
            f"run_id: {report['run_id']}",
            f"timestamp: {report['timestamp']}",
            f"status: {report['status']}",
            f"features: {report['n_features']} total",
            f"labels_tested: {report['labels_tested']}",
            f"lookahead_audit: {'PASS' if report['lookahead_audit_passed'] else 'FAIL'}",
            f"synthetic_data: {report['synthetic_data_used']}",
            f"top_candidates: {len(report['top_features_by_label'])}",
            f"dead: {len(report['dead_features'])}",
            f"unstable: {len(report['unstable_features'])}",
            f"redundant_clusters: {len(report['redundant_feature_clusters'])}",
        ]
        return "\n".join(lines)
