# Qullamaggie-Style Strongest Mover Screener

**Leader discovery / candidate generation system** — NOT a complete trading strategy. The screener identifies stocks with sustained multi-horizon momentum; tightness filters and breakout rules determine actionability separately.

**Core Thesis**: Rank liquid universe by 1W/1M/3M/6M strength → find consolidation/tightness → trade defined breakouts. Screener creates candidates; tightness + breakout rules determine entry.

**Source**: [[qullamaggie-strongest-mover-spec]] (user-provided batch 4)
**Date**: 2026-05-17

---

## 1. Concept Overview

The system has two distinct layers:

| Layer | Purpose | Signal |
|---|---|---|
| Momentum screener | Find stocks that are actually moving and have institutional demand | Relative strength across timeframes |
| Tightness + breakout filter | Find stocks that are resting/consolidating before continuation | Range contraction, volume dry-up, proximity to high |

**Critical rule**: A stock with the highest momentum score but no tightness = buying an extension, not a setup. The screener identifies demand; tightness confirms supply absorption. They are separate signals that must both be present for actionability.

---

## 2. TC2000 Momentum Formulas

The system uses **price extension ratios** rather than raw momentum (C / Cn) because extension normalizes for scale and directly represents deviation from recent average price.

| Metric | TC2000 Formula | Window | Purpose |
|---|---|---|---|
| 1W strength | `C / AVGC5` | 5-bar average | Short-term burst, freshness filter |
| 1M strength | `C / AVGC25` | 25-bar average | Recent trend strength |
| 3M strength | `C / AVGC66` | 66-bar average | Medium-term trend (primary strength signal) |
| 6M strength | `C / AVGC126` | 126-bar average | Long-term trend persistence |

**Why C/AVGC, not C/Cn**:
- `C/AVGC25` = price relative to its 25-period average — answers "is price above its recent norm, and by how much?"
- `C/C25` = percent change — answers "how much has price moved in 25 bars?" — conflates old moves with current extension
- Extension ratio treats "price 10% above 25-bar avg" identically regardless of whether it happened over 3 bars or 25 bars
- Better for cross-stock comparability (a $20 stock and $200 stock both at 1.12x extension are equally extended)

**Thresholds (typical)**:
- Strongest movers: 1M > 1.10, 3M > 1.20, 6M > 1.30 (20-50% above 3M/6M averages)
- Fresh mover spike: 1W > 1.05 with 1M not yet extreme

---

## 3. Liquidity Filters

Liquidity must be checked before momentum scoring to avoid illiquid traps.

| Filter | Threshold | Rationale |
|---|---|---|
| Price | > $5 | Eliminates penny stocks and OTC |
| ADV20 | > 300K shares | Ensures tradable volume on average |
| Min dollar volume | > $20M today | Guarantees execution safety right now |
| ADR20% | > 3-5% | Minimum daily range — needs enough movement to generate profit |

**Why ADV20**: 20-day average daily volume captures recent liquidity without being dominated by a single anomalous day. The 300K threshold ensures the average participant can enter/exit without market impact.

**Why dollar volume matters**: A stock trading 500K shares at $2 has less liquidity than 100K shares at $50. Dollar volume (price × volume) filters both dimensions simultaneously.

---

## 4. ADR Calculation

**Formula**: `ADR20% = 100 * AVG(H-L, 20) / C`

- `AVG(H-L, 20)` = 20-day average of daily high-minus-low range
- Divided by current price = normalizes as a percent
- Minimum threshold of 3-5% ensures the stock moves enough intraday to reach targets

**Implication**: Stocks with ADR < 2% are too slow — even a good setup may not generate enough range to cover spreads and reach targets. ADR 5-8%+ is ideal for swing trading (provides room for stops below and targets above).

---

## 5. Tightness Features

Tightness identifies consolidation within the context of prior strength. Six features combine into a composite score:

### 5.1 base_width_10
`100 * (MAX(H, 10) - MIN(L, 10)) / C`
- 10-day range as percentage of current price
- Lower = tighter (consolidation = good)
- Typically < 8% is tight, < 5% is very tight

### 5.2 base_width_20
Same over 20-day window. Confirms tightness is not just a 1-week pause.

### 5.3 near_3m_high
`C / MAX(H, 66)` or `C / MAX(Highest High in 66 bars)`
- Proximity to recent highs
- > 0.90 = within 10% of 3M high = poised for breakout
- < 0.80 = too far from high = momentum may have faded

### 5.4 range_contraction
`base_width_10 / base_width_20` or volatility ratio
- < 0.7 = 10-day range is 70% smaller than 20-day range = contraction within larger range
- Indicates energy building before expansion

### 5.5 volume_dryup
`AVG(V, 5) / AVG(V, 20)` or current volume relative to norm
- < 0.5 = volume has dried up to half its recent average
- Selling pressure exhausted — the calm before breakout
- MUST be accompanied by tight price action (dry volume with wide ranges = distribution, not accumulation)

### 5.6 trend_support
`AVGC25 > AVGC66` or `C > AVGC25`
- Confirms underlying trend is still intact
- Short-term MA above medium-term MA = trend not broken
- Without this, tightness could be terminal distribution rather than accumulation

### 5.7 Composite Tightness Score
```
tightness_score = (
    0.30 * (inverse_normalize(base_width_10))
    + 0.25 * (inverse_normalize(base_width_20))
    + 0.20 * (normalize(near_3m_high))
    + 0.15 * (normalize(inverse_base_width_ratio))
    + 0.10 * (normalize(volume_dryup_inverse))
)
```

---

## 6. Candidate Type Taxonomy

Every stock falls into one of four categories based on momentum × tightness profile:

### 6.1 Fresh Mover
- Highest 1W strength score
- 1M/3M/6M moderate but rising
- Price just broke out of multi-week base
- Tightness: may not be tight yet (just broke out)
- **Action**: Wait for pullback and re-tightening, or accept a wider stop on the breakout

### 6.2 Persistent Leader
- High on ALL timeframes (1W through 6M)
- Already ran 30-100%+
- May or may not be tight
- **Action**: If tight → classic Qullamaggie breakout candidate. If extended → avoid or use very tight stop

### 6.3 Base Builder
- Moderate 1M/3M strength
- Very tight base_width scores
- Volume dry-up present
- Near 3M high
- **Action**: Pre-breakout watchlist — highest R:R potential if it breaks

### 6.4 Blowoff / Avoid
- 1W score extremely high (>1.20+)
- 6M already extended
- Wide daily ranges, high volume
- **Action**: Avoid — buying the parabolic top. Distribution likely imminent.

---

## 7. Ranking System

The composite rank combines five dimensions with weighted scoring:

| Component | Weight | What It Rewards |
|---|---|---|
| Momentum score | 40% | Multi-timeframe strength (1W-6M composite) |
| Tightness score | 25% | Consolidation quality and proximity to high |
| Liquidity score | 15% | ADV, dollar volume, spread quality |
| ADR score | 10% | Sufficient daily range for targets |
| Proximity score | 10% | Nearness to 52-week/3M highs |

```
composite_rank = (
    0.40 * momentum_zscore
    + 0.25 * tightness_score
    + 0.15 * liquidity_zscore
    + 0.10 * adr_percentile
    + 0.10 * proximity_to_high
)
```

**Why 40% momentum**: The system is momentum-first — you want leaders, not laggards. But tightness at 25% ensures you're not just buying extensions.

---

## 8. Python Pipeline

### 8.1 build_strongest_mover_watchlist
```python
def build_strongest_mover_watchlist(df: pd.DataFrame, date: str) -> pd.DataFrame:
    """
    Takes OHLCV dataframe with columns: symbol, date, open, high, low, close, volume
    Filters, scores, and ranks stocks for strongest mover watchlist.
    """
    d = df.copy()

    # --- Liquidity filters ---
    d['adv20'] = d.groupby('symbol')['volume'].transform(lambda x: x.rolling(20).mean())
    d['dollar_vol'] = d['close'] * d['volume']
    d = d[d['close'] > 5]
    d = d[d['adv20'] > 300_000]
    d = d[d['dollar_vol'] > 20_000_000]

    # --- Momentum extension ratios ---
    d['ext_1w']  = d.groupby('symbol')['close'].transform(lambda x: x / x.rolling(5).mean())
    d['ext_1m']  = d.groupby('symbol')['close'].transform(lambda x: x / x.rolling(25).mean())
    d['ext_3m']  = d.groupby('symbol')['close'].transform(lambda x: x / x.rolling(66).mean())
    d['ext_6m']  = d.groupby('symbol')['close'].transform(lambda x: x / x.rolling(126).mean())

    # --- ADR ---
    d['adr20_pct'] = 100 * d.groupby('symbol').apply(
        lambda g: g.rolling(20).apply(lambda w: (w['high'] - w['low']).mean() / w['close'].iloc[-1])
    )

    # --- Filter on ADR ---
    d = d[d['adr20_pct'] >= 3.0]

    # --- Tightness features ---
    d['base_w10'] = d.groupby('symbol').apply(
        lambda g: 100 * g.rolling(10).apply(lambda w: (w['high'].max() - w['low'].min()) / w['close'].iloc[-1])
    )
    d['base_w20'] = d.groupby('symbol').apply(
        lambda g: 100 * g.rolling(20).apply(lambda w: (w['high'].max() - w['low'].min()) / w['close'].iloc[-1])
    )
    d['near_3m_high'] = d.groupby('symbol')['close'] / d.groupby('symbol')['high'].transform(
        lambda x: x.rolling(66).max()
    )
    d['vol_dryup'] = d.groupby('symbol')['volume'].transform(
        lambda x: x.rolling(5).mean() / x.rolling(20).mean()
    )
    d['trend_ok'] = d.groupby('symbol')['close'].transform(lambda x: x.rolling(25).mean()) > \
                    d.groupby('symbol')['close'].transform(lambda x: x.rolling(66).mean())

    # --- Composite scoring ---
    d['momentum_score'] = (0.3*d['ext_1w'] + 0.25*d['ext_1m'] + 0.25*d['ext_3m'] + 0.2*d['ext_6m']).rank(pct=True)
    d['tightness_score'] = score_tightness(d)  # sub-function
    d['liq_score'] = d['dollar_vol'].rank(pct=True)
    d['adr_score'] = d['adr20_pct'].rank(pct=True)
    d['prox_score'] = d['near_3m_high'].rank(pct=True)

    d['composite'] = (0.40*d['momentum_score'] + 0.25*d['tightness_score'] +
                       0.15*d['liq_score'] + 0.10*d['adr_score'] + 0.10*d['prox_score'])

    # --- Return latest date, top ranked ---
    latest = d[d['date'] == date].sort_values('composite', ascending=False)
    return latest[['symbol', 'composite', 'ext_1w','ext_1m','ext_3m','ext_6m',
                    'base_w10','near_3m_high','vol_dryup','adr20_pct']].head(50)
```

### 8.2 get_top_movers_for_date
```python
def get_top_movers_for_date(df: pd.DataFrame, date: str, n: int = 20) -> pd.DataFrame:
    """
    Convenience wrapper: filter to date, apply liquidity gates, compute
    momentum scores only, return top N by pure momentum (no tightness).
    Used for separate "pure momentum" view vs "tightness-prioritized" view.
    """
    d = df[df['date'] == date].copy()
    # Apply same liquidity filters
    d['adv20'] = d.groupby('symbol')['volume'].transform(lambda x: x.rolling(20).mean())
    d = d[(d['close'] > 5) & (d['adv20'] > 300_000)]
    d['ext_1m'] = d['close'] / d['close'].shift(1).rolling(25).mean()
    d['ext_3m'] = d['close'] / d['close'].shift(1).rolling(66).mean()
    d['momentum_rank'] = (0.5*d['ext_1m'].rank(pct=True) + 0.5*d['ext_3m'].rank(pct=True))
    return d.nlargest(n, 'momentum_rank')
```

---

## 9. Entry Logic (Separate System)

Entry rules are **not part of the screener** — they belong to the breakout strategy layer. The screener produces candidates; the entry system decides actionability.

### Breakout Entry Conditions:
- Price breaks above tight range high (e.g., 10-day or 20-day high)
- Volume on breakout day > 1.5× average volume
- ADR supports reaching target before stop is hit
- **Not** extended on 1W at time of entry (1W extension ratio < 1.08)

### Stop Logic:
- Initial stop: below tight range low (e.g., 10-day low or 5× ATR below entry)
- Tight ranges allow tight stops → favorable R:R
- Trail stop using [[trailing-stop-methods]] (e.g., 10EMA, swing lows)

### Trigger Validation:
- Must pass tightness filter (base_width_10 < 8%) OR be a fresh breakout (1W spike with pullback)
- Volume confirms — not a low-volume false break

---

## 10. Key Concepts

- **Candidate vs. Setup**: The screener generates candidates. A candidate becomes a setup only when tightness + breakout conditions are met simultaneously.
- **Extension vs. Strength**: Raw momentum (C/Cn) measures how far price has traveled. Extension ratios (C/AVGC) measure how far price deviates from its recent average. The screener uses extension because it normalizes across stocks and better represents "overbought vs. trending."
- **Tightness is the gate**: Without tightness, momentum screening = chasing parabolic moves. Tightness indicates supply absorption and energy building.
- **Timeframe hierarchy**: 1W = freshness, 1M = recent trend, 3M = core strength, 6M = persistence. The weighting (30/25/25/20) balances recency with durability.
- **Volume dry-up is necessary but insufficient**: Low volume with wide ranges = distribution, not consolidation. Tightness must be confirmed by both price range AND volume.

---

## 11. Implications for Trading Systems

- **Separation of concerns**: The screener must remain pure — do not conflate candidate quality with entry quality. A rank-50 candidate with perfect tightness may be a better setup than a rank-1 candidate that's fully extended.
- **Dual output**: Maintain both a "pure momentum" ranking (top leaders) and a "momentum + tightness" ranking (actionable setups). They serve different purposes.
- **Pre-market workflow**: Screener runs after close → watchlist produced → next day monitor for breakouts from tight bases.
- **Regime dependency**: In broad market downtrends, even the strongest movers fail breakouts. Combine with [[regime-detection-features]] to gate candidate generation.
- **Portfolio construction**: Ranking provides ordering, but position sizing must account for ADR (wider ADR needs smaller size for same dollar risk) and correlation (multiple tech stocks in same sector = correlated risk).
- **Walk-forward revalidation**: Extension thresholds that work in high-vol regimes may be too tight in low-vol regimes. Recalibrate thresholds periodically using [[epoch-learning-retraining]].

---

## 12. Failure Modes

### 12.1 Buying Extension Without Tightness
Highest momentum score often means "most extended." Without tightness confirmation, entries catch blowoff tops rather than breakout continuations. The screener must be paired with a tightness filter at equal or higher importance.

### 12.2 Survivorship Bias in Thresholds
Extension thresholds (1.10, 1.20, 1.30) calibrated on recent bull markets may be far too aggressive for neutral/bear regimes. Fixed thresholds produce zero candidates in bear markets, which is a sign to recalibrate, not to lower standards to find bad candidates.

### 12.3 Volume Dry-Up Misread as Accumulation
Low volume can mean selling pressure exhausted (good) OR no institutional interest at all (bad). Volume dry-up must be preceded by a sustained uptrend and accompanied by tightness. Without the preceding trend, dry volume means the stock is dead, not coiling.

### 12.4 False Breakouts from Low Float
Tight bases in low-float stocks breakout violently but reverse immediately. The ADV20 and dollar volume > $20M filters catch most of these, but borderline cases (ADV 300-500K) still slip through. Higher ADV threshold or float filter adds robustness.

### 12.5 Regime Overlook
In a broad bear market or high-vol selloff, the strongest movers from the prior week are often the hardest fallers. The screener has no market-regime awareness. Must be gated by [[regime-detection-features]] or market-index filter.

### 12.6 Sector Clustering
Top 20 strongest movers are often 12-15 stocks from the same sector (e.g., all semis, all biotech). Ranking without diversification produces concentrated risk. Apply sector caps or de-duplication in the final watchlist.

### 12.7 Earnings / Event Risk
Stocks often make explosive moves immediately before earnings. The screener captures these as "strongest movers" but they are gambling candidates, not setups. An earnings calendar filter is essential.

---

## 13. Cross-Links

- [[qullamaggie-strongest-mover-spec]] — source specification
- [[regime-detection-features]] — market regime gates for candidate generation
- [[cross-asset-feature-engineering]] — cross-asset signals can supplement momentum scoring
- [[data-quality-checks]] — data integrity for OHLCV feeds feeding the screener
- [[data-pipeline-architecture]] — production deployment of the scoring pipeline
- [[logging-audit-monitoring]] — track screener predictions vs. realized breakouts
- [[epoch-learning-retraining]] — recalibrate thresholds across market epochs
- [[trailing-stop-methods]] — exit management for breakout trades
- [[feature-leakage-prevention]] — avoid look-ahead bias in rolling calculations
- [[build-doctrine]] — systematic development of the screener as a reusable component
- [[momentum-factor-premium]] — academic foundation for momentum as persistent anomaly

---

## Anti-Cookie-Cutter Insight

> **Buying the strongest mover without a tightness filter = buying extension.** The screener identifies demand; tightness confirms supply absorption. They are separate signals. Many traders conflate "top-ranked by momentum" with "best setup" — but the rank-1 strongest mover is often the most extended and least actionable. The system only works when both layers are applied: momentum finds leaders, tightness finds entries.
