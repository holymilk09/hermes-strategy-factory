# Compliance Boundaries — Strategy Factory

> **Version:** 1.0  
> **Date:** 2026-07-01  
> **Status:** PLANNING — not reviewed by legal counsel  
> **Critical:** This document must be reviewed by a securities attorney before any production deployment.

---

## 1. Regulatory Classification

### 1.1 What Strategy Factory Is

Strategy Factory is a **research publication service**. It publishes observations about historical market data, filter performance, and maturity tracking. It does not:

- Execute trades
- Hold customer funds
- Recommend specific buy/sell actions
- Provide personalized financial advice
- Manage portfolios
- Offer investment advisory services

### 1.2 Regulatory Implications

| Regulator | Jurisdiction | Relevance |
|---|---|---|
| SEC | United States | Investment adviser registration (likely NOT required — see §2) |
| FINRA | United States | Broker-dealer registration (NOT required — no order execution) |
| FTC | United States | Truth in advertising, subscription disclosures |
| CFPB | United States | Consumer financial protection (subscription billing) |
| GDPR | EU | Data protection (if EU subscribers) |
| CCPA | California | Data privacy (if CA subscribers) |

### 1.3 Publisher vs Adviser Distinction

The **publisher exclusion** (SEC Investment Advisers Act of 1940, Section 202(a)(11)(D)) exempts "the publisher of any bona fide newspaper, news magazine or business or financial publication of general and regular circulation" from investment adviser registration.

Key factors (per SEC v. Lowe, 472 U.S. 181, and subsequent guidance):

| Factor | Strategy Factory Position | Risk |
|---|---|---|
| Publication is impersonal (no individual tailoring) | ✅ No personalized advice, no KYC, no portfolio management | Low |
| Publication is regular and periodic | ✅ Daily edge sheets | Low |
| Publication is available to the general public | ✅ Subscription-based, not invite-only advisory | Low |
| No client-specific recommendations | ✅ Ticker cards are universal, not per-user | Low |
| Clear disclaimers | ✅ Research-only on every output | Low |
| No performance claims | ✅ No "win rates", no "returns", no "beating the market" | Low |

**Conclusion:** Strategy Factory likely qualifies for the publisher exclusion. However, this is not a legal opinion — counsel must confirm.

---

## 2. Forbidden Behaviors

These are **permanent, non-negotiable** constraints. Violating any of them crosses the line from publisher to adviser.

### 2.1 Trading & Execution

| # | Forbidden | Why |
|---|---|---|
| C1 | Broker execution (placing trades) | Requires broker-dealer registration (FINRA) |
| C2 | Holding customer funds or securities | Requires custody registration |
| C3 | Routing orders to any broker | Requires order routing disclosures |
| C4 | Accepting payment for order flow | Requires disclosure + registration |
| C5 | Offering leverage, margin, or derivatives recommendations | Requires additional registration |
| C6 | Any API endpoint that creates, modifies, or cancels orders | API contract explicitly forbids this |

### 2.2 Advice & Recommendations

| # | Forbidden | Why |
|---|---|---|
| C7 | "Buy", "sell", "hold", "accumulate", "reduce" language | Constitutes investment recommendation |
| C8 | Price targets ("AMD will hit $600") | Constitutes investment recommendation |
| C9 | Entry/exit timing ("buy at open on Monday") | Constitutes trade recommendation |
| C10 | Position sizing ("allocate 5% to this") | Constitutes portfolio advice |
| C11 | Personalized advice based on user input | Requires KYC + suitability + fiduciary duty |
| C12 | "Alert" or "signal" terminology | Implies actionable instruction |
| C13 | Risk ratings per user ("conservative investors should...") | Constitutes suitability assessment |

### 2.3 Performance & Claims

| # | Forbidden | Why |
|---|---|---|
| C14 | "Win rate" claims (e.g., "71% win rate") | Misleading without statistical significance (n=7) |
| C15 | "Returns" claims (e.g., "average return of +16%") | Implies investment performance |
| C16 | Backtested performance as current indicator | "Past performance does not guarantee future results" |
| C17 | "Beating the market" / "alpha" claims | Not validated with sufficient independent samples |
| C18 | "Profitable" / "proven" / "tested" / "reliable" | No commercial edge has been established |
| C19 | Sharpe ratio, Sortino, CAGR in customer-facing output | Quantitative metrics imply investment product |
| C20 | Benchmark comparison as proof of edge | "Outperformed SPY" implies the system can do it again |

### 2.4 Automation

| # | Forbidden | Why |
|---|---|---|
| C21 | Auto-publishing edge sheets without admin review | Single most critical safety gate |
| C22 | Auto-adjusting thresholds from small sample | n=7 is statistically meaningless |
| C23 | Auto-generating new strategy types and publishing | Each strategy requires full pipeline validation |
| C24 | Auto-responding to user questions about specific stocks | Could be construed as personalized advice |
| C25 | Auto-emailing "alerts" when new observations appear | Implies urgency/actionability |

---

## 3. Required Disclaimers

### 3.1 On Every Output

The following must appear on every edge sheet, every API response, every email, and every web page that displays research data:

> **Research-Only Disclaimer:** This report is for research tracking and education only. It is not investment advice. It does not recommend buying or selling any security. Past observations do not guarantee future outcomes. The Strategy Factory is a research publication, not a registered investment adviser or broker-dealer. No trading is executed. No personalized advice is provided. All observations are generated by automated systems and manually reviewed before publication. Subscribers should conduct their own research and consult a qualified financial adviser before making investment decisions.

### 3.2 On Subscription Pages

> Strategy Factory is a research publication. Your subscription gives you access to daily market observations, maturity tracking, and research audit reports. It does not include investment advice, trade recommendations, or portfolio management. No trading is executed on your behalf.

### 3.3 On Emails

Every email footer:

> Research-only. Not investment advice. No trading recommendations.
> Unsubscribe: [link]

### 3.4 Sample Size Warning

Must appear prominently while observations < 30:

> ⚠️ **Small Sample Notice:** The Strategy Factory has fewer than 30 independent observations. Results are preliminary and should not be used to make investment decisions. More data is needed before any pattern can be considered evidence of a reliable setup.

---

## 4. Subscription & Billing Compliance

### 4.1 Required Disclosures

| Disclosure | Where | Requirement |
|---|---|---|
| Price | Pricing page | Clear, no hidden fees |
| Billing cycle | Checkout page | Monthly or annual, auto-renewal stated |
| Cancellation policy | Terms of Service | How to cancel, no long-term contracts |
| Refund policy | Terms of Service | 7-day refund window stated |
| Free trial terms | Checkout page | Duration, when card is charged |
| Auto-renewal notice | Email before renewal | 3 days before charge (Stripe automated) |

### 4.2 FTC Compliance

- No "dark patterns" — cancellation must be as easy as signup
- No pre-checked boxes for upsells
- Clear "Cancel Subscription" button in account page
- Confirmation email on cancellation with effective date

### 4.3 Stripe Compliance

- PCI compliance handled by Stripe (no card data on our servers)
- Strong Customer Authentication (SCA) for EU customers
- Receipts auto-generated by Stripe
- Dispute resolution via Stripe dashboard

---

## 5. Data Privacy

### 5.1 Data We Hold

| Data | Location | Retention |
|---|---|---|
| Email address | Supabase Auth | Until account deletion |
| Subscription status | Supabase (subscriptions table) | Until account deletion + 30 days |
| Email delivery log | Supabase (email_delivery_log table) | 90 days |
| Observation data | Supabase + VPS ledgers | Permanent (research archive) |
| No IP addresses | — | Not collected |
| No browsing history | — | Not collected |
| No financial account data | — | Not collected |
| No KYC data | — | Not collected |

### 5.2 GDPR Considerations

If serving EU subscribers:

- Privacy Policy with clear data inventory
- Data Processing Agreement (DPA) with Supabase
- Right to deletion (delete Supabase Auth account = all user data deleted)
- Cookie consent (minimal — we don't use tracking cookies)

### 5.3 CCPA Considerations

If serving California subscribers:

- "Do Not Sell My Personal Information" link (we don't sell data → simple notice)
- Data inventory in Privacy Policy
- Deletion request process

---

## 6. Content Boundaries

### 6.1 Allowed In Customer-Facing Output

- Ticker symbols with observation context
- Plain-English analysis of why a setup looks strong or weak
- Setup-break levels (price areas that matter)
- Score and grade
- Maturity status
- Market weather
- Reject ledger (failed strategies)

### 6.2 NOT Allowed In Customer-Facing Output

- "Buy" / "sell" / "hold" / "accumulate" / "reduce"
- "Watch" / "monitor" / "keep an eye on"
- "Constructive" / "positive setup" / "good entry"
- Price targets ("could reach $X")
- Percentage return projections
- "Win rate", "hit rate", "accuracy" in plain text
- "Alpha", "beta", "factor exposure"
- "Signal decay" / "edge erosion"
- "Poor regime fit" / "neutral" (from audit terminology)
- "Not covered" (implies some are covered → recommendation)

### 6.3 Edge Cases (Require Counsel Review)

| Case | Risk | Counsel Question |
|---|---|---|
| "Market is helping this setup" | Low — descriptive, not predictive | Is this a market opinion? |
| "Setup breaks below $X" | Low — factual data point | Could this be seen as a stop-loss recommendation? |
| Grade B / C / D | Medium — implies quality assessment | Could a subscriber read "Grade B" as "good to trade"? |
| Score "80" | Medium — implies quantitative rating | What does 80 mean in plain English? Must be explained. |
| "Waiting for Pullback" | Medium — implies timing | Could this be seen as "wait to buy on a dip"? |

---

## 7. Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Subscriber treats observation as trade recommendation | High | High — financial loss, regulatory complaint | Clear disclaimers, no buy/sell language, prominent sample-size warning |
| SEC inquiry on publisher vs adviser classification | Low | High — legal costs, possible registration requirement | Publisher exclusion analysis, counsel review, clear separation of research vs advice |
| Subscriber disputes charge | Medium | Low — chargeback fee | Clear billing disclosures, easy cancellation, 7-day refund |
| Stale data published (freshness gate fails silently) | Low | Medium — misleading subscribers | Healthcheck + freshness gate + admin review + monitoring |
| Ledger corruption (duplicate IDs, missing rows) | Low | Medium — incorrect output | Integrity invariants, backup restore, audit trail |
| Strategy overfitting from small sample | Medium | High — misleading when sample grows | No threshold tuning, sample-size warning, multi-cohort evidence required before grade change |
| Admin publishes without reviewing | Low | High — stale/misleading output, reputational damage | Approval audit trail, only super admins can approve, 2FA |

---

## 8. Insurance Recommendations

| Insurance | Purpose | Estimated Cost |
|---|---|---|
| Errors & Omissions (E&O) | Covers claims of negligent advice or errors in published research | $1,000–$3,000/yr |
| Cyber Liability | Covers data breach response (if any user data is leaked) | $500–$1,500/yr |
| General Liability | Basic business coverage | $500–$1,000/yr |

**Note:** This is not insurance advice. Consult a licensed insurance broker.

---

## 9. Legal Review Checklist

Before any production deployment, the following must be reviewed by a securities attorney:

- [ ] Publisher exclusion applicability (SEC v. Lowe analysis)
- [ ] Disclaimer language (sufficient for publisher exclusion)
- [ ] Terms of Service (liability limitations, arbitration clause, governing law)
- [ ] Privacy Policy (GDPR/CCPA compliance)
- [ ] Subscription agreement (billing terms, cancellation, refunds)
- [ ] Content boundaries (what constitutes investment advice vs research)
- [ ] Email marketing compliance (CAN-SPAM Act)
- [ ] State-level "investment newsletter" regulations (some states have specific rules)
- [ ] International subscriber considerations (cross-border securities laws)
- [ ] Intellectual property (who owns the research — us or subscribers?)

---

## 10. Emergency Contact

| Scenario | Contact |
|---|---|
| SEC/FINRA inquiry | Securities attorney (retained before launch) |
| Data breach | Cyber liability insurer + Supabase support |
| Subscriber complaint | Support email → admin review → escalate if legal threat |
| Payment dispute | Stripe dashboard |
| Service outage | VPS provider + Supabase status page |