# Qullamaggie-Style Strongest Mover Watchlist — Source Specification

**Source**: User-provided batch 4, deep dive document on momentum-first watchlist generator
**Date**: 2026-05-17
**Type**: Leader discovery / candidate generation system (NOT a complete trading strategy)
**Core Thesis**: Rank liquid universe by multi-horizon momentum strength → find consolidation/tightness → trade defined breakouts. Screener creates candidates only; tightness + breakout rules determine actionability.

---

## Full Specification (Preserved from User Message)

### System Architecture
Two-layer design:
1. **Momentum Screener**: Ranks stocks by 1W/1M/3M/6M strength using TC2000 extension formulas
2. **Tightness + Breakout Filter**: Determines actionability; not part of the screener itself

### TC2000 Formulas
- `C/AVGC5` — 1-week extension ratio
- `C/AVGC25` — 1-month extension ratio
- `C/AVGC66` — 3-month extension ratio
- `C/AVGC126` — 6-month extension ratio

Uses price extension (C/AVGC) rather than raw momentum (C/Cn) because extension normalizes for scale and represents deviation from recent average, not just distance traveled.

### Liquidity Filters
- Price > $5
- ADV20 > 300K shares
- Dollar volume > $20M
- ADR20% > 3–5%

### ADR Calculation
```
ADR20% = 100 * AVG(H-L, 20) / C
```

### Tightness Features
- `base_width_10` / `base_width_20`: range contraction over 10/20 bars
- `near_3m_high`: proximity to 66-bar high
- `range_contraction`: ratio of short-to-long window ranges
- `volume_dryup`: 5-day avg volume / 20-day avg volume
- `trend_support`: AVGC25 > AVGC66 confirms underlying trend intact

### Candidate Taxonomy
1. **Fresh Mover** — high 1W score, breakout in progress
2. **Persistent Leader** — high on all timeframes, already extended
3. **Base Builder** — moderate momentum, very tight, volume dry-up
4. **Blowoff/Avoid** — extreme 1W score, parabolic, wide ranges

### Ranking Weights
40% momentum + 25% tightness + 15% liquidity + 10% ADR + 10% proximity

### Entry Logic (Separate from Screener)
- Breakout above tight range high
- Volume confirmation (> 1.5× average)
- Tight stop below range low
- Must pass tightness filter at time of entry

### Failure Modes (7)
1. Buying extension without tightness
2. Survivorship bias in threshold calibration
3. Volume dry-up misread as accumulation
4. False breakouts from low-float stocks
5. Regime blindness (no market-context awareness)
6. Sector clustering concentrated risk
7. Earnings/event risk masquerading as momentum

### Key Insight
The screener creates candidates only. Tightness + breakout rules determine actionability. Buying the strongest mover without a tightness filter = buying extension, not a setup.

---

**Synthesized notes**:
- [[strongest-mover-screener]] — full vault note with formulas, pipeline, failure modes
