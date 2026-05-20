# Multi-Strategy Systems, Pattern Recognition, and ICT/SMC + Volumetric

**Source**: Batch 3 — Strategy Encyclopedia, sections 07-12 and 09-10
**Core Rules**: (1) One strategy is fragile, a portfolio of weakly-correlated strategies is more robust — only if correlation is measured properly. (2) ICT/SMC = retail pattern language, not institutional microstructure. (3) No subjective chart pattern is testable until converted to coordinates, thresholds, and timestamps.

---

## Part A: Multi-Strategy Portfolio Systems (14 Concepts)

**Core Thesis**: Individual strategies fail idiosyncratically. A portfolio of uncorrelated (or negatively correlated) strategies reduces path dependency and drawdown severity — IF correlation is measured correctly and regime shifts are accounted for.

### Concept Cards

#### MSP-001: Ensemble Signal Model
- **What**: Combine signals from multiple independent strategies into a single composite score
- **Edge Source**: Statistical (diversification)
- **Data Required**: Signals from ≥ 3 uncorrelated strategies
- **Failure Mode**: Strategies that appear uncorrelated in-sample become correlated during stress (correlation → 1 during crises)
- **Test**: Walk-forward portfolio optimization with regime-stratified correlation testing
- **Professional Equivalent**: Multi-factor models; equivalent to combining alpha signals from independent sources

#### MSP-002: Strategy Stack Design
- **What**: Organize strategies by frequency, edge source, and capital allocation
- **Structure**: Layer 1 (high freq execution alpha) → Layer 2 (medium freq stat arb) → Layer 3 (low freq factor/trend)
- **Failure Mode**: Capital contention between strategies during drawdowns; over-allocation to recent winners

#### MSP-003: Strategy Correlation Matrix
- **What**: Measure pairwise strategy correlations across time windows and regimes
- **Key Rule**: Correlation must be measured on P&L, not on signals. Signal correlation ≠ P&L correlation.
- **Failure Mode**: Correlation estimates change dramatically during regime transitions; using global correlation misses this

#### MSP-004: Risk Budgeting Across Strategies
- **What**: Allocate capital/volatility budget across strategies based on risk contribution, not equal weight
- **Professional Equivalent**: Risk parity applied to strategy allocation; marginal risk contribution analysis
- **Failure Mode**: Risk budget models assume stable covariance — during stress, correlations converge to 1

#### MSP-005: Volatility-Targeted Strategy Pool
- **What**: Scale individual strategy positions to achieve target portfolio volatility
- **Failure Mode**: Vol targeting amplifies losses during trending markets (selling into declines to reduce vol)

#### MSP-006: Dynamic Strategy Weighting
- **What**: Adjust strategy capital allocation based on recent performance, regime fit, or capacity
- **Failure Mode**: Mean reversion in strategy performance is real — chasing recent winners underperforms equal weighting
- **Professional Equivalent**: Adaptive asset allocation; manager of managers approach

#### MSP-007: Regime-Switching Strategy Allocation
- **What**: Allocate capital to strategies based on identified market regime (trending, mean-reverting, high vol, low vol)
- **Data Required**: Regime detection system with leading indicators
- **Failure Mode**: Regime lag (detection happens after regime change); overfitting to historical regime definitions
- **Professional Equivalent**: Tactical asset allocation with regime overlay

#### MSP-008: Capital Ladder by Strategy
- **What**: Progressive capital allocation — start small, scale only after validation milestones passed
- **Failure Mode**: Slowly scaling into a losing strategy delays inevitable; no strategy deserves infinite patience

#### MSP-009: Champion-Challenger System
- **What**: Run current best strategy (champion) alongside experimental alternatives (challengers)
- **Professional Equivalent**: A/B testing for strategies; continuous improvement loop
- **Failure Mode**: Over-promoting challengers based on short lucky streaks

#### MSP-010: Strategy Retirement Policy
- **What**: Defined criteria for when to kill a strategy (max drawdown hit, Sharpe below threshold, edge decay confirmed)
- **Professional Equivalent**: Hedge fund strategy redemption / fund closure criteria
- **Failure Mode**: Killing strategies too early (regime-based underperformance, not edge decay); or too late (overconfidence)

#### MSP-011: Portfolio of Alphas
- **What**: Treat each strategy as an alpha source; combine at signal level, not trade level
- **Professional Equivalent**: Multi-strategy hedge fund structure (Two Sigma, D.E. Shaw style)
- **Failure Mode**: Alpha sources aren't independent in practice; cross-alpha contamination (one strategy's signal affects another's execution)

#### MSP-012: Multi-Asset Strategy Rotation
- **What**: Apply same strategy logic across different asset classes; rotate capital based on relative signal strength
- **Failure Mode**: Different asset classes have different microstructure — same parameters don't transfer

#### MSP-013: Hierarchical Risk Parity for Strategies
- **What**: Use HRP to allocate capital across strategies, clustering by correlation rather than using covariance matrix
- **Professional Equivalent**: Lopez de Prado's HRP applied to strategy allocation
- **Failure Mode**: Clustering instability during regime shifts

#### MSP-014: Drawdown-Based Strategy Throttling
- **What**: Reduce or pause strategy allocation when drawdown exceeds defined thresholds
- **Failure Mode**: Throttling at wrong time (mean-reverting drawdown, not broken edge); creates performance drag

---

## Part B: Pattern Recognition Library (12+ Patterns)

**Core Rule**: No subjective chart pattern is testable until converted into coordinates, thresholds, and timestamps.

### Chart Patterns (Quantified Definitions Required)

| Pattern ID | Pattern | Required Quantification |
|---|---|---|
| PAT-001 | Head and Shoulders | Must define: left shoulder peak timestamp + value, head peak timestamp + value, right shoulder, neckline slope and break threshold, volume confirmation |
| PAT-002 | Inverse H&S | Mirror of PAT-001 for bottoms |
| PAT-003 | Double Top | Two peaks within X% of each other, within Y bars; neckline break threshold defined |
| PAT-004 | Double Bottom | Mirror of double top |
| PAT-005 | Triangles | Converging high/lower highs + rising low/lower lows; convergence rate quantified |
| PAT-006 | Wedges | Both trendlines converging; slope relationship to prior trend quantified |
| PAT-007 | Flags/Pennants | Sharp impulse followed by consolidation; consolidation slope must be against trend |
| PAT-008 | Cup and Handle | U-shaped trough with defined depth, duration, handle breakout threshold |

### Candlestick Patterns (Already Algorithmic)

| Pattern | Testable Definition | Failure Mode |
|---|---|---|
| Doji | Open ≈ Close within threshold; body < body_threshold × range | Pattern occurs randomly in ~10% of candles |
| Hammer | Small body at top, long lower shadow ≥ N× body | No edge without support context |
| Engulfing | Body of candle N fully contains body of candle N-1 | Frequent; needs confluence with trend/volume |
| Morning/Evening Star | 3-candle pattern with specific body/shadow relationships | Subjective in practice; needs precise rule conversion |
| Shooting Star | Mirror of hammer at top | Same as hammer |

### Pattern Quantification Rules

**Schema for every pattern test**:
```
pattern_name, required_coordinates, time_window, volume_threshold,
breakout_threshold, false_positive_rate, expected_hold_period,
required_confluence_indicators, minimum_sample_size_for_validation
```

**Pattern Failure Modes**:
- Subjective recognition bias (humans see patterns in noise)
- Survivorship bias (looking at successful patterns, ignoring failed attempts)
- No volume confirmation (pattern without volume = weak signal)
- Pattern occurs frequently in random data (Sullivan/Timmermann/White bootstrap correction)

---

## Part C: ICT/SMC / Liquidity Sweep Strategies (16 Concepts)

**⚠️ RETAIL CLAIMS WARNING**: ICT/SMC concepts are retail pattern language. They are NOT automatically institutional microstructure. The academic bridge to market microstructure requires: timestamped level definition, predefined sweep rules, volume confirmation, spread/liquidity filter, order-flow confirmation, post-event return distribution, and false-breakout statistics. Cont, Kukanov & Stoikov (2014) demonstrate that short-horizon price changes are driven by order-flow imbalance, not by subjective pattern recognition.

### ICT/SMC → Testable Equivalence Map

| Retail Term | Testable Equivalent | Academic Bridge | ICT-001 Testability |
|---|---|---|---|
| Liquidity Sweep | Stop-driven breakout failure at recent high/low level | Cont-Kukanov-Stoikov: price impact of order-flow imbalance | Needs: predefined level + volume confirmation + false breakout statistics |
| Fair Value Gap | Fast displacement candle creating low-volume gap area | Market microstructure: liquidity void between trades | Needs: gap size quantified + fill probability + mean time to fill |
| Order Block | Prior impulse origin candle before directional move | Supply/demand zone; absorption at prior impulse level | Needs: defined candle properties + subsequent price action statistics |
| Break of Structure (BOS) | Higher high in uptrend / lower low in downtrend confirmed | Trend regime detection via rolling extrema | Needs: rolling window definition + confirmation lag |
| Change of Character (CHoCH) | First lower high in uptrend / higher low in downtrend | Trend reversal detection | Needs: prior trend definition + statistical confirmation |
| Breaker Block | Failed order block that broke structure then flips | Support/resistance flip after structural break | Needs: defined failure condition + retest statistics |
| Mitigation Block | Price return to origin level of move that created imbalance | Mean reversion to origin zone | Needs: origin definition + probability distribution |
| Stop Hunt | Liquidity-taking event near obvious levels | Order book dynamics at known stop cluster levels | Needs: level identification + order flow confirmation |
| Equal Highs/Equal Lows | Price level tested multiple times at same value | Obvious stop cluster hypothesis; mean number of touches before break | Needs: tolerance band + statistical significance of cluster |
| Premium/Discount Zones | Price above/below 50% of recent range | Statistical mean reversion zones | Needs: range definition + mean reversion probability |
| Optimal Trade Entry (OTE) | Retracement to 62-79% Fibonacci level | Fibonacci retracement statistics | Needs: empirical distribution of retracement levels |
| Killzone | Session/time-of-day liquidity effect (London/NY open) | Time-of-day volume/liquidity patterns | Needs: session definition + intraday volume analysis |
| Displacement Candle | Fast directional move candle with large body | Statistical outlier in candle size distribution | Needs: body size threshold + volume confirmation |
| Imbalance / Repricing | Low-volume gap that needs refilling | Order book imbalance → mean reversion | Needs: volume threshold + fill statistics |
| Liquidity Pool Mapping | Identifying clusters of stops or resting orders | Market depth analysis + known psychological levels | Needs: depth data + order clustering analysis |
| ICT → Microstructure Map | Full translation of all ICT concepts to testable microstructure equivalents | This document | See mapping above |

### ICT/SMC Failure Modes

| Failure | Consequence | Mitigation |
|---|---|---|
| Subjective level definition | Different traders identify different "order blocks" → untestable | Pre-define coordinate rules for every concept |
| Relabeling failure | When a sweep fails to reverse, it's relabeled as "stop run" post-hoc | Define falsification criteria BEFORE analysis |
| Pattern overfit | 16 concepts can be combined to fit any historical price action | Require out-of-sample validation with fixed rules |
| No academic anchor | Zero peer-reviewed evidence for any ICT concept as predictive signal | Ground every concept in microstructure equivalents |
| Volume blindness | ICT often ignores volume, which is critical for microstructure validation | Require volume confirmation for every ICT-derived signal |

---

## Part D: Volumetric / Order Flow Strategies (22 Concepts)

**Core Requirement**: These strategies require tick data, bid/ask data, L2 order book, market depth, trade aggressor side, session metadata, and volume profile history. OHLCV alone is insufficient.

### Volumetric Concepts

| Concept ID | Concept | Data Required | Professional Equivalent |
|---|---|---|---|
| VOL-001 | Footprint Chart Basics | Tick-level bid/ask, volume per price level | Order flow visualization; see Easley/O'Hara |
| VOL-002 | Volume Delta | Tick data with aggressor side | Net buying/selling pressure |
| VOL-003 | Cumulative Delta | Cumulative running sum of volume delta | Persistent order flow direction |
| VOL-004 | Bid/Ask Imbalance | L2 order book | OFI (Cont-Kukanov-Stoikov) |
| VOL-005 | Stacked Imbalance | Multiple consecutive bid/ask imbalance levels | Concentrated order flow at multiple levels |
| VOL-006 | Absorption | Large volume at level with no price movement | Hidden liquidity; limit order absorption |
| VOL-007 | Exhaustion | Declining volume despite continued price move | Liquidity depletion; reversal catalyst |
| VOL-008 | Initiative Buying/Selling | Aggressive market orders pushing price | Order flow initiation vs response |
| VOL-009 | Responsive Buying/Selling | Passive orders at levels absorbing flow | Limit order provision at value levels |
| VOL-010 | Volume Profile | Volume-by-price distribution over period | Market memory of traded levels |
| VOL-011 | Market Profile | Time-at-price distribution | Auction market theory; value area identification |
| VOL-012 | Point of Control (POC) | Price level with highest volume | Magnet effect; mean reversion target |
| VOL-013 | High Volume Nodes (HVN) | Price ranges with above-average volume | Support/resistance zones |
| VOL-014 | Low Volume Nodes (LVN) | Price ranges with below-average volume | Fast-move areas; liquidity voids |
| VOL-015 | Anchored VWAP | VWAP anchored to specific event/date | Institutional benchmark; execution evaluation |
| VOL-016 | Order Book Imbalance | (Bid volume - Ask volume) / (Bid + Ask volume) | Microstructure feature for short-horizon prediction |
| VOL-017 | Depth / Liquidity Wall | Large resting orders at specific levels | Absorption zones; resistance to price movement |
| VOL-018 | Time & Sales / Tape Reading | Tick-level trade prints with aggressor flag | Real-time order flow analysis |
| VOL-019 | Iceberg Detection | Repeated small fills at same level | Hidden liquidity detection |
| VOL-020 | Spoofing Warning | Large orders placed and quickly canceled | Manipulation detection; false liquidity signals |
| VOL-021 | Liquidity Void | Price gap with minimal volume traded | Fast move areas; risk of continued acceleration |

### Order Flow Data Quality Requirements

| Requirement | Why | Failure if Missing |
|---|---|---|
| Tick data accuracy | OFI calculations need precise tick sequencing | Wrong volume delta values |
| Bid/ask identification | Need aggressor side for delta calculation | Directional noise in order flow |
| Time synchronization | Order book changes must be temporally aligned | Misaligned imbalance calculations |
| Venue filtering | Different venues have different liquidity | Cross-venue noise contaminates signals |
| Corporate action adjustment | Adjusted prices needed for volume/profile | Volume profile misaligned after splits |

---

*Cross-linked: [[Schema-and-Taxonomy]], [[Professional-Equivalent-Map]], [[Feature-Engineering-Catalog]], [[Validation-Framework]], [[Failure-Mode-Catalog]], [[Indicator-Catalog]], [[Basic-Intermediate-Strategies]], [[Professional-Quant-Strategies]], [[AI-ML-Strategies]]*
