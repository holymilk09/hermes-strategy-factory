# Quant Strategy Encyclopedia — Source Specification

**Source**: User-provided batch 3, pasted as text specification.
**Date**: 2026-05-17
**Core Thesis**: Normalize every strategy family into testable hypotheses with data requirements, failure modes, and validation gates. Not a strategy list — a strategy ontology + validation map.

## Core Rules
1. Every strategy is a hypothesis, not a money printer
2. No card may claim: Works, Profitable, Validated, High win rate, Institutional edge
3. Every card must state: what it claims to exploit, data needed, how to test, why it may fail, professional equivalent, related indicators/features
4. Indicator ≠ strategy. Indicator + hypothesis + execution + risk + validation = strategy
5. No subjective chart pattern is testable until converted into coordinates, thresholds, and timestamps
6. LLM output is not a trade — LLM output is input to validation
7. No ML strategy passes without beating: naive baseline, linear baseline, random signal, turnover-matched random
8. ICT/SMC = retail pattern language, not institutional microstructure (no academic anchor)

## Difficulty Ladder (10 levels)
| Level | Description |
|---|---|
| 1 | Basic discretionary / educational (buy-hold, DCA) |
| 2 | Rule-based technical (RSI, MACD, MA crossover) |
| 3 | Multi-factor technical (multi-timeframe trend, vol breakout) |
| 4 | Statistical / cross-sectional (pairs, stat arb, factor models) |
| 5 | ML-assisted (XGBoost, HMM, meta-labeling) |
| 6 | Portfolio of strategies (ensemble allocation) |
| 7 | Microstructure / execution alpha (OFI, market making) |
| 8 | Options volatility / relative value (VRP, gamma scalping) |
| 9 | Adaptive AI/ML research system |
| 10 | Institutional multi-strategy platform |

## Edge Source Taxonomy (10 edges)
behavioral, trend, mean_reversion, liquidity, volatility, carry, statistical, order_flow, structural, informational

## Strategy Card Schema (all fields required)
strategy_id, strategy_name, category, difficulty (level), edge_source[], asset_classes[], timeframes[], data_required[], entry_logic, exit_logic, position_sizing, risk_controls, indicators_used, features_used, validation_tests[], failure_modes[], professional_equivalent, paper_references[], implementation_notes, live_trading_risk, status (research_only|testable|code_template_ready|deprecated)

---

*Full spec text from user preserved in this file.*