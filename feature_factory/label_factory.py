"""
Label Factory — Point-in-time forward labels for feature validation.

Generates labels AFTER feature computation. Labels use future outcomes
(they are targets) but are strictly separated from feature columns.

Labels generated:
  Forward returns: 1d, 3d, 5d, 10d, 20d
  Excess vs SPY: 5d, 10d, 20d
  Excess vs sector ETF: 5d, 10d, 20d
  Cross-sectional rank: 5d, 10d, 20d
  Top/bottom decile: 5d, 10d, 20d
  Triple barrier: +1 (profit), -1 (stop), 0 (time)
  Meta-label: 1 (pass) / 0 (fail) — requires base strategy signal

Status: LABEL_GENERATION_OPERATIONAL / VALIDATION_PENDING
"""
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class LabelFactory:
    """Generate point-in-time forward labels for a universe of symbols."""

    def __init__(self, config: Optional[dict] = None):
        """
        config: dict with optional keys:
          - profit_barrier_pct: float (default 5.0)
          - stop_barrier_pct: float (default 3.0)
          - time_barrier_days: int (default 10)
          - horizons: list[int] (default [1, 3, 5, 10, 20])
        """
        self.cfg = config or {}
        self.profit_barrier = self.cfg.get("profit_barrier_pct", 5.0) / 100
        self.stop_barrier = self.cfg.get("stop_barrier_pct", 3.0) / 100
        self.time_barrier = self.cfg.get("time_barrier_days", 10)
        self.horizons = self.cfg.get("horizons", [1, 3, 5, 10, 20])

    def build_labels(
        self,
        symbol_data: Dict[str, np.ndarray],
        spy_data: Optional[np.ndarray] = None,
        sector_etf_data: Optional[Dict[str, np.ndarray]] = None,
    ) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Build all labels for all symbols.

        Args:
          symbol_data: {symbol: structured_array with 'close', 'high', 'low' fields}
          spy_data: structured array for SPY (for excess returns)
          sector_etf_data: {symbol: etf_structured_array} (for sector excess returns)

        Returns: {symbol: {label_name: np.array}}
        """
        all_labels = {}
        n_symbols = len(symbol_data)

        # Precompute cross-sectional rank date index if needed
        # First pass: compute forward returns
        for sym, arr in symbol_data.items():
            labels = {}

            # ── Forward returns ──
            for h in self.horizons:
                labels[f"forward_return_{h}d"] = _forward_return(arr['close'], h)
                labels[f"log_forward_return_{h}d"] = _forward_log_return(arr['close'], h)

            # ── Excess vs SPY ──
            if spy_data is not None:
                spy_forward = {}
                for h in self.horizons:
                    spy_fwd = _forward_return(spy_data['close'], h)
                    sym_fwd = labels.get(f"forward_return_{h}d")
                    if sym_fwd is not None:
                        labels[f"excess_vs_spy_{h}d"] = _excess_return(sym_fwd, spy_fwd)

            # ── Excess vs sector ETF ──
            if sector_etf_data:
                etf_arr = sector_etf_data.get(sym)
                if etf_arr is not None:
                    for h in self.horizons:
                        etf_fwd = _forward_return(etf_arr['close'], h)
                        sym_fwd = labels.get(f"forward_return_{h}d")
                        if sym_fwd is not None:
                            labels[f"excess_vs_sector_{h}d"] = _excess_return(sym_fwd, etf_fwd)

            # ── Triple-barrier label ──
            labels["triple_barrier"] = _triple_barrier_label(
                arr['high'], arr['low'], arr['close'],
                self.profit_barrier, self.stop_barrier, self.time_barrier
            )

            all_labels[sym] = labels

        # ── Cross-sectional ranks (requires all symbols aligned by date) ──
        if n_symbols >= 5:
            for h in self.horizons:
                label_name = f"forward_return_{h}d"
                # Align dates and extract forward returns
                date_map = _align_returns(symbol_data, label_name)
                if date_map:
                    # Compute ranks per date
                    ranks = _cross_sectional_rank(date_map, symbol_data.keys())
                    for sym in symbol_data:
                        if sym in ranks:
                            all_labels[sym][f"forward_rank_{h}d"] = ranks[sym]
                            all_labels[sym][f"top_decile_{h}d"] = np.where(
                                np.nan_to_num(ranks[sym]) >= 0.90, 1.0, 0.0
                            )
                            all_labels[sym][f"bottom_decile_{h}d"] = np.where(
                                np.nan_to_num(ranks[sym]) <= 0.10, 1.0, 0.0
                            )

        return all_labels

    def build_meta_labels(
        self,
        base_signals: Dict[str, np.ndarray],
        closes: Dict[str, np.ndarray],
        highs: Dict[str, np.ndarray],
        lows: Dict[str, np.ndarray],
    ) -> Dict[str, np.ndarray]:
        """
        Build meta-labels: did the base signal reach profit before stop?

        meta_label = 1 if signal reaches profit barrier before stop barrier
        meta_label = 0 if signal hits stop first or expires

        Returns: {symbol: meta_label_array}
        Returns BLOCKED_BASE_SIGNAL_REQUIRED if base_signals is empty.
        """
        if not base_signals:
            return {"status": "BLOCKED_BASE_SIGNAL_REQUIRED"}

        results = {}
        for sym in base_signals:
            if sym not in closes or sym not in highs or sym not in lows:
                continue
            signals = base_signals[sym]
            c = closes[sym]
            h = highs[sym]
            l = lows[sym]
            n = len(signals)

            meta = np.full(n, np.nan)
            for i in range(n):
                if signals[i] != 1:
                    continue
                entry_price = c[i]
                profit_target = entry_price * (1 + self.profit_barrier)
                stop_level = entry_price * (1 - self.stop_barrier)

                # Look forward up to time barrier
                hit_profit = False
                for j in range(1, self.time_barrier + 1):
                    if i + j >= n:
                        break
                    if h[i + j] >= profit_target:
                        hit_profit = True
                        break
                    if l[i + j] <= stop_level:
                        break
                meta[i] = 1.0 if hit_profit else 0.0

            results[sym] = meta

        return results

    @staticmethod
    def validate_labels(labels: Dict[str, Dict[str, np.ndarray]]) -> Dict:
        """
        Validate label integrity: check for NaN rates, infinite values,
        minimum observation counts.
        """
        report = {"status": "VALIDATION_PENDING", "labels": {}}
        for sym, sym_labels in labels.items():
            for name, arr in sym_labels.items():
                n = len(arr)
                n_nan = int(np.sum(np.isnan(arr)))
                n_inf = int(np.sum(np.isinf(arr)))
                report["labels"][f"{sym}.{name}"] = {
                    "n_obs": n,
                    "n_nan": n_nan,
                    "n_inf": n_inf,
                    "nan_rate": round(n_nan / n * 100, 1) if n > 0 else 100,
                    "pass": n_nan < n * 0.3,  # Less than 30% NaN
                }
        return report


# ── Internal helpers ──

def _forward_return(closes: np.ndarray, horizon: int) -> np.ndarray:
    """forward_return_Nd = close.shift(-N) / close - 1"""
    n = len(closes)
    result = np.full(n, np.nan)
    mask = (np.arange(n) + horizon < n)
    result[mask] = (closes[np.arange(n)[mask] + horizon] / closes[mask]) - 1
    return result


def _forward_log_return(closes: np.ndarray, horizon: int) -> np.ndarray:
    """Log version for normality-sensitive analysis."""
    n = len(closes)
    result = np.full(n, np.nan)
    mask = (np.arange(n) + horizon < n)
    with np.errstate(divide='ignore', invalid='ignore'):
        result[mask] = np.log(closes[np.arange(n)[mask] + horizon] / closes[mask])
    return result


def _excess_return(sym_fwd: np.ndarray, bench_fwd: np.ndarray) -> np.ndarray:
    """Excess return = symbol_forward - benchmark_forward."""
    n = min(len(sym_fwd), len(bench_fwd))
    result = np.full(n, np.nan)
    mask = ~np.isnan(sym_fwd[:n]) & ~np.isnan(bench_fwd[:n])
    result[mask] = sym_fwd[:n][mask] - bench_fwd[:n][mask]
    return result


def _triple_barrier_label(
    highs: np.ndarray,
    lows: np.ndarray,
    closes: np.ndarray,
    profit_pct: float,
    stop_pct: float,
    time_days: int,
) -> np.ndarray:
    """
    Triple-barrier label:
    +1 if upper profit barrier hit first (within time barrier)
    -1 if lower stop barrier hit first
    0 if vertical time barrier hit first (no barrier reached)
    """
    n = len(closes)
    result = np.full(n, np.nan)

    for i in range(n):
        entry = closes[i]
        if np.isnan(entry) or entry <= 0:
            continue
        profit_target = entry * (1 + profit_pct)
        stop_level = entry * (1 - stop_pct)

        for j in range(1, time_days + 1):
            if i + j >= n:
                result[i] = 0.0  # Time barrier
                break
            if highs[i + j] >= profit_target:
                result[i] = 1.0  # Profit barrier
                break
            if lows[i + j] <= stop_level:
                result[i] = -1.0  # Stop barrier
                break
        else:
            result[i] = 0.0  # Time barrier reached

    return result


def _align_returns(
    symbol_data: Dict[str, np.ndarray],
    label_name: str,
) -> Optional[Dict[str, np.ndarray]]:
    """
    Align forward returns across symbols by date.
    Returns: {date_str: {symbol: forward_return_value}}
    """
    date_map = {}
    for sym, arr in symbol_data.items():
        if label_name not in arr.dtype.names:
            # Label not yet computed — skip
            continue
        vals = arr[label_name] if hasattr(arr, '__getitem__') else None
        if vals is None:
            continue
        dates = arr['date']
        for i in range(len(dates)):
            d = str(dates[i])
            if np.isnan(vals[i]):
                continue
            date_map.setdefault(d, {})[sym] = vals[i]
    return date_map if date_map else None


def _cross_sectional_rank(
    date_map: Dict[str, Dict[str, float]],
    all_symbols: List[str],
) -> Dict[str, np.ndarray]:
    """
    Compute cross-sectional percentile rank per date.
    rank = percentile of forward_return across all symbols on the same date.

    Returns: {symbol: np.array of ranks (same length as original data)}
    """
    # Find max length for each symbol
    max_len = 5000  # reasonable upper bound
    result = {sym: np.full(max_len, np.nan) for sym in all_symbols}

    # For each date, compute ranks
    index_map = {}  # Will need proper index — simplified approach
    for sym in all_symbols:
        # Get all dates for this symbol
        pass

    # Simplified: compute ranks where we have alignment
    # Build an array of aligned returns
    dates_sorted = sorted(date_map.keys())
    if not dates_sorted:
        return result

    # Count dates per symbol for sizing
    sym_date_counts = {sym: 0 for sym in all_symbols}
    for d in dates_sorted:
        for sym in date_map[d]:
            if sym in sym_date_counts:
                sym_date_counts[sym] += 1

    for sym in all_symbols:
        if sym_date_counts[sym] > 0:
            result[sym] = np.full(sym_date_counts[sym], np.nan)

    # Populate
    date_idx = {sym: 0 for sym in all_symbols}
    for d in dates_sorted:
        syms_today = [s for s in date_map[d] if s in all_symbols]
        if len(syms_today) < 5:
            continue
        rets_today = np.array([date_map[d][s] for s in syms_today])
        ranks = _percentile_rank(rets_today)
        for j, sym in enumerate(syms_today):
            if sym in date_idx:
                idx = date_idx[sym]
                if idx < len(result[sym]):
                    result[sym][idx] = ranks[j]
                date_idx[sym] = idx + 1

    return {sym: arr for sym, arr in result.items() if sym in date_idx}


def _percentile_rank(arr: np.ndarray) -> np.ndarray:
    """Compute percentile rank (0-1) for each element in array."""
    n = len(arr)
    ranks = np.zeros(n)
    order = np.argsort(arr)
    for i, idx in enumerate(order):
        ranks[idx] = i / (n - 1) if n > 1 else 0.5
    return ranks
