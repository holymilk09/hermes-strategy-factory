# Deployment Options — Strategy Factory

> **Version:** 1.0  
> **Date:** 2026-07-01  
> **Status:** PLANNING — no deployment executed  

---

## 1. Architecture Overview

The system has three deployment domains:

| Domain | Where | What |
|---|---|---|
| **Data Pipeline** | VPS (existing) | OHLCV refresh, observation cycle, outcome resolution, edge audit, edge sheet generation |
| **Database + Auth** | Supabase (managed) | PostgreSQL, Row-Level Security, user authentication, API |
| **Retail Web App** | Vercel / Netlify | Customer-facing dashboard, subscription management |

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   DATA PIPELINE   │     │    SUPABASE       │     │   RETAIL APP      │
│   (VPS — private) │────▶│   (managed cloud) │────▶│   (Vercel edge)   │
│                    │     │                    │     │                    │
│ Hermes cron jobs  │     │ PostgreSQL 15     │     │ Next.js / React    │
│ Python scripts    │     │ Row-Level Security│     │ Tailwind CSS       │
│ CSV → PG sync     │     │ Supabase Auth     │     │ Stripe Checkout    │
│ Healthcheck       │     │ PostgREST API     │     │ Shopify Buy Button │
│                    │     │                    │     │                    │
│ NEVER exposed to  │     │ READ-ONLY for     │     │ Customer-facing    │
│ public internet   │     │ subscribers       │     │ only               │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

---

## 2. Data Pipeline (Existing VPS)

### 2.1 Current Infrastructure

| Component | Detail |
|---|---|
| Host | VPS running Linux 6.8.0 |
| Agent | Hermes (Nous Research) |
| Scheduler | Hermes cron (cronjob tool) |
| Python | 3.13.5, venv at `/opt/data/.venv` |
| Data | CSVs at `/opt/data/data/` |
| Gateway | Hermes gateway with watchdog auto-restart |
| Test suite | 398 tests, pytest + markers |

### 2.2 Required Additions for Production

| Addition | Purpose |
|---|---|
| PostgreSQL client (`psycopg2`) | Sync ledgers to Supabase after each cycle |
| Supabase service role key | Write access to PG (stored in `.env`, never committed) |
| Sync script | `scripts/sync_ledgers_to_supabase.py` — CSV → PG upsert after each cycle |
| Monitoring webhook | Notify admin on pipeline failure |
| Log rotation | `logrotate` for pipeline logs |

### 2.3 Security

- VPS is NOT exposed to public internet on any port except Hermes gateway
- Hermes gateway is Telegram-only (no public HTTP API)
- Alpaca API keys have DATA-ONLY permissions (no trading)
- Supabase service role key is the only outbound credential
- No customer data on VPS — all user data lives in Supabase

---

## 3. Supabase (Database + Auth + API)

### 3.1 Setup

```
Project: strategy-factory
Region: us-east-1 (or closest to user base)
Plan: Pro ($25/mo) — required for daily backups, no pausing
```

### 3.2 Features Used

| Feature | Purpose | Cost |
|---|---|---|
| PostgreSQL 15 | All 7 tables (observations, outcomes, ghost, edge_sheets, audit, subscriptions, email) | Included |
| Supabase Auth | User accounts, magic link, Google OAuth | 50,000 MAU free |
| Row-Level Security | Public vs subscriber vs admin access | Included |
| PostgREST API | Auto-generated REST API from PG schema | Included |
| Daily Backups | Point-in-time recovery | Pro plan required |
| Edge Functions | Stripe webhooks, email triggers | 500K invocations free |

### 3.3 API Generation

Supabase auto-generates REST endpoints from PostgreSQL tables + RLS:

```
GET https://[project].supabase.co/rest/v1/observations?select=*
GET https://[project].supabase.co/rest/v1/edge_sheets?status=eq.published&order=sheet_date.desc&limit=1
```

No server code needed for CRUD operations. RLS handles authorization automatically.

### 3.4 Auth Flow

```
User visits retail app
  │
  ├── Public / not logged in → sees latest published edge sheet (anon RLS)
  │
  └── Logs in via Supabase Auth
        │
        ├── Free tier → same as public (rate limited)
        │
        └── Active subscription → full access (observation detail, archive, ghost ledger)
              │
              └── Stripe webhook updates subscription status in PG
```

---

## 4. Retail Web App (Vercel + Next.js)

### 4.1 Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS |
| Auth | Supabase Auth React helpers |
| Database | Supabase JS client |
| Payments | Stripe Checkout + Stripe Customer Portal |
| Storefront | Shopify Buy Button (embedded) |
| Email | Resend (transactional) |
| Hosting | Vercel (free tier → Pro as needed) |

### 4.2 Pages

| Route | Content | Auth Required |
|---|---|---|
| `/` | Landing page — what is this, sample edge sheet | No |
| `/dashboard` | Today's edge sheet, scoreboard | Subscriber |
| `/archive` | Past edge sheets (date picker) | Subscriber |
| `/symbols/:symbol` | Single symbol history, all observations | Subscriber |
| `/account` | Subscription management (Stripe Customer Portal) | Subscriber |
| `/pricing` | Plans and pricing | No |
| `/login` | Supabase Auth (magic link) | No |

### 4.3 Design Principles

- **Mobile-first** — users will check on their phones
- **No charts** — plain English summaries, not candlestick charts
- **No real-time** — daily data, no websockets
- **Clear disclaimers** — research-only banner on every page
- **Grade visible** — honest B-grade (current) shown prominently

---

## 5. Shopify / Stripe Integration

### 5.1 Why Both?

| Tool | Purpose |
|---|---|
| **Stripe** | Subscription billing, recurring payments, customer portal |
| **Shopify** | One-time product purchases (edge sheet packs, research reports), brand presence |

### 5.2 Stripe Setup

```
Products:
  - Strategy Factory Monthly — $29/mo (base)
  - Strategy Factory Annual — $249/yr (~$20.75/mo)

Checkout:
  - Stripe Checkout (hosted) — no PCI compliance burden
  - Customer Portal — users manage their own subscription
  - Webhook → Supabase Edge Function → update subscriptions table

Flow:
  User clicks "Subscribe" → Stripe Checkout → Payment → Webhook → PG updated
  User clicks "Manage" → Stripe Customer Portal → self-service
```

### 5.3 Shopify Setup

```
Products (one-time purchases):
  - Edge Sheet Deep Dive ($9 one-time)
  - Observation Archive Pack ($19 one-time)
  - Strategy Factory Research Report ($49 one-time)

Integration:
  - Shopify Buy Button embedded in retail app
  - No separate Shopify storefront required
  - Inventory: digital products (unlimited)
```

### 5.4 Payment Flow

```
User on retail app:
  │
  ├── Subscription → Stripe Checkout popup
  │     └── Webhook → Supabase → subscription active → RLS unlocks
  │
  └── One-time purchase → Shopify Buy Button
        └── Digital delivery → email with download link (Resend)
```

---

## 6. Email Delivery

### 6.1 Provider: Resend

| Feature | Detail |
|---|---|
| Provider | Resend (resend.com) |
| Free tier | 100 emails/day |
| Pro | $20/mo for 50,000 emails |
| Templates | React Email (JSX-based email templates) |

### 6.2 Email Types

| Type | Trigger | Recipient | Content |
|---|---|---|---|
| Daily Edge Sheet | Edge sheet approved + published | Subscribers with email delivery on | Full edge sheet in email body |
| Weekly Summary | Every Monday 9am ET | Subscribers with weekly digest on | Past week's scoreboard changes |
| Welcome | New subscription | New subscriber | Getting started guide |
| Subscription Renewal | 3 days before period end | Subscriber | Renewal reminder |
| Admin Alert | Pipeline failure, healthcheck fail | Admins | Incident details |

### 6.3 Email Content Rules

- Every email MUST include: "Research-only. Not investment advice."
- No buy/sell language
- No "alert" / "signal" / "recommendation" in subject lines
- Subject: "Strategy Factory — Daily Edge Sheet, July 1 2026" (descriptive, neutral)

---

## 7. Cost Estimate

### 7.1 Monthly (soft launch)

| Service | Plan | Monthly Cost |
|---|---|---|
| Supabase | Pro | $25 |
| Vercel | Pro | $20 |
| Resend | Free → Pro | $0 → $20 |
| Stripe | Pay-as-you-go (2.9% + $0.30) | Variable |
| Shopify | Basic ($39/mo) or Buy Button only ($9/mo) | $9–$39 |
| VPS (existing) | Already paid | $0 incremental |
| Domain | strategyfactory.io | ~$15/yr |
| **Total** | | **$54–$104/mo + Stripe fees** |

### 7.2 Break-Even

At $29/mo subscription:
- ~2 subscribers = break-even at $54/mo
- ~4 subscribers = break-even at $104/mo

---

## 8. Monitoring Stack

| Tool | Purpose | Cost |
|---|---|---|
| Supabase Dashboard | DB health, query performance, auth metrics | Included |
| Vercel Analytics | Web app traffic, page views | Pro included |
| Hermes cron logs | Pipeline execution history | Existing |
| Resend Dashboard | Email delivery, bounces, opens | Included |
| Stripe Dashboard | Revenue, churn, failed payments | Included |
| UptimeRobot | Public API health check | Free tier (5-min interval) |

---

## 9. Deployment Sequence

### Phase 1: Database Migration (offline)
1. Create Supabase project
2. Run migration SQL from DATABASE_SCHEMA.md
3. Migrate existing CSV data → PG
4. Validate row counts, hashes, constraints
5. Set up RLS policies

### Phase 2: API + Auth (staging)
1. Set up Supabase Auth
2. Test PostgREST endpoints with anon/authenticated roles
3. Verify RLS: anon sees only published, authenticated sees all
4. Load test with 100 concurrent requests

### Phase 3: Sync Pipeline
1. Write `sync_ledgers_to_supabase.py`
2. Wire into Hermes cron (run after observation cycle)
3. Test idempotency (run twice → no duplicate rows)
4. Add sync to healthcheck

### Phase 4: Retail App (staging)
1. Next.js app scaffold
2. Supabase client integration
3. Dashboard page (latest edge sheet)
4. Archive page (date picker)
5. Account page (Stripe Customer Portal link)

### Phase 5: Payments (staging)
1. Stripe Checkout integration
2. Stripe webhook → Supabase Edge Function
3. Test subscription lifecycle (create → renew → cancel)

### Phase 6: Email (staging)
1. Resend integration
2. Daily edge sheet email template
3. Welcome email automation
4. Email delivery log in PG

### Phase 7: Soft Launch
1. DNS: strategyfactory.io → Vercel
2. SSL enforced
3. Invite-only beta (5-10 users)
4. Monitor for 2 weeks
5. Collect feedback, fix issues

### Phase 8: Public Launch
1. Remove invite gate
2. Enable Stripe live mode
3. Marketing site live
4. Paid subscriptions active