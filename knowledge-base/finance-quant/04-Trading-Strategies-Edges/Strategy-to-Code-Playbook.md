# Strategy-to-Code Playbook

**Source**: Extracted and synthesized from implementation library documentation.

**Purpose**: Transform vague trading ideas into testable, falsifiable hypotheses with clear implementation paths.

---

## The Bad-to-Good Transformation

### Bad Form (Unusable):
> "RSI plus volume should work"

### Good Form (Testable Hypothesis):
> "When realized volatility is below its 60-day median and 20-day momentum is positive, pullbacks with short-term oversold readings have positive expected return over the next 5 sessions after costs."

---

## Required Hypothesis Fields

| Field | Purpose | Example |
|---|---|---|
| Asset Class | Define universe and liquidity filter | US equities, liquid top 500 by dollar volume |
| Horizon | Holding period | 5 trading days |
| Signal | Entry conditions | 20-day momentum + 3-day pullback |
| Regime Filter | When does signal activate? | Realized vol below 60-day median |
| Entry | Exact entry timing | Next bar after signal close |
| Exit | Exit conditions | 5 bars, stop, or signal invalidation |
| Costs | Commission + spread + slippage | Model explicitly |
| Falsification | How is the hypothesis proven wrong? | No positive OOS expectancy after costs |

---

## Implementation Conversion Sequence

1. **Write signal function** — independent of portfolio/execution
2. **Write feature function** — independent of signal
3. **Write sizing function** — independent of broker
4. **Write risk veto** — independent of alpha
5. **Write test fixtures** — for features, signal, sizing, and risk
6. **Run baseline** — with no optimization
7. **Run sensitivity map** — heatmap analysis
8. **Run OOS epoch** — walk-forward validation
9. **Write review** — before changing any parameters

---

## Anti-Cookie-Cutter Insight

The most common mistake is skipping step 1 (signal independence) and mixing signal logic with portfolio construction. This makes it impossible to tell whether a strategy fails because:
- The edge never existed, or
- The sizing/risk layer is destroying a good signal, or
- The execution layer is leaking too much alpha

**Rule**: Isolate each layer. Test each layer independently. Only then combine them.

---

*Cross-linked: [[Trading-System-Build-Doctrine]], [[Agentic-Workflow-Patterns]], [[Strategy-Backtest-Contracts]], [[Strategy-Weak-Point-Detection]]*
