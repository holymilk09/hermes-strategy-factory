# Qullamaggie Strongest Mover Screener — Candidate Generation System

**Type**: Leader Discovery / Momentum Screening
**Core Thesis**: Rank liquid universe by multi-horizon strength -> find consolidation/tightness -> trade defined breakouts. The screener creates candidates only; tightness + breakout rules determine actionability.
**Professional Equivalent**: Cross-sectional momentum candidate generation + volatility contraction breakout filter

---

## 1. Why This Works (Academic Foundation)
Based on **Cross-Sectional Momentum** (Jegadeesh & Titman): buying recent winners and selling recent losers generates positive returns over 3-12 month holding periods.
- Time-series momentum shows return persistence over 1-12 months across futures markets.
- Retail version manually/algorithmically finds tight setups -> trades breakouts.

---

## 2. Core TC2000 Formulas
Crucial distinction: `C/AVGCn` is **Price Extension**, while `C/Cn` is **Raw Momentum**.

| Horizon | Extension Formula (Sustained) | Raw Momentum Formula (Point-to-Point) |
|---|---|---|
| 1 Week | `C / AVGC5` | `100 * (C / C5 - 1)` |
| 1 Month | `C / AVGC25` | `100 * (C / C25 - 1)` |
| 3 Month | `C / AVGC66` | `100 * (C / C66 - 1)` |
| 6 Month | `C / AVGC126` | `100 * (C / C126 - 1)` |

**Interpretation**: Extension measures sustained elevation above average price. Raw momentum measures absolute return. The screener prefers Extension to find stocks where demand is persistently strong.

---

## 3. Liquidity & Universe Filters
Do not scan blindly. Apply these minimum filters to avoid noise:
- **Price**: > $5
- **Average Volume (20d)**: > 300,000 shares
- **Dollar Volume (20d)**: > $20M
- **Exchange**: NYSE / NASDAQ / AMEX only
- **Exclude**: Warrants, rights, preferreds, illiquid OTC names

---

## 4. ADR (Average Daily Range) Filter
ADR ensures the stock has enough movement to justify the risk.
`ADR20% = 100 * AVG(H - L, 20) / C`
- **> 3%**: Conservative liquid momentum
- **> 4%**: Stronger swing candidate (Qullamaggie standard)
- **> 5%**: High movement; higher opportunity but higher danger

---

## 5. Candidate Classification
Once ranked, candidates fall into 4 types:

| Type | Profile | Action | Risk |
|---|---|---|---|
| **A: Fresh Mover** | Strong 1W + 1M, not yet 3M/6M | Watch for catalyst/EP | Pump/exhaustion |
| **B: Persistent Leader** | Strong 1M + 3M + 6M | Institutional momentum | Already extended |
| **C: Base Builder** | Strong 3M/6M, cooling 1M/1W | Tight consolidation | Breakdown risk |
| **D: Blowoff / Avoid** | Extreme 1W, climax volume | Wait for rest | High volatility/news risk |

---

## 6. Tightness: The Real Filter
"Strongest movers" get you onto the list. "Tightness" decides if it is actionable.

| Feature | Formula | Interpretation |
|---|---|---|
| **10-day base width** | `(MAXH10 - MINL10) / C` | Smaller = tighter |
| **20-day base width** | `(MAXH20 - MINL20) / C` | Larger base view |
| **Near 3M High** | `C / MAXH66` | > 0.85 indicates strength |
| **Volume Dry-Up** | `AVGV5 / AVGV20` | < 1.0 indicates less activity |
| **Range Contraction** | `AVG(H-L,5) / AVG(H-L,20)` | < 1.0 indicates tightening |
| **Trend Support** | `C > EMA10 > EMA20` | Short-term structure intact |

Practical Rules: Price within 5-15% of recent high; higher lows; range getting smaller; volume drying up.

---

## 7. Python Implementation Spec
```python
def get_top_movers(df, date, top_n=25):
    day = df[df['date'] == date].copy()
    # Apply filters
    day = day[(day['close'] >= 5) & (day['dollvol20'] >= 20_000_000) & (day['adr20'] >= 3)]
    
    t1 = day.nlargest(top_n, 'strength_1w')
    t2 = day.nlargest(top_n, 'strength_1m')
    t3 = day.nlargest(top_n, 'strength_3m')
    t4 = day.nlargest(top_n, 'strength_6m')
    
    merged = pd.concat([t1.assign(src='1w'), t2.assign(src='1m'), ...])
    # De-duplicate and score
    watchlist = merged.groupby('symbol').agg({'src': 'count', ...})
    return watchlist.sort_values(['src', 'strength_3m'], ascending=False)
```

---

## 8. Entry & Risk Logic
**Screener ≠ Buy Signal.** 
- **Entry**: Breakout above 10-day base high.
- **Stop**: Below base low or breakout-day low.
- **Trailing**: Under 10-day/20-day EMA.
- **Invalidation**: Failed breakout + close back inside range.

---

## 9. Validation Design (Backtest)
Do not backtest the screener alone; test the *modules*:
1. **Forward Return Study**: Do top-ranked names actually outperform SPY/Random?
2. **Tightness Study**: Does adding tightness score improve returns vs. just ranking?
3. **Breakout Study**: Does breakout entry improve payoff vs random entry?
4. **Regime Breakdown**: Does it work outside bull markets?

---

*Cross-linked: [[Momentum-Strategies]], [[Volatility-Contraction-Breakouts]], [[Trading-System-Build-Doctrine]]*
