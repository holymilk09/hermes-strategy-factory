# 13F Macro Alt-Data Tactics

Institutional filing data, macroeconomic releases, and alternative datasets require special handling to avoid look-ahead bias and to justify their cost in complexity.

## Key Concepts

### 13F Filings
- **Use case**: slow institutional-positioning studies, crowding proxies, clone strategies
- **Critical limitation**: filings are delayed (45 days after quarter-end) and holdings can change before publication
- **Not a real-time signal**: the market prices in this information well before retail sees it
- **Value**: measuring crowding and institutional conviction over multi-quarter horizons

### Macro Data
- **Use release timestamps**: always use the *first release* value, not revised values
- **Separate concerns**: event avoidance (don't trade around CPI releases) is different from predictive macro modeling (use CPI surprise to predict next-week returns)
- **Revised-data leakage**: macro data gets revised; using the final revised value in backtests creates phantom accuracy

### Alternative Data
Alt data is only justified if **all** of these hold:
1. Timestamp is reliable (you know exactly when the market could have seen this data)
2. Coverage is stable (no gaps, no changing universe definition)
3. Data generation process is understood (you know how the vendor collects and cleans)
4. It can be joined without look-ahead (point-in-time alignment is possible)
5. It improves out-of-sample performance after all costs are accounted for

## Implications

- 13F data is best used as a **secondary filter** (avoid crowded trades) rather than a primary signal (copy institutional moves)
- Macro calendar events should gate entries for short-horizon strategies — a 5-day signal launched 1 day before FOMC is essentially gambling
- Alt data vendors often overstate coverage and quality; independent validation is mandatory
- The 5-criteria filter for alt data eliminates most "interesting but useless" datasets before they enter the pipeline

## Failure Modes

- **13F filing delay ignored**: treating a Q1 filing as available on March 31 when it actually appears mid-May
- **Revised macro data leakage**: using September's revised August NFP number in an August backtest
- **Alt data survivorship bias**: sentiment data on stocks that later delisted — the coverage looked better historically than it would have been live
- **Vendor timestamp bias**: news sentiment assigned with a publication timestamp but the vendor actually processed it hours later
- **Alt data cost blindness**: a dataset costs $50K/year but adds 0.02 Sharpe — the net contribution is negative
- **Crowding misread**: 13F crowding signals can be misleading if the institutions are hedged or using the position for non-directional purposes

## Cross-Links

- [[cross-asset-feature-engineering]] — macro data and event avoidance
- [[Feature Leakage Prevention]] — 13F filing delays and revised macro data are top leakage vectors
- [[regime-detection-features]] — 13F and news sentiment rated low/medium priority, high leakage risk
- [[Regime Detection Features]] — macro release calendar feeds event regime detection
- [[Build Doctrine]] — Phase 1 requires point-in-time feature timestamps; macro and 13F data are common violators
