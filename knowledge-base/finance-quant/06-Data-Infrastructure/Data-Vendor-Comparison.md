# Data Vendor Comparison

Comparison of three data vendors and research tools: Databento, OpenBB, and Polygon/Massive-style APIs.

## Comparison Matrix

| Vendor | Best Use | Strengths | Limitations |
|---|---|---|---|
| **Databento** | Serious historical market data with institutional-quality schemas. APIs and reference data included. | Best-in-class data quality, DBN schema, tick/quote/orderbook depth, historical replay support | Premium pricing, complex pricing model that rewards efficient data usage |
| **OpenBB** | Data connector/research layer. Building financial dashboards, agent workflows, quick access to multiple datasets. | Unified API to dozens of data sources, Python-first, extensible, good for research prototyping | Abstraction layer may hide quality differences between underlying sources. Not optimized for execution-critical latency. |
| **Polygon / Massive-style APIs** | Accessible retail-to-prosumer equities, options, crypto data. REST-first, documentation-driven. | Easy onboarding, good documentation, reasonable pricing for retail, real-time and historical options data | Data quality varies by symbol and date. Corporate action handling may have edge cases. Must validate before relying on execution-sensitive strategies. |

## Evaluation Criteria

Do not compare vendors only by price. Evaluate across all dimensions:

- **Asset coverage:** Equities, options, futures, FX, crypto. Does the vendor cover all asset classes you need?
- **Historical depth:** How far back does historical data go? Some vendors have gaps around 2008, delistings, or exchange migrations.
- **Tick/quote/bar availability:** Does the vendor offer tick-level data, NBBO quotes, consolidated bars, or only end-of-day?
- **Corporate actions:** How are splits, dividends, and spin-offs handled? Is raw or adjusted data available?
- **Options chain completeness:** Does historical options data include open_interest, volume, greeks, and full chain snapshots?
- **Rate limits:** API call limits, concurrent connection limits, bulk download restrictions.
- **Latency:** How fresh is real-time data? Millisecond-level for Databento vs seconds for Polygon REST APIs.
- **Adjustment policies:** Price adjustment continuity for backtesting. Surv-bias handling.
- **Delisting coverage:** Does historical data include delisted securities, or does it suffer from survivorship bias?
- **API reliability:** Uptime SLAs, error handling, retry behavior, and data gap detection tools.

## Implications

- **Databento for execution-quality research:** When strategy edge depends on precise orderbook dynamics, spread capture, or tick-level signal generation, Databento's schema-aware data is worth the premium.
- **OpenBB as a research accelerator:** Use OpenBB to quickly pull fundamentals, macro data, and cross-asset data for hypothesis generation. Don't rely on it for latency-sensitive backtesting.
- **Polygon for retail-level backtesting:** Good enough for daily/minute bar strategies on liquid equities and options. Always validate with [[Data-Quality-Checks]] before deploying capital.
- **Multi-vendor strategy:** No single vendor is best for everything. Use Databento for high-fidelity historical data, Polygon for real-time streaming during live trading, and OpenBB for macro/fundamental overlays.

## Failure Modes

- **Survivorship bias:** Data vendors that exclude delisted companies produce inflated backtest results. Check delisting coverage before trusting long-horizon equity results.
- **Silent data gaps:** Vendors occasionally have missing days or hours (exchange holidays, technical issues). Always validate data continuity before backtesting.
- **Adjustment inconsistencies:** Vendor A adjusts for splits one way and Vendor B adjusts another. Cross-vendor comparison on the same symbol can produce different backtest results.
- **Rate-limit-induced data corruption:** Aggressive parallel downloading can trigger rate limits, resulting in partial data sets without clear error signals.
- **Options chain gaps in Polygon:** Historical options data may have gaps for certain strikes or expiries. Validate chain completeness before deploying options strategies.
- **OpenBB quality masking:** The abstraction layer can hide that underlying data source A has 10% fewer data points than source B. Always audit the underlying source quality.

## Cross-Links

- [[Framework-Comparison-Selection]] — data needs drive framework choice
- [[Data-Quality-Checks]] — validate any vendor data before backtesting
- [[Data-Pipeline-Architecture]] — integrate vendor data into the pipeline
- [[Feature-Leakage-Prevention]] — vendor data quirks that cause look-ahead bias
- [[Schema-Catalog]] — data schemas that vendor data should conform to
- [[Aggregated-Data-Tactics]] — tactics for using data effectively
- [[Broker-API-Comparison]] — broker data may substitute for or complement vendor data
- [[LEAN-Local-Backtesting]] — LEAN requires local data setup with vendor data
