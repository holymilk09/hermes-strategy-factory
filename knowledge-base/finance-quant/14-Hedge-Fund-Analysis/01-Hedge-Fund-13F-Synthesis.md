# Hedge Fund Analysis & 13F Literature Synthesis

## Key Papers

**Hedge Fund Factor Decomposition**
- **Fung & Hsieh (2001)** — *The Risk in Hedge Fund Strategies: Theory and Evidence from Trend Followers*. RFS. The benchmark paper for decomposing hedge fund returns into systematic factors. Shows that many "alpha" claims are actually compensated beta exposures (trend following, volatility, etc. payoff structures). PAYWALLED.
- **Fung & Hsieh (2004)** — *Hedge Fund Benchmarks: A Risk-Based Approach*. FAJ. Develops appropriate risk-based benchmarks for hedge fund performance. Prevents confusing structured beta with manager alpha. PAYWALLED.
- **Agarwal & Naik (2004)** — *Risks and Portfolio Decisions Involving Hedge Funds*. RFS. Foundation paper for hedge fund risk analysis. Essential reading before attempting any alpha inference from HF returns or holdings. PAYWALLED.

**Holdings-Based Skill Inference**
- **Agarwal, Jiang, Tang & Yang (2013)** — *Uncovering Hedge Fund Skill from the Portfolio Holdings They Hide*. RFS. **Directly relevant to 13F alpha**. Uses confidential holdings data to show that skill information lives in positions that are deliberately hidden from public disclosure. The unreported positions contain more skill signal than the reported ones. PAYWALLED.
- **Anton, Cohen & Polk (2021)** — *Best Ideas*. SSRN/HBS Working Paper. Shows that managers' concentrated positions represent their highest-conviction ideas. Useful as a feature-engineering input: weight 13F holdings by concentration, not just binary presence. PREPRINT.
- **Angelini, Iqbal & Jivraj (2019)** — *Systematic 13F Hedge Fund Alpha*. SSRN Working Paper. The practical applied paper. Tests systematic alpha extraction from public 13F filings. Use as a practical benchmark for any custom 13F strategy. PREPRINT.

**Strategic Misreporting & Limitations**
- **Da et al. (2020)** — *Do Hedge Funds Strategically Misreport Their Holdings?*. Notre Dame working paper. **Critical warning**: Shows that hedge funds strategically misreport or time their 13F disclosures. Reported holdings may not be a clean behavioral trace but a strategic signal. FREE LANDING.
- **Brunnermeier & Nagel (2004)** — *Hedge Funds and the Technology Bubble*. Journal of Finance. Shows hedge funds can ride mispricing rather than correct it. Relevant to understanding HF positioning during bubbles. PAYWALLED.
- **Agarwal, Daniel & Naik (2009)** — *Role of Managerial Incentives and Discretion in Hedge Fund Performance*. Journal of Finance. Shows incentive structures drive risk-taking and reporting behavior. Useful for interpreting 13F behavior through incentive lens. PAYWALLED.

**Industry Context**
- **Goldman Sachs (2020)** — *X-Ray Machine Reveals About Hedge Funds*. GSAM industry report. Industry perspective on hedge fund holdings/risk decomposition. Lower priority but potentially practical for applied strategies. INDUSTRY REPORT.

## Core Theses

1. **Most hedge fund "alpha" is structured beta**: Fung-Hsieh showed that a large portion of what is marketed as manager alpha decomposes into known factor exposures (trend, volatility, credit). Always factor-adjust before inferring skill.
2. **Hidden holdings contain the skill signal**: Agarwal et al. (2013) — the positions that hedge funds don't report in 13Fs contain more skill information than the ones they do. Public 13F data is a lower bound on skill inference.
3. **Concentration matters**: Anton-Cohen-Polk show that best ideas are found in managers' highest-conviction (most concentrated) positions, not average holdings. Weight by conviction.
4. **13Fs are strategically distorted**: Da et al. (2020) shows strategic misreporting in 13F filings. You're not reading a clean diary of manager beliefs — you're reading a strategically crafted disclosure.
5. **Incentives drive behavior**: Hedge fund managers' incentives (fee structures, career concerns) shape both trading and reporting behavior. Always model through incentive lens.

## Implications for Trading Systems

- **13F-based copy strategies require factor adjustment**: Before mimicking 13F positions, decompose the fund's style using Fung-Hsieh factors to ensure you're not buying structured beta with high latency disadvantage.
- **Conviction-weighted 13F signals**: Weight 13F positions by portfolio concentration (Anton-Cohen-Polk style) rather than treating all disclosed positions as equally informative.
- **Treat 13Fs as noisy/strategic**: Model 13F disclosures as strategic signals (Da et al.), not truthful revelations. Look for systematic misreporting patterns — they are themselves signals.
- **Benchmark correctly**: Use risk-based benchmarks (Fung-Hsieh 2004) to evaluate any 13F-following strategy against appropriate factor exposures.
- **Systematic 13F benchmarks**: Use Angelini et al. (2019) as a baseline for any 13F alpha extraction strategy.
- **Incentive-based features**: Engineer features based on fund fee structures, AUM, and recent performance to predict reporting behavior (Agarwal-Daniel-Naik 2009).

## Failure Modes & Critiques

- **Publication lag**: 13F filings are reported with a 45-day lag after quarter-end. By the time you see the position, the informational edge has decayed or been arbitraged.
- **Strategic misreporting is uncorrectable**: Da et al. suggests you cannot fully correct for strategic misreporting because the strategy itself is adaptive. Any correction model can be gamed.
- **Hidden positions are unknowable**: The most skillful positions are precisely those not disclosed. Public 13Fs capture the least informative subset of a manager's portfolio.
- **Small fund noise**: Small or new hedge funds have volatile 13F filings that may reflect operational constraints rather than conviction.
- **Regulatory changes**: SEC rule changes (e.g., Form 13F amendments, position disclosure thresholds) can create artificial discontinuities in 13F-based strategies.
- **Overfitting to visible managers**: Copy strategies tend to overweight well-known, publicly visible funds, which may already have their alpha priced in by the market.

## Cross-Links

- [[Trading-System-Build-Doctrine]] (13F follow-on strategies, factor-adjusted mimicry)
- [[INDEX-Metrics-Diagnostics]] (style decomposition, benchmark construction)
- [[Core-Statistical-Principles]] (factor model estimation, performance attribution)
- [[07-01-Behavioral-Finance]] (manager incentives, strategic disclosure behavior)
