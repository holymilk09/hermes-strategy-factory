# Compliance basis for the research layer

2026-10-09. Facts below were checked against primary sources by an independent research pass;
items it could not verify are marked. **This is not legal advice.** A dated, counsel-reviewed
memo on adviser status must be on file before any paid distribution (§6).

## 1. Investment Advisers Act — the line the product is built on

- 15 U.S.C. §80b-2(a)(11) defines an investment adviser as anyone who, for compensation,
  advises others on securities "either directly or through publications or writings … **or who,
  for compensation and as part of a regular business, issues or promulgates analyses or reports
  concerning securities**". The second prong reaches analyses with no recommendation at all.
  Exclusion (D): "the publisher of any bona fide newspaper, news magazine or business or
  financial publication of general and regular circulation." ([LII](https://www.law.cornell.edu/uscode/text/15/80b-2))
- *Lowe v. SEC*, 472 U.S. 181 (1985): the exclusion holds "as long as the communications …
  remain entirely impersonal and do not develop into the kind of fiduciary, person-to-person
  relationships" of adviser and client; what the Act targets is "individualized advice attuned
  to any specific portfolio or to any client's particular needs." ([LII](https://www.law.cornell.edu/supremecourt/text/472/181))
- Where the exclusion was lost: *In re Weiss Research* (IA-2525, 2006) — auto-trading of
  newsletter picks through cooperating brokers gave the publisher effective discretion.
  ([SEC](https://www.sec.gov/litigation/admin/2006/ia-2525.pdf))
- Where it held: *Lingley v. Seeking Alpha* (S.D.N.Y. Aug. 15, 2024) — subscribers linked
  brokerage accounts and got portfolio-based alerts; the court held a filter "based on his or
  her own personal mix of investments" over generally available content does not make it
  personal, and distinguished cases where the publisher controlled funds or decisions.
  ([summary](https://www.gtlaw.com/en/insights/2024/8/no-need-for-seeking-alpha-to-seek-registration))
- SEC staff factors for information providers (Datastream 1993, RDM 1996, cited at IA-6050
  n.29): information readily available in raw form; categories not highly selective; not
  organised "in a manner that suggests the purchase, holding, or sale of any security."
  The SEC's 2022 request for comment flagged that "sophistication and customization" of
  analytics may warrant adviser regulation. ([IA-6050](https://www.govinfo.gov/content/pkg/FR-2022-06-22/pdf/2022-13307.pdf))
- FINRA's test for a "recommendation" (not binding on a non-member, but the vocabulary
  regulators use): a "call to action"; the more tailored, the more likely. User-directed
  screens, research libraries and user-selected alerts generally are not. ([NTM 01-23](https://www.finra.org/rules-guidance/notices/01-23))
- States: NSMIA bars state registration of an adviser with no place of business in the state
  and fewer than six clients there in 12 months; anti-fraud authority is preserved.
  ([15 U.S.C. §80b-18a](https://www.law.cornell.edu/uscode/text/15/80b-18a))

**Design rules enforced in code (`compliance.py`, tested):**
1. One published methodology, applied identically to every request. The user's profile is a
   filter over generally available data; the server computes, never judges, and stores nothing.
2. No call to action anywhere in rendered text: no buy/sell/hold, overweight, targets, "watch
   for", "consider", "you should" (`FORBIDDEN_PHRASES`; every brief/report is linted at render).
3. No per-user list of securities to trade; no discretion, no auto-trade, no broker link
   (`sent_to_broker` is False everywhere; the server has no write path).
4. No human-tailored commentary: every note is a statistic with its threshold and window.

## 2. Performance and marketing claims

- SEC Marketing Rule 206(4)-1 binds registered advisers; "hypothetical performance" includes
  backtested and model results and may be shown only with policies, assumptions and risks
  disclosed; nine advisers were fined in 2023 for mass-audience hypothetical performance.
  ([rule](https://www.law.cornell.edu/cfr/text/17/275.206(4)-1); [SEC 2023-173](https://sec.gov/news/press-release/2023-173))
- FTC Act §5 applies to everyone: a representation "likely to mislead the consumer, acting
  reasonably" on a material point is deceptive, and "pro forma statements or disclaimers may
  not cure otherwise deceptive messages." WealthPress paid ≈$1.7M for touted trading
  "strategies" with buried disclaimers. ([Deception Policy Statement](https://www.ftc.gov/sites/default/files/attachments/training-materials/policy_deception.pdf); [FTC](https://www.ftc.gov/node/85108))
- Repo rule (`docs/BLOCKED_ACTIONS.md`): no "profitable", "validated", "ready to trade",
  "high confidence" or "guaranteed" claims. The lint list includes them.

**Rules:** no performance claims of any kind; the forward-test ledger is published whole
(including failures) with methodology and the word "hypothetical" where results are not
realised; written substantiation (the ledger and validation files) backs every accuracy
statement made in product copy.

## 3. Market data: what may be shown to customers

- Robinhood Customer Agreement §2.B: "I agree not to reproduce, distribute, sell or
  commercially exploit the Market Data in any manner"; §2.C: personal, non-business use;
  §3.B (Nasdaq data): "personal use and not for any business purpose." The agentic-trading
  pages add no data licence. ([Customer Agreement](https://cdn.robinhood.com/assets/robinhood/legal/Customer%20Agreement.pdf))
  **Consequence:** Robinhood data is for development and Matt's own use only. `check_distribution`
  refuses customer mode on it. UNVERIFIED: whether a separate MCP developer licence exists.
- Exchange policies: UTP end-of-day data is not fee-liable and multi-security derived data
  that cannot be reverse-engineered is not fee-liable; Nasdaq's Global Data Agreement makes no
  proprietary claim to derived data; NYSE licenses external redistribution of stored data
  separately. The vendor contract is what actually governs what may be shown.
  ([UTP](https://utpplan.com/DOC/Datapolicies.pdf); [Nasdaq](https://www.nasdaqtrader.com/content/AdministrationSupport/Policy/USEquitiesandOptionsDataPolicies.pdf); [NYSE](https://www.nyse.com/publicdocs/nyse/data/NYSE_Proprietary_Market_Data_Comprehensive_Policy_Package.pdf))
- Vendors whose official terms allow end-user display of derived analytics (verified items
  only; prices/adjusted-data availability partly UNVERIFIED):
  - Massive (formerly Polygon.io) Business terms: display to authorised users and distribute
    derived "analyses, calculations, models" provided they do not contain the raw data; no
    feed/file redistribution. Individual plans are personal-use only.
    ([terms](https://massive.com/legal/businesses-terms-of-service))
  - Twelve Data Business plans: commercial display allowed; redistribution of data needs a
    separate agreement; derived data must not be reverse-engineerable. ([terms](https://twelvedata.com/terms))
  - Intrinio Startup plan and above: "display data to your application's users"; raw
    redistribution separate; exchange-governed datasets may need exchange approval.
    ([licensing](https://help.intrinio.com/licensing-data-usage-requirements))
  - Databento: most datasets redistributable internally or externally after 24 hours
    (Plus tier lists external distribution); raw prices with an adjustment-factor dataset.
    ([pricing](https://databento.com/pricing))
  - EODHD and Alpha Vantage: commercial use requires a separate commercial licence;
    Alpha Vantage's standard terms are personal, non-commercial. FMP: individual plans bar
    showing FMP-derived data to others even for free.
- **Rule:** the product returns derived, non-reverse-engineerable analytics (betas, returns
  over windows, z-scores, correlations), never a price feed or file; attribution/delay
  labels per the chosen vendor; the vendor's restrictions flow down into the end-user terms.

## 4. Privacy

GLBA covers institutions "significantly engaged" in financial activities (whether a
research-only analytics tool qualifies is UNVERIFIED as applied); SEC Regulation S-P covers
only brokers, dealers, funds and registered advisers; CCPA applies above revenue/volume
thresholds. Independent of statutes, the FTC treats unreasonable data security as unfair, and a
"we store nothing" statement is itself a §5 claim that must be true across logs, backups and
LLM-provider processing. ([16 CFR 313.3](https://www.law.cornell.edu/cfr/text/16/313.3); [15 U.S.C. §45(n)](https://www.law.cornell.edu/uscode/text/15/45))
**Rule:** profiles are per-request and never written or logged by the server (no logging of
tool arguments); the privacy policy says exactly that and names any third-party processor.

## 5. Conflicts and the ledger

Securities Act §17(b) makes it unlawful to publish about a security for consideration from an
issuer, underwriter or dealer without full disclosure; the Park/"Tokyo Joe" theory reaches
trading around one's own published calls regardless of adviser status.
([15 U.S.C. §77q](https://www.law.cornell.edu/uscode/text/15/77q))
**Rule:** every output carries the operator's position/compensation disclosure
(`disclosures.yaml`; customer mode refuses to start until it is configured); the ledger is
append-only with hashes, failures included, and the operator's positions in named securities
are disclosed on it.

## 6. Open items (not code)

- Counsel-reviewed, dated memo on adviser status for the exact feature set; re-review if any
  feature starts ranking or selecting securities for a user rather than reporting on the
  user's own selection.
- Terms of service / EULA and privacy policy (flow-down of vendor terms; retention statement).
- Vendor choice and licence tier; attribution text; re-run Phase 1 on the vendor's data.
- Whether a Robinhood MCP developer licence exists that changes §3 (UNVERIFIED).
