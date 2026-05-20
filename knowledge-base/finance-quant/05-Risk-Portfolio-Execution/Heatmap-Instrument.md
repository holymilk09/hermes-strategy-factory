# Heatmap Instrument Playbook

**Source**: `06_heatmaps_diagnostics/instrument_heatmaps.md`, `06_heatmaps_diagnostics/heatmap_playbook.md`

## Key Concepts

Instrument heatmaps reveal whether a strategy's edge is broad and diversifiable or concentrated in a few symbols. Concentrated edges are inherently less robust than broad ones.

### Views

- Symbol x month -> PnL
- Symbol x regime -> Sharpe
- Sector x month -> PnL
- Liquidity bucket x expectancy
- Spread bucket x slippage
- Market cap bucket x win rate

### Red Flags

- Most profit comes from one symbol.
- Losses are hidden in lower-liquidity instruments.
- Strategy works only in names with unrealistic fills.

### Heatmap Construction

| Axis | Description |
|---|---|
| X-axis | Symbol, sector, or market cap bucket |
| Y-axis | Month/quarter or regime |
| Cell | PnL, Sharpe, win rate, or expectancy |

### Interpretation Rules

- **Broad profit distribution across symbols**: Diversifiable, robust edge.
- **One or two symbols dominate PnL**: Concentrated edge; may reflect idiosyncratic properties rather than generalizable signal.
- **Losses in low-liquidity names**: Fills are unreliable for these instruments; consider filtering by liquidity.
- **Consistent losses in a sector**: The strategy may be systematically exposed to a sector-specific factor you haven't accounted for.

## Implications

1. **Diversification is a robustness test**: If your edge works across 50+ instruments, it's likely capturing a real market phenomenon. If it works only for 3, it's likely noise or idiosyncratic.
2. **Liquidity screening is free alpha** — or rather, avoiding ill-liquid instruments where fills are unreliable prevents negative alpha.
3. **Sector analysis reveals hidden factor exposure** — if your strategy loses in financials and wins in tech, you may accidentally be a tech bet.
4. **Market cap analysis matters** — small-cap instruments often have wider spreads, lower liquidity, and different microstructure behavior.

## Failure Modes / Misinterpretations

- **Survivorship bias in instrument selection**: If your universe includes only currently active symbols, you've excluded the ones that went bankrupt. Backtest with a point-in-time universe.
- **Equal-weight analysis hides concentration**: A heatmap showing 80% of symbols profitable but one symbol generating 10x the total PnL is a concentration warning.
- **Sector classification changes**: A stock changing sector (e.g., company restructuring) breaks sector-level analysis if not handled.
- **Ignoring delisted/merged symbols**: Instrument-level analysis must account for corporate actions; M&A events create outlier returns that distort per-symbol metrics.
- **Liquidity buckets with insufficient observation counts**: A "low liquidity" bucket with only 5 trades cannot support statistical conclusions.

## Cross-Links

- [[Heatmap-Time-Regime]] for regime effects across instruments
- [[Heatmap-Slippage]] for symbol-specific execution quality
- [[Risk-Metrics]] for concentration and sector exposure limits
- [[Heatmap-Trade-Failure]] for which instrument+trade-type combinations fail
