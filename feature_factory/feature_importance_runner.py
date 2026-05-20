"""
Feature Importance Runner — Score each feature against each label.

Methods:
  - Rank IC (Spearman correlation between feature and forward return)
  - Mutual information
  - Decile spread (top decile forward return - bottom decile forward return)
  - Hit rate by feature bucket
  - Stability by year
  - Stability by regime

Status: VALIDATION_RUNNING — do not claim VALIDATED_FOR_RESEARCH yet.
"""
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

from feature_factory.selection import mutual_information


class FeatureImportanceRunner:
    """Score each feature against each label horizon."""

    def __init__(self, config: Optional[dict] = None):
        self.cfg = config or {}
        self.results: List[dict] = []

    def run(
        self,
        features: Dict[str, Dict[str, dict]],  # {symbol: {category: {feat_name: np.array}}}
        labels: Dict[str, Dict[str, np.ndarray]],  # {symbol: {label_name: np.array}}
        feature_registry: Optional[dict] = None,
    ) -> Dict:
        """
        Score all features against all labels.

        Returns dict with:
          - scored_features: list of {feature_name, label_name, ...metrics...}
          - dead_features: list
          - unstable_features: list
          - redundant_features: mark for redundancy analyzer
          - features_with_missing_data: list
          - summary: aggregate stats
        """
        all_scores = []
        dead_features = []
        missing_features = []
        labels_tested = set()

        # Flatten features per symbol
        for sym, cats in features.items():
            if sym not in labels:
                continue

            sym_labels = labels[sym]

            for cat_name, cat_features in cats.items():
                for feat_name, feat_arr in cat_features.items():
                    if not isinstance(feat_arr, np.ndarray):
                        continue

                    # Skip string features
                    if feat_arr.dtype.kind not in ('f', 'i'):
                        continue

                    for label_name, label_arr in sym_labels.items():
                        if not isinstance(label_arr, np.ndarray):
                            continue
                        if label_arr.dtype.kind not in ('f', 'i'):
                            continue

                        labels_tested.add(label_name)
                        score = self._score_feature_label(
                            feat_arr, label_arr, feat_name, label_name, sym
                        )
                        if score:
                            all_scores.append(score)
                            if score["status"] == "DEAD":
                                dead_features.append(score)
                            if score["status"] == "BLOCKED_MISSING_DATA":
                                missing_features.append(score)

        # Summary
        summary = {
            "n_feature_label_pairs": len(all_scores),
            "n_unique_features": len(set(s["feature_name"] for s in all_scores)),
            "n_labels_tested": len(labels_tested),
            "labels": sorted(labels_tested),
            "n_dead": len(dead_features),
            "n_missing": len(missing_features),
            "top_candidates": self._top_candidates(all_scores, n=20),
        }

        return {
            "scored_features": all_scores,
            "dead_features": dead_features,
            "unstable_features": self._find_unstable(all_scores),
            "features_with_missing_data": missing_features,
            "summary": summary,
            "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        }

    def _score_feature_label(
        self,
        feat: np.ndarray,
        label: np.ndarray,
        feat_name: str,
        label_name: str,
        symbol: str,
    ) -> Optional[dict]:
        """Score one feature-label pair."""
        # Align and clean
        n = min(len(feat), len(label))
        x = feat[:n]
        y = label[:n]
        mask = ~np.isnan(x) & ~np.isnan(y) & ~np.isinf(x) & ~np.isinf(y)

        x_clean = x[mask]
        y_clean = y[mask]

        n_obs = len(x_clean)
        if n_obs < 50:
            return None

        n_total = n
        missing_rate = 1.0 - (n_obs / n_total)
        inf_rate = float(np.sum(np.isinf(feat[:n]))) / n_total

        # Rank IC (Spearman)
        if n_obs >= 10:
            from scipy.stats import spearmanr as _spearmanr
            try:
                rank_ic_val, rank_ic_p = _spearmanr(x_clean, y_clean)
                rank_ic_val = rank_ic_val if not np.isnan(rank_ic_val) else 0.0
            except ImportError:
                rank_ic_val = _spearman_corr(x_clean, y_clean)
            except Exception:
                rank_ic_val = 0.0
        else:
            rank_ic_val = 0.0

        # Mutual information
        mi_val = mutual_information(x_clean, y_clean)

        # Decile spread
        decile_stats = self._decile_analysis(x_clean, y_clean)
        decile_spread = decile_stats.get("spread", 0.0)
        top_decile_ret = decile_stats.get("top_decile_mean", 0.0)
        bottom_decile_ret = decile_stats.get("bottom_decile_mean", 0.0)

        # Stability by year (if date info available)
        stability_year = self._stability_by_year(x, y, mask, n)

        # Status determination
        status = self._determine_status(
            rank_ic_val, mi_val, decile_spread, missing_rate, n_obs
        )

        return {
            "feature_name": feat_name,
            "label_name": label_name,
            "symbol": symbol,
            "n_obs": n_obs,
            "n_total": n_total,
            "missing_rate": round(missing_rate, 4),
            "inf_rate": round(inf_rate, 4),
            "rank_ic_mean": round(rank_ic_val, 4),
            "rank_ic_t_stat": round(rank_ic_val * np.sqrt(n_obs - 2) / np.sqrt(1 - rank_ic_val**2), 4) if abs(rank_ic_val) < 1 else 0,
            "mutual_information": round(mi_val, 6),
            "decile_spread_return": round(decile_spread, 6),
            "top_decile_forward_return": round(top_decile_ret, 6),
            "bottom_decile_forward_return": round(bottom_decile_ret, 6),
            "stability_by_year": stability_year,
            "stability_by_regime": "NOT_IMPLEMENTED",  # Requires regime feature integration
            "status": status,
        }

    def _decile_analysis(self, x: np.ndarray, y: np.ndarray) -> dict:
        """Forward return by feature decile."""
        n = len(x)
        if n < 100:
            return {"spread": 0.0}

        deciles = np.percentile(x, np.arange(0, 101, 10))
        decile_returns = []
        for i in range(10):
            mask = (x >= deciles[i]) & (x < deciles[i + 1]) if i < 9 else (x >= deciles[9])
            if np.sum(mask) > 0:
                decile_returns.append(np.nanmean(y[mask]))
            else:
                decile_returns.append(np.nan)

        top = decile_returns[-1] if len(decile_returns) >= 10 else 0
        bottom = decile_returns[0] if decile_returns else 0
        return {
            "spread": (top - bottom) if not np.isnan(top) and not np.isnan(bottom) else 0.0,
            "top_decile_mean": top if not np.isnan(top) else 0.0,
            "bottom_decile_mean": bottom if not np.isnan(bottom) else 0.0,
        }

    def _stability_by_year(self, x: np.ndarray, y: np.ndarray, mask: np.ndarray, n: int) -> Dict:
        """Check IC stability across year segments (approximate)."""
        if n < 500:
            return {"not_enough_data": True}

        segment_size = n // 3
        years = {}
        for seg in range(3):
            start = seg * segment_size
            end = min((seg + 1) * segment_size, n)
            seg_mask = mask[start:end]
            x_seg = x[start:end][seg_mask]
            y_seg = y[start:end][seg_mask]
            if len(x_seg) < 20:
                continue
            from scipy.stats import spearmanr
            try:
                ic, _ = spearmanr(x_seg, y_seg)
                years[f"segment_{seg}"] = round(ic, 4) if not np.isnan(ic) else None
            except:
                years[f"segment_{seg}"] = None

        return years

    def _determine_status(self, ic: float, mi: float, decile_spread: float,
                          missing_rate: float, n_obs: int) -> str:
        """Classify feature-label pair status."""
        if missing_rate > 0.5:
            return "BLOCKED_MISSING_DATA"
        if abs(ic) < 0.01 and mi < 0.001 and abs(decile_spread) < 0.001:
            return "DEAD"
        if abs(ic) < 0.02:
            return "WEAK"
        return "CANDIDATE"

    def _find_unstable(self, scored: List[dict]) -> List[dict]:
        """Identify features with unstable IC across time segments."""
        unstable = []
        for s in scored:
            stability = s.get("stability_by_year", {})
            ic_vals = [v for v in stability.values() if isinstance(v, (int, float))]
            if len(ic_vals) >= 2:
                ic_std = np.std(ic_vals)
                if ic_std > 0.05:  # High variance in IC = unstable
                    unstable.append(s)
        return unstable

    def _top_candidates(self, scored: List[dict], n: int = 20) -> List[dict]:
        """Return top N candidate features ranked by |IC|."""
        candidates = [s for s in scored if s["status"] in ("CANDIDATE", "WEAK")]
        candidates.sort(key=lambda x: abs(x["rank_ic_mean"]), reverse=True)
        return candidates[:n]


def _spearman_corr(x: np.ndarray, y: np.ndarray) -> float:
    """Pure numpy Spearman rank correlation (fallback when scipy unavailable)."""
    n = len(x)
    if n < 3:
        return 0.0
    # Rank
    x_rank = np.zeros(n)
    y_rank = np.zeros(n)
    for i, val in enumerate(x):
        x_rank[i] = np.sum(x < val) + 0.5 * (np.sum(x == val) - 1) + 1
    for i, val in enumerate(y):
        y_rank[i] = np.sum(y < val) + 0.5 * (np.sum(y == val) - 1) + 1
    # Normalize to [0,1]
    x_rank = x_rank / n
    y_rank = y_rank / n
    # Pearson on ranks
    mean_x = np.mean(x_rank)
    mean_y = np.mean(y_rank)
    num = np.sum((x_rank - mean_x) * (y_rank - mean_y))
    den = np.sqrt(np.sum((x_rank - mean_x)**2) * np.sum((y_rank - mean_y)**2))
    return num / den if den > 0 else 0.0
