"""Research record: forward-observation cohort summaries and hypothesis status.

Reads ledgers READ-ONLY (hash before and after; a read that changes the file is an
error). Never writes a ledger. Ledgers are not in git — they come from Matt's
hash-verified recovery bundle or the hypothesis scanner's own output.

Two ledgers, two unit conventions (the documented −6.66pp -> +23.30pp trap):

  frozen lineage   relative_strength_continuation_outcome_ledger*.csv
                   column outcome_return, FRACTION (0.0542 = +5.42%)
  hypothesis       momentum_ret5d_ma50_observations.csv (scanner output)
                   column outcome_return_pp, PERCENTAGE POINTS (5.42 = +5.42%)

Units are DECLARED per ledger spec and converted once, here. A unit sanity check
flags values implausible for the declared unit instead of guessing.
"""
from __future__ import annotations

import csv
import hashlib
import pathlib
import statistics
from dataclasses import asdict, dataclass, field
from datetime import date

NOT_LOADED = "NOT_LOADED"
LOADED = "LOADED"
UNIT_SUSPECT = "UNIT_SUSPECT"
MUTATED = "MUTATED_DURING_READ"

FRACTION = "fraction"
PP = "pp"


@dataclass(frozen=True)
class LedgerSpec:
    name: str
    return_col: str
    unit: str
    status_col: str = "outcome_status"
    resolved_value: str = "RESOLVED"
    date_cols: tuple[str, ...] = ("signal_date", "observation_date", "as_of_date", "date")
    excess_col: str | None = None
    lineage_note: str = ""


FROZEN_LINEAGE = LedgerSpec(
    "relative_strength_continuation_phase28a_weak_pass", "outcome_return", FRACTION,
    lineage_note=("Frozen lineage, watch-only since 2026-10-05. The matched-window audit found no "
                  "consistent filter lift; this is a forward observation record, not a validated strategy."))
HYPOTHESIS_V1 = LedgerSpec(
    "momentum_continuation_ret5d_ma50_v1", "outcome_return_pp", PP, excess_col="excess_vs_spy_pp",
    lineage_note="Preregistered 2026-10-05. Forward test only; no verdict until its sample target is met.")

# Known canonical state (HANDOFF_NEXT_OPERATOR.md §1-2). A file with this hash must
# reproduce these numbers or the record is reported as a reconciliation failure.
CANONICAL = {
    "9320d53cad242a2c155ef356289d8d77cc5b9b627b635db32bb89a9fcd2dddd7":
        {"n_resolved": 13, "mean_pp": 11.4930, "hit_rate": 0.6154},
}

CAVEATS = (
    "Forward observations, not portfolio returns: overlapping holding periods are not netted.",
    "Raw close-to-close returns over 10 completed sessions after the signal (signal bar excluded).",
    "Cost (-0.15pp) and delay (-0.05pp) adjustments are flat reporting deductions, not a simulation.",
    "Sample size is shown on every figure; small samples are not evidence of an edge.",
)


@dataclass(frozen=True)
class CohortStats:
    signal_date: str
    n: int
    mean_pp: float
    median_pp: float
    hit_rate: float


@dataclass(frozen=True)
class RecordSummary:
    ledger: str
    status: str
    path: str = ""
    sha256: str = ""
    n_rows: int = 0
    n_resolved: int = 0
    n_pending: int = 0
    mean_pp: float | None = None
    median_pp: float | None = None
    hit_rate: float | None = None
    mean_cost_adj_pp: float | None = None
    mean_excess_pp: float | None = None
    cohorts: tuple[CohortStats, ...] = ()
    date_col: str = ""
    unit: str = ""
    canonical_check: str = "not applicable"
    notes: tuple[str, ...] = ()
    caveats: tuple[str, ...] = CAVEATS
    evidence: str = "COMPUTED — from ledger file (read-only, hashed before/after)"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["cohorts"] = [asdict(c) for c in self.cohorts]
        return d


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _to_pp(v: float, unit: str) -> float:
    return v * 100.0 if unit == FRACTION else v


def summarize(path: str | pathlib.Path | None, spec: LedgerSpec) -> RecordSummary:
    if path is None or not pathlib.Path(path).exists():
        return RecordSummary(spec.name, NOT_LOADED, str(path or ""),
                             notes=("Ledger not available in this environment. Supply the hash-verified "
                                    "bundle file; nothing is reconstructed from memory or chat.",
                                    spec.lineage_note))
    p = pathlib.Path(path)
    before = _sha(p)
    with open(p, newline="") as f:
        rows = list(csv.DictReader(f))
    after = _sha(p)
    if before != after:
        return RecordSummary(spec.name, MUTATED, str(p), before, notes=("file changed during read — stop",))
    if not rows:
        return RecordSummary(spec.name, LOADED, str(p), before, notes=("empty ledger", spec.lineage_note))
    cols = rows[0].keys()
    date_col = next((c for c in spec.date_cols if c in cols), "")
    if spec.return_col not in cols or spec.status_col not in cols:
        return RecordSummary(spec.name, UNIT_SUSPECT, str(p), before, len(rows),
                             notes=(f"expected columns {spec.return_col!r}/{spec.status_col!r} not found: "
                                    f"{sorted(cols)}",))
    resolved = [r for r in rows if r[spec.status_col] == spec.resolved_value]
    vals = [_to_pp(float(r[spec.return_col]), spec.unit) for r in resolved]
    notes = [spec.lineage_note]
    status = LOADED
    if vals:
        raw = [float(r[spec.return_col]) for r in resolved]
        if spec.unit == FRACTION and max(abs(x) for x in raw) > 5:
            status = UNIT_SUSPECT
            notes.append("declared FRACTION but a value exceeds 500% — likely percentage points")
        if spec.unit == PP and len(raw) >= 5 and max(abs(x) for x in raw) < 1:
            status = UNIT_SUSPECT
            notes.append("declared PP but every value is under 1pp — likely fractions")

    def stats(xs):
        return (statistics.fmean(xs), statistics.median(xs), sum(1 for x in xs if x > 0) / len(xs))

    cohorts = []
    if date_col:
        by: dict[str, list[float]] = {}
        for r, v in zip(resolved, vals):
            by.setdefault(r[date_col][:10], []).append(v)
        for d in sorted(by):
            m, md, h = stats(by[d])
            cohorts.append(CohortStats(d, len(by[d]), round(m, 4), round(md, 4), round(h, 4)))
    mean = med = hit = cost = exc = None
    if vals:
        mean, med, hit = stats(vals)
        cost = mean - 0.15
        if spec.excess_col and spec.excess_col in cols:
            ex = [float(r[spec.excess_col]) for r in resolved if r[spec.excess_col] not in ("", None)]
            exc = statistics.fmean(ex) if ex else None
    canon = "not applicable"
    if before in CANONICAL:
        c = CANONICAL[before]
        ok = (len(vals) == c["n_resolved"] and mean is not None
              and abs(mean - c["mean_pp"]) < 5e-4 and abs(hit - c["hit_rate"]) < 5e-5)
        canon = "MATCHES canonical 2026-10-04 state" if ok else "MISMATCH vs canonical 2026-10-04 state — stop"
        if not ok:
            status = UNIT_SUSPECT
    return RecordSummary(
        spec.name, status, str(p), before, len(rows), len(resolved), len(rows) - len(resolved),
        None if mean is None else round(mean, 4), None if med is None else round(med, 4),
        None if hit is None else round(hit, 4), None if cost is None else round(cost, 4),
        None if exc is None else round(exc, 4), tuple(cohorts), date_col, spec.unit, canon, tuple(notes))


# --------------------------------------------------------------------------- hypothesis status

REGISTERED = date(2026, 10, 5)
DEADLINE = date(2027, 4, 5)  # "or 6 months elapse"
TARGET_N = 30
TARGET_DATES = 3

PENDING_SAMPLE = "PENDING — sample target not met"
SUCCESS = "SUCCESS — all preregistered success bars met"
KILL = "KILL — a preregistered kill bar was hit"
INCONCLUSIVE = "INCONCLUSIVE — target met, neither bar hit; needs Matt's explicit extension decision"
EXPIRED = "INCONCLUSIVE — 6-month window elapsed before target; needs Matt's explicit decision"


@dataclass(frozen=True)
class HypothesisStatus:
    hypothesis: str
    rule: str
    as_of: str
    verdict: str
    n_resolved: int
    n_pending: int
    distinct_signal_dates: int
    target: str
    success_bars: tuple[str, ...]
    kill_bars: tuple[str, ...]
    mean_excess_vs_spy_pp: float | None = None
    hit_rate: float | None = None
    selected_mean_pp: float | None = None
    rejected_mean_pp: float | None = None
    selected_ledger: str = NOT_LOADED
    rejected_ledger: str = NOT_LOADED
    notes: tuple[str, ...] = ()
    scan_setups_gated: bool = True


def hypothesis_status(selected_path, rejected_path, as_of: date) -> HypothesisStatus:
    sel = summarize(selected_path, HYPOTHESIS_V1)
    rej = summarize(rejected_path, HYPOTHESIS_V1)
    n, dates = sel.n_resolved, len(sel.cohorts)
    notes: list[str] = []
    verdict = PENDING_SAMPLE
    if sel.status == LOADED and n >= TARGET_N and dates >= TARGET_DATES:
        kill = ((sel.mean_excess_pp is not None and sel.mean_excess_pp < -2.0)
                or (sel.hit_rate is not None and sel.hit_rate < 0.45))
        success = (sel.mean_excess_pp is not None and sel.mean_excess_pp > 0
                   and sel.hit_rate is not None and sel.hit_rate >= 0.55
                   and rej.mean_pp is not None and sel.mean_pp is not None and sel.mean_pp > rej.mean_pp)
        if kill:
            verdict = KILL
        elif success:
            verdict = SUCCESS
        else:
            verdict = INCONCLUSIVE
        if rej.status != LOADED:
            notes.append("rejected-cohort ledger missing: the 'selected beats rejected' bar cannot be checked")
    elif as_of > DEADLINE:
        verdict = EXPIRED
    if sel.status != LOADED:
        notes.append("selected ledger not loaded — counts shown as 0, not as evidence of anything")
    notes.append("Completeness-failure kill bar (>10% of scans) is checked from scan logs, not ledgers; "
                 "not evaluated here.")
    return HypothesisStatus(
        HYPOTHESIS_V1.name, "ret_5d > 0 AND close > ma50 on a complete daily series",
        as_of.isoformat(), verdict, n, sel.n_pending, dates,
        f">= {TARGET_N} resolved selected across >= {TARGET_DATES} signal dates, or by {DEADLINE.isoformat()}",
        ("mean excess vs SPY > 0", "hit rate >= 55%", "selected mean > same-date rejected mean"),
        ("mean excess vs SPY < -2pp at n>=30", "hit rate < 45% at n>=30",
         "data-completeness failure in >10% of scans"),
        sel.mean_excess_pp, sel.hit_rate, sel.mean_pp, rej.mean_pp, sel.status, rej.status,
        tuple(notes), verdict != SUCCESS)
