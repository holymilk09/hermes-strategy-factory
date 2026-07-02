from __future__ import annotations

"""Drift Attribution Audit — attribute observation returns to market, sector, beta, or ticker.

Pure audit layer. Never modifies strategy behavior, thresholds, scoring, or ledgers.
Produces additive audit labels only.
"""

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


# ─── Labels ───────────────────────────────────────────────────

LABEL_INDEPENDENT_STRENGTH = "Independent Strength"
LABEL_INDEPENDENT_STRENGTH_SECTOR_PENDING = (
    "Independent Strength vs SPY/QQQ; sector verification pending"
)
LABEL_MARKET_HELPED_SETUP = "Market Helped Setup"
LABEL_SECTOR_DRIFT = "Sector Drift"
LABEL_BETA_DRIFT = "Beta Drift"
LABEL_TICKER_DRIFT = "Ticker Drift"
LABEL_NO_CONFIRMED_EDGE = "No Confirmed Edge"
LABEL_FAILED_EDGE = "Failed Edge"
LABEL_COMPOUNDING_RISK = "Compounding Risk"
LABEL_COST_FRAGILE = "Cost Fragile"
LABEL_INSUFFICIENT_DATA = "Insufficient Data"

ALL_LABELS = [
    LABEL_INDEPENDENT_STRENGTH,
    LABEL_INDEPENDENT_STRENGTH_SECTOR_PENDING,
    LABEL_MARKET_HELPED_SETUP,
    LABEL_SECTOR_DRIFT,
    LABEL_BETA_DRIFT,
    LABEL_TICKER_DRIFT,
    LABEL_NO_CONFIRMED_EDGE,
    LABEL_FAILED_EDGE,
    LABEL_COMPOUNDING_RISK,
    LABEL_COST_FRAGILE,
    LABEL_INSUFFICIENT_DATA,
]

# ─── Thresholds ───────────────────────────────────────────────

POSITIVE_RETURN_THRESHOLD = 0.0  # > 0 is positive
SECTOR_OUTPERFORM_THRESHOLD = 0.0  # stock must beat sector by at least this (percentage points)
BETA_DOMINANCE_THRESHOLD = 0.5  # stock beta correlation threshold for beta drift label
MARKET_RELATIVE_THRESHOLD = 0.0  # how much stock beats market to not be "market helped"


# ─── Dataclasses ──────────────────────────────────────────────


@dataclass(frozen=True)
class DriftMetrics:
    """Per-observation drift attribution metrics."""

    observation_id: str
    symbol: str
    signal_timestamp: str
    stock_forward_return: float | None
    SPY_forward_return: float | None
    QQQ_forward_return: float | None
    sector_forward_return: float | None
    benchmark_relative_return: float | None
    sector_relative_return: float | None
    drift_attribution_label: str = LABEL_INSUFFICIENT_DATA
    missing_data_keys: list[str] = ()


@dataclass(frozen=True)
class BatchDriftReport:
    """Aggregate drift attribution report."""

    total_observations: int
    labeled_observations: int
    label_counts: dict[str, int]
    label_breakdown: list[DriftMetrics]


# ─── Sector ETF mapping (optional) ────────────────────────────

# Default sector ETF mapping for common symbols.
# Extend or override by passing a custom mapping.
DEFAULT_SECTOR_ETFS: dict[str, str] = {
    # Technology
    "AAPL": "QQQ", "MSFT": "QQQ", "NVDA": "QQQ", "AMD": "QQQ",
    "CRM": "QQQ", "ADBE": "QQQ", "INTC": "QQQ", "CSCO": "QQQ",
    "ORCL": "QQQ", "IBM": "QQQ", "QCOM": "QQQ", "TXN": "QQQ",
    "MU": "QQQ", "AMAT": "QQQ", "KLAC": "QQQ", "LRCX": "QQQ",
    "NOW": "QQQ", "ADP": "QQQ", "FIS": "QQQ", "FISV": "QQQ",
    "ANSS": "QQQ", "CDNS": "QQQ", "SNPS": "QQQ", "NXPI": "QQQ",
    "MRVL": "QQQ", "WDAY": "QQQ", "DDOG": "QQQ", "CRWD": "QQQ",
    "MDB": "QQQ", "ZS": "QQQ", "PANW": "QQQ", "FTNT": "QQQ",
    "CHKP": "QQQ", "CYBR": "QQQ", "OKTA": "QQQ", "NET": "QQQ",
    "TEAM": "QQQ", "VRSN": "QQQ", "AKAM": "QQQ",
    # Consumer Discretionary
    "AMZN": "XLY", "TSLA": "XLY", "HD": "XLY", "MCD": "XLY",
    "NKE": "XLY", "SBUX": "XLY", "TGT": "XLY", "LOW": "XLY",
    "BKNG": "XLY", "MAR": "XLY", "HLT": "XLY", "DHI": "XLY",
    "LEN": "XLY", "CMG": "XLY", "YUM": "XLY", "DPZ": "XLY",
    "ABNB": "XLY", "RCL": "XLY", "CCL": "XLY", "NCLH": "XLY",
    # Consumer Staples
    "PG": "XLP", "KO": "XLP", "PEP": "XLP", "WMT": "XLP",
    "COST": "XLP", "PM": "XLP", "MO": "XLP", "CL": "XLP",
    "KMB": "XLP", "SYY": "XLP", "MDLZ": "XLP", "KHC": "XLP",
    "CAG": "XLP", "CPB": "XLP", "GIS": "XLP", "HRL": "XLP",
    "K": "XLP", "SJM": "XLP", "HSY": "XLP", "CLX": "XLP",
    # Health Care
    "JNJ": "XLV", "UNH": "XLV", "PFE": "XLV", "ABBV": "XLV",
    "MRK": "XLV", "ABT": "XLV", "TMO": "XLV", "DHR": "XLV",
    "BMY": "XLV", "LLY": "XLV", "AMGN": "XLV", "GILD": "XLV",
    "VRTX": "XLV", "REGN": "XLV", "ISRG": "XLV", "SYK": "XLV",
    "BSX": "XLV", "MDT": "XLV", "EW": "XLV", "ZBH": "XLV",
    "IDXX": "XLV", "DXCM": "XLV", "HOLX": "XLV", "WST": "XLV",
    "ALGN": "XLV", "STE": "XLV", "COO": "XLV",
    # Financials
    "JPM": "XLF", "BAC": "XLF", "WFC": "XLF", "C": "XLF",
    "GS": "XLF", "MS": "XLF", "V": "XLF", "MA": "XLF",
    "AXP": "XLF", "DFS": "XLF", "COF": "XLF", "USB": "XLF",
    "PNC": "XLF", "TFC": "XLF", "BK": "XLF", "STT": "XLF",
    "SCHW": "XLF", "BLK": "XLF", "MCO": "XLF", "SPGI": "XLF",
    "CME": "XLF", "ICE": "XLF", "MKTX": "XLF", "NDAQ": "XLF",
    # Energy
    "XOM": "XLE", "CVX": "XLE", "COP": "XLE", "EOG": "XLE",
    "OXY": "XLE", "SLB": "XLE", "HAL": "XLE", "BKR": "XLE",
    "PSX": "XLE", "VLO": "XLE", "MPC": "XLE", "DVN": "XLE",
    "HES": "XLE", "FANG": "XLE", "CTRA": "XLE", "MRO": "XLE",
    # Industrials
    "GE": "XLI", "CAT": "XLI", "BA": "XLI", "MMM": "XLI",
    "HON": "XLI", "UPS": "XLI", "FDX": "XLI", "RTX": "XLI",
    "LMT": "XLI", "GD": "XLI", "NOC": "XLI", "TXT": "XLI",
    "DE": "XLI", "CMI": "XLI", "EMR": "XLI", "ETN": "XLI",
    "ITW": "XLI", "ROK": "XLI", "IR": "XLI", "DOV": "XLI",
    "PH": "XLI", "PWR": "XLI", "CSX": "XLI", "NSC": "XLI",
    "UNP": "XLI", "JBHT": "XLI",
    # Materials
    "LIN": "XLB", "APD": "XLB", "ECL": "XLB", "SHW": "XLB",
    "NEM": "XLB", "FCX": "XLB", "DOW": "XLB", "DD": "XLB",
    "LYB": "XLB", "PPG": "XLB", "ALB": "XLB", "IFF": "XLB",
    "CF": "XLB", "MOS": "XLB", "FMC": "XLB",
    # Real Estate
    "PLD": "XLRE", "AMT": "XLRE", "CCI": "XLRE", "EQIX": "XLRE",
    "PSA": "XLRE", "O": "XLRE", "DLR": "XLRE", "WELL": "XLRE",
    "AVB": "XLRE", "EQR": "XLRE", "ESS": "XLRE", "MAA": "XLRE",
    "UDR": "XLRE", "CPT": "XLRE", "REG": "XLRE",
    # Utilities
    "NEE": "XLU", "DUK": "XLU", "SO": "XLU", "D": "XLU",
    "AEP": "XLU", "EXC": "XLU", "ED": "XLU", "SRE": "XLU",
    "PEG": "XLU", "XEL": "XLU", "EIX": "XLU", "WEC": "XLU",
    "ES": "XLU", "AWK": "XLU", "AES": "XLU",
    # Communication Services
    "GOOGL": "XLC", "GOOG": "XLC", "META": "XLC", "NFLX": "XLC",
    "DIS": "XLC", "CMCSA": "XLC", "CHTR": "XLC", "T": "XLC",
    "TMUS": "XLC", "VZ": "XLC", "EA": "XLC", "TTWO": "XLC",
    "ATVI": "XLC", "WBD": "XLC", "PARA": "XLC", "ROKU": "XLC",
    "SNAP": "XLC", "PINS": "XLC", "SPOT": "XLC", "LYV": "XLC",
    # ARK Innovation (for high-growth names not covered above)
    "SQ": "ARKK", "ROKU": "ARKK", "ZM": "ARKK", "PTON": "ARKK",
    "TDOC": "ARKK", "COIN": "ARKK", "HOOD": "ARKK",
    # Semiconductors (SMH)
    "NVDA": "SMH", "AMD": "SMH", "INTC": "SMH", "MU": "SMH",
    "QCOM": "SMH", "TXN": "SMH", "AMAT": "SMH", "KLAC": "SMH",
    "LRCX": "SMH", "MRVL": "SMH", "NXPI": "SMH",
    "MPWR": "SMH", "ON": "SMH", "SWKS": "SMH", "QRVO": "SMH",
    "MCHP": "SMH", "STM": "SMH", "ASML": "SMH",
    # Software (IGV)
    "MSFT": "IGV", "CRM": "IGV", "ADBE": "IGV", "NOW": "IGV",
    "DDOG": "IGV", "CRWD": "IGV", "MDB": "IGV", "ZS": "IGV",
    "PANW": "IGV", "FTNT": "IGV", "TEAM": "IGV", "WDAY": "IGV",
    "NET": "IGV", "OKTA": "IGV", "VRSN": "IGV", "AKAM": "IGV",
    "PATH": "IGV", "COUP": "IGV", "ESTC": "IGV", "DOCU": "IGV",
    "SMAR": "IGV", "NEWR": "IGV", "PCTY": "IGV", "PAYC": "IGV",
    "TTD": "IGV", "MKTX": "IGV",
}

# Persistent overwrite: NVDA maps to SMH (semis), not QQQ
# QQQ remains as the tech-heavy benchmark for reference
# SMH is the sector-specific ETF
DEFAULT_SECTOR_ETFS["NVDA"] = "SMH"
DEFAULT_SECTOR_ETFS["AMD"] = "SMH"

# Phase 7C: approved observation cohort sector mappings
#   AMD / MRVL / ARM → SMH (semiconductors)
#   CRWD / DDOG → IGV (software/cloud)
#   SEDG → TAN (solar/clean energy)
DEFAULT_SECTOR_ETFS["ARM"] = "SMH"
DEFAULT_SECTOR_ETFS["SEDG"] = "TAN"
DEFAULT_SECTOR_ETFS["ENPH"] = "TAN"
DEFAULT_SECTOR_ETFS["FSLR"] = "TAN"
DEFAULT_SECTOR_ETFS["RUN"] = "TAN"


# ─── Sector data freshness validation (Phase 7C) ──────────────


def validate_sector_freshness(
    root: Path,
    sector_etfs: list[str] | None = None,
    ohlcv_dir: Path = Path("data/cache/ohlcv_1d"),
    max_stale_calendar_days: int = 5,
    now: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Report freshness of each required sector ETF's OHLCV data.

    Returns {etf: {"exists": bool, "latest_date": str|None, "age_days":
    float|None, "fresh": bool}}. An ETF is fresh when its latest bar is
    within ``max_stale_calendar_days`` of ``now``. Missing files are
    reported as not fresh — never silently skipped.
    """
    if sector_etfs is None:
        sector_etfs = ["SMH", "IGV", "TAN"]
    if now is None:
        now = datetime.now().astimezone()

    out: dict[str, dict[str, Any]] = {}
    for etf in sector_etfs:
        path = root / ohlcv_dir / f"{etf}_1D.csv"
        rows = load_ohlcv_rows(path)
        if not rows:
            out[etf] = {"exists": path.exists(), "latest_date": None,
                        "age_days": None, "fresh": False}
            continue
        latest_dt = rows[-1]["dt"]
        age_days = (now - latest_dt).total_seconds() / 86400.0
        out[etf] = {
            "exists": True,
            "latest_date": latest_dt.isoformat(),
            "age_days": round(age_days, 2),
            "fresh": age_days <= max_stale_calendar_days,
        }
    return out


# ─── Helpers ──────────────────────────────────────────────────


def _parse_pct(s: str) -> float | None:
    """Parse percentage string to float."""
    if not s or s.strip() == "":
        return None
    try:
        return float(s.replace("%", "").replace("+", ""))
    except (ValueError, TypeError):
        return None


def _to_dt(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def load_ohlcv_rows(path: Path) -> list[dict[str, Any]]:
    """Load OHLCV CSV rows sorted by date."""
    if not path.exists():
        return []
    with path.open() as f:
        rows = list(csv.DictReader(f))
    out: list[dict[str, Any]] = []
    for r in rows:
        date_raw = r.get("date") or r.get("timestamp") or r.get("datetime") or r.get("time")
        if not date_raw:
            continue
        try:
            dt = _to_dt(date_raw)
        except Exception:
            continue
        try:
            close = float(r.get("close") or "nan")
        except Exception:
            close = float("nan")
        out.append({"dt": dt, "close": close})
    out.sort(key=lambda x: x["dt"])
    return out


def compute_forward_return(
    initial_price: float,
    future_rows: list[dict[str, Any]],
    bars: int,
) -> float | None:
    """Compute forward return over N bars."""
    if len(future_rows) < bars:
        return None
    px = future_rows[bars - 1]["close"]
    return (px / initial_price - 1.0) * 100.0


def _resolve_sector_etf(
    symbol: str,
    sector_etf_map: dict[str, str] | None,
) -> str | None:
    """Resolve sector ETF for a symbol, or fall back to None."""
    sym_upper = symbol.upper()
    if sector_etf_map and sym_upper in sector_etf_map:
        return sector_etf_map[sym_upper]
    if sym_upper in DEFAULT_SECTOR_ETFS:
        return DEFAULT_SECTOR_ETFS[sym_upper]
    return None


# ─── Core attribution logic ───────────────────────────────────


def classify_drift(
    stock_return: float | None,
    spy_return: float | None,
    qqq_return: float | None,
    sector_return: float | None,
    sector_expected: bool = False,
) -> str:
    """Classify a single observation's return into a drift label.

    Logic hierarchy (first match wins):

    1. If any required data is None → Insufficient Data
    2. If stock_return is None or effectively missing → Insufficient Data
    3. If stock_return <= 0 → Failed Edge (negative or flat)
    4. If stock_return > 0 but stock <= best of (SPY, QQQ) → Market Helped Setup
    5. If stock > sector (when sector available) → Independent Strength
    6. If sector available and stock > SPY but not > sector → Sector Drift
    7. If stock > SPY but not > QQQ → check if it's a tech name, if sector not avail → Beta Drift
    8. If stock > 0 and no benchmark beats it → Independent Strength

    Phase 7C overclaim guard: when ``sector_expected`` is True (a sector ETF
    mapping exists for the symbol) but ``sector_return`` is None (sector data
    missing or stale), the full "Independent Strength" label is NOT allowed.
    The conservative label "Independent Strength vs SPY/QQQ; sector
    verification pending" is used instead. When no sector mapping exists at
    all (sector_expected=False), the original behavior is preserved.
    """
    if stock_return is None:
        return LABEL_INSUFFICIENT_DATA

    if spy_return is None and qqq_return is None:
        # No benchmark data at all
        if stock_return > POSITIVE_RETURN_THRESHOLD:
            # Can't attribute without benchmarks — safe default
            return LABEL_NO_CONFIRMED_EDGE
        return LABEL_FAILED_EDGE

    # Compute best available benchmark return (max of SPY, QQQ)
    benchmark_vals = [v for v in [spy_return, qqq_return] if v is not None]
    best_benchmark = max(benchmark_vals) if benchmark_vals else None

    # Failed edge: stock return not positive
    if stock_return <= POSITIVE_RETURN_THRESHOLD:
        return LABEL_FAILED_EDGE

    # Tiny positive but below meaningful threshold
    if stock_return < 1.0 and stock_return > 0:
        worst_benchmark = min(benchmark_vals) if benchmark_vals else None
        if worst_benchmark is not None and stock_return <= worst_benchmark:
            return LABEL_MARKET_HELPED_SETUP
        if best_benchmark is not None and stock_return <= best_benchmark:
            return LABEL_NO_CONFIRMED_EDGE

    # Stock outperformed ALL available benchmarks — genuine edge
    if best_benchmark is not None and stock_return > best_benchmark:
        if sector_return is not None:
            if stock_return > sector_return:
                return LABEL_INDEPENDENT_STRENGTH
            else:
                return LABEL_SECTOR_DRIFT
        # Sector mapping exists but sector data is missing/stale —
        # do NOT allow full Independent Strength (Phase 7C overclaim guard)
        if sector_expected:
            return LABEL_INDEPENDENT_STRENGTH_SECTOR_PENDING
        # No sector mapping at all and outperformed all benchmarks
        return LABEL_INDEPENDENT_STRENGTH

    # Stock did not outperform best benchmark — check factor exposure
    # Beta Drift: stock beats SPY but not QQQ (tech beta), no sector available
    if qqq_return is not None and spy_return is not None:
        if stock_return > spy_return and stock_return <= qqq_return:
            return LABEL_BETA_DRIFT
        if stock_return > qqq_return and stock_return <= spy_return:
            return LABEL_BETA_DRIFT

    # Market Helped Setup: stock goes up only because market went up
    if best_benchmark is not None and stock_return <= best_benchmark:
        return LABEL_MARKET_HELPED_SETUP

    return LABEL_NO_CONFIRMED_EDGE


def compute_drift_attribution(
    observation: dict[str, str],
    stock_ohlcv_rows: list[dict[str, Any]],
    spy_ohlcv_rows: list[dict[str, Any]],
    qqq_ohlcv_rows: list[dict[str, Any]],
    sector_ohlcv_rows: list[dict[str, Any]] | None = None,
    sector_etf: str | None = None,
    outcome_window: int | None = None,
) -> DriftMetrics:
    """Compute drift attribution for a single observation.

    Pure function — never modifies observation.

    ``sector_etf`` marks that a sector mapping EXISTS for this symbol. If it
    is set but sector data is missing/stale (no usable forward return), the
    full Independent Strength label is downgraded to the conservative
    "sector verification pending" variant (Phase 7C overclaim guard).
    """
    obs_id = observation.get("observation_id", "")
    symbol = (observation.get("symbol") or "").upper()
    signal_ts = observation.get("signal_timestamp", "")

    if not signal_ts:
        return DriftMetrics(
            observation_id=obs_id, symbol=symbol,
            signal_timestamp=signal_ts,
            stock_forward_return=None,
            SPY_forward_return=None, QQQ_forward_return=None,
            sector_forward_return=None,
            benchmark_relative_return=None, sector_relative_return=None,
            drift_attribution_label=LABEL_INSUFFICIENT_DATA,
            missing_data_keys=["signal_timestamp"],
        )

    try:
        signal_dt = _to_dt(signal_ts)
    except Exception:
        return DriftMetrics(
            observation_id=obs_id, symbol=symbol,
            signal_timestamp=signal_ts,
            stock_forward_return=None,
            SPY_forward_return=None, QQQ_forward_return=None,
            sector_forward_return=None,
            benchmark_relative_return=None, sector_relative_return=None,
            drift_attribution_label=LABEL_INSUFFICIENT_DATA,
            missing_data_keys=["signal_timestamp_parse"],
        )

    try:
        initial_price = float(observation.get("signal_close") or 0.0)
    except (ValueError, TypeError):
        initial_price = 0.0

    if initial_price <= 0.0:
        return DriftMetrics(
            observation_id=obs_id, symbol=symbol,
            signal_timestamp=signal_ts,
            stock_forward_return=None,
            SPY_forward_return=None, QQQ_forward_return=None,
            sector_forward_return=None,
            benchmark_relative_return=None, sector_relative_return=None,
            drift_attribution_label=LABEL_INSUFFICIENT_DATA,
            missing_data_keys=["initial_price"],
        )

    # Resolve outcome window
    window = outcome_window
    if window is None:
        try:
            window = int(observation.get("outcome_window", "10"))
        except (ValueError, TypeError):
            window = 10

    # Compute forward returns
    def _forward_for(rows: list[dict[str, Any]], dt: datetime, bars: int) -> float | None:
        future = [r for r in rows if r["dt"] > dt]
        if len(future) < bars:
            return None
        px = future[0]["close"]  # entry price = first bar close after signal
        return compute_forward_return(px, future, bars)

    missing_keys: list[str] = []

    # Stock forward return
    stock_future = [r for r in stock_ohlcv_rows if r["dt"] > signal_dt]
    stock_entry = stock_future[0]["close"] if stock_future else None
    if stock_entry is not None:
        stock_ret = compute_forward_return(stock_entry, stock_future, window)
    else:
        stock_ret = None

    if stock_ohlcv_rows and (stock_entry is None or stock_ret is None):
        missing_keys.append("stock_price_data")

    # SPY forward return
    spy_future = [r for r in spy_ohlcv_rows if r["dt"] > signal_dt]
    spy_entry = spy_future[0]["close"] if spy_future else None
    spy_ret = compute_forward_return(spy_entry, spy_future, window) if spy_entry is not None else None
    if not spy_ohlcv_rows or spy_ret is None:
        missing_keys.append("SPY")

    # QQQ forward return
    qqq_future = [r for r in qqq_ohlcv_rows if r["dt"] > signal_dt]
    qqq_entry = qqq_future[0]["close"] if qqq_future else None
    qqq_ret = compute_forward_return(qqq_entry, qqq_future, window) if qqq_entry is not None else None
    if not qqq_ohlcv_rows or qqq_ret is None:
        missing_keys.append("QQQ")

    # Sector forward return
    sector_ret = None
    if sector_ohlcv_rows is not None and sector_ohlcv_rows:
        sector_future = [r for r in sector_ohlcv_rows if r["dt"] > signal_dt]
        sector_entry = sector_future[0]["close"] if sector_future else None
        sector_ret = compute_forward_return(sector_entry, sector_future, window) if sector_entry is not None else None

    # Track missing/stale sector data when a sector mapping exists
    sector_expected = sector_etf is not None
    if sector_expected and sector_ret is None:
        missing_keys.append(f"sector_etf:{sector_etf}")

    # Relative returns
    benchmark_vals = [v for v in [spy_ret, qqq_ret] if v is not None]
    best_benchmark = max(benchmark_vals) if benchmark_vals else None
    benchmark_relative = stock_ret - best_benchmark if (stock_ret is not None and best_benchmark is not None) else None
    sector_relative = stock_ret - sector_ret if (stock_ret is not None and sector_ret is not None) else None

    # Classify
    label = classify_drift(stock_ret, spy_ret, qqq_ret, sector_ret,
                           sector_expected=sector_expected)

    return DriftMetrics(
        observation_id=obs_id,
        symbol=symbol,
        signal_timestamp=signal_ts,
        stock_forward_return=stock_ret,
        SPY_forward_return=spy_ret,
        QQQ_forward_return=qqq_ret,
        sector_forward_return=sector_ret,
        benchmark_relative_return=benchmark_relative,
        sector_relative_return=sector_relative,
        drift_attribution_label=label,
        missing_data_keys=missing_keys,
    )


def compute_batch_drift(
    observations: list[dict[str, str]],
    root: Path,
    ohlcv_dir: Path = Path("data/cache/ohlcv_1d"),
    sector_etf_map: dict[str, str] | None = None,
    outcome_window: int | None = None,
) -> BatchDriftReport:
    """Compute drift attribution across all observations.

    Pure audit — never modifies observations or ledgers.
    """
    if not observations:
        return BatchDriftReport(
            total_observations=0,
            labeled_observations=0,
            label_counts={label: 0 for label in ALL_LABELS},
            label_breakdown=[],
        )

    # Preload benchmark data
    def _load(ticker: str) -> list[dict[str, Any]]:
        path = root / ohlcv_dir / f"{ticker}_1D.csv"
        return load_ohlcv_rows(path)

    spy_rows = _load("SPY")
    qqq_rows = _load("QQQ")

    label_counts: dict[str, int] = {label: 0 for label in ALL_LABELS}
    breakdown: list[DriftMetrics] = []

    for obs in observations:
        symbol = (obs.get("symbol") or "").upper()
        stock_path = root / ohlcv_dir / f"{symbol}_1D.csv"
        stock_rows = load_ohlcv_rows(stock_path)

        # Resolve sector ETF
        sector_etf = _resolve_sector_etf(symbol, sector_etf_map)
        sector_rows = _load(sector_etf) if sector_etf else None

        metrics = compute_drift_attribution(
            observation=obs,
            stock_ohlcv_rows=stock_rows,
            spy_ohlcv_rows=spy_rows,
            qqq_ohlcv_rows=qqq_rows,
            sector_ohlcv_rows=sector_rows,
            sector_etf=sector_etf,
            outcome_window=outcome_window,
        )

        label = metrics.drift_attribution_label
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts[label] = 1

        breakdown.append(metrics)

    labeled = sum(v for k, v in label_counts.items() if k != LABEL_INSUFFICIENT_DATA)

    return BatchDriftReport(
        total_observations=len(observations),
        labeled_observations=labeled,
        label_counts=label_counts,
        label_breakdown=breakdown,
    )


def drift_to_dict(metrics: DriftMetrics) -> dict[str, Any]:
    """Convert DriftMetrics to a JSON-serializable dict."""
    return {
        "observation_id": metrics.observation_id,
        "symbol": metrics.symbol,
        "signal_timestamp": metrics.signal_timestamp,
        "stock_forward_return": metrics.stock_forward_return,
        "SPY_forward_return": metrics.SPY_forward_return,
        "QQQ_forward_return": metrics.QQQ_forward_return,
        "sector_forward_return": metrics.sector_forward_return,
        "benchmark_relative_return": metrics.benchmark_relative_return,
        "sector_relative_return": metrics.sector_relative_return,
        "drift_attribution_label": metrics.drift_attribution_label,
        "missing_data_keys": list(metrics.missing_data_keys),
    }


def report_to_dict(report: BatchDriftReport) -> dict[str, Any]:
    """Convert BatchDriftReport to a JSON-serializable dict."""
    return {
        "total_observations": report.total_observations,
        "labeled_observations": report.labeled_observations,
        "label_counts": report.label_counts,
        "label_breakdown": [drift_to_dict(m) for m in report.label_breakdown],
    }