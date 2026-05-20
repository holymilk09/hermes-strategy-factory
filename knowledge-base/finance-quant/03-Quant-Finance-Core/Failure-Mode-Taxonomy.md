# Failure Mode Taxonomy

**Source**: `algo_trading_implementation_library/00_core_bot_structure/failure_modes.md`

---

## Core Concept

Trading system failures cluster into **four categories**, each originating at a different layer of the [[Trading-System-Component-Architecture]] and requiring distinct detection and mitigation strategies:

### 1. Strategy Failure
- Edge exists only before transaction costs
- Edge exists only in one instrument
- Edge exists only in one market regime
- Parameter heatmap has a cliff (non-robust optimization)
- Returns depend on a few outlier trades
- High win rate but poor payoff ratio
- Unintentional short volatility exposure
- Unintentional long beta exposure

### 2. Data Failure
- Look-ahead leakage
- Survivorship bias
- Corporate actions mishandled
- Delisted names excluded
- Time zone mismatch
- Missing bars treated as zero movement
- Vendor data changed without versioning
- Features calculated on future-adjusted data

### 3. Backtest Failure
- Bar-close signal fills at same bar close
- No spread / slippage / partial fills
- No borrow, margin, fees, or funding cost
- Unrealistic liquidity assumptions
- No rejection path for invalid orders
- Parameter search reuses test set

### 4. Live Failure
- Broker order state diverges from internal state
- Duplicate order sent after retry
- API outage creates stale positions
- Kill switch fails or is not tested
- Latency changes execution quality
- Paper fills are unrealistic
- Position reconciliation is skipped

---

## Implications for Trading Systems

- **Layer-specific detection**: Strategy failures surface in the [[Core-Module-Contracts|Review Contract]] (run comparison, heatmaps, decay review). Data failures surface at the layer boundary (quality flags, timestamp validation). Backtest failures are caught by comparing paper vs. live slippage distributions. Live failures require continuous reconciliation (see [[Event-Loop-and-State-Machine|on_timer]]).
- **Cross-layer compounding**: Failures cascade. A data failure (e.g., missing bars) contaminates features, which corrupts signals, which produces bad portfolios, which execution faithfully implements. Detection must occur at the failure's origin layer, not downstream.
- **The "unintentional exposure" pattern**: Both "unintentional short vol" and "unintentional long beta" indicate the strategy's actual risk profile diverges from its stated profile. This requires [[Trading-System-Component-Architecture|Metrics Engine]] risk attribution, not just return tracking.
- **Paper-trading is not validation**: Paper fills fail to model partial fills, adverse selection, and latency — these are live failure modes that paper testing cannot detect.
- **Kill switch testing**: The fact that "kill switch fails or is not tested" is a listed failure mode implies that kill switches are often deployed but never exercised under stress.

---

## Potential Failure Modes and Critiques

- **Incomplete taxonomy**: The taxonomy omits infrastructure failures: disk full, memory exhaustion, network partition at the OS level, DNS failures, and clock drift (which silently breaks timestamp ordering).
- **No severity classification**: All failure modes are listed equally. A look-ahead leakage is catastrophic; a parameter heatmap cliff is a research risk. Without severity tiers, risk prioritization is impossible.
- **Missing mitigation mapping**: Each failure mode needs a corresponding control (e.g., look-ahead leakage → strict point-in-time feature snapshots per [[Core-Module-Contracts|Signal Contract]]). The source does not provide this mapping.
- **No detection frequency guidance**: How often should reconciliation run? How frequently should the review loop analyze strategy decay? The taxonomy lists what can fail but not how often to check for it.
- **Backtest failures are research-time**: Backtest failures should be caught before deployment, but the architecture places the review layer after live trading. The review layer needs a backtest-review mode.
- **Regime shift detection gap**: "Edge exists only in one market regime" implies regime labels exist ([[Trading-System-Component-Architecture|Feature Layer]]), but detecting *when* the market transitions between regimes is a harder unsolved problem not addressed by labeled taxonomy alone.

---

**Related**: [[Trading-System-Component-Architecture]] · [[Event-Loop-and-State-Machine]] · [[Core-Module-Contracts]]
