# Production Readiness Plan — Strategy Factory

> **Version:** 1.0  
> **Date:** 2026-07-01  
> **Status:** PLANNING / NO PRODUCTION CODE EXECUTED  
> **Branch:** `trust-calibration-working`  
> **Base commit:** `398e526`

---

## 1. Product Vision

**Strategy Factory** is a read-only retail research product. It publishes observation-based market analysis — not trade signals, not recommendations, not broker execution. The user sees what the system observes, how those observations mature, and what the audit layers found. They make their own decisions.

### 1.1 What It Is

- A daily-updating research dashboard showing selected momentum setups
- A maturity tracker showing how past observations resolved
- An edge audit showing drift attribution, filter quality, and economic sanity
- A scoreboard with plain-English summaries per ticker

### 1.2 What It Is Not

- It does **not** execute trades
- It does **not** recommend buy/sell actions
- It does **not** provide personalized financial advice
- It does **not** auto-optimize thresholds
- It does **not** publish without admin review

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        STRATEGY FACTORY                              │
│                      Production Architecture                        │
└─────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │  Alpaca API  │
                              │  (Data Only)  │
                              └──────┬───────┘
                                     │ daily bars (read-only)
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DATA PIPELINE (Hermes Cron — private VPS only)                     │
│                                                                     │
│  ┌──────────┐    ┌────────────┐    ┌───────────────┐               │
│  │ OHLCV    │───▶│ Observation │───▶│ Outcome       │               │
│  │ Refresh  │    │ Cycle       │    │ Resolution    │               │
│  └──────────┘    └─────┬──────┘    └───────┬───────┘               │
│                        │                    │                       │
│                        ▼                    ▼                       │
│               ┌──────────────┐    ┌───────────────┐                │
│               │ Observation  │    │ Outcome       │                │
│               │ Ledger (CSV) │    │ Ledger (CSV)  │                │
│               └──────┬───────┘    └───────┬───────┘                │
│                      │                    │                         │
│                      ▼                    ▼                         │
│               ┌──────────────────────────────────┐                 │
│               │  Ghost Ledger (CSV)              │                 │
│               │  — rejected candidates tracked   │                 │
│               └──────────────┬───────────────────┘                 │
│                              │                                     │
│                              ▼                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  EDGE AUDIT LAYER                                              │ │
│  │  ├─ Economic Sanity    (cost/delay-adjusted returns)           │ │
│  │  ├─ Drift Attribution  (Independent Strength / Beta Drift)     │ │
│  │  └─ Filter Quality     (pass rate, ghost baseline return)      │ │
│  └────────────────────────────┬──────────────────────────────────┘ │
│                               │                                    │
│                               ▼                                    │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  EDGE SHEET GENERATOR                                          │ │
│  │  ├─ Ticker cards (7 fields per symbol)                        │ │
│  │  ├─ Scoreboard (maturity tracking)                            │ │
│  │  ├─ Reject ledger (failed strategies)                         │ │
│  │  └─ Research-only disclaimer                                  │ │
│  └────────────────────────────┬──────────────────────────────────┘ │
│                               │                                    │
│                    ┌──────────▼──────────┐                         │
│                    │   Admin Approval    │                         │
│                    │   Gate (manual)     │                         │
│                    └──────────┬──────────┘                         │
│                               │ approved                           │
└───────────────────────────────┼────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PUBLIC API LAYER (Supabase / FastAPI — read-only)                  │
│                                                                     │
│  GET /v1/observations        — current observation universe          │
│  GET /v1/observations/:id    — single observation with audit         │
│  GET /v1/scoreboard          — maturity scoreboard                   │
│  GET /v1/edge-sheet/latest   — latest approved edge sheet            │
│  GET /v1/edge-sheet/:date    — historical edge sheets                │
│  GET /v1/ghost-ledger        — rejected candidates summary           │
│  GET /v1/health             — system status                          │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DELIVERY LAYER                                                     │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ Shopify  │  │ Stripe   │  │ Supabase │  │ Email (Resend /  │    │
│  │ Store    │  │ Billing  │  │ Auth + DB│  │ SendGrid)        │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘    │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  Retail Web App (React / Next.js)                          │      │
│  │  ├─ Dashboard: today's observations                       │      │
│  │  ├─ Scoreboard: maturity tracker with results             │      │
│  │  ├─ Archive: past edge sheets                             │      │
│  │  └─ Account: subscription management                      │      │
│  └──────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow

```
Alpaca Market Data API
  │
  │  GET /v2/stocks/{SYMBOL}/bars?timeframe=1Day
  │  Headers: APCA-API-KEY-ID, APCA-API-SECRET-KEY
  │  Free tier: 200 requests/minute, historical bars
  │
  ▼
OHLCV CSV Cache (data/cache/ohlcv_1d/{SYMBOL}_1D.csv)
  │  columns: date, open, high, low, close, volume, dividends, stock_splits, capital_gains
  │  freshness: checked against Alpaca trading calendar daily
  │  stale threshold: >5 calendar days behind latest completed session
  │
  ▼
Observation Pipeline
  │  1. discover_symbol_paths() → all CSVs excluding benchmark ETFs
  │  2. build_current_relative_strength_universe() → features + ranks + selected column
  │  3. latest_fresh_signals() → selected=True rows at latest timestamp
  │  4. build_observation_rows() → deterministic SHA256 observation IDs
  │  5. append_observations_atomic() → write to CSV ledger
  │  6. record_observation_rejections() → ghost ledger for non-selected
  │
  ▼
Outcome Resolution
  │  1. resolve_observation_outcomes() → for each PENDING observation
  │  2. Load OHLCV, skip past signal_timestamp
  │  3. If >= 10 future bars → compute outcome_close / signal_close - 1
  │  4. Status: RESOLVED | PENDING | PENDING_NO_OHLCV | PENDING_OHLCV_ERROR
  │
  ▼
Edge Audit Layer
  │  1. Economic Sanity → cost-adjusted return, delay-adjusted return, concurrent exposure
  │  2. Drift Attribution → classify each observation into 10 labels
  │  3. Filter Quality Audit → pass rate, ghost baseline, monotonicity
  │
  ▼
Edge Sheet Generator
  │  1. Ticker cards → per-symbol plain-English summaries
  │  2. Scoreboard → maturity tracker with checkpoint results
  │  3. Reject ledger → failed strategies graveyard
  │  4. Research disclaimer → mandatory on every output
  │
  ▼
Admin Approval Gate
  │  1. Edge sheet generated → draft state
  │  2. Admin reviews: no forbidden claims, no stale data, no broken setups
  │  3. Admin approves → published state
  │  4. Published → visible to subscribers
  │
  ▼
Public API / Retail App
     Read-only GET endpoints
     No mutation endpoints
     No trading endpoints
     No personalization endpoints
```

---

## 4. Fable Gate Requirements

Before any production deployment, every item below must be **confirmed true**. This is the Fable Gate — named after the fable of the emperor's new clothes: no pretending things work when they don't.

### 4.1 Data Integrity

| # | Requirement | Current Status | Blocking? |
|---|---|---|---|
| F1 | Observation ledger has no duplicate IDs | ✅ 0 duplicates | No |
| F2 | Outcome rows match observation rows 1:1 | ✅ 7=7 | No |
| F3 | Ghost ledger is append-only, idempotent by ghost_id | ✅ Verified | No |
| F4 | OHLCV refresh auto-resolves target from Alpaca calendar | ✅ Phase 6J hardening | No |
| F5 | No stale data published (>5 calendar days behind) | ✅ Freshness gate | No |
| F6 | All hashes recorded pre/post every ledger mutation | ✅ Phase 6M protocol | No |
| F7 | Ledger backups exist and are verifiable | ✅ Phase 6M backup gate | No |

### 4.2 Audit Layer

| # | Requirement | Status | Blocking? |
|---|---|---|---|
| F8 | All 16 edge audit metrics computed per observation | ✅ Implemented | No |
| F9 | All 10 drift attribution labels available | ✅ Implemented | No |
| F10 | No "Profitable" / "Validated" claims in output | ✅ Forbidden-words test | No |
| F11 | Sample-size warning active when n < 30 independent signals | ✅ Golden test validates | No |
| F12 | Research-only disclaimer on every output | ✅ Required section test | No |

### 4.3 Safety

| # | Requirement | Status | Blocking? |
|---|---|---|---|
| F13 | No broker_order_id populated in any ledger | ✅ Invariant test | No |
| F14 | No sent_to_broker=True in any ledger | ✅ Invariant test | No |
| F15 | Healthcheck passes before any publish | ✅ Daily check | No |
| F16 | Full test suite (398 tests) passes before any deploy | ✅ Current state | No |
| F17 | Source-only suite (344 tests) passes in CI | ✅ Fresh-clone capable | No |

### 4.4 Production Blockers (still required)

| # | Requirement | Status | Blocking? |
|---|---|---|---|
| F18 | PostgreSQL migration from CSV ledgers | ❌ Not started | **YES** |
| F19 | Admin approval workflow implemented | ❌ Not started | **YES** |
| F20 | Read-only API with Supabase Row-Level Security | ❌ Not started | **YES** |
| F21 | Stripe subscription integration | ❌ Not started | **YES** |
| F22 | Email delivery pipeline (daily edge sheet) | ❌ Not started | **YES** |
| F23 | Shopify storefront for subscriptions | ❌ Not started | **YES** |
| F24 | Multi-cohort evidence (3+ independent signal dates) | ⚠️ 2 dates so far | **YES** |
| F25 | 30+ independent observations across 10+ dates | ❌ 7 observations, 2 dates | **YES** |
| F26 | Legal review of disclaimers and terms | ❌ Not started | **YES** |
| F27 | Full-universe data refresh executed (≥50 fresh symbols; 6-symbol refresh is invalid for ranking) | ⚠️ Phase 7C code complete; refresh run required | **YES** |
| F28 | Sector ETFs (SMH/IGV/TAN) fresh — required for full "Independent Strength" labels | ⚠️ SMH cached; IGV/TAN pending first full refresh | **YES** |
| F29 | Ghost outcomes resolved (`update_ghost_outcomes.py --write`); ghost baseline + accepted-vs-rejected lift populated | ⚠️ Resolver available; controlled run required | **YES** |

**Production remains BLOCKED until F18–F29 are resolved.**

---

## 5. Monitoring Requirements

| Monitor | Check | Alert If |
|---|---|---|
| Data freshness | `check_market_data_freshness.py` | >5 calendar days stale |
| Healthcheck | `run_feature_factory_healthcheck.py` | Any invariant fails |
| Ledger integrity | SHA256 comparison | Hash changes without approved mutation |
| Ghost ledger growth | Row count monitoring | Unexpected spike in rejections |
| Observation count | Row count monitoring | Sudden drop (data issue) or surge (universe change) |
| API availability | Alpaca calendar endpoint | Unreachable |
| Hermes gateway | Watchdog script | Gateway process dead |
| Disk space | `df -h` | <20% free on /opt partition |

---

## 7. Backup Requirements

| Backup | Frequency | Retention | Verification |
|---|---|---|---|
| Observation ledger | Before every cycle | 30 days rolling | SHA256 comparison |
| Outcome ledger | Before every cycle | 30 days rolling | SHA256 comparison |
| Ghost ledger | Before every cycle | 30 days rolling | SHA256 comparison |
| OHLCV cache | Weekly full | 90 days | Spot-check latest bar vs Alpaca |
| Off-box backup | Before every observation cycle | Permanent | SHA256 manifest + manual download |
| PostgreSQL (future) | Daily pg_dump | 30 days rolling | Restore test monthly |

---

## 8. Forbidden Behavior

These are **permanent** constraints — not temporary, not negotiable:

| # | Forbidden | Reason |
|---|---|---|
| B1 | Broker execution / trade placement | Research-only product; no Series 7/63 licensing |
| B2 | Buy/sell/hold recommendations | Constitutes investment advice; regulatory minefield |
| B3 | Personalized financial advice | No KYC, no suitability assessment, no fiduciary relationship |
| B4 | Threshold auto-tuning from small sample | n=7 is not enough for statistical optimization |
| B5 | Auto-publishing without admin review | Single point of failure; edge sheet could contain stale/misleading data |
| B6 | "Win rate" / "Performance" / "Returns" claims | Unbacked by independent statistical evidence |
| B7 | Real-time or intraday data | Infrastructure for daily only; real-time requires different licensing |
| B8 | Short-sale or options signals | Strategy is long-only continuation; extending requires new validation |
| B9 | Production code changing strategy behavior | Strategy changes require full research pipeline re-validation |
| B10 | Removing research-only disclaimers | Required by compliance — non-negotiable |

---

## 9. Phased Rollout Plan

### Phase 7A (current) — Architecture Plan
- [x] PRODUCTION_READINESS_PLAN.md
- [x] API_CONTRACT.md
- [x] DATABASE_SCHEMA.md
- [x] ADMIN_APPROVAL_FLOW.md
- [x] DEPLOYMENT_OPTIONS.md
- [x] COMPLIANCE_BOUNDARIES.md

### Phase 7B — Database Migration
- CSV → PostgreSQL migration script
- Row-Level Security policies
- Data validation (row counts, checksums)
- Migration test suite

### Phase 7C — Read-Only API
- Supabase project setup
- FastAPI / PostgREST endpoints
- API key management
- Rate limiting

### Phase 7D — Admin Approval
- Draft/published state machine
- Admin review dashboard
- Publish/rollback workflow

### Phase 7E — Subscription & Delivery
- Stripe Checkout integration
- Shopify storefront
- Email delivery (Resend)
- Webhook for new edge sheets

### Phase 7F — Multi-Cohort Evidence
- 3+ independent signal dates accumulated
- 30+ independent observations minimum
- Evidence reclassification: "first cohort" → "multi-cohort"

### Phase 7G — Legal & Compliance
- Terms of Service
- Privacy Policy
- Disclaimer language reviewed by counsel
- SEC/FINRA boundary analysis

### Phase 7H — Soft Launch
- Invite-only beta
- Feedback collection
- Monitoring dashboards

### Phase 7I — Public Launch
- Remove beta flag
- Marketing site live
- Paid subscriptions active

---

## 10. Current State Summary

| Metric | Value |
|---|---|
| Branch | `trust-calibration-working` |
| Commit | `398e526` |
| Full test suite | 398 passed / 0 failed |
| Source-only suite | 344 passed / 54 deselected |
| Healthcheck | PASS |
| Observations | 7 resolved, 0 pending |
| Independent signal dates | 2 (2026-05-20, 2026-06-05) |
| Distinct symbols | 6 (AMD, ARM, CRWD, DDOG, MRVL, SEDG) |
| Ghost ledger records | 87 |
| Edge audit labels | All 10 available, 16 metrics per observation |
| Strategy | `relative_strength_continuation_phase28a_weak_pass` |
| Production status | **BLOCKED** — research only |
| Live trading | **BLOCKED** |
| Broker execution | **DISABLED** |