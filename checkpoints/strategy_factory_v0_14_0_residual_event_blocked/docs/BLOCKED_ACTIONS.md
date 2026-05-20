# Blocked Actions

These actions are EXPLICITLY BLOCKED until further validation:

## Production & Trading
- NO live trading on any signal
- NO production strategy migration
- NO production dependency on FMP
- NO Alpaca live orders

## Research
- NO trend-extension rescue (retuning, threshold mining, seed hunting)
- NO FMP alpha use (FMP is event blocker only)
- NO standalone alpha claims on any current signal
- NO validation claims without full event context

## Repository Safety
- NO API keys in repo (FMP_API_KEY, ALPACA keys, etc.)
- NO large cache data in git
- NO raw API responses committed
- NO secrets in docs or configs

## Language
- NO "profitable" claims
- NO "validated" claims
- NO "ready to trade" claims
- NO "high confidence" claims
- NO "guaranteed" claims
