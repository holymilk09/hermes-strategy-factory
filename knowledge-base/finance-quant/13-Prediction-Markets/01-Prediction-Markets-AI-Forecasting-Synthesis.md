# Prediction Markets & AI Forecasting Synthesis

## Key Papers

**Foundational Prediction Markets**
- **Wolfers & Zitzewitz (2004)** — *Prediction Markets*. Journal of Economic Perspectives. **FREE LANDING**. Foundational survey of prediction markets as forecasting mechanisms. Covers how market prices aggregate dispersed information. Establishes the central claim: prediction prices are often efficient (or near-efficient) as probability forecasts.
- **Hanson (2003)** — *Combinatorial Information Market Design*. Information Systems Frontiers. Develops market mechanisms for structured/combinatorial prediction events. Important for designing multi-event forecasting systems.
- **Hanson (2007)** — *Logarithmic Market Scoring Rules for Modular Combinatorial Information Aggregation*. JPM. **FREE LANDING**. The LMSR mechanism — central for automated market makers in prediction markets. Critical infrastructure paper for building AI-forecasting systems.

**Interpretation & Limits**
- **Manski (2006)** — *Interpreting the Predictions of Prediction Markets*. Economics Letters. **Important caution**: Prediction market prices are NOT automatically equal to true probabilities. Risk aversion, market manipulation, and other frictions distort prices. Essential reading to avoid naively treating prices as probabilities. PAYWALLED.
- **Gjerstad (2005)** — *Risk Aversion, Beliefs, and Prediction Market Equilibrium*. Working paper. Shows trader risk preferences systematically distort prices relative to underlying beliefs. Relevant to AI-agent forecasting markets too.

**Modern Prediction Markets (Kalshi/Polymarket)**
- **Le et al. (2026)** — *Decomposing Crowd Wisdom: Effects of Investor Beliefs and Strategies on Kalshi and Polymarket*. arXiv:2602.19520. **FREE**. Directly analyzes real prediction-market data. Decomposes crowd wisdom into belief aggregation versus strategic trading effects. Essential for understanding modern retail prediction markets.
- **Tadasco et al. (2025)** — *Fake Prediction Markets, Real Confidence Signals*. arXiv:2512.05998. **FREE**. Surprising finding: simulated/fake prediction markets (no real money) can still extract confidence signals from participants. Challenges the assumption that only real-money markets work. Potentially useful for AI confidence extraction.

**LLM Forecasting Benchmarks**
- **Yu, Li, You (2025)** — *LiveTradeBench: Benchmarking LLMs on Real-Time Financial Forecasting and Trading*. arXiv:2511.03628. **FREE**. Benchmarks LLMs on real-time (not static) financial forecasting. Important: static/retrospective benchmarks overstate LLM capability; real-time evaluation is the true test.
- **Zhang et al. (2026)** — *Prediction Arena: A Benchmark for LLM Forecasting over Prediction Markets*. arXiv:2604.07355. **FREE**. Benchmark tying LLM forecasting to prediction-market-style evaluation. Evaluates LLMs' ability to forecast the same types of events that real prediction markets resolve.

## Core Theses

1. **Prediction markets aggregate information efficiently (with caveats)**: Wolfers-Zitzewitz established the baseline — prediction markets are among the best available forecasting tools. But Manski showed they aren't perfect probability measures.
2. **Real-money vs fake markets**: Tadasco et al. suggests that even simulated markets can reveal confidence signals, which opens the door to using prediction-market-style mechanisms for AI confidence calibration without real money.
3. **Kalshi/Polymarket as data sources**: Le et al. shows these modern platforms contain decomposable signals — you can separate pure belief aggregation from strategic trading effects.
4. **LLM forecasting needs real-time evaluation**: LiveTradeBench and Prediction Arena establish benchmarks for evaluating LLM forecasting ability, emphasizing real-time performance over retrospective accuracy.
5. **LMSR is the infrastructure backbone**: For building automated market prediction systems, the logarithmic market scoring rule is the mechanism design foundation.

## Implications for Trading Systems

- **LLM confidence extraction**: Use prediction-market-inspired scoring (LMSR-style) to elicit and calibrate confidence from AI forecasting agents. The "fake market" insight from Tadasco et al. means this could work even without real money.
- **Kalshi/Polymarket as features**: Decompose real prediction market prices into belief and strategy components (following Le et al.) as input features for cross-market prediction models.
- **Real-time evaluation harness**: Build LiveTradeBench-style real-time evaluation for any LLM-based forecasting system. Retrospective backtesting alone is insufficient.
- **Market design for AI agents**: If deploying multi-agent forecasting systems, use LMSR-based automated market makers to aggregate agent predictions efficiently.
- **Probability calibration**: Apply Manski's caution — always adjust prediction market prices for risk aversion and strategic distortions before using as probability forecasts.

## Failure Modes & Critiques

- **Prices ≠ probabilities**: The single biggest failure mode is naively treating prediction market prices as true probabilities. Risk aversion, low liquidity, and strategic betting create systematic biases (Manski, Gjerstad).
- **Liquidity distortion**: Illiquid prediction markets (especially exotic/out-of-the-money contracts) can have wildly noisy prices that carry no forecasting value.
- **Manipulation risk**: Thinly traded prediction markets are vulnerable to price manipulation, especially on new platforms with low participant counts.
- **Real-money assumption may be wrong**: Tadasco et al.'s finding that fake markets work too complicates the traditional efficient-market justification. Need to clarify under what conditions simulated vs real markets differ.
- **LLM overconfidence**: LLMs tend to be poorly calibrated in their confidence. Prediction-market-style scoring mechanisms are necessary but may not be sufficient for full calibration.
- **Platform dependence**: Kalshi, Polymarket, and similar platforms have different mechanisms, user bases, and regulatory constraints. Signals may not generalize across platforms.

## Cross-Links

- [[15-Pattern-Recognition/01-Pattern-Recognition-Synthesis]] (AI agent simulation, Hanson combinatorial mechanisms, Tadasco fake-markets connection)
- [[Core-Statistical-Principles]] (probability calibration, Manski's interpretation critique)
- [[07-01-Behavioral-Finance]] (crowd wisdom, confidence extraction, strategic behavior in markets)
- [[06-Data-Infrastructure]] (benchmark design, real-time evaluation pipelines)
