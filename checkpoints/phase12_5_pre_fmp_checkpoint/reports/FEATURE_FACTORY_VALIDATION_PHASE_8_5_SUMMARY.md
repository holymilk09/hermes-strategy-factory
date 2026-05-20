# Feature Factory Validation Phase 8.5 Complete — Filter Logic Integrity Audit

Status: AUDIT_COMPLETE / BUGS_FOUND_AND_CORRECTED / BACKTRADER_ALLOWED_FOR_QUALIFYING_VARIANTS

## Bugs Found
1. Phase 8 D8/D9 count inversion (259 vs 698) was a BUG — fresh audit shows D8_D10=838t > D9_D10=713t (correct subset order)
2. Phase 8 structural_mr rejection was a BUG — fresh audit shows D8_D10 pf=1.64 vs BASE=0.82 (strong improvement)
3. Phase 8 "84t/+8.4%" duplicate was a BUG — fresh audit shows different values for each strategy

## Corrected Results (Fresh Audit)

mean_reversion (BASE: pf=0.55, cash=$49.9k):
  D8_D10: 838t, pf=1.20, cash=$130.6k → PROVISIONAL_CANDIDATE
  D9_D10: 713t, pf=0.78, cash=$69.9k → WEAK_FILTER
  D10_ONLY: 517t, pf=0.78, cash=$77.0k → WEAK_FILTER
  AVOID_D1_D3: 921t, pf=0.68, cash=$61.3k → WEAK_FILTER

structural_mr (BASE: pf=0.82, cash=$72.4k):
  D8_D10: 547t, pf=1.64, cash=$201.2k → PROVISIONAL_CANDIDATE (strongest)
  AVOID_D1_D3: 767t, pf=1.22, cash=$135.4k → WEAK_FILTER
  D9_D10: 432t, pf=0.77, cash=$77.2k → WEAK_FILTER (worse than base)
  D10_ONLY: 272t, pf=0.67, cash=$78.7k → WEAK_FILTER (worse than base)

qullamaggie (BASE: pf=0.56, cash=$54.0k):
  AVOID_D1_D3: 836t, pf=0.72, cash=$68.6k → WEAK_FILTER
  D8_D10: 37t, pf=1.77 → SAMPLE_BLOCKED

## Decile Polarity: PASS
D1=most extended (rev=-1.59, raw=+1.59), D10=least extended (rev=+1.62, raw=-1.62)
Inversion correct. Filter labels are accurate.

## Nested Subsets: ALL PASS
D10_ONLY ⊆ D9_D10 ⊆ D8_D10 ⊆ BASE at signal level. Filter logic is correct.

## D8/D9 Count: RESOLVED
Signal level: D9_D10(5,634) < D8_D10(8,143) — correct subset
Execution level: D9_D10(713t) < D8_D10(838t) — correct ordering now
Phase 8 inversion was a bug. Fresh run shows proper behavior.

## Backtrader Gate
- decision: BACKTRADER_ALLOWED_FOR_QUALIFYING_VARIANTS
- allowed: mean_reversion/D8_D10, structural_mr/D8_D10
- blocked: qullamaggie, momentum_swing, ml_enhanced, factor_residual_mr
- production migration: BLOCKED
- live trading: BLOCKED

## Critical Note
BASE portfolios lose money across all strategies (pf 0.55-0.82). This means either:
- The signal logic or position management is flawed at the base level
- The 7-day time stop + 12.5% position sizing is not viable
- Filter comparisons (D8_D10 vs BASE) remain valid directionally but
  absolute returns are unreliable

Backtrader simulation must validate whether D8_D10 truly improves these strategies
with proper stop/exit/sizing/cost logic, not just the simplified position management
used in Phase 6-8.5.

No profitability claims. No live-readiness claims.
