# Event and Market Arbitrage Strategies

**Source**: Batch 5 — Arbitrage Strategy Research Pack; synthesized from [[Professional-Quant-Strategies]] and research literature.
**Family**: Event-Driven / Market Making Arbitrage (Difficulty 7–10)
**Core Rule**: Event-driven edges are probability-weighted, not deterministic — edge comes from better risk assessment than the market average.
**Key Insight**: The spread in any event arb is the market's collective probability assessment. Your edge is knowing a probability the market doesn't.

---

## EMA-001: Merger Arbitrage

**Edge source**: structural, informational, statistical
**Asset classes**: Equities
**Timeframes**: Days to months

**Core Mechanism**:
When a merger or acquisition is announced, the target stock typically trades below the announced deal price. The difference is the "spread" — a probability-weighted discount reflecting market assessment of deal break risk. Merger arb goes long the target (and short the acquirer if not all-cash), earning the spread upon deal completion.

**Execution Structure**:
1. Identify announced M&A deal with spread
2. Long target company at current market price
3. Short acquirer (in stock or stock/cash mix deals) to hedge market risk
4. Hold until deal closes or breaks
5. If deal closes: earn the spread (target price converges to deal price)
6. If deal breaks: target drops sharply, short leg partially offsets

**Key Variables**:
- **Spread size**: Larger spreads = higher market-assessed break probability, higher potential return if deal succeeds
- **Timeline**: Longer timelines → more time value decay and more uncertainty
- **Deal type**: Cash deals are simpler (just long target); stock deals require shorting acquirer
- **Regulatory scrutiny**: Antitrust risk (FTC, DOJ, EU Commission) is the most common deal killer

**Probability Framework**:
Expected return = (Deal price − Current price) × Prob(close) − (Current price − Crash price) × Prob(break)

The professional edge is in estimating Prob(close) more accurately than the market. This requires:
- Regulatory precedent analysis (how have similar deals been treated?)
- Political landscape assessment (current administration's antitrust posture?)
- Competitive bid analysis (white knight potential)
- Financial modeling (deal financing, buyer solvency, earn-out structure)

**Professional Equivalent**:
- Dedicated M&A arb hedge funds (event-driven strategies)
- Special situations desks at hedge funds (S-PR-015 in [[Professional-Quant-Strategies]])
- Law firms + regulatory analysts providing qualitative probability estimates

**Data needed**: Deal announcement terms, deal price/ratio, regulatory timeline history, antitrust precedent database, competitor landscape, financial statements of both parties
**Failure modes**:
- **Deal break** — the single most catastrophic risk. A deal breaking can cause 30-60% drops in the target
- Regulatory rejection (antitrust, CFIUS, etc.)
- Financing failure (buyer cannot raise capital, credit deterioration)
- Material adverse change clause triggered
- Competing bid changes deal terms unfavorably
- Market risk on short acquirer leg (short leg gains can exceed deal spread)
- Correlated deal breaks during market stress (portfolio diversification fails)

**Anti-Cookie-Cutter Insight**:
Merger arb looks like "easy money" — buy a stock cheap, it goes to the deal price, done. But the returns are left-skewed by construction. A portfolio of 20 deals with 2% average spread and 90% completion probability will show 19 small wins and 1 catastrophic loss. The edge isn't in predicting any single deal; it's in building a diversified portfolio where probability misestimations average out, and in knowing when NOT to take a deal (regulatory overhang, political risk).

---

## EMA-002: ADR Arbitrage (ADR / Underlying Arb)

**Edge source**: structural
**Asset classes**: Equities, ADRs, foreign exchanges
**Timeframes**: Intraday to multi-day

**Core Mechanism**:
American Depository Receipts (ADRs) represent shares of foreign companies traded on US exchanges. Each ADR maps to a specific number of underlying foreign shares (the ratio, e.g., 1 ADR = 5 underlying shares). After currency conversion and ratio adjustment, the ADR price should equal the underlying foreign price. Deviations occur due to:
- Time zone mismatches (US market hours vs. foreign market closed)
- Liquidity differences between the US ADR and foreign underlying
- Currency FX rate changes during trading day
- Information asymmetry (news breaks during foreign market closure)

**Execution Structure**:
1. Calculate fair ADR price: Underlying foreign price × ADR ratio × FX rate
2. When ADR deviates from fair value:
   - ADR overpriced: Short ADR, buy underlying foreign shares
   - ADR underpriced: Buy ADR, short underlying foreign shares
3. Hold until prices converge (often at foreign market open or US market close)
4. Profit = converging price difference minus transaction costs

**Edge Context**:
- **During foreign market hours**: Edge is tight and arb windows close rapidly (both markets pricing simultaneously)
- **During foreign market closure (US hours)**: Edge from information flow — US news affects ADR price before foreign market can react, creating a directional bet rather than pure arb
- **FX hedging**: Currency moves during the holding period can completely erase the arb profit

**Professional Equivalent**:
- Cross-exchange execution desks at global brokerages
- Proprietary trading desks with direct access to multiple exchanges

**Data needed**: ADR chain (ratio, custody details), real-time US price, real-time foreign exchange price, real-time FX spot rate, foreign trading hours calendar, dividend/split calendars for both venues
**Failure modes**:
- **FX risk** is the largest variable. An ADR trade without FX hedging is a currency bet, not an arb
- Transaction costs across two venues + FX spread compound significantly
- Shorting foreign shares may be impossible or extremely expensive
- Settlement timing differences between venues create overnight exposure
- Trading halts on either leg leave one side exposed
- ADR creation/redemption mechanics have costs and minimum unit requirements
- Corporate actions (splits, dividends) differ between ADR and underlying

**Anti-Cookie-Cutter Insight**:
ADR arbitrage during US hours (when foreign markets are closed) is not true arbitrage — it's information-driven directional positioning. The ADR price is reacting to news that the foreign market hasn't priced in yet, and the "arb" is actually a bet on how the foreign market will open. True ADR arb only exists during overlapping trading hours, and those windows are milliseconds thick, captured by HFT infrastructure.

---

## EMA-003: Market Making Arbitrage

**Edge source**: liquidity, order_flow
**Asset classes**: Equities, options, futures, crypto
**Timeframes**: Tick, intraday

**Core Mechanism**:
Market making earns the bid-ask spread by providing continuous two-sided quotes. The edge comes from skillful management of inventory risk and adverse selection — not from predicting price direction. Market makers profit on average because the spread compensates for:
1. Inventory risk (holding a position while quotes update)
2. Adverse selection (being picked off by informed traders)
3. Capital cost of maintaining a book

**Execution Structure**:
1. Post bid and ask quotes at a defined spread
2. When executed on one side, adjust quotes to rebalance inventory
3. Manage net inventory position (limit exposure on any single direction)
4. Capture spread on round-trip trades (buy at bid, sell at ask)
5. Earn exchange rebates for providing liquidity where applicable

**Key Professional Components**:
- **Inventory models**: Avellaneda-Stoikov framework for optimal quoting given inventory
- **Adverse selection detection**: Identifying when order flow is toxic (informed) vs. uninformed
- **Queue position**: Understanding where your order sits in the book and probability of execution
- **Exchange rebate optimization**: Different venues pay different rebates for limit orders

**Spread Determinants**:
Spread width should reflect: (a) volatility of the asset, (b) inventory position, (c) estimated adverse selection probability, (d) exchange rebate rate, (e) minimum tick size

**Professional Equivalent**:
- Citadel Securities, Jump Trading, Virtu, Two Sigma Securities
- Exchange-designated specialists and designated market makers (DMMs)
- Systematic liquidity provision in crypto (market maker bots on CEX and DEX venues)

**Data needed**: Order book data (L2/L3 minimum), tick-level trade data, queue position estimates, exchange rules and rebate schedules, inventory tracking system
**Failure modes**:
- **Toxic order flow** — being on the wrong side of informed traders consistently. This is the silent killer of market makers
- Inventory risk: a directional move against the accumulated inventory creates losses exceeding spread income
- Latency disadvantage: faster competitors front-run quote adjustments and pick off stale quotes
- Adverse selection during news/events: spreads widen but stale quotes get filled before adjustment
- Regulatory requirements: market makers may have quoting obligations that force unfavorable positions
- Infrastructure cost: competitive market making requires sub-millisecond systems; retail cannot compete
- Flash crash scenarios: liquidity providers get wiped out in seconds when all participants withdraw

**Anti-Cookie-Cutter Insight**:
Market making is not trading — it's a service business. You're selling liquidity, not predicting prices. The analogy that works: you're a toll booth. You charge every car (trade) a fee (the spread), and your profit depends on traffic volume, not on where the road goes. The danger is when a speeding truck (informed trader) goes through — you can't charge a toll fast enough, and the truck causes more damage than your tolls. The key metric is not "win rate" but "adverse selection ratio" — what percentage of fills are against informed flow.

---

## Cross-References

- [[Professional-Quant-Strategies]] — S-PR-015: Merger Arb, S-PR-021: Market Making
- [[08-Market-Microstructure-LOB-Execution-Synthesis]] — Order book dynamics, execution costs
- [[Schema-and-Taxonomy]] — Edge taxonomy, difficulty ladder
- [[Failure-Mode-Catalog]] — 11 failure types
- [[Professional-Equivalent-Map]] — Retail to professional translations
- [[Master-Index]] — Full encyclopedia index
