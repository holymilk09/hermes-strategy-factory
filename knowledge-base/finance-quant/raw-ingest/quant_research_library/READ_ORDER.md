# READ_ORDER

Assumption: reader is a technical founder building algorithmic trading systems, not a PhD literature reviewer. The goal is to build judgment: what is inferable, what is tradable, what is overfit, and what is executable.

## Stage 1 - Core decision-logic inference

1. Koijen & Yogo (2019), *A Demand System Approach to Asset Pricing*.
2. Gabaix, Koijen, Richmond & Yogo (2025), *Asset Embeddings*.
3. Gabaix & Koijen (2021), *Inelastic Markets Hypothesis*.
4. Koijen & Yogo (2025), *Theory and Econometrics of Demand System Asset Pricing*.
5. Koijen, Richmond & Yogo (2024), *Which Investors Matter?*.

Reason: this is the strongest academic route from observed holdings to latent investor demand. For reverse-engineering decision logic, start here before touching LLM agents.

## Stage 2 - Statistical discipline before strategy generation

1. Cont (2001), *Empirical Properties of Asset Returns*.
2. Bailey et al. (2014), *Probability of Backtest Overfitting*.
3. Bailey & Lopez de Prado (2014), *Deflated Sharpe Ratio*.
4. Harvey, Liu & Zhu (2016), *...and the Cross-Section of Expected Returns*.
5. Lo (2002), *The Statistics of Sharpe Ratios*.

Reason: without this layer, every LLM-generated or pattern-generated strategy will look better than it is.

## Stage 3 - Market microstructure and execution reality

1. Almgren & Chriss (2000), *Optimal Execution of Portfolio Transactions*.
2. Cont, Kukanov & Stoikov (2014), *Price Impact of Order Book Events*.
3. Avellaneda & Stoikov (2008), *High-Frequency Trading in a Limit Order Book*.
4. Easley, Lopez de Prado, O'Hara & Zhang (2020), *Microstructure in the Machine Age*.
5. Hasbrouck (2007), *Empirical Market Microstructure*.

Reason: a signal that cannot survive impact, spread, queue priority, and execution is not a strategy.

## Stage 4 - Machine learning asset pricing

1. Gu, Kelly & Xiu (2020), *Empirical Asset Pricing via Machine Learning*.
2. Kelly, Pruitt & Su (2019), *Characteristics Are Covariances*.
3. Chen, Pelger & Zhu (2024), *Deep Learning in Asset Pricing*.
4. Kelly et al. (2025), *Artificial Intelligence Asset Pricing Models*.
5. Nagel (2021), *Machine Learning in Asset Pricing*.

Reason: this gives the real ML asset-pricing baseline. Most retail AI trading demos are weaker than this literature.

## Stage 5 - IRL and imitation learning

1. Ng & Russell (2000), *Algorithms for IRL*.
2. Abbeel & Ng (2004), *Apprenticeship Learning via IRL*.
3. Ziebart et al. (2008), *Maximum Entropy IRL*.
4. Ho & Ermon (2016), *GAIL*.
5. Dixon & Halperin (2020), *G-Learner and GIRL*.
6. Roa-Vicens et al. (2019), *Towards IRL for LOB Dynamics*.

Reason: this tells you how to infer objectives from behavior, then shows why finance-specific constraints make it difficult.

## Stage 6 - LLM agents as research assistants, not autonomous traders

1. Lopez-Lira (2025), *Can Large Language Models Trade?*.
2. GPT-Signal (2024).
3. TradingAgents (2024).
4. LLM Trading in Experimental Asset Markets (2025).
5. Behavioral Consistency Validation for LLM Agents (2026).
6. LiveTradeBench (2025).

Reason: LLMs are more credible for research summarization, feature ideation, and hypothesis generation than direct autonomous trading. Validate behavior consistency before trusting any agent loop.

## Stage 7 - Options/volatility if the system touches derivatives

1. Black & Scholes (1973).
2. Merton (1973).
3. Heston (1993).
4. Dupire (1994).
5. Carr & Madan (1999).
6. Gatheral, *The Volatility Surface*.
7. Bergomi, *Stochastic Volatility Modeling*.

Reason: derivatives strategies require model risk literacy. A surface-fitting error can look like alpha until it gets repriced.

## Stage 8 - Technical analysis and pattern recognition under academic filters

1. Lo, Mamaysky & Wang (2000), *Foundations of Technical Analysis*.
2. Brock, Lakonishok & LeBaron (1992), *Simple Technical Trading Rules*.
3. Sullivan, Timmermann & White (1999), *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*.
4. Cont, Kukanov & Stoikov (2014), *Price Impact of Order Book Events*.
5. Micro-trading pattern recognition papers in Group R.

Reason: retail pattern language must be translated into testable features and then attacked with data-snooping controls.
