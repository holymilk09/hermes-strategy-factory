"""
Feature Factory Core — orchestrates the full feature pipeline.

Architecture:
  Ingestion → Cleaning → Feature Modules → Store → (Selection) → Backtest/Model

Point-in-time integrity: features computed using only data available at each timestamp.
No look-ahead bias. All config-driven via feature_config.yaml.
"""
import os
import json
import statistics
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np

from feature_factory.ingestion import fetch_ohlcv, build_price_df
from feature_factory.technical import compute_technical_features
from feature_factory.statistical import compute_statistical_features
from feature_factory.regime import compute_regime_features
from feature_factory.residual import compute_residual_features
from feature_factory.microstructure import compute_microstructure_features
from feature_factory.store import FeatureStore
from feature_factory.selection import rank_features


class FeatureFactory:
    """Main orchestrator for feature computation pipeline."""

    def __init__(self, config: dict):
        """
        config: loaded from feature_config.yaml or inline dict.
        Must include: universe, date_range, feature_categories, feature_store_path
        """
        self.cfg = config
        self.store = FeatureStore(config.get("feature_store_path", "/opt/data/feature_store"))
        self._metadata = {}  # feature_name → metadata dict

    def run(self, symbols: List[str], start_date: str, end_date: str) -> Dict:
        """
        Full pipeline: fetch → clean → compute → store → return.

        Returns dict: {symbol: {category: {feature_name: np.array}}}
        Also writes to feature store if enabled.
        """
        print(f"FeatureFactory: {len(symbols)} symbols, {start_date} to {end_date}")

        # ── Stage 1: Fetch and build DataFrames ──
        price_data = {}
        for sym in symbols:
            df = build_price_df(sym, start_date, end_date, self.cfg)
            if df is not None and len(df) > 0:
                price_data[sym] = df

        if not price_data:
            print("FeatureFactory: No price data loaded.")
            return {}

        print(f"FeatureFactory: Loaded {len(price_data)} symbols with data")

        # ── Stage 2: Compute features per symbol ──
        all_features = {}
        feature_config = self.cfg.get("feature_categories", {})

        for sym, df in price_data.items():
            symbol_features = {}

            if feature_config.get("technical", {}).get("enabled", True):
                symbol_features["technical"] = compute_technical_features(
                    df, feature_config.get("technical", {})
                )

            if feature_config.get("statistical", {}).get("enabled", True):
                symbol_features["statistical"] = compute_statistical_features(
                    df, feature_config.get("statistical", {})
                )

            if feature_config.get("regime", {}).get("enabled", True):
                symbol_features["regime"] = compute_regime_features(
                    df, feature_config.get("regime", {})
                )

            if feature_config.get("residual", {}).get("enabled", True):
                # Residual features need sector ETF data.
                # Fallback: sector ETF → SPY (market-only) → BLOCKED
                etf_ticker = self.cfg.get("sector_etf_map", {}).get(sym)
                etf_df = price_data.get(etf_ticker) if etf_ticker else None

                if etf_df is None:
                    # Try SPY as market-only residual fallback
                    spy_df = price_data.get("SPY")
                    if spy_df is None:
                        spy_df = price_data.get("spy")
                    if spy_df is not None:
                        symbol_features["residual"] = compute_residual_features(
                            df, spy_df, feature_config.get("residual", {}),
                            benchmark_type="market_only"
                        )
                    else:
                        # No benchmark — residual features will be all NaN
                        # Explicitly block rather than silently produce NaN
                        import numpy as np
                        n = len(df)
                        symbol_features["residual"] = {
                            "residual_z": np.full(n, np.nan),
                            "residual_beta": np.full(n, np.nan),
                            "residual_alpha": np.full(n, np.nan),
                            "cumulative_residual": np.full(n, np.nan),
                            "residual_half_life": np.full(n, np.nan),
                            "residual_r2": np.full(n, np.nan),
                            "residual_return": np.full(n, np.nan),
                        }
                        self._metadata[f"{sym}.residual.status"] = {
                            "symbol": sym, "category": "residual",
                            "name": "status", "version": "latest",
                            "n_values": 0, "n_nan": 0, "mean": None, "std": None,
                            "blocked_reason": "BLOCKED_RESIDUAL_NAN_RATE — no sector ETF or SPY data available",
                        }
                else:
                    symbol_features["residual"] = compute_residual_features(
                        df, etf_df, feature_config.get("residual", {}),
                        benchmark_type="sector"
                    )

            if feature_config.get("microstructure", {}).get("enabled", True):
                symbol_features["microstructure"] = compute_microstructure_features(
                    df, feature_config.get("microstructure", {})
                )

            all_features[sym] = symbol_features

        # ── Stage 3: Store (if enabled) ──
        if self.cfg.get("store_enabled", True):
            print("FeatureFactory: Writing to feature store...")
            self._store_features(all_features)

        # ── Stage 4: Build metadata catalog ──
        self._build_metadata(all_features)

        print(f"FeatureFactory: Complete. {self._count_features(all_features)} features computed.")
        return all_features

    def _store_features(self, all_features: Dict):
        """Write computed features to the feature store."""
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.store.write(all_features, version=version)

    def _build_metadata(self, all_features: Dict):
        """Build metadata for each feature."""
        for sym, cats in all_features.items():
            for cat_name, features in cats.items():
                for feat_name, values in features.items():
                    fqn = f"{cat_name}.{feat_name}"
                    self._metadata[fqn] = {
                        "symbol": sym,
                        "category": cat_name,
                        "name": feat_name,
                        "dtype": str(values.dtype) if hasattr(values, 'dtype') else 'unknown',
                        "n_values": len(values) if hasattr(values, '__len__') else 0,
                        "n_nan": int(np.sum(np.isnan(values.astype(np.float64)))) if hasattr(values, 'dtype') and values.dtype.kind in ('f', 'i') else 0,
                        "mean": float(np.nanmean(values.astype(np.float64))) if hasattr(values, 'dtype') and values.dtype.kind in ('f', 'i') and len(values) > 0 else None,
                        "std": float(np.nanstd(values.astype(np.float64))) if hasattr(values, 'dtype') and values.dtype.kind in ('f', 'i') and len(values) > 0 else None,
                    }

    def get_metadata(self) -> Dict:
        """Return current metadata catalog."""
        return self._metadata

    def get_feature_matrix(self, symbols: List[str], features: List[str] = None) -> Dict:
        """
        Build aligned feature matrix for model training.
        Returns {symbol: np.array of shape (n_timesteps, n_features)}
        """
        result = {}
        all_data = self.store.read(symbols, version="latest")
        for sym in symbols:
            if sym not in all_data:
                continue
            sym_data = all_data[sym]
            arrays = []
            feat_names = []
            for cat_name, cat_features in sym_data.items():
                for feat_name, values in cat_features.items():
                    fqn = f"{cat_name}.{feat_name}"
                    if features and fqn not in features:
                        continue
                    if isinstance(values, np.ndarray):
                        arrays.append(values.reshape(-1, 1))
                        feat_names.append(fqn)
            if arrays:
                result[sym] = {
                    "matrix": np.hstack(arrays),
                    "feature_names": feat_names,
                }
        return result

    def _count_features(self, all_features: Dict) -> int:
        total = 0
        for sym, cats in all_features.items():
            for cat_name, features in cats.items():
                total += len(features)
        return total

    def summary(self) -> str:
        """Print feature catalog summary."""
        cats = {}
        for fqn, meta in self._metadata.items():
            cat = meta["category"]
            cats.setdefault(cat, 0)
            cats[cat] += 1

        lines = [
            "Feature Factory — Catalog",
            f"Total features: {len(self._metadata)}",
        ]
        for cat, count in sorted(cats.items()):
            lines.append(f"  {cat}: {count} features")
        return "\n".join(lines)
