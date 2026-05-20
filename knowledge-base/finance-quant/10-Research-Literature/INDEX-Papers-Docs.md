# Research Papers & Official Docs — Index

**Scope**: Embedded PDFs, linked papers, and official documentation relevant to algorithmic trading, quantitative finance, and backtesting discipline.

---

## Embedded PDFs (Verified & Available Locally)

### Overfitting & Multiple Testing
| Paper | Authors | Year | Pages | Link | Why It Matters |
|---|---|---|---|---|---|
| Deflated Sharpe Ratio | Bailey & López de Prado | 2014 | 22 | [[Research-Deflated-Sharpe-Ratio]] | Corrects for selection bias, backtest overfitting, non-normality |
| Probability of Backtest Overfitting | Bailey et al. | 2015 | 34 | [[Research-PBO]] | PBO, CSCV, strategy-selection controls |
| Statistical Overfitting | Bailey et al. | 2014 | 10 | [[Research-Statistical-Overfitting]] | Why repeated strategy search inflates apparent performance |
| Sharpe Ratio Efficient Frontier | Bailey & López de Prado | 2012 | 46 | | Performance metric geometry and Sharpe frontier diagnostics |
| Cross-Section of Expected Returns | Harvey, Liu & Zhu | 2016 | 64 | [[Research-Harvey-Liu-Zhu]] | Factor discovery thresholds; multiple-comparison discipline |

### Market Properties & Stylized Facts
| Paper | Authors | Year | Pages | Why It Matters |
|---|---|---|---|---|
| Empirical Properties of Asset Returns | Cont | 2001 | 14 | Fat tails, volatility clustering, nonlinear dependence |
| Revisiting Cont's Stylized Facts | Ratliff-Crain et al. | 2023 | 31 | Modern sanity check using intraday equity data |

### Technical Analysis & Pattern Recognition
| Paper | Authors | Year | Pages | Why It Matters |
|---|---|---|---|---|
| Foundations of Technical Analysis | Lo, Mamaysky & Wang | 2000 | 61 | Pattern-recognition baseline without retail folklore |
| Simple Technical Trading Rules | Brock, Lakonishok & LeBaron | 1992 | 35 | Baseline MA and trading-range-rule tests |

---

## Official Documentation (Source-Linked)
| Resource | URL |
|---|---|
| QuantConnect/LEAN Engine | https://www.quantconnect.com/docs/v2/lean-engine/ |
| LEAN Algorithm Framework | https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/ |
| LEAN CLI | https://www.quantconnect.com/docs/v2/lean-cli |
| NautilusTrader Backtesting | https://nautilustrader.io/docs/latest/concepts/backtesting/ |
| NautilusTrader Live | https://nautilustrader.io/docs/latest/concepts/live/ |
| vectorbt | https://vectorbt.dev/ |
| Backtrader | https://www.backtrader.com/ |
| Databento API | https://databento.com/docs |
| OpenBB ODP | https://docs.openbb.co/odp |
| Alpaca Trading API | https://docs.alpaca.markets |
| IBKR TWS Order Submission | https://interactivebrokers.github.io/tws-api/ |
| CCXT | https://docs.ccxt.com/ |

---

## Cross-Link Map
- Overfitting papers → [[Overfit-Detection-Metrics]], [[Metric-Formulas]]
- Stylized facts papers → [[Data-Quality-Checks]], [[Heatmap-Time-Regime]]
- Technical analysis papers → [[Trading-System-Build-Doctrine]], [[Agentic-Workflow-Patterns]]
- Broker API docs → [[Broker-API-Comparison]]
- Framework docs → [[Framework-Comparison-Selection]], [[LEAN-Reference]], [[NautilusTrader-Reference]]

---

## Companion: Quant Research Library (Batch 2 — Research Scaffold)

**Location**: `raw-ingest/quant_research_library/`

**Scope**: 162 indexed papers across 18 topic groups (A-R) covering reverse-engineering investor decision logic, IRL, LLM trading agents, market microstructure, ML asset pricing, options, behavioral finance, hedge-fund/13F literature, technical analysis, prediction markets, and pattern recognition. Includes READ_ORDER.md (8-stage reading sequence), SYNTHESIS.md (intellectual lineages and open questions), PAYWALL_SUMMARY.md (access strategy), MASTER_INDEX.md (sortable source-of-truth), and a download tool (`download_open_pdfs.py`).

**Vault Notes**:
- [[Research-Read-Order-Guide]] — the 8-stage reading sequence with rationale per stage
- [[Research-Library-Synthesis]] — intellectual lineage map, cross-domain connections, open research questions
- [[Research-Paywall-Strategy]] — what's accessible vs. blocked, legal workaround strategies

**Relationship to this file**: Batch 1 embedded papers (overfitting, stylized facts, TA foundations) overlap with the library's priority-1 papers in Groups M, O, and R. The library expands coverage to demand-system pricing, IRL, LLM agents, microstructure, options, behavioral finance, and hedge-fund analysis — areas not represented in the embedded PDFs. Treat this file as the **core verified paper index** and the library notes as the **broader research scaffold** pointing to 100+ additional papers to acquire.

---

*Source manifest and PDF verification status tracked in original library.*
