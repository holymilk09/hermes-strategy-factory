# AI, ML & Agent Strategies

> Synthesized reference for all 17 AI agent roles and 24 ML models. **HARD RULES: (1) LLM output is not a trade — LLM output is input to validation. (2) No ML strategy passes without beating 4 baselines: naive baseline, linear baseline, random signal, turnover-matched random.** Every entry is a hypothesis, not a claim of profitability.

---

## Core Directives (Non-Negotiable)

1. **Every strategy is a hypothesis, not a money printer**
2. No card may claim: Works, Profitable, Validated, High win rate, Institutional edge
3. **LLM output is not a trade** — LLM output is input to validation
4. **No ML strategy passes without beating ALL 4 baselines**: naive (buy-and-hold), linear (logistic/linear regression), random signal, turnover-matched random signal
5. **ML requires leak-proof feature engineering** — all leakage tests from [[Feature Engineering Catalog]] must pass
6. Indicator ≠ strategy. Feature engineering + model + hypothesis + execution + risk + validation = strategy
7. **ML models are function approximators, not oracles** — they interpolate within training distribution and fail on regime changes

---

## Section A: AI Agent Strategies (17 Roles)

> Category: `ai_agent` | Use: Research automation, information processing, signal generation, portfolio oversight. **LLM output must ALWAYS pass through validation before becoming a trade.**

---

### AG-001: News Agent

**Edge source**: informational
**Role**: Monitor, classify, and extract trade-relevant information from news feeds in real-time.

**Key Concepts**: NLP pipeline for news ingestion: fetch → classify (asset, event, sentiment, impact) → extract structured fields → score → flag for review. Processes Reuters, Bloomberg, PR Newswire, and alternative sources.

- **Data needed**: News feeds (API or RSS), entity mapping (company → ticker), event taxonomy
- **Test method**: News classification accuracy vs human annotators; event extraction F1 score; timeliness measurement (seconds from publication to extraction); signal quality test on extracted structured data
- **Failure modes**: NLP misclassification (false positives/negatives); timing advantage eliminated by speed of professional news desks; news already priced in by time extracted; hallucinated extraction from LLM
- **Professional equivalent**: Bloomberg Terminal AI, RavenPack news analytics, Dow Jones Newswires — professionals have direct feeds with millisecond timestamps
- **Implications**: The edge is not the news itself (public), but speed and accuracy of extraction. Retail is at massive latency disadvantage
- **Cross-links**: [[Schema and Taxonomy]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### AG-002: Earnings Agent

**Edge source**: informational, behavioral
**Role**: Analyze earnings reports, transcripts, and guidance for signals. Extract surprises, sentiment shifts, guidance changes.

**Key Concepts**: Parse earnings releases and call transcripts. Extract: EPS/revenue vs consensus, guidance changes, management sentiment, keyword shifts, competitive mentions, margin commentary. Structure into quantifiable signals.

- **Data needed**: Earnings releases, earnings call transcripts, consensus estimates, historical guidance
- **Test method**: Extracted signal vs actual price reaction; accuracy of surprise magnitude extraction; guidance change classification accuracy; PEAD replication from extracted signals
- **Failure modes**: LLM misinterprets financial context; nuanced language ("headwinds" vs "tailwinds"); sarcasm/hedging in management speech; transcript timing lag
- **Professional equivalent**: Earnings analysis desks, NLP-driven fundamental research, earnings call sentiment scoring platforms
- **Implications**: Earnings signals are well-studied. The agent must extract information the market hasn't priced, which is increasingly difficult
- **Cross-links**: [[Validation Framework]], [[Professional Equivalent Map]]

---

### AG-003: SEC Filing Agent

**Edge source**: informational, structural
**Role**: Monitor SEC filings (10-K, 10-Q, 8-K, 13F, 4, S-4, SC 13D) for trade-relevant information. Extract changes from prior filings.

**Key Concepts**: Ingest and parse SEC filings. Detect changes from prior period: accounting changes, risk factor additions, insider transactions, material events, mergers, legal proceedings. Quantify significance.

- **Data needed**: SEC EDGAR API, filing type mapping, prior filing history for comparison, entity-to-ticker mapping
- **Test method**: Filing classification accuracy; change detection accuracy; signal value from extracted changes; timeliness vs filing publication time
- **Failure modes": SEC filing volume is massive (noise dominates signal); most filing changes are immaterial; LLM hallucination in financial document parsing; filing language is deliberately obfuscated
- **Professional equivalent": SEC filing monitoring services, regulatory analysis platforms, compliance intelligence systems
- **Implications": The edge is in filtering signal from noise — most filing content is boilerplate. The agent must identify material changes efficiently
- **Cross-links": [[Schema and Taxonomy]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### AG-004: Macro Agent

**Edge source**: informational, structural
**Role**: Track and interpret macroeconomic data releases, central bank communications, and policy changes. Map to asset class implications.

**Key Concepts**: Monitor economic calendar (CPI, NFP, GDP, PMI, Fed meetings). Extract data vs consensus. Map surprises to expected asset class reactions. Track central bank rhetoric shifts via NLP on speeches.

- **Data needed**: Economic calendar, consensus estimates, actual releases, central bank communications, asset class prices
- **Test method**: Surprise vs market reaction accuracy; central bank tone change detection accuracy; mapping quality (surprise → expected direction); timeliness
- **Failure modes": Mac data is already instantly priced; LLM interpretation of nuanced central bank language is unreliable; market reaction may contradict "intuitive" mapping; correlation changes over time
- **Professional equivalent": Global macro research desks, central bank analysis teams, macro data platforms
- **Implications": The macro signal → asset mapping is not stable. What worked pre-2020 may not work post-2020. Regime dependency is critical.
- **Cross-links": [[Validation Framework]], [[Schema and Taxonomy]], [[Professional Equivalent Map]]

---

### AG-005: Sentiment Agent

**Edge source**: informational, behavioral
**Role**: Aggregate sentiment from social media, news, forums, and other text sources into quantifiable sentiment scores.

- **Edge source**: behavioral, informational
- **Data needed**: Social media APIs (Twitter/X, Reddit, StockTwits), news headlines, sentiment model (LLM or lexicon-based)
- **Test method**: Sentiment score vs subsequent returns; precision/recall of sentiment classification; noise filtering effectiveness; compare to VIX/Fear & Greed as benchmark
- **Failure modes**: Social media is noisy and manipulable (pump-and-dump, bot networks); retail sentiment is often a contrarian signal at extremes; lexicon models miss context; LLM sentiment is expensive at scale
- **Professional equivalent**: Social listening platforms (Bloomberg Social Velocity, alternative sentiment data providers)
- **Implications**: Sentiment is a behavioral edge but is easily gamed. Must distinguish genuine sentiment from manufactured hype
- **Cross-links**: [[Failure Mode Catalog]], [[Professional Equivalent Map]], [[Schema and Taxonomy]]

---

### AG-006: Debate Agent

**Edge source**: informational
**Role**: Act as adversarial challenger to trading hypotheses. Force rigor through structured debate: bull case vs bear case, counter-arguments, evidence grading.

**Key Concepts**: Given a hypothesis, the debate agent generates structured counter-arguments, identifies logical fallacies, demands evidence, grades strength of argument. Multi-agent debate (two opposing agents + judge).

- **Data needed**: The hypothesis, supporting evidence, counter-evidence
- **Test method**: Measure debate quality by reduction in false-positive hypotheses; track whether debated-then-approved hypotheses outperform non-debated ones; expert evaluation of debate rigor
- **Failure modes": LLM generates plausible-sounding but factually incorrect counter-arguments; debate quality depends on prompt quality; overconfidence in LLM reasoning; sycophancy (LLM agrees with stronger prompt)
- **Professional equivalent": Investment committee process, red-teaming, devil's advocate review — institutional debate with domain experts, not LLMs
- **Implications": The debate agent is a thinking tool, not a signal generator. Value comes from forcing rigor, not from LLM consensus
- **Cross-links": [[Schema and Taxonomy]], [[Master Index]]

---

### AG-007: Portfolio Review Agent

**Edge source**: informational
**Role**: Periodic review of portfolio composition, concentration, risk exposure, and alignment with strategy mandates.

**Key Concepts**: Analyze portfolio for: concentration risk, sector/country/asset-class drift, correlation changes, factor exposure drift, drawdown status, position sizing compliance, mandate violations.

- **Data needed**: Current portfolio holdings, target allocation, risk limits, correlation matrix, factor exposures
- **Test method": Review accuracy (correctly identifies issues); actionability of recommendations; false positive rate (flags non-issues); expert review of output quality
- **Failure modes": LLM may miss subtle risk interactions; recommendations may be generic rather than specific; lag between portfolio change and review; over-reliance on agent replacing human judgment
- **Professional equivalent": Portfolio risk review process, investment committee portfolio review, risk management overlay
- **Implications": The agent assists review but does not replace quantitative risk systems. Portfolio risk requires precise calculation, not LLM approximation
- **Cross-links": [[Schema and Taxonomy]], [[Failure Mode Catalog]]

---

### AG-008: Risk Review Agent

**Edge source**: informational
**Role**: Stress test strategies and portfolios against historical and hypothetical scenarios. Identify tail risks, concentration, and regime vulnerabilities.

**Key Concepts**: Generate stress scenarios (2008, 2020, rate shock, vol spike, liquidity crisis). Apply to strategy/portfolio. Quantify potential loss. Identify vulnerabilities. Recommend mitigations.

- **Data needed": Strategy/portfolio specifications, historical crisis data, scenario parameters, risk models
- **Test method": Stress test accuracy (does historical simulation match actual losses?); scenario generation quality; identification of actual tail risks; compare to human risk manager assessment
- **Failure modes": LLM may not understand complex strategy interactions; historical scenarios may not represent future tail events; false confidence from "tested" scenarios; missing black swan events
- **Professional equivalent": Enterprise risk management, stress testing frameworks (CCAR, Basel), scenario analysis teams
- **Implications": Stress testing requires precise quantitative modeling. LLM can generate scenarios and narrative risk assessment, but VaR/ES calculation must be done by quantitative models
- **Cross-links": [[Validation Framework]], [[Schema and Taxonomy]], [[Professional Equivalent Map]]

---

### AG-009: Journal Autopsy Agent

**Edge source**: informational
**Role**: Post-trade analysis of trading journal. Identify patterns in wins/losses, behavioral errors, regime-dependent performance, position sizing errors.

**Key Concepts**: Analyze trade journal entries. Extract: win/loss patterns, error classification (rule violation, sizing error, timing error, regime misidentification), performance by market regime, psychological state correlation.

- **Data needed": Trade journal (entries, exits, P&L, sizing, reasoning), market regime labels, rule definitions
- **Test method": Pattern detection accuracy; behavioral error identification; actionable insight generation; trader improvement tracking over time
- **Failure modes": LLM misclassifies errors without precise definitions; journal entries may be incomplete/biased; retrospective narrative construction (hindsight bias in both journal and analysis); generic advice
- **Professional equivalent": Trading desk post-mortem analysis, performance review process, behavioral coaching for traders
- **Implications": Journal autopsy is about self-awareness, not signal generation. The value is behavioral improvement, not finding trading edges
- **Cross-links": [[Master Index]], [[Schema and Taxonomy]]

---

### AG-010: Strategy Discovery Agent

**Edge source**: informational, statistical
**Role**: Systematically explore hypothesis space for potential trading signals. Generate, rank, and prioritize hypotheses for testing.

**Key Concepts**: Generate hypotheses from: academic literature review, cross-market pattern analogues, feature interaction exploration, literature gap identification. Rank by: theoretical plausibility, data availability, testability, prior evidence.

- **Data needed": Academic papers, strategy descriptions, available data, hypothesis space definition
- **Test method": Hypothesis quality rating (expert review); hit rate (hypotheses that survive validation vs generated); diversity of hypothesis generation; redundancy detection
- **Failure modes": LLM generates untestable hypotheses; generates hypotheses already tested; hallucinated academic citations; ignores transaction cost reality; over-optimistic about data availability
- **Professional equivalent": Quantitative research process, academic literature review, alpha research teams
- **Implications": Strategy discovery is idea generation, not validation. Every generated hypothesis must pass through the full validation pipeline. LLM is a brainstorming tool, not a validator
- **Cross-links": [[Validation Framework]], [[Schema and Taxonomy]], [[Master Index]]

---

### AG-011: Paper-to-Strategy Agent

**Edge source**: informational, statistical
**Role**: Translate academic papers into testable strategy hypotheses. Extract methodology, data requirements, and validation approach from research papers.

**Key Concepts**: Parse academic paper → extract: hypothesis, data used, methodology, results, limitations → translate into testable strategy card with entry/exit logic, data requirements, validation tests.

- **Data needed": Academic papers (PDFs), strategy card schema, paper extraction methodology
- **Test method": Extraction accuracy vs manual review; completeness of strategy card fields; testability of extracted methodology; comparison to existing implementations
- **Failure modes": LLM misinterprets mathematical notation; hallucinates results not in paper; misses critical caveats and limitations; overstates findings; simplifies complex methodology beyond testability
- **Professional equivalent": Academic-to-practical translation, quant research review process, paper replication teams
- **Implications": Academic papers may not translate directly to live trading. Sample period, universe, and costs matter. The agent translates; it does not validate
- **Cross-links": [[Schema and Taxonomy]], [[Validation Framework]], [[Professional Equivalent Map]]

---

### AG-012: Signal Extraction Agent

**Edge source**: informational
**Role**: Extract structured trading signals from unstructured data sources. Convert text, images, or raw data into quantitative inputs.

**Key Concepts**: Process unstructured data (text, charts, audio) → extract: signal type, direction, confidence, supporting evidence, timestamp → output structured signal for validation pipeline.

- **Data needed": Unstructured data source, signal taxonomy, extraction template, confidence calibration framework
- **Test method": Signal extraction precision/recall; calibration of confidence scores; signal-to-noise ratio; downstream strategy performance using extracted signals
- **Failure modes": LLM extraction hallucination; signal overconfidence; calibration drift (confidence scores drift over time); latency; cost at scale
- **Professional equivalent": Alternative data processing, signal extraction pipelines, data science feature extraction
- **Implications": Extracted signals require rigorous validation. LLM confidence scores are not calibrated probabilities. Must test extracted signal quality against ground truth
- **Cross-links": [[Validation Framework]], [[Feature Engineering Catalog]], [[Schema and Taxonomy]]

---

### AG-013: Event Classification Agent

**Edge source**: informational
**Role**: Classify market events into structured taxonomy. Map events to expected market reactions. Build event-driven signal database.

**Key Concepts**: Detect events in data streams → classify into taxonomy (earnings, M&A, Fed, geopolitical, technical, etc.) → map to historical reaction patterns → generate structured event signal.

- **Data needed": Event taxonomy, historical event database with outcomes, real-time data stream, entity mapping
- **Test method": Classification accuracy; mapping quality (do historical patterns repeat?); timeliness; signal predictive power from classified events
- **Failure modes": Event taxonomy may not cover novel events; historical patterns may not repeat (regime change); classification errors compound across pipeline; overlap/confusion between event types
- **Professional equivalent": Event-driven research, event study databases, systematic event trading
- **Implications": Event classification is a data engineering challenge. The edge is not in classification but in the mapping from event to market reaction
- **Cross-links": [[Schema and Taxonomy]], [[Professional Equivalent Map]], [[Validation Framework]]

---

### AG-014: Research Summarizer Agent

**Edge source**: informational
**Role**: Summarize academic papers, research reports, and strategy documentation. Extract key findings, methodology, and limitations.

**Key Concepts**: Process research documents → extract: hypothesis, methodology, data, results, limitations, practical implications → create structured summary → compare to existing knowledge base.

- **Data needed": Research documents, summarization template, knowledge base for deduplication
- **Test method": Summary accuracy vs manual review; information retention (key points captured or lost?); hallucination rate; usefulness rating by researcher
- **Failure modes": Over-simplification of complex methodology; loss of critical caveats; hallucination of findings; bias toward positive findings; missing key limitations
- **Professional equivalent": Research review process, literature management, knowledge management systems
- **Implications": Summaries are input for research, not conclusions. Always verify against original source, especially for methodology details
- **Cross-links": [[Master Index]], [[Schema and Taxonomy]]

---

### AG-015: Regime Commentary Agent

**Edge source**: informational
**Role**: Generate narrative commentary on current market regime. Synthesize multiple indicators and signals into coherent regime assessment.

**Key Concepts**: Aggregate: trend indicators, volatility regime, breadth, macro data, sentiment → generate regime narrative (bull/bear/choppy/transition) → identify regime change risks → recommend strategy adjustments.

- **Data needed**: All indicator data, macro data, regime classification framework, historical regime labels
- **Test method": Regime classification accuracy; timeliness of regime change detection; quality of regime narrative; actionability of recommendations
- **Failure modes": LLM generates plausible-sounding but incorrect regime assessment; narrative bias (anchoring to recent events); regime labels are inherently subjective; recommendations may conflict across strategies
- **Professional equivalent": Chief Investment Officer commentary, market commentary teams, macro research reports
- **Implications": Narrative commentary is useful for human understanding, not for automated trading decisions. Regime detection should be quantitative; commentary is supplementary
- **Cross-links": [[Validation Framework]], [[Schema and Taxonomy]], [[Master Index]]

---

### AG-016: Multi-Agent Committee

**Edge source**: informational
**Role**: Coordinate multiple specialized agents to evaluate trading hypotheses through structured committee process.

**Key Concepts**: Multiple agents (News, Earnings, Macro, Sentiment, Risk Review) each provide independent assessment → synthesis agent aggregates → committee vote on hypothesis → output: approval/rejection/more-research-needed with reasoning.

- **Data needed**: All agent outputs, voting framework, hypothesis, evaluation criteria
- **Test method": Committee decision quality vs single-agent decisions; diversity of agent perspectives; conflict resolution quality; hypothesis tracking over time
- **Failure modes": All agents share same LLM foundation model biases; sycophancy between agents (agents agree rather than debate); coordination overhead; committee groupthink; computational cost
- **Professional equivalent": Investment committee, research review panel, risk committee — but with LLM agents substituting for human domain experts
- **Implications": Multi-agent coordination does not automatically improve decision quality. Agent diversity and independence are critical. Committee output must still pass validation
- **Cross-links": [[Schema and Taxonomy]], [[Validation Framework]], [[Master Index]]

---

### AG-017: Risk/Portfolio Review (Combined AI Agent)

**Edge source**: informational
**Role**: Combined portfolio review + risk review agent. Full portfolio and risk assessment in single analysis.

- **Edge source**: informational
- **Data needed**: Portfolio holdings, risk parameters, correlation data, stress scenarios, mandate definitions
- **Test method": Comprehensive accuracy; actionability; comparison to separate agents + human review
- **Failure modes": Same as individual portfolio + risk agents, plus compound errors from combined analysis; scope too large for LLM to process thoroughly
- **Professional equivalent": Portfolio management + risk management integration, CIO reporting, comprehensive risk dashboards
- **Implications": Combined analysis covers breadth but may sacrifice depth. Critical risk calculations should use quantitative models, not LLM
- **Cross-links": [[Schema and Taxonomy]], [[Failure Mode Catalog]]

---

## Section B: ML Strategies (24 Models)

> Category: `ml_model` | HARD RULE: **No ML strategy passes validation without beating ALL 4 baselines**:  
> (1) Naive baseline (buy-and-hold)  
> (2) Linear baseline (linear/logistic regression)  
> (3) Random signal  
> (4) Turnover-matched random signal

---

### ML Hard Rules

1. Every ML model must pass **all 5 leakage tests** from [[Feature Engineering Catalog]]
2. Feature importance must be documented and interpretable
3. Model must include **drift detection** for live deployment
4. Cross-validation must use **time-series split**, not random k-fold
5. Hyperparameter tuning must use walk-forward, not IS optimization
6. Model outputs → validation → (IF passes THEN live consideration). **LLM/ML output is NEVER directly a trade.**

---

### ML-001: Linear Regression

**Edge source**: statistical  
**Type**: Baseline model

**Key Concepts**: Ordinary least squares regression mapping features to continuous target (returns). Simplest ML baseline. Interpretable. Assumes linear relationship between features and target.

- **Data needed**: Feature matrix, continuous target variable
- **Test method**: R², RMSE, directional accuracy; compare to other ML models; cross-validation with time-series split
- **Failure modes**: Assumes linearity (markets are non-linear); sensitive to outliers; multicollinearity between features; non-stationarity
- **Role**: Primary baseline model. If complex ML cannot beat linear regression, the complex model is adding no value
- **Cross-links**: [[Validation Framework]], [[Feature Engineering Catalog]], [[Schema and Taxonomy]]

---

### ML-002: Logistic Regression

**Edge source**: statistical  
**Type**: Baseline model

**Key Concepts**: Linear model for binary classification (up/down, win/loss). Interpretable coefficients. Assumes linear decision boundary.

- **Data needed**: Feature matrix, binary target
- **Test method**: Accuracy, precision, recall, log-loss, AUC-ROC; calibration curve; compare to tree-based models
- **Failure modes**: Assumes linear separability; poor handling of non-linear interactions; sensitive to feature scaling
- **Role**: Baseline classification model. Must be beaten by any more complex classifier
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]]

---

### ML-003: Random Forest

**Edge source**: statistical  
**Type**: Ensemble tree model

**Key Concepts**: Ensemble of decision trees with bagging and random feature selection. Handles non-linear relationships, feature interactions, and is robust to outliers. Provides feature importance.

- **Data needed**: Feature matrix, target variable (classification or regression)
- **Test method**: Out-of-bag error; feature importance analysis; cross-validation; compare to linear baselines; compare to gradient boosting
- **Failure modes**: Overfitting with deep trees; slow inference at deployment; cannot extrapolate beyond training range; feature importance biased toward high-cardinality features
- **Role**: Strong baseline for non-linear relationships. Often beats linear models but may be beaten by gradient boosting
- **Cross-links**: [[Validation Framework]], [[Feature Engineering Catalog]], [[Schema and Taxonomy]]

---

### ML-004: XGBoost

**Edge source**: statistical  
**Type**: Gradient boosting

**Key Concepts**: Gradient boosting with regularization. State-of-the-art for tabular data. Handles non-linearities, interactions, missing values. Built-in regularization prevents overfitting.

- **Data needed**: Feature matrix, target variable
- **Test method**: Cross-validation with early stopping; feature importance; compare to other boosting methods; hyperparameter sensitivity analysis
- **Failure modes**: Overfitting despite regularization; slow training on large datasets; cannot extrapolate; sensitive to hyperparameter choices; data leakage amplification
- **Role**: Primary candidate for tabular financial data. Often wins Kaggle competitions. Must still beat 4 baselines.
- **Cross-links**: [[Validation Framework]], [[Feature Engineering Catalog]], [[Schema and Taxonomy]]

---

### ML-005: LightGBM

**Edge source**: statistical  
**Type**: Gradient boosting (histogram-based)

**Key Concepts**: Gradient boosting with histogram-based tree construction. Faster training than XGBoost on large datasets. Leaf-wise tree growth. Handles categorical features natively.

- **Data needed**: Feature matrix, target variable, large datasets (>1M rows advantage)
- **Test method**: Training speed comparison; accuracy vs XGBoost; cross-validation; feature importance; compare to baselines
- **Failure modes**: Leaf-wise growth can overfit on small datasets; histogram binning loses precision; less robust to noisy features than XGBoost
- **Role**: XGBoost alternative for large datasets. Choose based on dataset size and speed requirements
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]]

---

### ML-006: CatBoost

**Edge source**: statistical  
**Type**: Gradient boosting (ordered + categorical)

**Key Concepts**: Gradient boosting with ordered boosting to prevent target leakage and native categorical feature handling. Robust to overfitting without extensive tuning.

- **Data needed**: Feature matrix with categorical features, target variable
- **Test method**: Cross-validation; compare to XGBoost/LightGBM on datasets with categorical features; target leakage prevention verification
- **Failure modes**: Slower training than LightGBM; ordered boosting reduces performance on small datasets; native categorical handling may not be optimal for all feature types
- **Role**: Best choice when dataset has significant categorical features (sector, industry, event type)
- **Cross-links**: [[Validation Framework]], [[Feature Engineering Catalog]], [[Schema and Taxonomy]]

---

### ML-007: Ridge / Lasso Regression

**Edge source**: statistical  
**Type**: Regularized linear model

**Key Concepts**: Linear regression with L2 (ridge) or L1 (lasso) regularization. Ridge shrinks all coefficients; Lasso produces sparse models (feature selection). Elastic net combines both.

- **Data needed**: Feature matrix, continuous target
- **Test method**: Cross-validation with regularization parameter sweep; compare OLS; coefficient stability analysis; feature selection quality (Lasso)
- **Failure modes**: Same as linear regression plus regularization parameter sensitivity; Lasso may select wrong features in high correlation settings
- **Role**: Regularized baseline. Essential when feature count is large. Lasso provides automatic feature selection
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]]

---

### ML-008: PCA (Principal Component Analysis)

**Edge source**: statistical  
**Type**: Dimensionality reduction

**Key Concepts**: Linear transformation to orthogonal components ordered by variance explained. Reduces feature dimensionality while preserving maximum information. Used for feature engineering and noise reduction.

- **Data needed**: Feature matrix (standardized)
- **Test method**: Variance explained curve; component stability over rolling windows; downstream model performance with PCA features vs raw features
- **Failure modes**: Components are not economically interpretable; component instability over time; linear assumption; variance ≠ predictive power
- **Role**: Feature engineering tool, not a prediction model. Reduces dimensionality and multicollinearity before feeding to predictive models
- **Cross-links**: [[Feature Engineering Catalog]], [[Schema and Taxonomy]]

---

### ML-009: IPCA (Incremental PCA) / Rolling PCA

**Edge source**: statistical  
**Type**: Online dimensionality reduction

**Key Concepts**: PCA updated incrementally as new data arrives. Adapts to changing covariance structure. Addresses PCA's static nature in non-stationary markets.

- **Data needed**: Streaming feature matrix, standardization parameters
- **Test method**: Component drift tracking; downstream model performance vs static PCA; computational efficiency comparison
- **Failure modes": Component tracking instability; forgetting factor tuning; drift may be noise not signal; computational overhead
- **Role": Feature engineering tool for non-stationary environments. More realistic than static PCA for live trading
- **Cross-links": [[Feature Engineering Catalog]], [[Validation Framework]]

---

### ML-010: Autoencoder

**Edge source**: statistical  
**Type**: Neural network dimensionality reduction / anomaly detection

**Key Concepts:** Neural network that learns compressed representation (bottleneck) of input data. Encoder compresses, decoder reconstructs. Reconstruction error for anomaly detection; bottleneck representation for feature engineering.

- **Data needed**: Feature matrix, hyperparameters (bottleneck size, architecture, training epochs)
- **Test method:** Reconstruction error distribution; anomaly detection precision/recall (if labeled anomalies); downstream model performance with encoded features; compare to PCA
- **Failure modes:** Overfitting to training data; bottleneck may lose predictive information; training instability; interpretation difficulty; anomaly detection threshold selection
- **Role:** Feature engineering (encoded representations) and anomaly detection (reconstruction error). Non-linear alternative to PCA.
- **Cross-links:** [[Feature Engineering Catalog]], [[Schema and Taxonomy]], [[Failure Mode Catalog]]

---

### ML-011: LSTM (Long Short-Term Memory)

**Edge source**: statistical  
**Type**: Recurrent neural network

**Key Concepts:** Neural network with memory cells that capture temporal dependencies. Handles sequential data. Can model long-term dependencies in time series.

- **Data needed:** Sequential feature matrix, target variable, sequence length parameter
- **Test method:** Cross-validation with walk-forward; compare to simpler sequential models; sequence length sensitivity; overfitting monitoring
- **Failure modes:** Severe overfitting risk on financial data; training instability (vanishing/exploding gradients); computationally expensive; difficult to interpret; often no better than simpler models on financial data
- **Role:** Candidate for sequential pattern modeling. Must prove it beats simpler models and baselines. LSTM complexity is often unnecessary for financial prediction.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]], [[Failure Mode Catalog]]

---

### ML-012: TCN (Temporal Convolutional Network)

**Edge source**: statistical  
**Type**: Convolutional sequence model

**Key Concepts:** Causal convolutions with dilated filters for sequence modeling. Parallelizable (unlike RNN). Captures long-range dependencies through dilation.

- **Data needed:** Sequential feature matrix, target variable, filter size and dilation parameters
- **Test method:** Cross-validation with walk-forward; compare to LSTM on same dataset; computational efficiency; sequence length coverage
- **Failure modes:** Same overfitting risks as LSTM; receptive field tuning; less intuitive parameter tuning; may not outperform LSTM on financial data
- **Role:** LSTM alternative for sequence modeling. Faster training and better parallelization. Same caveat — must prove value over simpler models.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]]

---

### ML-013: Transformer

**Edge source**: statistical  
**Type:** Attention-based neural network

**Key Concepts:** Self-attention mechanism captures global dependencies in sequences. Originally for NLP, adapted for time series. Handles long-range dependencies better than RNNs.

- **Data needed:** Sequential feature matrix, positional encoding, attention parameters
- **Test method:** Cross-validation with walk-forward; compare to LSTM/TCN; attention pattern analysis; computational cost; must beat simpler models
- **Failure modes:** Massive overfitting risk on small financial datasets; computational cost extremely high; requires very large datasets; attention patterns may not be interpretable; often no advantage over simpler models on financial data
- **Role:** Candidate for complex pattern recognition in large datasets. Overkill for most financial prediction tasks. Must prove value over simpler approaches.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]], [[Failure Mode Catalog]]

---

### ML-014: GNN (Graph Neural Network)

**Edge source**: statistical, structural  
**Type:** Graph-based neural network

**Key Concepts:** Neural network operating on graph-structured data. Captures relationships between entities (stocks in same sector, supply chain relationships, correlation networks). Node-level and graph-level predictions.

- **Data needed:** Graph structure (nodes, edges, edge weights), node features, edge features (optional), target variable
- **Test method:** Cross-validation on graph; compare to non-graph models; graph construction stability; feature propagation analysis
- **Failure modes:** Graph construction is itself a hypothesis (and may be wrong); graph instability over time; over-smoothing with deep layers; computationally expensive; interpretation difficulty
- **Role:** Candidate when relationship structure is important (sector relationships, supply chain, correlation network). Requires careful graph construction.
- **Cross-links:** [[Feature Engineering Catalog]], [[Schema and Taxonomy]], [[Validation Framework]]

---

### ML-015: HMM (Hidden Markov Model)

**Edge source**: statistical  
**Type:** Probabilistic state sequence model

**Key Concepts:** Statistical model for systems with unobserved (hidden) states that generate observed data. Market regimes as hidden states. Probabilistic transition between states.

- **Data needed:** Observable time series, number of hidden states (K), emission distribution parameters
- **Test method:** BIC/AIC for state number selection; Viterbi path interpretation; regime classification accuracy (if labeled); predictive power from state probabilities
- **Failure modes:** State number selection is arbitrary; emissions assume specific distributions (often Gaussian, but returns are not); state interpretation is post-hoc; regime transitions may not be Markovian
- **Role:** Regime detection tool. Hidden states often correspond to market regimes (bull, bear, volatile, calm). Must be combined with strategy conditional on regime.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]], [[Feature Engineering Catalog]]

---

### ML-016: Bayesian Regime Detection

**Edge source**: statistical  
**Type:** Probabilistic regime model (Bayesian)

**Key Concepts:** Bayesian approach to regime detection with prior distributions on parameters. Posterior distributions provide uncertainty estimates. Handles small sample sizes better than frequentist HMM.

- **Data needed:** Observable time series, prior specifications, MCMC or variational inference framework
- **Test method:** Posterior convergence diagnostics; regime state quality; uncertainty quantification; compare to HMM; computational cost
- **Failure modes:** Prior specification bias; computational expense (MCMC); convergence may be slow or stuck; posterior interpretation requires expertise
- **Role:** Regime detection with uncertainty quantification. Better for small samples and when uncertainty matters. More computationally intensive than HMM.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]], [[Professional Equivalent Map]]

---

### ML-017: Reinforcement Learning (Execution)

**Edge source**: order_flow, liquidity  
**Type:** RL for optimal execution

**Key Concepts:** Train RL agent to minimize market impact and execution cost. Agent learns optimal order splitting, timing, and venue selection through interaction with market simulator.

- **Data needed:** Order book data, execution data, market simulator, reward function definition
- **Test method:** Simulation-based testing; comparison to TWAP/VWAP benchmarks; reward convergence; sample efficiency; generalization to out-of-sample data
- **Failure modes:** Sim-to-real gap (simulator ≠ real market); reward function misspecification; exploration risk in training; sample inefficiency; overfitting to specific market conditions
- **Role:** Advanced execution optimization. Requires realistic market simulator. Not feasible without institutional-grade execution infrastructure.
- **Cross-links:** [[Schema and Taxonomy]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### ML-018: Reinforcement Learning (Portfolio)

**Edge source**: statistical, behavioral  
**Type:** RL for portfolio allocation

**Key Concepts:** Train RL agent to optimize portfolio allocation over time. State = portfolio + market features; Action = rebalance weights; Reward = portfolio return with risk penalty.

- **Data needed:** Asset returns, portfolio features, risk parameters, training environment
- **Test method:** Portfolio return vs benchmarks; risk-adjusted return; transaction cost simulation; compare to analytical portfolio optimization (mean-variance, risk parity)
- **Failure modes:** Overfitting to training period; reward function design is critical and difficult; instability (small changes in weights cause large policy changes); unrealistic transaction cost modeling
- **Role:** Candidate for dynamic portfolio allocation. Must beat static analytical approaches (mean-variance, risk parity, equal weight) net of costs.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]], [[Failure Mode Catalog]]

---

### ML-019: Inverse Reinforcement Learning (Trader Behavior)

**Edge source**: behavioral, informational  
**Type:** IRl for behavioral modeling

**Key Concepts:** Observe expert trader behavior → infer the reward function driving that behavior → replicate or optimize. Understand what skilled traders optimize for.

- **Data needed:** Expert trader decisions (actions, timing, sizing), market features, IRL algorithm
- **Test method:** Inferred reward function interpretability; replication accuracy; out-of-sample prediction of expert actions; compare to rule-based models of expert behavior
- **Failure modes:** Expert behavior may not be optimal; IRL ambiguity (many reward functions explain same behavior); data requirements (need many expert decisions); behavioral complexity
- **Role:** Behavioral modeling research tool. Understand what drives expert behavior. Useful for training and strategy development, not direct trading
- **Cross-links:** [[Schema and Taxonomy]], [[Master Index]]

---

### ML-020: Anomaly Detection

**Edge source**: statistical, order_flow  
**Type:** Unsupervised learning for outlier detection

**Key Concepts:** Identify anomalous patterns in trading data: unusual order flow, abnormal price movements, regime changes, data quality issues. Multiple algorithms: Isolation Forest, One-Class SVM, Autoencoder reconstruction error.

- **Data needed:** Normal (non-anomalous) training data, anomaly detection algorithm, threshold selection method
- **Test method:** Precision/recall on labeled anomalies; false positive rate; timeliness of detection; downstream utility (do detected anomalies enable profitable trades?)
- **Failure modes:** Threshold selection is arbitrary; false positives overwhelm; what is "anomalous" may be the new normal; concept drift; anomaly ≠ tradeable opportunity
- **Role:** Data quality, risk monitoring, and regime change detection. Anomaly detection is monitoring, not a trading signal by itself
- **Cross-links:** [[Failure Mode Catalog]], [[Schema and Taxonomy]], [[Validation Framework]]

---

### ML-021: Meta-Labeling

**Edge source**: statistical  
**Type:** Secondary classification model

**Key Concepts:** Primary model generates signal (long/short/flat). Meta-labeler (secondary model) decides whether to take or skip the signal. Trained on whether primary model was correct, not on market direction.

- **Data needed:** Primary model signals, signal outcomes, features for meta-model (different from primary model features)
- **Test method:** Meta-model accuracy on signal quality; combined performance (primary + meta-labeler) vs primary alone; out-of-sample signal quality
- **Failure modes:** Label leakage (meta-model features leak signal outcome); meta-model overfits to specific primary model; signal frequency becomes too low (meta-model rejects most signals)
- **Role:** Signal filtering. Improves precision of primary model. Popularized by Marcos López de Prado. Must test combined system, not just meta-model accuracy.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]], [[Feature Engineering Catalog]]

---

### ML-022: Conformal Prediction

**Edge source**: statistical  
**Type:** Prediction with calibrated uncertainty

**Key Concepts:** Wrap any predictive model to produce prediction sets with statistical guarantees. "The model predicts X with 95% confidence" becomes "the model guarantees 95% of predictions will contain the true value." Non-parametric, model-agnostic.

- **Data needed:** Predictive model predictions, calibration dataset, confidence level specification
- **Test method:** Coverage rate verification (do prediction sets achieve promised coverage?); prediction set size (tightness); downstream strategy performance using conformal outputs
- **Failure modes:** Prediction sets may be too wide to be useful; exchangeability assumption (distribution must be stable); non-stationary data reduces coverage guarantee
- **Role:** Model risk management. Provides calibrated uncertainty for any ML model. Useful for position sizing and risk control based on prediction confidence.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]], [[Failure Mode Catalog]]

---

### ML-023: Online Learning

**Edge source**: statistical  
**Type:** Incremental model updating

**Key Concepts:** Model updates incrementally as new data arrives. Adapts to changing distributions without full retraining. Algorithms: Online gradient descent, Hedge, Bayesian online learning, contextual bandits.

- **Data needed:** Streaming data, online learning algorithm, learning rate/decay parameters
- **Test method:** Regret analysis; comparison to periodic retraining; adaptation speed to regime changes; stability of online updates
- **Failure modes:** Catastrophic forgetting (learn recent, forget important past); learning rate tuning; concept drift detection; stability-plasticity trade-off; performance degradation during transitions
- **Role:** Adaptive modeling for non-stationary markets. Must balance adaptation with stability. Monitor for overfitting to recent data.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]], [[Failure Mode Catalog]]

---

### ML-024: Ensemble / Model Stacking

**Edge source**: statistical  
**Type:** Model combination

**Key Concepts:** Combine multiple models (linear, tree, neural) into ensemble. Averaging, weighted averaging, or meta-learner (stacking). Diversifies model error for more robust predictions.

- **Data needed:** Multiple base models, ensemble combination method, out-of-fold predictions for stacking
- **Test method:** Ensemble vs individual model performance; diversity measurement (do models make different errors?); weight stability; overfitting risk in stacking
- **Failure modes:** Ensemble may not improve if models are highly correlated; stacking overfits if meta-learner uses full-sample predictions; computational overhead; interpretation loss
- **Role:** Final-stage prediction refinement. If individual models beat baselines, ensemble typically improves further. Diversity among base models is key.
- **Cross-links:** [[Validation Framework]], [[Schema and Taxonomy]], [[Schema and Taxonomy]]

---

## Section C: AI + ML Integration Rules

### The Validation Pipeline for AI/ML Strategies

```
LLM/Agent Output ──┐
                   ├──→ Signal Extraction ──┐
Model Prediction ──┘                        ├──→ Validation Pipeline ──┐
                                            │                          ├──→ 4-Baseline Test
Baseline Predictions ───────────────────────┘                          │
                                                                       ├──→ Leakage Tests (5)
                                                                       │
                                                                       ├──→ Walk-Forward Validation
                                                                       │
                                                                       ├──→ Regime Segmentation
                                                                       │
                                                                       └──→ IF ALL PASS → Paper Trading
                                                                                    IF FAIL → Reject/Refine
```

### Hard Summary Rules

| Rule | Rationale |
|------|-----------|
| LLM output is never a trade | LLMs hallucinate, lack market microstructure understanding, and cannot estimate probability |
| ML must beat 4 baselines | If a neural network can't beat logistic regression, it's finding noise, not signal |
| Features must pass leak tests | Look-ahead bias is the #1 cause of ML strategy failure |
| Models must include drift detection | Financial data is non-stationary; models trained on past data may be invalid tomorrow |
| Cross-validation uses time-series split | Random k-fold violates temporal independence assumption |
| Confidence intervals required | Point predictions without uncertainty estimates are dangerous for position sizing |
| LLM/ML is input to validation, not output of it | Every prediction must go through the full validation pipeline |

---

## Cross-References

- [[Schema and Taxonomy]] — 24-field card schema
- [[Validation Framework]] — 14 validation tests + 4 ML baselines
- [[Professional Equivalent Map]] — AI/ML in professional context
- [[Failure Mode Catalog]] — 11 failure types (data leakage is #1 for ML)
- [[Feature Engineering Catalog]] — 15 feature types + 5 leakage tests
- [[Indicator Catalog]] — All technical indicators (not ML features)
- [[Master Index]] — Full encyclopedia overview
- ← Parent vault: [[Trading-System-Build-Doctrine]]
