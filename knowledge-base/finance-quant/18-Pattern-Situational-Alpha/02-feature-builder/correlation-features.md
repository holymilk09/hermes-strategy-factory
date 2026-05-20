---
title: Correlation & Cluster Features
pillar: 18
---

# Correlation / Clustering Engine

## Use Cases
1. Find similar stocks for pairs/stat-arb research
2. Avoid overconcentration in one cluster
3. Build sector/theme baskets
4. Create risk-budgeted portfolios
5. Detect regime shifts when correlations spike
6. Find uncorrelated strategy sleeves

## Key Rules
- Correlation is UNSTABLE. Use rolling correlations.
- Use shrinkage estimators if possible.
- Track correlation breakdown by regime.
- Do not assume yesterday's diversification survives a crash.

## Portfolio Construction Connection
López de Prado — Hierarchical Risk Parity: uses hierarchical clustering + correlation structure to address instability/concentration problems in classic quadratic optimizers.

## Metrics Required
- strategy_correlation_matrix
- asset_correlation_matrix (rolling)
- clustered_heatmap
- crisis_correlation (spike detection)
- correlation_by_volatility_regime
- correlation_by_macro_regime

## Diversification Insight
A strategy with lower standalone Sharpe can be valuable if it diversifies the portfolio.
A strategy with high standalone Sharpe can be dangerous if correlated with everything else.
