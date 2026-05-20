# FMP Point-In-Time Policy

## Rules
- Earnings calendar DATE: usable before event if provided by calendar API
- Actual EPS: ONLY usable after report date
- Earnings surprise: ONLY usable after report date
- Analyst rating changes: ONLY usable after publishedDate timestamp
- News: ONLY usable after publishedDate timestamp
- Financial statements: ONLY usable after filing/report timestamp

## Validation Checks
- No pre-event use of actual_eps
- No pre-event use of eps_surprise
- No future news timestamp
- No future analyst downgrade timestamp
- No calendar date use if date source missing

## Status: POLICY_DEFINED — enforced in client and feature pipeline
