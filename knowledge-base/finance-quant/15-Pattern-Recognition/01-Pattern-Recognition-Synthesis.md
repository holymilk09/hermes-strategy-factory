# Pattern Recognition Across Scales Synthesis

## Key Papers

**ML Asset Pricing (Highest Anchor)**
- **Gu, Kelly & Xiu (2020)** — *Empirical Asset Pricing via Machine Learning*. RFS. **FREE LANDING**. The benchmark for ML-based pattern recognition in asset pricing. Tests a wide range of ML methods (lasso, trees, neural nets) on asset pricing predictability. Found that ML methods beat linear models, especially when using many predictors. High-dimensional non-linearities matter. This is the standard any pattern recognition claim must beat.

**Stylized Facts (Ground Truth)**
- **Cont (2001)** — *Empirical Properties of Asset Returns: Stylized Facts and Statistical Issues*. Quantitative Finance. **FREE LANDING**. The canonical survey of empirical regularities: fat tails, volatility clustering, absence of autocorrelation in returns, leverage effects, volume-volatility correlation. Any pattern recognition model or market simulation must reproduce these stylized facts to be credible. If your simulator looks normal-distributed and uncorrelated, it's fake.

**Academic Pattern Recognition**
- **Lo, Mamaysky & Wang (2000)** — *Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation*. JFE. **Cross-listed from Group O**. Converts visual chart patterns into algorithmic pattern detectors. Tests statistical significance. Establishes the methodology bar: algorithmic definition before testing.

**Micro-Pattern Recognition**
- **Kong et al. (2020)** — *Pattern Recognition in Micro-Trading Behaviors before Stock Price Jumps*. arXiv:2011.04939. **FREE**. Detects patterns in order-flow microstructure before price jumps. Moves pattern recognition from chart labels to observable micro-trading behaviors. Bridges technical analysis with market microstructure. The modern, rigorous approach to pattern recognition.

**Agent-Based / Artificial Markets**
- **Arthur, Holland, LeBaron, Palmer & Tayler (1997)** — *Asset Pricing under Endogenous Expectations in an Artificial Stock Market*. SFI book chapter. **FREE LANDING**. Classic Santa Fe Institute artificial stock market. Shows how micro-agent rules produce emergent macro-market phenomena (bubbles, crashes, volatility clustering). Foundational for multi-agent market simulation.
- **Brock & Hommes (1998)** — *Heterogeneous Beliefs and Routes to Chaos in a Simple Asset Pricing Model*. Journal of Economic Dynamics and Control. Heterogeneous belief switching (chartist vs fundamentalist traders) produces complex dynamics and can explain real market phenomena. Links micro behavioral rules to macro market dynamics. PAYWALLED.
- **Nakagawa et al. (2024)** — *Replicating Financial Market Dynamics with Self-Improvement for AI Traders*. arXiv:2409.12516. **FREE**. Uses self-improving AI traders in agent-based models to reproduce volatility clustering and other stylized facts. Shows that trader learning behavior naturally generates realistic market dynamics.
- **Farmer & Foley (2009)** — *The Economy Needs Agent-Based Modelling*. Nature. **PAYWALLED**. Macro/micro modeling manifesto arguing for agent-based approaches over pure equilibrium models. Relevant for simulation-first quant research.
- **Mizuta (2019)** — *An Agent-Based Model for Designing a Financial Market that Works Well*. arXiv:1906.06000. **FREE**. Connects micro decision rules to market-level design outcomes. Practical ABM for market design.

**Discretionary Pattern + ML**
- **Pal (2024)** — *LSTM Pattern Recognition in Currency Trading: Identifying Wyckoff Accumulation and Distribution Phases*. arXiv:2403.18839. **FREE**. Applies LSTMs to recognize Wyckoff-style patterns in FX data. Novel but lower-anchor quality. Demonstrates sequence model approach to discretionary pattern language. Treat as sandbox exploration, not evidence of robust edge.

## Core Theses

1. **ML beats linear models in asset pricing**: Gu-Kelly-Xiu establish that non-linear ML patterns exist in asset pricing data, but they are subtle and high-dimensional. Simple patterns (moving averages, chart shapes) have been arbed away.
2. **Stylized facts are the ground truth**: Cont's stylized facts are the minimum validation bar. Any pattern recognition system that generates normal-distributed, uncorrelated returns is producing fantasy.
3. **Micro-patterns are the frontier**: Kong et al. points toward pattern recognition in order-flow and micro-trading behavior, not in price charts. This is where genuine edge may still exist.
4. **Heterogeneous beliefs generate emergent patterns**: Brock-Hommes shows that simple heterogeneous agent models — not complex ones — can generate the complex market dynamics observed in reality. Occam's razor for ABM design.
5. **Self-improving agents reproduce stylized facts**: Nakagawa et al. demonstrates that when AI traders learn and adapt, realistic market dynamics emerge naturally. This bridges the gap between agent-based modeling and ML-based pattern recognition.
6. **Simulation must be validated**: Any market simulator (Arthur SFI, Nakagawa, Mizuta) must be validated against stylized facts before being used for pattern discovery or strategy development.

## Implications for Trading Systems

- **ML over manual pattern detection**: Use Gu-Kelly-Xiu-style ML methods (trees, neural nets with regularization) for pattern recognition, not subjective chart reading. The edge is in high-dimensional non-linearities.
- **Micro-pattern features as inputs**: Engineer Kong-style micro-trading behavior features (order-flow sequences, order book dynamics before events) as pattern recognition inputs.
- **Simulation for validation**: Use agent-based market simulation (Arthur SFI, Nakagawa, Mizuta) to stress-test strategies before live deployment. Validate simulation against stylized facts first (Cont's list).
- **Heterogeneous agent models for regime prediction**: Brock-Hommes suggests that tracking the mix of behavioral types in a market (fundamentalist vs trend-following) can predict regime shifts.
- **Algorithmic pattern validation**: Follow Lo-Mamaysky-Wang's methodological bar — all patterns must be algorithmically definable and statistically testable.
- **Stylized facts checklist**: Use Cont (2001) as a checklist for any new pattern recognition model: does it reproduce fat tails? Volatility clustering? Leverage effect? Volume-volatility correlation?

## Failure Modes & Critiques

- **Overfitting to high-dimensional spaces**: Gu-Kelly-Xiu's ML methods, while powerful, carry high overfitting risk. Strict out-of-sample validation and regularization are mandatory.
- **Simulators are simplifications**: Agent-based models (Arthur SFI, Nakagawa, Mizuta) are always simplifications. Their value is in generating hypotheses, not in precise prediction. Validate against real stylized facts.
- **Pattern decay**: Lo-Mamaysky-Wang patterns that once worked may have been arbed away since the paper was published (2000). Always re-test on current data.
- **Discretionary patterns are unfalsifiable**: Wyckoff, head-and-shoulders, and similar discretionary patterns cannot be tested without algorithmic definitions. The LSTM approach (Pal 2024) is a step toward algorithmization but needs rigorous validation.
- **Simulation-to-real gap**: Strategies that work in simulated agent-based markets often fail in real markets due to unmodeled frictions (latency, transaction costs, liquidity dynamics).
- **Regime non-stationarity**: Pattern recognition models trained on one market regime may fail entirely in another. The stylized facts themselves can shift (e.g., volatility clustering intensity changes in low-vol regimes).

## Cross-Links

- [[08-Market-Microstructure/01-Order-Flow-Microstructure-Synthesis]] (Kong micro-patterns, order-flow as pattern input, Cont order book)
- [[12-Technical-Analysis-Evidence/01-Technical-Analysis-Academic-Evidence]] (Lo-Mamaysky-Wang, Wyckoff LSTM, pattern validation)
- [[Trading-System-Component-Architecture]] (stylized facts, ML asset pricing baselines)
- [[07-01-Behavioral-Finance]] (heterogeneous beliefs, behavioral agent types, SFI artificial market)
- [[13-Prediction-Markets/01-Prediction-Markets-AI-Forecasting-Synthesis]] (AI agent simulation, Tadasco fake markets, Hanson mechanism design)
