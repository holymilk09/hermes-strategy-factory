"""
Redundancy Analyzer — cluster features by correlation and select representatives.

Rules:
  1. Compute feature correlation matrix
  2. Group features with |correlation| >= 0.90
  3. For each cluster, select one representative
  4. Mark others as redundant but DO NOT DELETE
  5. Output redundancy report
"""
import numpy as np
from typing import Dict, List, Tuple


class RedundancyAnalyzer:
    """Detect and cluster redundant features."""

    def __init__(self, threshold: float = 0.90):
        """
        threshold: absolute correlation above which features are considered redundant
        """
        self.threshold = threshold

    def analyze(
        self,
        feature_arrays: Dict[str, np.ndarray],  # {feature_name: values}
        feature_registry: dict = None,
    ) -> Dict:
        """
        Find redundant feature clusters.

        Returns dict with:
          - clusters: list of cluster dicts with representative + redundant features
          - n_redundant: total redundant features
          - n_representatives: number of unique clusters
          - correlation_matrix_note: "not stored; too large"
        """
        names = list(feature_arrays.keys())
        n = len(names)
        if n < 2:
            return {"clusters": [], "n_redundant": 0, "n_representatives": 0}

        # Align and compute correlation matrix
        max_len = max(len(arr) for arr in feature_arrays.values())
        matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                corr = self._aligned_correlation(
                    feature_arrays[names[i]],
                    feature_arrays[names[j]],
                )
                matrix[i, j] = corr
                matrix[j, i] = corr

        # Find clusters (greedy)
        visited = set()
        clusters = []
        cluster_id = 0

        for i in range(n):
            if i in visited:
                continue
            cluster = [i]
            for j in range(i + 1, n):
                if j in visited:
                    continue
                if abs(matrix[i, j]) >= self.threshold:
                    cluster.append(j)
                    visited.add(j)

            if len(cluster) > 1:
                visited.add(i)
                clusters.append(self._build_cluster(
                    cluster_id, cluster, names, feature_arrays
                ))
                cluster_id += 1

        n_redundant = sum(len(c["redundant_features"]) for c in clusters)

        return {
            "clusters": clusters,
            "n_redundant": n_redundant,
            "n_representatives": len(clusters),
            "total_features_analyzed": n,
        }

    def _aligned_correlation(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute correlation on aligned non-NaN indices."""
        n = min(len(a), len(b))
        x = a[:n]
        y = b[:n]
        mask = ~np.isnan(x) & ~np.isnan(y)
        if np.sum(mask) < 20:
            return 0.0
        xc = x[mask]
        yc = y[mask]
        return float(np.corrcoef(xc, yc)[0, 1])

    def _build_cluster(
        self,
        cluster_id: int,
        indices: List[int],
        names: List[str],
        arrays: Dict[str, np.ndarray],
    ) -> dict:
        """Build cluster: pick representative, list redundant, assign theme."""
        cluster_names = [names[i] for i in indices]

        # Representative: feature with highest variance (most informative)
        best_name = cluster_names[0]
        best_var = 0
        for name in cluster_names:
            arr = arrays[name]
            clean = arr[~np.isnan(arr)]
            if len(clean) > 0:
                var = float(np.var(clean))
                if var > best_var:
                    best_var = var
                    best_name = name

        # Theme: extract common root from feature names
        theme = self._infer_theme(cluster_names)

        redundant = [n for n in cluster_names if n != best_name]

        return {
            "cluster_id": f"cluster_{theme}_{str(cluster_id).zfill(3)}",
            "theme": theme,
            "representative_feature": best_name,
            "redundant_features": redundant,
            "cluster_size": len(cluster_names),
            "reason": "correlation_above_0.90",
        }

    def _infer_theme(self, names: List[str]) -> str:
        """Infer a theme from shared feature name components."""
        # Simple: extract shared prefix/suffix
        parts = [n.split('_') for n in names]
        common_prefix = []
        for i in range(min(len(p) for p in parts)):
            vals = set(p[i] for p in parts)
            if len(vals) == 1:
                common_prefix.append(list(vals)[0])
            else:
                break
        if common_prefix:
            return '_'.join(common_prefix)
        return "general"
