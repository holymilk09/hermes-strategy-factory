# Research Paywall Strategy

**Scope**: Assessment of what's accessible vs. paywalled across the quant_research library, with legal workaround strategies extracted from PAYWALL_SUMMARY.md and the library's MASTER_INDEX.md.

---

## Overview

The library indexes **162 records** across 18 topic groups. Status distribution:

- **FREE_DIRECT_PDF**: ~62 papers — direct legal PDF URLs captured, ready for download via `download_open_pdfs.py`
- **FREE_LANDING**: ~20 papers — author pages or landing pages exist, PDF likely retrievable
- **PREPRINT_ONLY**: ~6 papers — SSRN/NBER/arXiv preprints, not final journal versions
- **PAYWALLED**: ~55 papers — require institutional access via publisher
- **BOOK_SAMPLE**: ~15 items — textbook/reference chapters only
- **WARNING\_NO\_ACADEMIC\_ANCHOR**: 1 item (ICT/Smart Money Concepts — no valid academic evidence found)

---

## Access by Lineage

### Strongly Accessible (≥75% free/preprint)

| Lineage | Coverage | Notes |
|---|---|---|
| Foundational IRL (C) | 100% free | Ng, Abbeel, Ziebart, Ho-Ermon — all directly downloadable |
| LLM Trading Agents (F) | 100% free | Entire group F (15 papers) is arXiv-accessible |
| Model Extraction (D) | 100% free | Papernot, Tramer — adversarial ML papers are open |
| Prediction Markets (P) | ~80% free | Only 1 of 9 paywalled (Manski) |

### Moderately Accessible (40-70% free)

| Lineage | Coverage | Notes |
|---|---|---|
| Demand System (A) | ~60% free | Koijen-Yogo core is NBER-accessible; Which Investors? is paywalled |
| IRL in Finance (B) | ~60% free | Most are arXiv; Transaction-Aware IRL (Springer) is paywalled |
| RL Trading (G) | ~60% free | IEEE papers are paywalled, arXiv alternatives often available |
| ML Asset Pricing (K) | ~65% free | NBER working papers open; Kelly-Pruitt-Su, Nagel book blocked |
| Pattern Recognition (R) | ~50% free | Academic papers mostly paywalled, some arXiv alternatives |

### Mostly Paywalled (<40% free)

| Lineage | Coverage | Notes |
|---|---|---|
| Behavioral Finance (E) | ~20% free | Odean, Barberis, Tetlock, Shiller — Journal of Finance is heavily blocked |
| Market Microstructure (H) | ~30% free | Avellaneda-Stoikov, Cartea book, Hasbrouck book — expensive |
| Options/Volatility (L) | ~20% free | Black-Scholes, Heston, Dupire, Gatheral, Bergomi — almost all paywalled |
| Hedge Fund/13F (Q) | ~10% free | Only industry reports available, academic papers all paywalled |
| Technical Analysis (O) | ~25% free | Sullivan, Lo-Mamaysky-Wang, JF/JFQA articles blocked |
| Volume/Order Flow (N) | ~15% free | Glosten-Milgrom, Kyle, Easley-O'Hara all paywalled |
| Renaissance/Simons (I) | 0% direct | Zuckerman book, Thorp papers — use reviews/interviews/library only |

---

## Paywall Access Strategies

### Tier 1: Preprint Substitution (works for ~40% of paywalled items)

Many paywalled final journal versions have freely available preprints:
- **NBER working papers**: Koijen-Yogo demand system, asset embeddings, inelastic markets
- **SSRN preprints**: Kelly-Pruitt-Su, Best Ideas, 13F alpha papers
- **Author homepages**: Often host accepted manuscripts (author's version)
- **arXiv cross-references**: Some finance papers appear on arXiv alongside journal publication

**Action**: For every paywalled item, search `[paper title] site:ssrn.com`, `[paper title] site:nber.org`, and `[author] `[institution]`. Author preprints are often sufficient for system-building.

### Tier 2: Institutional Access

- **University library proxies**: Most academic publishers (Wiley, OUP, Elsevier) support institutional access
- **Interlibrary loan**: Books (Gatheral, Bergomi, Nagel, Cartea, Hasbrouck) can be requested through most university libraries
- **CFA Institute Research Foundation**: Free access to industry-facing research (Halperin/Kolm/Ritter IRL practitioner guide)

**Action**: If affiliated with a university, configure institutional proxy. If not, consider public library interlibrary loan services.

### Tier 3: Legal Open Alternatives

- **Book reviews and excerpts**: For Zuckerman (Simons biography), use reviews, interviews, and publisher excerpts
- **Conference presentations**: Many authors present at YouTube/MIT/IQST — search for public talks
- **Industry reports**: Goldman Sachs Asset Management X-Ray, CFA Institute chapters provide practitioner perspectives
- **Textbook sample chapters**: Often sufficient for understanding methodology (Cartea, Guéant, Bergomi)

---

## Items Worth Specific Access

These paywalled papers are load-bearing — worth the effort to access:

| Paper | Why It's Critical | Access Strategy |
|---|---|---|
| Koijen, Richmond & Yogo (2024) *Which Investors Matter?* | Identifies which investor types move prices most | OUP institutional; search author pages for preprint |
| Odean (1998) *Are Investors Reluctant to Realize Their Losses?* | Foundational disposition-effect evidence | Wiley/JSTOR; Terrance Odean often shares PDFs |
| Carr & Madan (1999) FFT option pricing | Practitioner standard for fast option valuation | Journal of Computational Finance; arXiv versions exist |
| Lo, Mamaysky & Wang (2000) Foundations of TA | Academic pattern-recognition baseline | JF paywalled; author Jiang Wang may share preprint |
| Sullivan, Timmermann & White (1999) bootstrap | Data-snooping controls for pattern testing | JF paywalled; SSRN preprint may exist |
| Kyle (1985) Continuous Auctions | Foundation of market microstructure theory | Econometrica/JSTOR; classic — check library access |
| Heston (1993) Stochastic Volatility | Standard stochastic vol model for practical options | RFS/OUP; widely cited — preprints often circulated |
| Avellaneda & Stoikov (2008) HFT market making | Market-making baseline for execution systems | Quantitative Finance; author preprint often available |

---

## Non-Obvious Insights from Paywall Analysis

1. **The most valuable research is also the most paywalled.** Demand-system pricing, behavioral finance, and microstructure foundations — the three lineages most critical for reverse-engineering decision logic — are heavily locked behind JF, JPE, and RFS paywalls. ArXiv dominance is in adjacent areas (LLM agents, foundational IRL) that are useful but not sufficient alone.

2. **Preprints are often enough for building, not sufficient for citing.** Working-paper versions contain the core methodology needed to design systems. Final journal versions add reviewer-polished exposition and sometimes additional robustness tests — worth checking before formal citation.

3. **Books represent the hardest barrier.** Cartea, Hasbrouck, Gatheral, Bergomi, Nagel, Lopez de Prado's book series — these are practitioner-critical references that cost $80-200 each. Use library access, interlibrary loan, or sample chapters. The methodology is often replicated in the authors' open papers.

4. **ICT/Smart Money Concepts have zero academic anchor.** The library's scan found no scholarly evidence supporting fair-value-gap and smart-money-concept frameworks as standalone predictive signals. Any strategy built on these must create its own feature-validation pipeline grounded in microstructure data (order-flow imbalance, spread behavior, liquidity gaps) — not terminology.

---

*Cross-links: [[Research-Read-Order-Guide]], [[Research-Library-Synthesis]], [[Data-Quality-Checks]]*
