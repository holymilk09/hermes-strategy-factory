# Behavioral Finance & Psychometric Inference

> **Group E** — Synthesized from raw research library
> **Tags:** behavioral-finance, prospect-theory, disposition-effect, investor-biases, psychometric-inference, narrative-economics
> **Cross-links:** [[07-02-LLM-Trading-Agents]], [[07-Index]]

## Key Papers

### Tier 1 — Foundational

- **Odean (1998)** — *Are Investors Reluctant to Realize Their Losses?* (Journal of Finance). Disposition-effect anchor: investors sell winners too early and hold losers too long, distorting realized PnL distributions. Directly maps into trader decision logic.
- **Barber & Odean (2000)** — *Trading Is Hazardous to Your Wealth* (Journal of Finance). Baseline empirical finding: frequent trading harms performance for individual investors. Any psychometric or behavior-inference model must account for this regularity first.

### Tier 2 — Core Behavioral Mechanisms

- **Barber & Odean (2001)** — *Boys Will Be Boys: Gender, Overconfidence, and Common Stock Investment* (QJE). Links overconfidence to trading intensity, warning that high activity volume should not be mistaken for skill.
- **Tetlock (2007)** — *Giving Content to Investor Sentiment: The Role of Media in the Stock Market* (Journal of Finance). Anchor paper for textual sentiment analysis. Empirical basis for LLM-news trading claims.
- **Shiller (2017)** — *Narrative Economics* (AER / NBER WP 23075, FREE). Framework for how economic narratives propagate contagiously and affect macro/market decisions. Connects story-driven flows to price action.
- **Bordalo et al. (2019)** — *Diagnostic Expectations and Stock Returns* (Journal of Finance). Investors overweight salient/representative outcomes and under-extrapolate base rates. One of the cleaner behavioral explanations for return predictability.
- **Frydman et al. (2014)** — *Using Neural Data to Test a Theory of Investor Behavior* (Journal of Finance). Neuroeconomic evidence linking neural activity around gains/losses to realization decisions. Bridges utility and reference-point theories with biological data.
- **Barberis, Jin & Wang (2021)** — *Prospect Theory and Stock Market Anomalies* (Journal of Finance). Connects prospect-theory preferences (loss aversion, reference dependence) to systematic asset-pricing anomalies.
- **Ramon et al. (2021)** — *Explainable AI for Psychological Profiling from Financial Transaction Records* (Information / arXiv, FREE). Uses explainable ML to infer psychological traits from transaction data. Not trading-specific but demonstrates what can be extracted from financial traces.

### Tier 3 — Complementary

- **Gennaioli, Ma & Shleifer (2016)** — *Expectations and Investment* (NBER Macroeconomics Annual, FREE). Expectation formation and real-economy investment linkages; adds macro counterpart to market-level behavioral models.
- **Modern Finance authors TBD (2026)** — *Bridging Personality and Behavior in Financial Trading* (FREE, needs bibliographic verification). Potentially connects personality measures with observed trading behavior.

## Core Theses

### The Disposition Effect (Odean 1998, Barberis/Jin/Wang 2021)

Investors systematically realize gains too early and defer realizing losses. This creates a predictable distortion in selling pressure: upward price pressure dissipates faster after a stock rises (selling winners), while downward price pressure extends after a stock falls (reluctance to sell). Prospect theory explains this via loss aversion and reference-point utility.

### Overconfidence and Trading Volume (Barber/Odean 2000, 2001)

Trading frequency is negatively correlated with returns for individual investors. Overconfidence drives excessive turnover, particularly among male traders. High activity is not evidence of skill — it is a tax.

### Diagnostic Expectations (Bordalo et al. 2019)

Investors overweight salient information and diagnostic signals relative to statistical base rates, producing systematic expectation errors. This explains why return predictability persists: market participants overreact to recent salient news and underreact to base-rate fundamentals.

### Narrative Contagion (Shiller 2017)

Economically relevant stories propagate through populations like epidemics. Narrative virality, not just fundamental information, drives collective investment behavior. This creates non-linear, threshold-dependent market effects.

### Neuroeconomic Grounding (Frydman et al. 2014)

Reference-point behavior has detectable neural correlates, suggesting investor biases are hardwired rather than learned. This means systematic biases should be persistent across market regimes and difficult to arbitrage away.

### Psychometric Transaction Profiling (Ramon et al. 2021)

Psychological traits can be inferred from financial transaction records using explainable ML. This opens both counterparty-profiling applications (inferring competitor biases) and self-monitoring applications (auditing one's own algorithmic behavior for human-like biases).

## Implications for Trading Systems

### Alpha Opportunity: Exploiting Systematic Biases

- **Disposition effect creates predictable order flow imbalances.** Stocks approaching 52-week highs face concentrated selling from retail investors locking in gains — this can be modeled as a microstructure feature.
- **Overconfidence-driven overtrading** means retail order flow systematically degrades in high-frequency environments; fading or front-running high-turnover retail patterns may capture a spread premium.
- **Diagnostic expectations** suggest that after salient but statistically marginal news events, prices will overshoot relative to fundamentals — mean-reversion strategies can exploit this.
- **Narrative economics** suggests tracking narrative velocity (media mentions, social propagation) as a regime-shift indicator. Early narrative adoption may precede price action.

### Defensiveness: Avoiding Self-Sabotage

- Trading systems should be explicitly audited for behavioral biases: do the model's position exits show disposition-effect patterns? Does activity level correlate negatively with PnL (the overconfidence trap)?
- The [[07-02-LLM-Trading-Agents]] problem in Group F is a direct parallel: just as humans are inconsistent due to bias, LLM agents shift behavior under prompt perturbation. Both require consistency validation frameworks.

### Feature Engineering Implications

- Realized vs. unrealized PnL ratios can serve as disposition-effect proxy features (per Odean methodology).
- Sentiment features built on Tetlock's framework (negative media word counts) have been validated for 18+ years and should be baseline features in any news-driven system.
- Narrative propagation velocity (from Shiller's framework) could be a regime-detection feature that modulates position sizing.

### Psychometric Applications

- If psychological traits can be inferred from transaction data (Ramon et al. 2021), trading firms could build counterparty-behavior models or audit their own algorithms for "personality drift."
- Cross-ref: [[07-02-LLM-Trading-Agents]] agent behavior should be benchmarked against human baselines — the goal is consistent execution, not human-like (biased) behavior.

## Failure Modes

### Bias Exploitation Decay

- Behavioral alpha may decay as more participants model the same biases. The disposition effect is well-known; any edge from exploiting it depends on new investors continuously entering markets (and they do, but margins compress).
- Diagnostic-expectation strategies could fail if the salience threshold shifts (e.g., algorithmic content curation changes what information becomes salient).

### Narrative Measurement Ambiguity

- Shiller's narrative framework is conceptually powerful but operationally vague. Quantifying narrative virality requires proxy choices (social mentions, news tone, Google Trends) that may not map cleanly to the theoretical construct.

### Neuroeconomic Translation Risk

- Frydman et al. show neural correlates, but these are lab-economy findings. Translating neural-behavioral theory into live-market feature engineering requires strong assumptions about ecological validity.

### Overconfidence Trap for Quant Systems

- The Barber-Odean finding that "trading is hazardous" applies directly to quant systems: excessive model retraining or feature-churning can degrade performance even as activity increases. This is the quant equivalent of overtrading.

### Psychometric Profiling Limitations

- Ramon et al.'s methodology infers traits from transactions, but psychological trait inference is noisy and culturally contingent. Deploying profiling-derived features without out-of-sample validation risks spurious correlations.

## Anti-Cookie-Cutter Insights

- **The quant equivalent of overtrading is excessive model retraining.** The Barber-Odean finding that "trading is hazardous" applies directly to systematic strategies: churning your feature set or retraining on noise will degrade performance even as activity increases.
- **Neural correlates suggest investor biases are hardwired, not learned.** This means systematic biases should persist across generations and market regimes — they are not arbitraged away by education or experience.
- **Psychological profiling from transactions works in both directions.** The same technology that lets you infer counterparty bias also makes you inferable. Any trading operation's transaction footprint is a leaky signal.
- **The disposition effect is not just about individual stocks** — it scales to portfolio-level behavior. Fund managers showing disposition patterns at the position level also show it in sector allocation, creating multi-scale alpha opportunities.

## Cross-Links

- [[07-02-LLM-Trading-Agents]] — LLM agents that trade should be validated against these behavioral baselines
- [[01-Market-Microstructure]] — Disposition effects manifest in order-flow microstructure
- [[02-Alpha-Research]] — Behavioral biases are a primary alpha source category
- [[Tetlock Media Sentiment]] — Direct cross-reference to news sentiment feature construction
- [[07-02-LLM-Trading-Agents]] — Agent consistency validation parallels human bias auditing
- [[Prospect Theory]] — Core theory underlying disposition effect and loss aversion
- [[Diagnostic Expectations]] — Salience-driven over-extrapolation framework

## Sources

- `/raw-ingest/quant_research_library/E_behavioral_finance_psychometric_inference/index.md`
- `/raw-ingest/quant_research_library/E_behavioral_finance_psychometric_inference/paywalled.md`
