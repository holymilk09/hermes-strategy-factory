# Feature Leakage Danger List

- Earnings surprise using final reported data before actual release timestamp.
- Macro data using revised value instead of first release.
- Index constituent membership from future date.
- Market cap/liquidity screen based on future values.
- Analyst ratings scraped without timestamp.
- News sentiment assigned to wrong timestamp.
- Options chain using contracts unavailable at decision time.
- Adjusted prices changing historical signal thresholds.
- Resampled bars that include future intraday data.
