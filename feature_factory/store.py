"""
Feature Store — versioned storage of computed features with metadata catalog.

Supports: write, read (latest or by version), list versions, metadata query.
Storage: NPZ files (compressed numpy arrays) with JSON metadata sidecar.
"""
import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np


class FeatureStore:
    """Version-controlled feature storage."""

    def __init__(self, base_path: str = "/opt/data/feature_store"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        self._metadata_path = os.path.join(base_path, "metadata.json")
        self._metadata = self._load_metadata()

    def write(self, features: Dict, version: str = None):
        """
        Write features to store.

        features: {symbol: {category: {feature_name: np.array}}}
        version: timestamp string, defaults to now.
        """
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")

        version_dir = os.path.join(self.base_path, version)
        os.makedirs(version_dir, exist_ok=True)

        total_features = 0
        for symbol, categories in features.items():
            symbol_dir = os.path.join(version_dir, symbol)
            os.makedirs(symbol_dir, exist_ok=True)

            for cat_name, cat_features in categories.items():
                # Convert numpy arrays to a single NPZ
                arrays = {}
                for feat_name, values in cat_features.items():
                    if isinstance(values, np.ndarray):
                        arrays[feat_name] = values
                        # Track metadata
                        key = f"{symbol}.{cat_name}.{feat_name}"
                        self._metadata[key] = {
                            "symbol": symbol,
                            "category": cat_name,
                            "name": feat_name,
                            "version": version,
                            "n_values": len(values),
                        "n_nan": int(np.sum(np.isnan(values.astype(np.float64)))) if values.dtype.kind in ('f', 'i') else 0,
                        "mean": float(np.nanmean(values.astype(np.float64))) if values.dtype.kind in ('f', 'i') and len(values) > 0 else None,
                        "std": float(np.nanstd(values.astype(np.float64))) if values.dtype.kind in ('f', 'i') and len(values) > 0 else None,
                            "updated": version,
                        }
                        total_features += 1

                if arrays:
                    np.savez_compressed(
                        os.path.join(symbol_dir, f"{cat_name}.npz"),
                        **arrays
                    )

        # Update version manifest
        manifest = self._load_manifest()
        manifest.setdefault("versions", []).append(version)
        manifest["latest"] = version
        self._save_manifest(manifest)
        self._save_metadata()

        print(f"Feature Store: Wrote {total_features} features — version {version}")

    def read(self, symbols: List[str], version: str = "latest") -> Dict:
        """
        Read features from store.

        Returns: {symbol: {category: {feature_name: np.array}}}
        """
        if version == "latest":
            manifest = self._load_manifest()
            version = manifest.get("latest")
            if not version:
                return {}

        version_dir = os.path.join(self.base_path, version)
        if not os.path.exists(version_dir):
            print(f"Feature Store: Version {version} not found")
            return {}

        result = {}
        for symbol in symbols:
            symbol_dir = os.path.join(version_dir, symbol)
            if not os.path.exists(symbol_dir):
                continue

            symbol_features = {}
            for npz_file in glob.glob(os.path.join(symbol_dir, "*.npz")):
                cat_name = os.path.splitext(os.path.basename(npz_file))[0]
                data = np.load(npz_file, allow_pickle=True)
                cat_features = {}
                for key in data.files:
                    cat_features[key] = data[key]
                symbol_features[cat_name] = cat_features
                data.close()

            if symbol_features:
                result[symbol] = symbol_features

        return result

    def list_versions(self) -> List[str]:
        """Return all stored versions."""
        manifest = self._load_manifest()
        return manifest.get("versions", [])

    def get_feature_metadata(self, fqn: str = None) -> Dict:
        """Get metadata for a specific feature or all features."""
        if fqn:
            return self._metadata.get(fqn, {})
        return self._metadata

    def summary(self) -> str:
        """Human-readable summary of what's in the store."""
        manifest = self._load_manifest()
        versions = manifest.get("versions", [])
        latest = manifest.get("latest", "none")

        cats = {}
        for key, meta in self._metadata.items():
            cat = meta.get("category", "unknown")
            cats[cat] = cats.get(cat, 0) + 1

        lines = [
            "Feature Store — Summary",
            f"Versions: {len(versions)} (latest: {latest})",
            f"Total features: {len(self._metadata)}",
        ]
        for cat, count in sorted(cats.items()):
            lines.append(f"  {cat}: {count}")
        return "\n".join(lines)

    def _load_manifest(self) -> Dict:
        path = os.path.join(self.base_path, "manifest.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {}

    def _save_manifest(self, manifest: Dict):
        with open(os.path.join(self.base_path, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)

    def _load_metadata(self) -> Dict:
        if os.path.exists(self._metadata_path):
            with open(self._metadata_path) as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        with open(self._metadata_path, "w") as f:
            json.dump(self._metadata, f, indent=2)

    # ═══════════════════════════════════════════════════════════
    # Strategy Consumer API — Phase 8
    # Strategies must request features through these methods.
    # No strategy file should rebuild indicators inline.
    # ═══════════════════════════════════════════════════════════

    def get_features(
        self,
        symbol: str,
        timestamp: str,
        feature_names: List[str],
        version: str = "latest",
    ) -> Dict[str, float]:
        """
        Point-in-time feature lookup for a single timestamp.
        Used by live/paper trading strategies.

        Returns: {feature_name: value_at_timestamp}
        """
        data = self.read([symbol], version=version)
        if symbol not in data:
            return {}

        sym_data = data[symbol]
        result = {}

        for cat_name, cat_features in sym_data.items():
            for feat_name, values in cat_features.items():
                if feat_name not in feature_names:
                    continue
                # Find value at timestamp
                # This requires a date index — simplified: return latest
                arr = values
                clean = arr[~np.isnan(arr)]
                if len(clean) > 0:
                    result[feat_name] = float(clean[-1])

        return result

    def get_feature_matrix(
        self,
        symbols: List[str],
        feature_names: List[str],
        version: str = "latest",
    ) -> Dict[str, dict]:
        """
        Build aligned feature matrix for model training.

        Returns: {symbol: {"matrix": np.array (n_timesteps, n_features),
                           "feature_names": [str]}}
        """
        data = self.read(symbols, version=version)
        result = {}

        for sym in symbols:
            if sym not in data:
                continue

            sym_data = data[sym]
            arrays = []
            names = []
            first_len = None

            for cat_name, cat_features in sym_data.items():
                for feat_name, values in cat_features.items():
                    if feat_name not in feature_names:
                        continue
                    if not isinstance(values, np.ndarray):
                        continue
                    if values.dtype.kind not in ('f', 'i'):
                        continue

                    if first_len is None:
                        first_len = len(values)
                    elif len(values) != first_len:
                        continue  # Skip misaligned

                    arrays.append(values.reshape(-1, 1))
                    names.append(feat_name)

            if arrays:
                result[sym] = {
                    "matrix": np.hstack(arrays),
                    "feature_names": names,
                }

        return result

    def get_labels(
        self,
        labels_store: Dict[str, Dict[str, np.ndarray]],
        symbols: List[str],
        label_names: List[str],
    ) -> Dict[str, np.ndarray]:
        """
        Retrieve labels for model training.

        labels_store: {symbol: {label_name: np.array}}
        Returns: {symbol: np.array (n_timesteps, n_labels)}
        """
        result = {}
        for sym in symbols:
            if sym not in labels_store:
                continue
            sym_labels = labels_store[sym]
            arrays = []
            for name in label_names:
                if name in sym_labels:
                    arr = sym_labels[name]
                    if isinstance(arr, np.ndarray):
                        arrays.append(arr.reshape(-1, 1))

            if arrays:
                result[sym] = np.hstack(arrays)

        return result

    def get_metadata(
        self,
        feature_names: List[str] = None,
    ) -> Dict:
        """
        Query metadata for specific features.
        If feature_names is None, return all metadata.
        """
        if feature_names is None:
            return self._metadata

        result = {}
        for fqn, meta in self._metadata.items():
            name = meta.get("name", "")
            if name in feature_names:
                result[fqn] = meta
        return result
