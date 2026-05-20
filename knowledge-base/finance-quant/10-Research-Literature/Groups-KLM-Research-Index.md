# Groups K, L, M — Research Index

**Section**: ML Asset Pricing (K), Options/Volatility (L), Risk/Statistical Modeling (M)
**Updated**: 2026-05-17

---

## Synthesized Notes

| Topic | Note | Source Group | Papers | Key Focus |
|---|---|---|---|---|
| ML Asset Pricing | [[ML-Asset-Pricing-Synthesis]] | K | 8 | IPCA, deep SDF estimation, characteristic interactions, transformer pricing models |
| Options & Volatility | [[Options-Volatility-Synthesis]] | L | 10 | BS → Heston → local vol → rough vol, SVI surface fitting, FFT pricing |
| Risk & Statistical Modeling | [[Risk-Statistical-Modeling-Synthesis]] | M | 9 | Fat tails, DSR, PBO, multiple testing, EVT, purged CV |

**Total indexed across 3 groups**: 27 papers/works (8 free PDF, 4 free landing, 4 paywalled, 5 book, 2 free/preprint)

---

## Cross-Topic Dependencies

```
                    ┌──────────────────────────────┐
                    │   [[Risk-Statistical-Modeling-│
                    │    Synthesis]] (M)             │
                    │   Statistical hygiene layer   │
                    └──────────┬───────────────────┘
                               │ applies to
                      ┌────────┴────────┐
                      ▼                 ▼
┌───────────────────────┐   ┌──────────────────────────┐
│ [[ML-Asset-Pricing-   │   │ [[Options-Volatility-    │
│  Synthesis]] (K)      │   │  Synthesis]] (L)         │
│ Predictive signals    │   │ Pricing & surface signals │
└───────────────────────┘   └──────────────────────────┘
          │                          │
          └────────┬─────────────────┘
                   ▼
        ┌─────────────────────┐
        │ Trading System      │
        │ (signals + risk mgmt)│
        └─────────────────────┘
```

- **M is prerequisite**: Statistical hygiene (DSR, PBO, fat-tail awareness) must be baked into any system using K or L papers. No exceptions.
- **K → M link**: ML predictions need uncertainty bounds → DSR adjustments → risk-aware sizing.
- **L → M link**: Volatility models are complex, multi-parameter systems → model risk → statistical validation.
- **K ↔ L link**: Implied volatility is a key characteristic input for ML asset pricing (K). ML-predicted vol dynamics feed options surface modeling (L).

---

## Key Papers by Access Status

### Free Direct PDF (downloadable)
- Chen, Pelger, Zhu (2024) — Deep Learning in Asset Pricing [K]
- Kelly, Kuznetsov, Malamud, Xu (2025) — AI Asset Pricing Models [K]
- Dixon, Polson, Goicoechea (2022) — Deep Partial Least Squares [K]
- Carr, López de Prado (2014) — Optimal Trading Rules w/o Backtesting [M]
- Ratliff-Crain et al. (2023) — Revisiting Stylized Facts [M]

### Free Landing Page (SSRN/arXiv/ResearchGate)
- Gu, Kelly, Xiu (2020) — Empirical Asset Pricing via ML [K]
- Bayer, Friz, Gatheral (2016) — Rough Volatility [L]
- Cont (2001) — Stylized Facts [M]
- Bailey & López de Prado (2014) — Deflated Sharpe Ratio [M]
- Bailey et al. (2014) — Probability of Backtest Overfitting [M]

### Paywalled (journals)
- Kelly, Pruitt, Su (2019) — Characteristics Are Covariances [K]
- Black & Scholes (1973) — Option Pricing [L]
- Merton (1973) — Rational Option Pricing [L]
- Heston (1993) — Stochastic Volatility [L]
- Dupire (1994) — Pricing with a Smile [L]
- Harvey, Liu, Zhu (2016) — Cross-Section of Returns [M]

### Books
- Nagel (2021) — Machine Learning in Asset Pricing [K]
- Gatheral (2006) — Volatility Surface [L]
- Bergomi (2016) — Stochastic Volatility Modeling [L]
- McNeil, Frey, Embrechts (2015) — Quantitative Risk Management [M]
- López de Prado (2018) — Advances in Financial ML [M]
- López de Prado (2020) — ML for Asset Managers [M]

---

## Reading Priority

1. **Start with M**: Cont (2001) stylized facts → Bailey/López de Prado (DSR, PBO) → Harvey/Liu/Zhu (multiple testing). This is the foundation.
2. **Then K**: Gu/Kelly/Xiu (2020) benchmark → Kelly/Pruitt/Su (IPCA) → Chen/Pelger/Zhu (deep SDF).
3. **Then L**: Gatheral (vol surface book) → Heston (stochastic vol) → Bayer/Friz/Gatheral (rough vol).

---

## Related Vault Notes

- [[Research-Library-Synthesis]] — broader intellectual lineage map across all 18 topic groups
- [[Research-Read-Order-Guide]] — 8-stage reading sequence
- [[Research-Paywall-Strategy]] — access strategies for paywalled papers
- [[INDEX-Papers-Docs]] — core verified paper index with embedded PDFs
- [[Research-Papers-Index]] — 18 papers archived as verified embedded PDFs
