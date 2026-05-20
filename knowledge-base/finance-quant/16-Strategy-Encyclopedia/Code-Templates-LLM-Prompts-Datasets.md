# Code Templates, LLM Prompts, and Datasets — Encyclopedia

**Source**: Batch 3 — Strategy Encyclopedia, sections 17-18-19-20
**Core Rules**: (1) LLM output is not a trade — it's input to validation, (2) Every prompt must convert raw ideas to testable rules, (3) Code templates enforce the 24-field strategy card schema.

---

## Part A: Strategy-to-Code Templates (8 Templates)

### CT-001: QuantConnect Alpha Model Template
```python
# Framework: QuantConnect Algorithm Framework
# Module: Alpha model (signal generation)
# Purpose: Convert strategy card → alpha signals
class {StrategyName}AlphaModel(AlphaModel):
    def __init__(self, config):
        self.config = config  # All parameters from strategy card
        self.edge_source = config["edge_source"]
        self.data_required = config["data_required"]
    
    def Update(self, algorithm, data):
        """Generate insight from strategy card rules"""
        # 1. Entry logic → signal condition
        # 2. Exit logic → close condition  
        # 3. Risk controls → veto condition
        # 4. Output: Insight object with direction, confidence, magnitude
```
**Required**: Strategy card with entry_logic, exit_logic, risk_controls, indicators_used
**Validation**: Test signal function independently from portfolio construction and execution

### CT-002: QuantConnect Risk Model Template
```python
class {StrategyName}RiskModel(RiskManagementModel):
    def ManageRisk(self, algorithm, targets):
        """Apply risk vetoes from strategy card"""
        # Max position size check
        # Max drawdown check
        # Kill switch check
        # Return: modified targets or None (veto)
```

### CT-003: VectorBT Strategy Template
```python
# Framework: vectorbt (vectorized backtesting)
# Purpose: Fast research and parameter sweeps
# WARNING: Cannot model production fills accurately
import vectorbt as vbt
# Entry condition vector → signals
# Exit condition vector → exits
# Portfolio.from_signals(signals, exits, ...)
# Feature: Rapid heatmap generation for parameter sweeps
```

### CT-004: Pandas Backtest Template
```python
# Framework: Pure pandas (custom backtesting)
# Purpose: Educational and simple strategy testing
# Not recommended for production
# Includes: OHLCV data loading, signal generation, position tracking,
#           portfolio accounting, metrics computation
```

### CT-005: Options Strategy Template
```python
# Specialized: Options strategies with Greeks tracking
# Includes: Options chain data parsing, Greeks calculation,
#           margin modeling, IV sensitivity analysis,
#           multi-leg fill simulation, assignment simulation
# Required: Options chain data, IV surface, dividend calendar
```

### CT-006: Order Flow Strategy Template
```python
# Specialized: Requires tick data + L2 order book
# Includes: Order book reconstruction, OFI calculation,
#           volume delta, depth analysis, tape parsing,
#           latency simulation, venue filtering
# Required: Tick data, bid/ask, L2 order book, aggressor flags
```

### CT-007: ML Strategy Template
```python
# Specialized: Machine learning strategies
# Includes: Feature timestamp audit, train/val/test split with
#           purged walk-forward, leakage prevention,
#           baseline models, feature importance tracking,
#           model drift monitoring, online learning pipeline
# Required: All ML validation tests (see Validation Framework)
# Hard Rule: Must beat naive baseline, linear baseline, random signal, turnover-matched random
```

### CT-008: AI Agent Signal Template
```python
# Specialized: LLM agent research output → structured signals
# Includes: Source document verification, timestamp anchoring,
#           claim extraction pipeline, confidence scoring,
#           ticker/entity mapping, rationale generation,
#           forbidden assumption checking, validation status tracking
# Hard Rule: LLM output is NEVER a trade; always passes through validation layer
```

---

## Part B: LLM Agent Prompts (10 Core Prompts)

### Hard Rules for ALL Prompts
1. The agent is NOT allowed to call any strategy profitable
2. Every response must convert the idea into testable rules
3. Every response must identify required data types
4. Every response must identify likely failure modes
5. Every response must define the minimum validation tests before any coding begins

### LLP-001: Convert Strategy to Schema
**Purpose**: Take a free-form strategy description and output a complete 24-field strategy card
**Input**: Strategy name, description, rules (free text)
**Output**: Complete strategy card with all required fields populated
**Key Instructions**:
- Identify edge source from the 10-edge taxonomy
- Specify exact entry/exit rules (no ambiguity)
- Map indicators to specific parameters
- Define 3+ failure modes
- Select validation tests from the validation framework
- State professional equivalent

### LLP-002: Convert YouTube Strategy to Testable Rules
**Purpose**: YouTube strategies are often vague; force specificity
**Input**: YouTube strategy description, video key points
**Output**: Structured strategy card with testable rules
**Key Instructions**:
- Strip all marketing language ("works great", "tested strategy")
- Convert rules to: IF condition THEN action format
- Define every threshold numerically
- Identify data sources needed
- Flag any subjective elements that can't be automated

### LLP-003: Convert ICT Concept to Quant Test
**Purpose**: Translate retail ICT/SMC language into testable microstructure equivalents
**Input**: ICT concept name, description
**Output**: Testable hypothesis with microstructure grounding
**Key Instructions**:
- Map retail term to professional microstructure equivalent
- Define coordinates, thresholds, timestamps
- Require volume confirmation
- Define falsification criteria BEFORE analysis
- Link to Cont-Kukanov-Stoikov (2014) where applicable
- WARNING: If concept has no academic anchor, state this explicitly

### LLP-004: Convert Indicator to Feature
**Purpose**: Transform a named indicator into engineered features
**Input**: Indicator name, parameters
**Output**: Feature set with leakage checks and decay monitoring
**Key Instructions**:
- Extract raw inputs used by indicator
- Create multiple feature transforms (raw, normalized, ranked, volatility-adjusted)
- Check for look-ahead leakage in calculation
- Define feature decay horizon
- Map to feature engineering catalog

### LLP-005: Convert Options Trade to Greeks Profile
**Purpose**: Structure an options trade idea into full risk profile
**Input**: Strategy name, strikes, expirations, underlying
**Output**: Complete options strategy card
**Key Instructions**:
- Calculate deltas, gammas, vegas, thetas for all legs
- Identify net Greeks profile
- Assess margin requirements
- Define IV regime needed
- List assignment risk scenarios
- Map to options strategy catalog

### LLP-006: Generate Failure Modes
**Purpose**: Systematically enumerate failure modes for any strategy
**Input**: Strategy card or description
**Output**: Comprehensive failure mode analysis
**Key Instructions**:
- Check all 11 failure mode categories
- For each applicable mode: describe mechanism, symptoms, detection method, mitigation
- Prioritize by likelihood × impact
- Cross-reference with failure mode catalog
- Suggest validation tests that detect each failure mode

### LLP-007: Generate Validation Plan
**Purpose**: Design the complete validation pipeline for a strategy
**Input**: Strategy card
**Output**: Ordered validation test plan with pass/fail criteria
**Key Instructions**:
- Select required tests from validation framework matrix
- Define specific pass thresholds for each test
- Order tests from simplest (baseline comparison) to most complex (walk-forward)
- Include regime-breakdown testing
- For ML strategies: enforce 4-baseline minimum
- Define promotion/rejection decision rules

### LLP-008: Generate QuantConnect Skeleton
**Purpose**: Convert strategy card into QuantConnect Algorithm Framework code
**Input**: Complete strategy card
**Output**: Python code skeleton with AlphaModel, RiskModel, PortfolioConstruction stubs
**Key Instructions**:
- Map strategy card fields to framework modules
- Implement entry/exit logic in AlphaModel
- Implement risk controls in RiskModel
- Add configuration for all parameters
- Include test fixtures for signal function
- Reference applicable code template

### LLP-009: Generate Backtest Manifest
**Purpose**: Create the run manifest and metadata for a backtest execution
**Input**: Strategy card, data availability, backtest configuration
**Output**: Complete run manifest with all tracking fields
**Key Instructions**:
- Generate run_id, config_hash, data_version, code_version
- List universe, calendar, parameter set
- Define metric pack to be emitted
- Link to required review report template
- Include reproducibility checklist

### LLP-010: Strategy Reviewer Prompt
**Purpose**: Act as a critical reviewer evaluating a completed strategy
**Input**: Strategy card, backtest results, validation test results
**Output**: Critical review with promotion/reject/hold decision
**Key Instructions**:
- NEVER allow the strategy to be called "profitable" — use precise metric language instead
- Evaluate against all applicable failure modes
- Check validation test pass/fail status
- Assess parameter stability
- Evaluate out-of-sample performance
- Identify top 3 weak points
- Recommend specific next experiments
- Make clear decision: PROMOTE / HOLD FOR MORE DATA / REJECT
- Link to relevant professional equivalent for benchmark comparison

---

## Part C: Dataset Requirements by Strategy Type

### DAT-001: Basic OHLCV Strategies (Levels 1-2)
- **Required**: OHLCV (daily or intraday), calendar data
- **Optional**: Adjusted prices for splits/dividends
- **Sources**: Yahoo Finance, Alpha Vantage, Polygon

### DAT-002: Intermediate Technical Strategies (Level 3)
- **Required**: OHLCV (intraday), volume profile, ATR data
- **Optional**: Market breadth indicators, sector data

### DAT-003: Statistical/Quant Strategies (Level 4)
- **Required**: OHLCV + tick data, cross-sectional data universe
- **Optional**: Fundamentals, macro data, options chain

### DAT-004: ML-Assisted Strategies (Level 5)
- **Required**: All Level 3 + feature history, label data
- **Optional**: Alternative data (news, sentiment, social)

### DAT-005: Microstructure Strategies (Level 7)
- **Required**: Tick data, L2 order book, bid/ask, market depth
- **Optional**: Trade aggressor flags, session metadata, ICE/fix data

### DAT-006: Options Strategies (Level 8)
- **Required**: Options chain data, IV surface, underlying OHLCV
- **Optional**: Volatility skew data, term structure, earnings calendar

### DAT-007: AI Agent Strategies (Level 9)
- **Required**: Source documents with timestamps, entity extraction pipeline
- **Optional**: LLM outputs, confidence scores, historical claim accuracy

### DAT-008: Multi-Strategy Systems (Level 10)
- **Required**: All applicable Level 1-8 data for constituent strategies
- **Optional**: Cross-strategy correlation history, regime labels

---

## Part D: Sample Strategy Card Format (Reference)

```yaml
strategy_id: STRAT-EXAMPLE-001
strategy_name: "Multi-Timeframe Trend with VWAP Pullback"
category: intermediate
difficulty:
  level: 3  # Multi-factor technical
edge_source:
  - trend
  - mean_reversion
asset_classes:
  - equities
  - futures
timeframes:
  - daily (trend filter)
  - 5-min (entry execution)
data_required:
  - OHLCV (daily + 5-min)
  - VWAP (5-min)
  - volume profile
entry_logic: "Daily trend bullish (price > 200 SMA AND 50 SMA > 200 SMA); 
  5-min VWAP reversion (price pulls 1.5 ATR below VWAP in uptrend)"
exit_logic: "Take profit at 2 ATR above entry OR stop at 1 ATR below entry OR 
  end of day if intraday"
position_sizing: "1% risk per trade, sized by ATR"
risk_controls:
  max_drawdown_pct: 10
  max_position_pct: 5
  kill_switch: true
indicators_used:
  - SMA (50, 200)
  - ATR (14)
  - VWAP
features_used:
  - trend_direction (binary)
  - pullback_depth (continuous)
  - vol_adjusted_distance
validation_tests:
  - random_signal_baseline
  - transaction_cost_stress
  - regime_breakdown
  - parameter_stability_heatmap
  - walkforward_test
failure_modes:
  - regime_dependency: "Trend strategy fails in mean-reverting regimes"
  - transaction_cost_failure: "Frequent pullback entries accumulate costs"
  - overfitting: "Pullback threshold optimized on historical data"
professional_equivalent:
  "Pullback in trend = institutional trend-following with scale-in 
   methodology (Turtle-style)"
paper_references:
  - "Moskowitz, Ooi, Pedersen (2012) - Time Series Momentum"
implementation_notes: "Ensure VWAP is calculated per session, not rolling across days"
live_trading_risk: "Whipsaw losses in choppy intraday regimes"
status: testable
```

---

*Cross-linked: [[Schema-and-Taxonomy]], [[Basic-Intermediate-Strategies]], [[Professional-Quant-Strategies]], [[AI-ML-Strategies]], [[Options-Trading-Strategies]], [[Multi-Strategy-Patterns-ICT-SMC]], [[Validation-Framework]], [[Feature-Engineering-Catalog]], [[Failure-Mode-Catalog]], [[Professional-Equivalent-Map]], [[Indicator-Catalog]], [[07-Master-Index]]*
