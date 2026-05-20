# 7. ETF/Index Arbitrage

---

## Key Concepts

### Core Mechanism
Exploit price discrepancies between an ETF's market price and its Net Asset Value (NAV), calculated from the real-time value of the underlying basket of securities.

- **NAV calculation**: `NAV = Σ (w_i · P_i) / Shares_Outstanding` where w_i are fund weights and P_i are current prices of underlying constituents.
- **Premium/discount**: When ETF market price > NAV, the ETF trades at a premium. When < NAV, it trades at a discount.
- **Arbitrage mechanism**:
  - ETF at **premium**: Buy underlying basket → create ETF shares (creation unit) → sell ETF shares on market → pocket premium minus costs.
  - ETF at **discount**: Buy ETF shares → redeem for underlying basket (creation unit) → sell basket constituents → pocket discount minus costs.
- **Creation/redemption units**: Typically 25,000-100,000 shares; minimum block size limits participation to Authorized Participants (APs).
- **Intraday NAV (iNAV)**: Real-time NAV calculation updated every 15 seconds during trading hours.

### Edge Source
- **AP monopoly/oligopoly**: Only Authorized Participants can create/redeem. If few APs are active or capital-constrained, premiums/discounts persist longer.
- **Cross-market timing**: ETFs holding foreign securities may trade while underlying markets are closed (e.g., US-listed Asian ETFs during US hours). Price discovery from futures/ADRs creates "implied NAV" edges.
- **Flow imbalances**: Massive retail or institutional buying/selling of an ETF without corresponding AP activity creates sustained premium/discount.
- **Illiquid underlying**: When basket constituents are illiquid (high-yield bonds, emerging market equities, small-cap stocks), NAV estimates become stale → mispricing windows open.
- **Information asymmetry**: APs have better real-time basket valuation data and faster execution infrastructure to capture the arbitrage.

### Specific Formulas

**NAV:**
```
NAV_t = Σ_(i=1)^N (w_i · P_(i,t)) / N_shares_outstanding
```

**Premium/Discount (%):**
```
PD_t = (P_ETF_t - NAV_t) / NAV_t × 100
```

**Theoretical arbitrage profit per creation unit:**
```
Profit = N_unit × (P_ETF - NAV) - TC_basket - TC_ETF - TC_creation
where N_unit = creation unit size
TC_basket = Σ transaction costs for underlying constituents
TC_ETF = ETF trading costs
TC_creation = creation/redemption fee (typically $300-1000 flat)
```

**Fair value with implied yields (cash drag adjusted):**
```
NAV_fair = NAV_spot × exp((r - δ) · τ)
where r = risk-free rate, δ = dividend yield, τ = time to settlement
```

**Cross-market implied NAV (for foreign holdings):**
```
iNAV = Σ (w_i · FX_rate · P_local,i · exp(r_us - r_local) · τ) 
       + Σ (w_j · ADR_parity_ratio · P_ADR,j)
```

**Break-even premium/discount threshold:**
```
PD_min = (TC_basket + TC_ETF + TC_creation) / (N_unit · NAV)
Trade only if |PD| > PD_min + margin_of_safety
```

### Implications for Trading Systems
- **AP access**: If you're not an AP, direct ETF arb is impossible. Alternatives: trade the premium/discount directionally (bet on mean reversion) or partner with an AP.
- **International ETF arb**: Most profitable arena. Currency fluctuations, time zone differences, and foreign market closures create persistent edges. But FX hedging costs must be modeled precisely.
- **Bond ETF arb**: Fixed income ETFs trade liquidly while many underlying bonds trade OTC and infrequently. Stale bond prices → NAV miscalculation → persistent premium/discount.
- **Monitoring infrastructure**: Need real-time basket data creation/redemption file (PCF), iNAV feeds, and constituent-level price aggregation.
- **Risk limits**: Position size limited by creation unit granularity and AP capital. A single creation unit can represent millions in notional.

## Key Implications
- **Premium/discount is NOT always an arbitrage**: It's an equilibrium outcome when costs (transaction + creation + risk) exceed the mispricing. A 0.5% discount on an EM bond ETF may be fully justified by illiquidity.
- **Tax considerations matter**: In-kind creation/redemption avoids capital gains realization, making this mechanism tax-efficient — this is a structural reason the mechanism works at scale.
- **ESG/thematic ETF proliferation**: Niche ETFs with exotic underlying baskets have fewer competing APs → wider/more persistent mispricing → higher edge but also higher execution risk.

## Failure Modes
- **Creation/redemption halted**: During extreme volatility (e.g., March 2020, bond market freeze), APs suspend creations. ETF trades at persistent, un-arbitrageable discount.
- **Stale pricing in NAV**: NAV calculation relies on last available prices. For illiquid holdings, NAV is outdated → apparent premium/discount is a calculation artifact, not a tradeable signal.
- **FX risk mismatch**: In cross-market arb, currency moves during execution window can wipe out the premium/discount profit. Hedging adds cost.
- **Dividend timing risk**: Ex-dividend dates affect NAV calculation. Missing a dividend adjustment turns an apparent arbitrage into a loss.
- **Corporate actions in underlying**: Mergers, spin-offs, or tender offers in basket constituents change weights without immediate NAV adjustment.
- **Regulatory restrictions**: SEC Rule 6c-11 and ETF rule changes alter creation/redemption mechanics. Regulatory changes can eliminate edge overnight.
- **Competition compression**: As more APs/algos compete for the same arb, premium/discount windows shrink from several basis points to negligible levels.

## Cross-Links
- [[Index-Futures-Cash-And-Carry]] — Similar cost-of-carry logic with futures
- [[6-PCA-ETF-Residual-Stat-Arb]] — ETF residuals vs. constituent baskets
- [[Cost-Of-Carry-Futures-Pricing]] — Fair value with financing and dividend yield
- [[Cross-Border-Timezone-Arb]] — International ETF timing arbitrage
- [[Bond-ETF-Underlying-Liquidity]] — Fixed income ETF specific challenges
- [[Authorized-Participant-Mechanics]] — AP role, creation/redemption process details
- [[5-US-Equity-Pairs-Trading]] — ETF vs. basket as a pair trade
- [[Execution-Cost-Management]] — Basket trading costs, impact estimation
