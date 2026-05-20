# Technical Analysis — Academic Evidence Synthesis

## Key Papers

**Foundational Evidence**
- **Brock, Lakonishok & LeBaron (1992)** — *Simple Technical Trading Rules and the Stochastic Properties of Stock Returns*. Journal of Finance. Tested moving-average crossover and trading-range-break rules on DJIA data (1897-1988). Found statistically significant evidence that these rules produce non-random returns. **Caution**: Pre-data-snooping correction era. PAYWALLED.
- **Lo, Mamaysky & Wang (2000)** — *Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation*. Journal of Finance. The legit academic anchor for chart patterns. Converts head-and-shoulders, triangles, etc. into algorithmic pattern detectors. Found some patterns have incremental predictive power. PAYWALLED.

**Data Snooping & Skeptical Controls**
- **Sullivan, Timmermann & White (1999)** — *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*. Journal of Finance. **Mandatory control**. When tested with bootstrap methods that account for searching thousands of rule variants, the Brock et al. results weakened substantially. Shows: if your edge survives only because you searched a huge parameter space, it's not alpha. PAYWALLED.

**Trend Following (Institutional Grade)**
- **Moskowitz, Ooi & Pedersen (2012)** — *Time Series Momentum*. JFE. Not traditional "technical analysis" but provides the rigorous institutional anchor for trend-following signals. Time-series momentum (lookback vs holdback) persists across 58 asset classes over 25+ years. Far more credible than retail indicator claims. PAYWALLED.

**Surveys**
- **Park & Irwin (2007)** — *What Do We Know About the Profitability of Technical Analysis?*. Journal of Economic Surveys. Comprehensive survey of 95+ papers. Mixed conclusions: some evidence for FX and commodity technical rules, weaker for equities post-1980s. Suggests market evolution reduces naive TA efficacy over time. PAYWALLED.

**Cross-Market Evidence**
- **Neely, Weller & Dittmar (1997)** — *Is Technical Analysis in the Foreign Exchange Market Profitable?*. JFQA. Finds some evidence for TA profitability in FX, where market structure differs from equities. PAYWALLED.

**Modern Pattern Recognition**
- **Kong et al. (2020)** — *Pattern Recognition in Micro-Trading Behaviors before Stock Price Jumps*. arXiv:2011.04939. **FREE**. Detects patterns in micro-level trading behavior (order flow) before price jumps. Moves beyond chart patterns to observable microstructure features. The modern successor to Lo-Mamaysky-Wang.
- **Pal (2024)** — *LSTM Pattern Recognition in Currency Trading: Identifying Wyckoff Accumulation and Distribution Phases*. arXiv:2403.18839. **FREE**. Applies LSTMs to recognize Wyckoff-style patterns. Novel but lower-anchor quality. Demonstrates sequence model approach to discretionary pattern language. Treat as exploration, not evidence of edge.

## Core Theses

1. **Technical analysis showed early evidence but decayed**: The 1990s findings (Brock et al.) were real in-sample but weakened out-of-sample and after data-snooping correction (Sullivan-Timmermann-White). Markets evolved and arb'd away simple patterns.
2. **Algorithmic validation required**: Lo-Mamaysky-Wang proved that vague chart patterns must be converted into algorithms before they can be tested. This is the minimum bar for any pattern claim.
3. **Trend following survives as institutional TA**: TSMOM/CTA strategies are the one form of "technical analysis" with strong, cross-asset, out-of-sample evidence (Moskowitz et al.).
4. **Market-specific effects matter**: Technical rules may work in some markets (FX, commodities) but not others (equities post-1986). TA profitability is not universal.
5. **Micro-level patterns > chart patterns**: Kong et al. suggests the future is pattern recognition on order-flow and micro-trading behavior, not on candlestick charts.

## Implications for Trading Systems

- **Use TSMOM, not RSI**: If deploying any TA-style signal, the institutional time-series momentum framework (Moskowitz et al.) offers the strongest evidence base.
- **Data-snooping correction is mandatory**: Any technical rule discovery pipeline must include bootstrap/Monte Carlo correction for the number of rules searched (Sullivan-Timmermann-White standard).
- **Algorithmic pattern detection**: Follow Lo-Mamaysky-Wang's approach: define patterns algorithmically before testing. No manual chart annotations.
- **Micro-pattern features**: Kong et al. opens the door to using order-flow micro-patterns as jump-prediction features, bridging the gap between technical analysis and market microstructure.
- **Cross-market testing**: Always test technical rules across multiple markets; if a "universal" indicator only works in one asset class, it's likely a data artifact.

## Failure Modes & Critiques

- **Data snooping is the #1 killer**: Sullivan-Timmermann-White shows most TA rules fail once you correct for multiple testing bias. Any claim from the "indicators" ecosystem (RSI, MACD, Bollinger Bands) that hasn't survived this bar should be treated as hypothesis, not evidence.
- **Decay after publication**: Many patterns lose efficacy after being published — market participants exploit and arb them away.
- **Subjectivity in pattern labeling**: Without algorithmic definitions, different analysts will see different patterns in the same chart. Unfalsifiable.
- **Liquidity regime shifts**: Technical rules calibrated on liquid, normal-market periods fail spectacularly during regime shifts (flash crashes, liquidity evaporation).
- **Low signal-to-noise in equities**: Park-Irwin survey concludes TA evidence is weakest for equities in modern periods. Any equity TA claim faces a high bar.

## Cross-Links

- [[08-Market-Microstructure/01-Order-Flow-Microstructure-Synthesis]] (micro-patterns, Kong 2020, order-flow vs chart patterns)
- [[15-Pattern-Recognition/01-Pattern-Recognition-Synthesis]] (Lo-Mamaysky-Wang pattern recognition, Wyckoff LSTM, stylized facts)
- [[Trading-System-Build-Doctrine]] (TSMOM/CTA strategies, rule testing frameworks)
- [[Core-Statistical-Principles]] (bootstrap methods, data-snooping, multiple testing correction)
