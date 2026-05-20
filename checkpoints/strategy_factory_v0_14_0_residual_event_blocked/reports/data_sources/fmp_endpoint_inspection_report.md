# FMP Endpoint Inspection Report

Status: SPEC_INSPECTION_ONLY — no API calls made

## Endpoint Categories

| Category | Endpoint | Fields Expected | Known-At-Time Risk | Use | Status |
|---|---|---|---|---|---|
| Earnings Calendar | /v3/earning_calendar | date, symbol, eps, epsEstimated, time | Calendar date usable before event. Actual EPS usable only after. | Block entries 5d before | READY |
| Earnings Surprises | /v3/earnings-surprises | symbol, date, actualEarningResult, estimatedEarning | Usable only after report date | Classify event severity | READY |
| Company Profile | /v3/profile/:symbol | sector, industry, mktCap, exchange | Static/slow-moving. Usable at time. | Sector mapping, liquidity seg | READY |
| Stock News | /v3/stock_news | symbol, publishedDate, title, text | Usable only after timestamp | Warn of repricing risk | READY |
| Analyst Changes | /v4/upgrades-downgrades | symbol, publishedDate, newGrade, action | Usable only after timestamp | Block after downgrade | READY |
| Financial Statements | /v3/income-statement | date, revenue, eps | Usable only after filing date | Fundamental context | READY |
| Index Constituents | /v3/sp500_constituent | symbol | Static | Universe segmentation | READY |

## Point-In-Time Rules
- Actual EPS: only after report date (not before)
- Earnings surprise: only after report date
- Analyst changes: only after publishedDate timestamp
- News: only after publishedDate timestamp

## Status
ALL_ENDPOINTS_SPEC_INSPECTED — no API calls performed
