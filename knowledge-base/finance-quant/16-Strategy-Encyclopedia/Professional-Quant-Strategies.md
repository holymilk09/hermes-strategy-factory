# Professional Quant Strategies

> Synthesized reference for 24 professional-level strategies (Difficulty 7-10). Each categorized by **actual edge source from the 10-edge taxonomy**, not indicator. Includes why these work institutionally. **CORE RULE: These are hypotheses requiring production-grade validation, not guaranteed profits.**

---

## Core Directives (Non-Negotiable)

1. **Every strategy is a hypothesis, not a money printer**
2. No card may claim: Works, Profitable, Validated, High win rate, Institutional edge
3. **Edge must be identified by mechanism, not indicator** — no professional strategy is defined by a technical indicator
4. LLM output is not a trade
5. No ML strategy passes without beating 4 baselines
6. Professional edge always includes structural or informational advantages not available to retail

---

## Edge Taxonomy Reference (10 Edges)

 behavioral | trend | mean_reversion | liquidity | volatility | carry | statistical | order_flow | structural | informational

---

## PROFESSIONAL STRATEGIES (Level 7-10) — 24 Strategies

---

### S-PR-001: Cross-Sectional Momentum

**Edge source**: trend, behavioral, statistical
**Asset classes**: Equities, futures, crypto, FX
**Timeframes**: 1d, 1w+

**Key Concepts**: Rank all assets in a universe by past return (typically 12-1 minus 1 month skip). Long top decile, short bottom decile. Rebalance monthly. The canonical momentum anomaly.

- **Why this works institutionally**: Slow information diffusion across thousands of securities. Institutional position-building takes time, creating persistent price trends. Behavioral anchoring and disposition effect (retail sells winners too early) creates continuation. Cross-sectional application diversifies idiosyncratic risk.
- **Data needed**: Cross-sectional price data for broad universe, market cap data, liquidity filters, trading cost model
- **Test method**: Jegadeesh-Titman methodology; portfolio sorts; Fama-MacBeth regression; test in live vs paper; transaction cost model with realistic spreads
- **Failure modes**: Momentum crashes (sharp reversals in bear markets); factor crowding; regime change to mean-reversion; turnover cost erosion; survivorship bias in universe construction
- **Mechanism**: Cross-sectional ranking exploits relative, not absolute, price movements. The short leg is as important as the long leg. Risk-adjusted momentum (residual momentum) is the professional refinement.
- **Pro equivalents**: Residual momentum, industry-neutral momentum, risk-parity momentum overlay
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-PR-002: Time-Series Momentum (TSMOM / CTA)

**Edge source**: trend
**Asset classes**: Futures (equity indices, bonds, commodities, FX), crypto
**Timeframes**: 1d, 1w+

**Key Concepts**: For each asset, if its own past return (12-month) is positive, go long; if negative, go short. Volatility-scale each position. Portfolio of 50-100+ uncorrelated futures contracts. Managed-futures/CTA approach.

- **Why this works institutionally**: Trend persistence across diverse asset classes is one of the most robust anomalies. Works across decades and geographies. Diversification across 50-100 markets reduces individual asset risk. Volatility targeting normalizes risk contributions. Systematic execution removes emotional interference.
- **Data needed**: Futures price history (front contracts), contract rollover data, volatility estimation (EWMA, GARCH), correlation matrix
- **Test method**: Moskowitz et al. (2012) methodology; test across asset classes; vol-targeted vs equal-weighted; rolling window sensitivity; regime segmentation
- **Failure modes**: Sharpe ratio deterioration after popularity; whipsaw in choppy regimes; correlation spikes during crises (diversification fails when needed most); drawdown periods of 2-5 years
- **Mechanism**: Institutional investors move slowly; macro trends persist due to slow policy transmission, capital flow inertia, and herding. Volatility scaling improves Sharpe by reducing large positions in volatile regimes.
- **Pro equivalents**: CTA systematic trend following, managed futures funds, risk parity with trend overlay
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]], [[Professional Equivalent Map]]

---

### S-PR-003: Factor Models

**Edge source**: statistical, structural, behavioral
**Asset classes**: Equities
**Timeframes**: 1d, 1w+

**Key Concepts**: Multi-factor model to predict cross-sectional expected returns. Factors include: value (B/M, E/P), momentum, quality (ROE, leverage), size, low volatility, investment. Portfolio weighted by factor scores.

- **Why this works institutionally**: Factors capture systematic risk premia that persist because they compensate for risk (CAPM extension) and/or behavioral biases (overreaction/underreaction). Academic foundation dating to Fama-French (1992). Institutional adoption allows factor timing, tilting, and smart-beta product creation.
- **Data needed**: Fundamental data (financial statements), price data, factor construction methodology, universe definition, transaction cost model
- **Test method**: Fama-MacBeth regressions; factor long-short portfolio tests; out-of-sample factor performance; factor correlation analysis; regime sensitivity
- **Failure modes**: Factor crowding (too much capital chasing same factors); factor timing is unreliable; definition changes (e.g., value metric evolution); regime-dependent factor performance
- **Mechanism**: Factors work through risk compensation (value = financial distress risk premium) and behavioral channels (momentum = slow diffusion, overreaction). Multi-factor combination diversifies factor-specific risk.
- **Pro equivalents**: Multi-factor smart-beta, factor tilts in institutional portfolios, AQR-style factor investing
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]], [[Master Index]]

---

### S-PR-004: Residual Momentum

**Edge source**: statistical, behavioral
**Asset classes**: Equities
**Timeframes**: 1d, 1w+

**Key Concepts**: Momentum after removing factor exposures. Regress returns on known factors (market, size, value, quality); use residuals as momentum signal. Isolates momentum not explained by factor exposures.

- **Why this works institutionally**: Standard momentum loads on other factors. Residual momentum removes these exposures, creating a purer signal. Reduces unintended factor bets. Provides diversification from standard momentum. Blitz & Kaul (2022) show improved risk-adjusted returns.
- **Data needed**: Factor returns, asset returns, factor model specification, regression framework
- **Test method**: Two-stage: (1) estimate factor model, (2) test residual momentum; compare to raw momentum; factor neutrality verification; walk-forward
- **Failure modes**: Model specification error (wrong factors); residual estimation error; overfitting factor model; crowding as this approach gains popularity
- **Mechanism**: Residual momentum captures idiosyncratic information not explained by systematic factors. This information diffuses slowly and creates continuation.
- **Pro equivalents**: Factor-neutral momentum, idiosyncratic momentum strategies, hedge fund cross-sectional stat arb
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]], [[Feature Engineering Catalog]]

---

### S-PR-005: Short-Term Reversal

**Edge source**: mean_reversion, liquidity, behavioral
**Asset classes**: Equities, futures, crypto
**Timeframes**: 1m - 1d

**Key Concepts**: Assets that moved sharply over short horizon (1-5 days) revert in subsequent period. Long recent losers, short recent winners (horizon = days, not months).

- **Why this works institutionally**: Liquidity-driven price impact causes temporary deviations from fundamental value. Market makers and liquidity providers profit from absorbing order flow. Institutional selling/bouncing creates temporary pressure. Behavioral overreaction at short horizons. Jegadeesh (1990) documented this.
- **Data needed**: High-frequency or daily price data, volume, liquidity measures, spread data
- **Test method**: Short-horizon return predictability test; portfolio sort by 1-5 day return; include transaction costs; slippage modeling
- **Failure modes**: Transaction costs overwhelm edge at short horizon; momentum regime dominates; liquidity dry-up during reversals; crowding reduces edge
- **Mechanism**: Short-term reversal is primarily a liquidity phenomenon. Large orders move price temporarily; patient capital absorbs the move. Works best in less liquid names but requires careful cost modeling.
- **Pro equivalents**: Statistical arbitrage mean reversion, market making spread capture, liquidity provision strategies
- **Cross-links**: [[Failure Mode Catalog]], [[Professional Equivalent Map]], [[Schema and Taxonomy]]

---

### S-PR-006: Statistical Arbitrage (Pairs/Basket)

**Edge source**: statistical, mean_reversion
**Asset classes**: Equities, ETFs, futures
**Timeframes**: 1d, 4h

**Key Concepts**: Long/short portfolio of securities identified as cointegrated or having mean-reverting spread. Trade when spread deviates from historical mean. Scale portfolio across hundreds of pairs.

- **Why this works institutionally**: Diversification across hundreds of pairs reduces individual pair risk. Statistical rigor in pair selection (cointegration tests, rolling stability). Real-time monitoring of pair degradation. Professional execution on both legs reduces slippage. Gate and Froot (1993) pioneered.
- **Data needed**: Price data for large universe, cointegration testing framework, spread calculation, execution infrastructure for paired legs
- **Test method**: Cointegration stability test (Engle-Granger/Johansen); spread mean-reversion test; portfolio diversification benefit; transaction cost model with paired execution
- **Failure modes**: Structural breaks breaking cointegration; crowding in popular pairs; correlation spikes in crisis (pairs diverge); execution risk if one leg fails
- **Mechanism**: Economic linkage between securities creates long-run equilibrium. Temporary deviations are mean-reverting. Portfolio approach diversifies idiosyncratic pair risk.
- **Pro equivalents**: Statistical arbitrage funds, pairs trading desks, multi-pair mean-reversion systems
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-PR-007: PCA Statistical Arbitrage

**Edge source**: statistical, structural
**Asset classes**: Equities, ETFs, futures
**Timeframes**: 1d, 4h

**Key Concepts**: Use PCA to identify principal components of return covariance. Trade residual returns (after removing top PCs as common factors). Long predicted residual movers, short predicted residual decliners.

- **Why this works institutionally**: PCA identifies systematic risk factors without pre-specifying them (unlike Fama-French). Residuals after removing common factors contain idiosyncratic signal. Reduces model specification risk. PCA is data-driven factor discovery.
- **Data needed**: Cross-sectional return matrix, PCA implementation, residual calculation, prediction model for residuals
- **Test method**: Component selection test (how many PCs?); residual return predictability; compare to factor-model approach; walk-forward with rolling PCA
- **Failure modes**: PCA components are not economically interpretable; component instability over time; overfitting to noise; high-dimensional PCA requires more data than available
- **Mechanism**: Returns are driven by common factors (captured by top PCs) plus idiosyncratic components (residuals). If residuals are predictable, there is alpha after controlling for systematic risk.
- **Pro equivalents**: Quantitative stat arb funds, eigenportfolios, factor-neutral residual trading
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]], [[Feature Engineering Catalog]]

---

### S-PR-008: ETF Constituent Arbitrage

**Edge source**: structural, statistical
**Asset classes**: Equities, ETFs
**Timeframes**: 1d, intraday

**Key Concepts**: Trade the mispricing between an ETF and its underlying constituents when NAV diverges from market price. Long cheap side, short expensive side. Edge source: ETF creation/redemption mechanism and liquidity segmentation.

- **Why this works institutionally**: APs (authorized participants) have creation/redemption rights but are capacity-constrained. ETFs tracking illiquid indices trade at premia/discounts. Index rebalancing creates predictable flows. ETF market structure creates temporary mispricing windows.
- **Data needed**: ETF prices, constituent prices, NAV/creation unit data, rebalancing schedule
- **Test method**: NAV premium/discount analysis; creation/redemption flow modeling; event-driven test around rebalancing dates
- **Failure modes": Arbitrage window closes quickly (requires fast execution); APs eliminate edge for liquid ETFs; creation/redemption mechanism works for liquid ETFs narrowing edge
- **Mechanism**: ETFs are baskets of securities with structural creation/redemption mechanisms. When basket and ETF prices diverge, arbitrage should close the gap. The edge exists in timing and execution speed.
- **Pro equivalents**: ETF arbitrage desks, AP trading desks, index arbitrage
- **Cross-links**: [[Schema and Taxonomy]], [[Professional Equivalent Map]], [[Failure Mode Catalog]]

---

### S-PR-009: Futures Carry

**Edge source**: carry, structural
**Asset classes**: Futures (commodities, equity indices, bonds, FX)
**Timeframes**: 1d, 1w+

**Key Concepts**: Long futures in backwardation (downward-sloping term structure, positive roll yield), short futures in contango (upward-sloping, negative roll yield). Harvest roll yield differential.

- **Why this works institutionally**: Futures carry is a well-documented risk premium in commodities (Gorton & Rouwenhorst). Producers hedge (short futures creating backwardation), creating natural long-side roll yield. Systematic across 50+ commodity markets. Institutional scale allows diversification across entire commodity complex.
- **Data needed": Futures term structure data (multiple contract months), roll schedule, contango/backwardation measurement
- **Test method": Long-backwardation/short-contango portfolio; roll yield calculation; term structure slope signal; compare to momentum overlay
- **Failure modes": Carry crashes during supply shocks; backwardation/contango shifts; roll timing errors; crowding in popular carry signals
- **Mechanism": Roll yield is structural — it comes from futures pricing mechanics, not price direction. Producers' hedging needs create systematic term structure slopes.
- **Pro equivalents**: Commodity carry funds, CTA carry overlay, roll yield harvesting strategies
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]], [[Master Index]]

---

### S-PR-010: FX Carry

**Edge source**: carry
**Asset classes**: FX
**Timeframes**: 1d, 1w+

**Key Concepts**: Long high-yielding currencies, short low-yielding currencies. Harvest interest rate differential. Classic carry trade.

- **Why this works institutionally**: Interest rate differentials are persistent and forward-looking. Carry works across decades but has fat left tail (crash risk). Institutional scale allows diversification across 20+ currency pairs. Risk management through vol scaling and crash protection.
- **Data needed": Interest rates by currency, FX spot/forward rates, inflation data for real rates
- **Test method": Long high-rate/short low-rate portfolio; test across decades; include crash periods (2008); vol scaling adjustment
- **Failure modes": Carry crashes during risk-off (2008, 2020); FX reversals; intervention by central banks; political events; transaction costs in EM currencies
- **Mechanism": Interest rate parity should eliminate carry returns, but deviations persist due to risk premia and slow capital reallocation. The "peso problem" — rare crashes make apparent returns misleading.
- **Pro equivalents": FX carry funds, global macro carry overlay, central bank divergence trades
- **Cross-links**: [[Failure Mode Catalog]], [[Schema and Taxonomy]], [[Professional Equivalent Map]]

---

### S-PR-011: Commodities Term Structure

**Edge source**: carry, structural
**Asset classes**: Commodities futures
**Timeframes**: 1d, 1w+

**Key Concepts**: Trade the term structure of commodity futures directly. Analyze and trade contango/backwardation patterns across the entire curve, not just front-back spread.

- **Why this works institutionally": Term structure contains information about supply/demand expectations, storage costs, and convenience yields. Different points on the curve may signal different things. Institutional commodity traders model full term structure, not just near/far spread.
- **Data needed": Full futures curve data (multiple contract months), storage cost estimates, convenience yield estimates
- **Test method": Term structure shape classification; predictability from curve slope/curvature; compare to simple carry signal
- **Failure modes": Curve dynamics change rapidly; storage/convenience yield estimation error; illiquid far-month contracts
- **Mechanism": Futures curve shape reflects market expectations of future supply/demand. Steep backwardation signals tightness; steep contango signals surplus. Trading curve shape changes captures this information.
- **Pro equivalents": Commodity curve trading, spread trading desks, physical commodity arbitrage
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]], [[Professional Equivalent Map]]

---

### S-PR-012: Rates Curve Trading

**Edge source**: carry, structural, informational
**Asset classes**: Government bonds, interest rate futures, swaps
**Timeframes**: 1d, 1w+

**Key Concepts**: Trade the shape of the yield curve. Steepening/flattening trades relative to expected changes. Butterfly trades to isolate curve segments.

- **Why this works institutionally": Yield curves reflect monetary policy expectations, inflation, and growth forecasts. Professional rates traders have access to central bank communications, dealer flow information, and economic models. Curve dynamics are more predictable than outright rate direction.
- **Data needed": Yield curve data (multiple tenors), swap rates, economic indicators, central bank communication
- **Test method": Curve shape classification; steepener/flattener predictability; event studies around Fed announcements; butterfly spread analysis
- **Failure modes": Central bank intervention distorts curve; QE/QT programs mechanically reshape curves; sudden policy pivots; liquidity in far end of curve
- **Mechanism": Yield curve shape is driven by term premium, expectations, and liquidity segments. Changes in these drivers create opportunities for curve positioning.
- **Pro equivalents": Rates relative value, curve trading desks, macro funds trading monetary policy
- **Cross-links**: [[Schema and Taxonomy]], [[Professional Equivalent Map]]

---

### S-PR-013: Volatility Risk Premium (VRP)

**Edge source**: volatility, carry, behavioral
**Asset classes**: Options, volatility indices (VIX), variance swaps
**Timeframes**: 1d, 1w+

**Key Concepts**: Systematic shorting of volatility (selling options, shorting VIX futures). IV consistently exceeds RV due to volatility risk premium. Harvest the premium systematically.

- **Why this works institutionally": VRP is one of the most persistent premiums across asset classes. Investors pay for insurance (puts), creating systematic overpricing of IV vs RV. Institutional scale allows portfolio-wide vol selling with tail risk management. Systematic VRP harvesting with crash protection generates steady returns.
- **Data needed": Options chain data, IV surfaces, historical vol, VIX futures, crash risk measures
- **Test method": Short vol portfolio returns; crash-adjusted returns; compare IV to realized; test different strikes/expiries; tail risk modeling
- **Failure modes": Tail risk (vol spikes wipe out months of premium); negative skew; margin requirements; black swan events; model risk in vol estimation
- **Mechanism": Investors are risk-averse and willing to overpay for portfolio insurance. This creates a persistent premium for volatility sellers. The edge is statistical but with fat left tail.
- **Pro equivalents": Volatility risk premium funds, variance swap dealers, systematic vol selling with tail hedging
- **Cross-links**: [[Failure Mode Catalog]], [[Validation Framework]], [[Schema and Taxonomy]]

---

### S-PR-014: Index Rebalancing Arbitrage

**Edge source**: structural
**Asset classes**: Equities, ETFs, index futures
**Timeframes**: Intraday, 1d

**Key Concepts**: Trade around index rebalancing events. Index funds must buy added stocks and sell deleted stocks at specific times. Front-run or trade alongside these flows.

- **Why this works institutionally": Index rebalancing creates predictable, inelastic demand for added stocks and selling for deleted stocks. The demand is mechanical (passive funds must trade). Size of flow is estimable from index methodology and assets tracking the index. Institutions model exact rebalance quantities and timing.
- **Data needed": Index methodology, rebalancing schedule, constituent changes, AUM of tracking funds, estimated flow sizes
- **Test method": Event study around rebalancing dates; measure price impact; test pre-announcement vs announcement vs effective date windows
- **Failure modes": Edge competed away by other index arbitrageurs; timing uncertainty; price impact from competing flows; front-running by other institutions
- **Mechanism": Index funds must trade at specific times regardless of price. This inelastic demand creates temporary price movements. The edge comes from knowing the demand before execution.
- **Pro equivalents": Index arbitrage desks, ETF creation/redemption strategies, flow-based trading
- **Cross-links**: [[Schema and Taxonomy]], [[Professional Equivalent Map]], [[Failure Mode Catalog]]

---

### S-PR-015: Merger Arbitrage

**Edge source**: structural, informational, statistical
**Asset classes**: Equities
**Timeframes**: Days to months

**Key Concepts**: Long target, short acquirer in announced M&A deals. Earn the spread between current price and deal price. Edge source: Deal completion probability assessment.

- **Why this works institutionally": M&A spreads are essentially probability-weighted returns. Professional M&A arb teams have legal, regulatory, and financial analysis capabilities to assess deal completion probability. Diversification across dozens of deals reduces single-deal risk. Risk-adjusted returns from probability edge, not deal prediction.
- **Data needed": Deal announcements, deal terms (price, ratio, conditions), regulatory timeline, competitor analysis, financial modeling
- **Test method": Historical deal completion rate analysis; spread vs expected return analysis; portfolio diversification benefit; deal break analysis
- **Failure modes": Deal break risk (catastrophic loss); regulatory rejection; financing failure; competing bids; market risk on short leg
- **Mechanism": M&A spreads reflect market-assessed deal break probability. Professional edge comes from better probability estimation, not from knowing deal outcome.
- **Pro equivalents": Merger arbitrage desks, event-driven hedge funds, special situations strategies
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]], [[Master Index]]

---

### S-PR-016: Post-Earnings Announcement Drift (PEAD)

**Edge source**: behavioral, informational
**Asset classes**: Equities
**Timeframes**: 1d - 3m

**Key Concepts**: Stocks with positive earnings surprises continue to outperform for weeks/months after announcement. Underreaction creates persistent drift.

- **Why this works institutionally": PEAD is one of the strongest and most robust anomalies across markets and decades. Ball & Brown (1968), Bernard & Thomas (1989 and 1990). Market underreacts to earnings information due to anchoring, attention constraints, and slow institutional position building. Professionals exploit this with faster signal processing and NLP on earnings calls.
- **Data needed": Earnings announcements, surprise measures (actual vs consensus), analyst estimates, guidance
- **Test method": Event study methodology; portfolio sort by surprise magnitude/standardized unexpected earnings; test drift window; include transaction costs
- **Failure modes": Earnings quality issues (restatements); guidance effect; attention anomaly decay; crowding in systematic PEAD strategies
- **Mechanism": Investors underreact to earnings information. This is behavioral — they anchor to prior estimates and adjust slowly. The drift persists because position adjustment takes time.
- **Pro equivalents": Earnings momentum strategies, fundamental quant strategies, alternative data earnings analysis
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]], [[Professional Equivalent Map]]

---

### S-PR-017: Insider Buying

**Edge source**: informational, behavioral
**Asset classes**: Equities
**Timeframes**: 1w+

**Key Concepts**: Track insider buying/selling transactions. Insiders buying their own stock signals confidence. Aggregate signals across multiple insiders for stronger signal.

- **Why this works institutionally": Insiders have superior information about their company's prospects. Legal insider buying (Form 4 filings) is public but processing lag creates edge. Cluster buying (multiple insiders buying) is strongest signal. Must control for routine selling (10b5-1 plans) vs discretionary buying.
- **Data needed": Insider transaction filings (SEC Form 4), insider identity, transaction size vs holdings, 10b5-1 plan status
- **Test method": Event study on filing dates; cluster analysis (multiple insiders); abnormal return calculation; control for insider role and transaction context
- **Failure modes": Insider signal noise (many buy signals are weak/irrelevant); filing lag (information is public when filed); insider motives vary (confidence vs diversification vs compensation)
- **Mechanism": Insiders buy because they believe stock is undervalued or prospects are positive. The signal works because information processing is slow and most retail ignores filings.
- **Pro equivalents": Alternative data insider tracking, fundamental quant signals, governance analysis
- **Cross-links**: [[Schema and Taxonomy]], [[Professional Equivalent Map]], [[Failure Mode Catalog]]

---

### S-PR-018: Share Buyback / Repurchase Programs

**Edge source**: structural, informational, statistical
**Asset classes**: Equities
**Timeframes**: 1w+

**Key Concepts**: Companies announcing or executing share buybacks see positive returns. Buybacks signal management confidence and create mechanical demand as shares are retired.

- **Why this works institutionally": Buybacks have two effects: signaling (management believes stock is undervalued) and mechanical demand (actual share reduction reduces supply). Research shows announcement effect and ongoing buyback execution effect. Professionals track actual execution pace vs authorized programs.
- **Data needed": Buyback announcements, authorization amounts, actual repurchase data, buyback yield, timing analysis
- **Test method": Event study on announcement; ongoing buyback yield signal; compare announced vs executed; test buyback intensity signal
- **Failure modes": Announcements without execution (management signaling without action); buyback timing is often poor (buy at highs); market already prices in large buyback programs
- **Mechanism": Buybacks reduce share count (increasing EPS mechanically) and signal management confidence. The mechanical demand from actual buyback execution creates ongoing support.
- **Pro equivalents": Corporate action strategies, shareholder yield investing, capital return analysis
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]], [[Professional Equivalent Map]]

---

### S-PR-019: 13F Clone

**Edge source**: informational, behavioral
**Asset classes**: Equities
**Timeframes**: Quarterly (13F reporting)

**Key Concepts**: Replicate top hedge fund/manager portfolios from SEC 13F filings. Follow money managers with proven track records.

- **Why this works institutionally": (Actually, it doesn't well — this is the caution.) 13F filings are lagged by 45 days, only cover long equity positions, and don't reflect hedging. The edge is limited to specific contexts: managers with concentrated, infrequently-changing portfolios. Cloning broad, frequent traders doesn't work.
- **Data needed": SEC 13F filings, manager performance history, portfolio holdings, filing dates
- **Test method**: Portfolio replication from filing data; lag-adjusted backtest (can only trade 45+ days after quarter end); compare to benchmark; test specific successful managers
- **Failure modes": 45-day filing lag makes information stale; 13Fs only show long equity positions (no shorts, options, or derivatives); herd behavior as many clone same managers; manager style drift
- **Mechanism": Only works for concentrated, infrequently-changing portfolios of managers with genuine skill. The 45-day lag eliminates most edge. Cloning is more useful as research input than as a trading strategy.
- **Pro equivalents**: Manager research (not cloning), fund-of-funds analysis, manager selection strategies
- **Cross-links**: [[Schema and Taxonomy]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

### S-PR-020: Execution Alpha

**Edge source**: liquidity, structural, order_flow
**Asset classes**: All (requires execution infrastructure)
**Timeframes**: Intraday, tick

**Key Concepts**: Achieve better execution prices than VWAP/twapped benchmarks through intelligent order slicing, timing, venue selection, and algorithms. Edge from execution quality, not from signal.

- **Why this works institutionally": Large orders impact price. Professional execution algorithms (VW algos, TWAP, implementation shortfall, adaptive) minimize market impact. Execution alpha is the difference between naive execution and optimized execution. Savings of 1-10bps on billions = significant alpha.
- **Data needed": Order flow data, venue data, spread data, historical execution data, market impact models
- **Test method": Execution analysis (VWAP/twapped benchmark comparison); algorithmic vs manual execution; market impact modeling; venue analysis
- **Failure modes": Not available to retail traders (execution infrastructure requirement); latency disadvantage; venue complexity; regulatory constraints (Reg NMS, MiFID II)
- **Mechanism": Market impact is real and unavoidable for large orders. Intelligent execution reduces this impact. The "alpha" comes from being a smarter trader of execution, not from predicting price.
- **Pro equivalents": Execution services desks smart order routers, algorithmic execution platforms
- **Cross-links**: [[Schema and Taxonomy]], [[Professional Equivalent Map]], [[Failure Mode Catalog]]

---

### S-PR-021: Market Making

**Edge source**: liquidity, order_flow
**Asset classes**: Equities, options, futures, crypto
**Timeframes**: Tick, intraday

**Key Concepts**: Provide liquidity by posting bid/ask quotes. Earn spread. Manage inventory risk. Edge from providing a service (liquidity) that others need.

- **Why this works institutionally": Market makers earn bid-ask spread by providing continuous quotes to the market. Edge comes from: (1) inventory management skill, (2) adverse selection modeling (avoiding being picked off by informed traders), (3) rebate capture from exchanges, (4) speed advantage. Professional market makers use sophisticated inventory models and adverse selection detection.
- **Data needed": Order book data (L2/L3), tick data, queue position, exchange rules, rebate structure
- **Test method": Quote profitability analysis; inventory risk modeling; adverse selection measurement; rebate impact; compare to passive investment
- **Failure modes": Adverse selection (trading against informed flow); inventory risk (stuck on wrong side); latency competition (HFT outpaces); regulatory requirements; capital requirements for quoting
- **Mechanism": Market makers provide a service. Spread is compensation for providing liquidity and bearing inventory risk. Edge comes from better inventory management and adverse selection avoidance than competitors.
- **Pro equivalents": Market making firms (Citadel Securities, Jump Trading, Virtu), exchange-designated market makers, liquidity provision strategies
- **Cross-links**: [[Validation Framework]], [[Schema and Taxonomy]], [[Failure Mode Catalog]]

---

### S-PR-022: Order Flow Imbalance (OFI)

**Edge source**: order_flow, informational
**Asset classes**: Equities, futures, crypto
**Timeframes**: Tick, 1s, 1m

**Key Concepts**: Track buy vs sell order flow imbalance at the order book level. Predict short-term price direction from order flow asymmetry. Cont model: OFI predicts price changes.

- **Why this works institutionally": Order flow contains information about supply/demand at the microsecond to second level. OFI is one of the most predictive variables for short-term price changes (Cont et al., 2014). Professional HFT firms build entire strategies on OFI. Retail traders cannot compete at tick/second level due to infrastructure limitations.
- **Data needed": Order book data (L2/L3), tick-by-tick trades, OFI calculation framework
- **Test method": OFI vs price change regression; predictive power at different horizons; compare to random walk; include latency modeling
- **Failure modes": Latency disadvantage (HFTs are microseconds ahead); data cost and quality; spoofing and order manipulation; edge decays rapidly as more participants use it
- **Mechanism": Order flow imbalance reflects net buying/selling pressure. When there are more buy than sell orders at the best levels, price tends to increase. This is mechanical, not behavioral.
- **Pro equivalents": HFT order flow strategies, market microstructure research desks, flow toxic detection
- **Cross-links**: [[Schema and Taxonomy]], [[Professional Equivalent Map]], [[Failure Mode Catalog]]

---

### S-PR-023: Liquidity Provision

**Edge source**: liquidity, structural
**Asset classes**: All, especially crypto, options
**Timeframes**: Intraday

**Key Concepts": Provide liquidity in markets where others need it. DeFi: LP in AMM pools. Traditional: limit order posting, dark pool liquidity. Earn spread/rebate for providing quotes.

- **Why this works institutionally": Liquidity providers earn compensation for taking the other side of trades. In DeFi, LPs earn fees from traders. In traditional markets, market makers earn rebates. Edge comes from understanding liquidity dynamics, inventory risk, and fee structures.
- **Data needed": Order flow data, fee structures, liquidity metrics, AMM formula (for DeFi)
- **Test method": LP return vs passive holding; impermanent loss analysis; fee income modeling; compare to market making
- **Failure modes": Impermanent loss in AMMs; toxic order flow; inventory risk; fee competition; smart contract risk (DeFi); regulatory risk
- **Mechanism": Liquidity provision earns compensation for bearing inventory risk and providing continuous quotes. The edge is in managing that risk intelligently.
- **Pro equivalents": Market making, DeFi liquidity mining, exchange liquidity programs
- **Cross-links**: [[Schema and Taxonomy]], [[Validation Framework]], [[Professional Equivalent Map]]

---

### S-PR-024: Latency-Sensitive Microstructure

**Edge source**: order_flow, liquidity, structural
**Asset classes**: Equities, futures, crypto
**Timeframes**: Tick, sub-millisecond

**Key Concepts: Exploit latency advantages in order routing, execution, and market data processing. Edge from speed, not prediction. Includes latency arbitrage, queue position strategies, and cross-venue arbitrage.

- **Why this works institutionally**: Speed is an edge in itself. Firms with faster data feeds, colocation, and optimized code can execute before others. Latency arbitrage: see price change on one venue, trade on lagging venue. Queue position: be first in line at a price level. Cross-venue: exploit price differences across exchanges. This requires infrastructure investment in millions.
- **Data needed**: Tick data from multiple venues, network latency measurement, colocation infrastructure, direct data feeds
- **Test method": Latency measurement, cross-venue price difference analysis, queue position modeling, compare execution timestamps
- **Failure modes": Infrastructure cost ($10M+ for competitive setup); regulatory scrutiny (SEC on latency arbitrage); race to the bottom (speed advantage decays as everyone gets faster); not feasible for retail
- **Mechanism": When prices change, they don't change simultaneously across all venues. The time difference (microseconds to milliseconds) creates an opportunity for fast traders. This is purely structural, not predictive.
- **Pro equivalents": HFT firms, proprietary trading with colocation, latency arbitrage strategies
- **Cross-links**: [[Schema and Taxonomy]], [[Failure Mode Catalog]], [[Professional Equivalent Map]]

---

## Summary: Why Professional Strategies Require Institutional Resources

### The Institutional Edge Is Not the Idea

The strategies above are not secret. They are documented in academic literature. The institutional advantage comes from:

1. **Data breadth**: Access to tick data, order book L2/L3 data, alternative data, options chains, full futures curves — not just OHLCV
2. **Execution infrastructure**: Sub-millisecond execution, smart order routing, algorithmic execution, colocation
3. **Capital scale**: Diversification across 50-200+ instruments; ability to absorb carry crashes and tail events
4. **Risk management**: Real-time risk systems, stress testing, scenario analysis, position limits
5. **Research platform**: Quantitative researchers, data scientists, and computing infrastructure to continuously research and validate
6. **Regulatory access**: Some strategies require institutional market access (dark pools, block trades, swaps)

### Retail Reality Check

For a retail trader attempting to replicate these strategies:

- **TSMOM/Factor**: Feasible with ETFs/futures, but must control costs and survive drawdowns
- **Stat Arb**: Very difficult without cross-sectional data infrastructure
- **Execution Alpha/Market Making/OFI**: Not feasible — requires infrastructure and capital
- **VRP**: Feasible but tail risk management is the challenge
- **13F Clone**: Feasible but edge is minimal due to lag

See [[Professional Equivalent Map]] for the full retail → professional translation.

---

## Cross-References

- [[Schema and Taxonomy]] — 24-field card schema
- [[Validation Framework]] — Required tests per difficulty level
- [[Professional Equivalent Map]] — Retail → professional translation
- [[Failure Mode Catalog]] — 11 failure types
- [[Feature Engineering Catalog]] — For ML transition
- [[Master Index]] — Full encyclopedia overview
- ← Parent vault: [[Trading-System-Build-Doctrine]]
