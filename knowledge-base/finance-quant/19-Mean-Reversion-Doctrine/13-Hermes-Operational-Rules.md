# Hermes Operational Rules — Mean Reversion

These are the rules Hermes uses when reasoning about, building, or evaluating any mean-reversion strategy.

## Prime Rule
Mean reversion is not "RSI low, buy" or "price high, short."

A valid mean-reversion setup requires:
1. An identifiable edge source
2. A valid fair-value anchor
3. A volatility-normalized deviation
4. Regime permission
5. Exhaustion or reclaim confirmation
6. Defined entry/stop/target/time stop
7. Cost/slippage/liquidity checks
8. Validation against baselines

## Edge Source Check
If no edge source is identified → mark: `NO_EDGE_SOURCE`

Valid sources: liquidity pressure, forced selling/buying, stop-run failure, VWAP/institutional execution distortion, factor residual dislocation, pair/relative-value spread dislocation, event overreaction, volatility overshoot, order-flow exhaustion.

## Fair-Value Anchor Check
Rule: Mean reversion should usually be RESIDUAL reversion, not raw price reversion.

If anchor is just "price vs MA" or "RSI level" → mark: `WEAK_ANCHOR`

## Deviation Check
Use volatility-normalized stretch. Do not trade because price "looks far."
If using fixed thresholds not normalized to vol → mark: `ARBITRARY_THRESHOLD`

## Confirmation Check
Stretch is NOT an entry. Entry requires exhaustion or failed continuation evidence.
If entering on stretch alone → mark: `NO_CONFIRMATION`

## Regime Check
MR is blocked in: crash, fresh repricing, confirmed breakdowns, earnings/fraud shocks, strong trend days.
If no regime gate → mark: `REGIME_UNFILTERED`

## Validation Check
Every MR strategy requires: random baseline, regime breakdown, cost/slippage stress, OOS test.
If skipped → mark: `UNVALIDATED`

## Forbidden Claims
Do NOT say: profitable, validated, safe, high confidence, ready to trade.
Allowed: candidate, blocked, research-only, setup detected, validation required, no trading conclusion.

## Current Engine Audit

| Check | Status | Mark |
|---|---|---|
| Edge source | Not defined | `NO_EDGE_SOURCE` |
| Fair-value anchor | Raw RSI | `WEAK_ANCHOR` |
| Deviation | RSI(2) < 10 fixed | `ARBITRARY_THRESHOLD` |
| Confirmation | None | `NO_CONFIRMATION` |
| Regime | SMA200 binary | `REGIME_UNFILTERED` (too slow) |
| Validation | IS/OOS done | Partial |

**Engine status: 5 of 6 checks flagged.** Fundamental redesign required.

## Cross-Links
- [[00-INDEX]] — full doctrine navigation
- [[18-Pattern-Situational-Alpha/00-doctrine/PATTERN_ALPHA_RULES]] — same discipline for pattern trading
- [[05-Risk-Portfolio-Execution/Overfit-Detection-Metrics]] — validation tools
