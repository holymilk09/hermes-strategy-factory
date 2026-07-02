# API Contract — Strategy Factory Read-Only API

> **Version:** 1.0  
> **Date:** 2026-07-01  
> **Status:** PLANNING — no endpoints implemented  
> **Authentication:** API key (Supabase Row-Level Security) or public read for free tier  
> **Base URL:** `https://api.strategyfactory.io/v1` (planned)

---

## 1. General Rules

### 1.1 All Endpoints Are Read-Only

- HTTP method: `GET` only
- No `POST`, `PUT`, `PATCH`, `DELETE` endpoints
- No mutation of any ledger, observation, or audit data
- No broker execution endpoints
- No trading endpoints
- No order placement endpoints

### 1.2 Authentication

| Tier | Auth | Rate Limit | Access |
|---|---|---|---|
| Public / Free | Supabase anon key | 10 req/min | Latest edge sheet only |
| Subscriber | Supabase authenticated JWT | 100 req/min | All endpoints |
| Admin | Supabase service_role key | 1000 req/min | All + approval endpoints |

### 1.3 Response Format

All responses are JSON. All timestamps are ISO 8601 UTC.

```json
{
  "data": { ... },
  "meta": {
    "generated_at": "2026-07-01T10:00:00Z",
    "data_freshness": "2026-06-30",
    "disclaimer": "Research-only: This is not investment advice. No trading recommendations."
  }
}
```

---

## 2. Endpoints

### 2.1 Observations

#### `GET /v1/observations`

Returns the current observation universe — all observations in the ledger, sorted by signal date descending.

**Response:**
```json
{
  "data": {
    "observations": [
      {
        "observation_id": "f6fda996fae00a3e35ed61c6",
        "symbol": "MRVL",
        "strategy": "relative_strength_continuation",
        "lineage": "relative_strength_continuation_phase28a_weak_pass",
        "signal_date": "2026-06-05T04:00:00Z",
        "signal_close": 263.47,
        "outcome_date": "2026-06-22T04:00:00Z",
        "outcome_close": 307.86,
        "outcome_return": 0.1685,
        "outcome_status": "RESOLVED",
        "drift_label": "Independent Strength",
        "benchmark_relative_return": 0.1592
      }
    ]
  },
  "meta": {
    "total_observations": 7,
    "resolved": 7,
    "pending": 0,
    "oldest_signal_date": "2026-05-20",
    "newest_signal_date": "2026-06-05",
    "disclaimer": "Research-only: This is not investment advice."
  }
}
```

#### `GET /v1/observations/:observation_id`

Returns a single observation with full audit detail.

**Response:**
```json
{
  "data": {
    "observation_id": "f6fda996fae00a3e35ed61c6",
    "symbol": "MRVL",
    "strategy": "relative_strength_continuation",
    "lineage": "relative_strength_continuation_phase28a_weak_pass",
    "signal_date": "2026-06-05T04:00:00Z",
    "signal_close": 263.47,
    "outcome_date": "2026-06-22T04:00:00Z",
    "outcome_close": 307.86,
    "outcome_return": 0.1685,
    "outcome_status": "RESOLVED",
    "audit": {
      "drift_label": "Independent Strength",
      "economic_sanity": {
        "cost_adjusted_return": 0.1592,
        "delay_adjusted_return": 0.0658,
        "concurrent_exposure_warning": true,
        "compounding_artifact_warning": false
      },
      "benchmark_comparison": {
        "stock_forward_return": 0.1685,
        "SPY_forward_return": 0.0093,
        "QQQ_forward_return": 0.0466,
        "benchmark_relative_return": 0.1592
      }
    }
  },
  "meta": {
    "disclaimer": "Research-only. Not investment advice."
  }
}
```

### 2.2 Scoreboard

#### `GET /v1/scoreboard`

Returns the maturity scoreboard — all observations with their checkpoint results.

**Response:**
```json
{
  "data": {
    "rows": [
      {
        "ticker": "MRVL",
        "observation_id": "f6fda996fae00a3e35ed61c6",
        "signal_date": "2026-06-05T04:00:00Z",
        "initial_price": 263.47,
        "current_price": 297.89,
        "days_elapsed": 14,
        "maturity_status": "Setup Broke",
        "result_5_day": "+6.16%",
        "result_10_day": "+16.85%",
        "result_20_day": null,
        "result_summary": "Setup Broke",
        "plain_english_result": "Price moved below the setup-break level before full maturity."
      }
    ]
  },
  "meta": {
    "total_rows": 7,
    "matured_5d": 7,
    "matured_10d": 7,
    "matured_20d": 6,
    "disclaimer": "Research-only. Not investment advice."
  }
}
```

### 2.3 Edge Sheets

#### `GET /v1/edge-sheet/latest`

Returns the most recently approved edge sheet (ticker cards + scoreboard + reject ledger).

**Response:**
```json
{
  "data": {
    "date": "2026-07-01",
    "active_lineage": "relative_strength_continuation",
    "market_weather": "Market is helping this setup",
    "grade": "B",
    "ticker_cards": [
      {
        "symbol": "MRVL",
        "main_view": "Waiting for Pullback",
        "score": "80",
        "price_area_that_matters": "255.57 to 271.37",
        "setup_breaks_below": "252.93",
        "setup_breaks_above": "268.74",
        "why_it_looks_strong_or_weak": "Relative strength ranks remain elevated...",
        "main_risk": "Too Stretched",
        "what_changed": "Large short-term move increased pullback risk.",
        "plain_english": "This setup currently maps to 'Waiting for Pullback'...",
        "maturity_status": "still maturing"
      }
    ]
  },
  "meta": {
    "observations": 7,
    "outcomes": 7,
    "pending_cards": 7,
    "disclaimer": "Research-only: This report is for research tracking and education only."
  }
}
```

#### `GET /v1/edge-sheet/:date`

Returns a historical edge sheet for a specific date. Format: `YYYY-MM-DD`.

**Response:** Same as `/latest`, with `date` field matching the requested date.

Available dates: every trading day from 2026-05-20 onward (when the first edge sheet was generated).

### 2.4 Ghost Ledger

#### `GET /v1/ghost-ledger`

Returns a summary of the ghost ledger — rejected candidates aggregated by rejection reason.

**Response:**
```json
{
  "data": {
    "total_ghost_records": 87,
    "rejection_reasons": {
      "20d_momentum_too_weak": 42,
      "recent_negative_return": 28,
      "below_50ma": 12,
      "60d_momentum_too_weak": 5
    },
    "matured_ghost_records": 65,
    "pending_ghost_records": 22,
    "top_ghost_winners": [
      {
        "ghost_id": "b649f7fcf787e4de0fa3...",
        "symbol": "AMD",
        "return_20d": "+12.34%"
      }
    ],
    "top_ghost_losers": [
      {
        "ghost_id": "8009e5c06af775803756...",
        "symbol": "SEDG",
        "return_20d": "-18.21%"
      }
    ]
  },
  "meta": {
    "disclaimer": "Ghost candidates are rejected setups — tracked for filter quality calibration."
  }
}
```

### 2.5 Health

#### `GET /v1/health`

Returns system status and data freshness.

**Response:**
```json
{
  "data": {
    "status": "healthy",
    "healthcheck": "HEALTHCHECK_PASS_CONTINUE_WAITING",
    "data_freshness": "DATA_CURRENT",
    "latest_completed_session": "2026-06-30",
    "observations_total": 7,
    "observations_resolved": 7,
    "observations_pending": 0,
    "production": "BLOCKED",
    "live": "BLOCKED",
    "broker_execution": "DISABLED",
    "shadow_orders": "DISABLED"
  }
}
```

---

## 3. Error Responses

| Status | Code | Meaning |
|---|---|---|
| 200 | OK | Success |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Valid key but insufficient tier (e.g., free tier accessing archive) |
| 404 | Not Found | Resource doesn't exist (invalid date, unknown observation ID) |
| 429 | Too Many Requests | Rate limit exceeded |
| 503 | Service Unavailable | Data pipeline hasn't run yet today |

Error body:
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Try again in 30 seconds.",
    "retry_after_seconds": 30
  }
}
```

---

## 4. Endpoints Explicitly NOT Provided

| Not Provided | Reason |
|---|---|
| `POST /orders` | No broker execution |
| `POST /signals` | No buy/sell recommendations |
| `POST /portfolio` | No personalized financial advice |
| `POST /backtest` | Research infrastructure, not production API |
| `POST /optimize` | Threshold tuning requires full research pipeline validation |
| `GET /user/profile` | No KYC, no suitability assessment |
| `GET /real-time` | Daily data only — intraday requires different licensing |
| `POST /admin/publish` | Admin approval is manual — not API-automated |

---

## 5. Implementation Notes

### 5.1 Backend Options

| Option | Pros | Cons |
|---|---|---|
| **Supabase + PostgREST** | No server code, auto-generated API from PG schema, RLS built-in | Less control over response shape |
| **FastAPI + PostgreSQL** | Full control, Python-native, easy integration with existing code | More infrastructure to manage |
| **Vercel + Supabase** | Edge functions, fast global delivery, free tier | Cold starts, vendor lock-in |

**Recommended:** Supabase for database + auth + RLS. FastAPI on VPS for data pipeline + edge sheet generation. Vercel for retail web app.

### 5.2 Rate Limiting

- Implemented at API gateway level (Supabase or Cloudflare)
- Free tier: 10 req/min, 100 req/day
- Subscriber: 100 req/min, 10,000 req/day

### 5.3 Caching

- Edge sheet: cached for 1 hour (updates once daily)
- Observations: cached for 5 minutes (immutable once resolved)
- Health: no cache (real-time status)

---

## 6. Contract Stability

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-07-01 | Initial contract — planning only |