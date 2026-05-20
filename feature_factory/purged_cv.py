"""
Purged / Embargo Cross-Validation — time-series split with label overlap prevention.

Forward labels overlap: forward_return_20d at day t and day t+5 share 15 days
of future window. Standard K-fold contaminates train/test.

This module implements:
  - Chronological splits (no random shuffle)
  - Purge window: remove training samples whose labels overlap test samples
  - Embargo window: after purge, add embargo gap
  - Label-horizon-aware: purge/embargo >= label horizon

Status: PURGED_CV_IMPLEMENTED — test must verify no overlap.
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class PurgedCV:
    """
    Time-series cross-validation with purging and embargo.

    Usage:
      cv = PurgedCV(n_splits=5, label_horizon=20)
      for train_idx, test_idx in cv.split(n_samples):
          X_train, y_train = X[train_idx], y[train_idx]
          X_test, y_test = X[test_idx], y[test_idx]
    """

    def __init__(
        self,
        n_splits: int = 5,
        label_horizon: int = 20,
        purge_window: Optional[int] = None,
        embargo_window: Optional[int] = None,
    ):
        """
        n_splits: number of chronological splits
        label_horizon: forward return horizon in bars (used for default purge/embargo)
        purge_window: override purge window (default: label_horizon)
        embargo_window: override embargo window (default: label_horizon)
        """
        self.n_splits = n_splits
        self.label_horizon = label_horizon
        self.purge_window = purge_window if purge_window is not None else label_horizon
        self.embargo_window = embargo_window if embargo_window is not None else label_horizon
        self.random_shuffle_used = False
        self.splits: List[Tuple[np.ndarray, np.ndarray]] = []

    def split(self, n_samples: int) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate purged/embargoed train/test splits.

        Args:
          n_samples: total number of chronological samples

        Returns:
          List of (train_indices, test_indices) tuples.
          Indices are chronological. Test sets are contiguous blocks.
        """
        if n_samples < self.n_splits * (self.purge_window + self.embargo_window + 10):
            raise ValueError(f"n_samples={n_samples} too small for {self.n_splits} splits")

        self.splits = []
        test_size = n_samples // (self.n_splits + 1)  # leave one for warmup

        for split_i in range(self.n_splits):
            # Test set: last block (most recent data)
            test_start = n_samples - (self.n_splits - split_i) * test_size
            test_end = min(n_samples, test_start + test_size)

            test_indices = np.arange(test_start, test_end)

            # Train set: everything before test_start, minus purge and embargo
            train_end_cutoff = test_start - self.purge_window - self.embargo_window
            if train_end_cutoff <= 0:
                # Not enough data for train — skip this split
                continue

            train_indices = np.arange(0, train_end_cutoff)

            # Purge: remove training samples whose labels overlap the test set
            # A training sample at index t with horizon H has label window [t+1, t+H]
            # It overlaps test if t+H > test_start
            overlap_mask = (train_indices + self.label_horizon) > test_start
            train_indices = train_indices[~overlap_mask]

            if len(train_indices) < 20 or len(test_indices) < 5:
                continue

            self.splits.append((train_indices, test_indices))

        return self.splits

    def verify_no_overlap(self) -> Dict:
        """
        Verify that no train-test label windows overlap.

        Returns dict with overlap check results.
        """
        if not self.splits:
            return {"status": "BLOCKED_SPLIT_OVERLAP", "reason": "no splits generated"}

        violations = []
        for i, (train_idx, test_idx) in enumerate(self.splits):
            for t_train in train_idx:
                train_label_end = t_train + self.label_horizon
                for t_test in test_idx:
                    test_label_end = t_test + self.label_horizon
                    # Overlap: train label window and test label window intersect
                    # Train covers [t_train+1, train_label_end]
                    # Test covers [t_test+1, test_label_end]
                    # Overlap if: max(train_start, test_start) <= min(train_end, test_end)
                    train_start = t_train + 1
                    test_start = t_test + 1
                    if max(train_start, test_start) <= min(train_label_end, test_label_end):
                        violations.append({
                            "split": i,
                            "train_sample": int(t_train),
                            "train_label_range": [int(train_start), int(train_label_end)],
                            "test_sample": int(t_test),
                            "test_label_range": [int(test_start), int(test_label_end)],
                            "overlap_length": int(min(train_label_end, test_label_end) - max(train_start, test_start) + 1),
                        })

        overlap_ok = len(violations) == 0
        return {
            "status": "PASS_NO_OVERLAP" if overlap_ok else "BLOCKED_SPLIT_OVERLAP",
            "n_violations": len(violations),
            "violations": violations[:10],
            "n_splits": len(self.splits),
        }

    def verify_chronological(self) -> Dict:
        """Verify all splits are in chronological order (train before test, no shuffle)."""
        if not self.splits:
            return {"status": "BLOCKED_NO_SPLITS"}

        violations = []
        for i, (train_idx, test_idx) in enumerate(self.splits):
            if len(train_idx) > 0 and len(test_idx) > 0:
                if np.max(train_idx) >= np.min(test_idx):
                    violations.append({
                        "split": i,
                        "max_train": int(np.max(train_idx)),
                        "min_test": int(np.min(test_idx)),
                    })

        chronological_ok = len(violations) == 0
        return {
            "status": "PASS_CHRONOLOGICAL" if chronological_ok else "BLOCKED_NON_CHRONOLOGICAL",
            "n_violations": len(violations),
            "random_shuffle_used": self.random_shuffle_used,
        }

    def generate_report(self) -> Dict:
        """Generate purged CV report dict."""
        overlap = self.verify_no_overlap()
        chronological = self.verify_chronological()

        overall = "PURGED_CV_AVAILABLE"
        if overlap["status"] != "PASS_NO_OVERLAP":
            overall = overlap["status"]
        elif chronological["status"] != "PASS_CHRONOLOGICAL":
            overall = chronological["status"]

        return {
            "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "split_method": "chronological_purged_embargoed",
            "n_splits": len(self.splits),
            "label_horizon": self.label_horizon,
            "purge_window": self.purge_window,
            "embargo_window": self.embargo_window,
            "overlap_check": overlap,
            "chronological_check": chronological,
            "random_shuffle_used": self.random_shuffle_used,
            "status": overall,
            "n_train_samples": [len(t) for t, _ in self.splits] if self.splits else [],
            "n_test_samples": [len(t) for _, t in self.splits] if self.splits else [],
        }

    @staticmethod
    def make_multi_horizon(
        n_samples: int,
        horizons: List[int],
        n_splits: int = 5,
    ) -> Dict[int, 'PurgedCV']:
        """
        Create PurgedCV instances for multiple label horizons.

        Returns: {horizon: PurgedCV_instance}
        """
        result = {}
        for h in horizons:
            cv = PurgedCV(
                n_splits=n_splits,
                label_horizon=h,
                purge_window=h,
                embargo_window=h,
            )
            cv.split(n_samples)
            result[h] = cv
        return result
