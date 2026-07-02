# Database Schema — Strategy Factory PostgreSQL Migration

> **Version:** 1.0  
> **Date:** 2026-07-01  
> **Status:** PLANNING — CSV → PostgreSQL migration not yet implemented  
> **Target:** Supabase PostgreSQL 15+

---

## 1. Overview

Current state: CSV files in `data/paper_observation/` and `data/trust_calibration/`.  
Target state: PostgreSQL tables with Row-Level Security, Supabase Auth, and indexed queries.

All tables are **append-mostly**. Observations and outcomes are written once, never updated (PENDING → RESOLVED is a status change in the outcome table, not an overwrite). Ghost records are append-only with idempotent inserts.

---

## 2. Tables

### 2.1 `observations`

Corresponds to `relative_strength_continuation_observation_ledger.csv`.

```sql
CREATE TABLE observations (
    id                  BIGSERIAL PRIMARY KEY,
    observation_id      TEXT UNIQUE NOT NULL,       -- SHA256[:24] deterministic
    signal_timestamp    TIMESTAMPTZ NOT NULL,
    symbol              TEXT NOT NULL,
    strategy            TEXT NOT NULL DEFAULT 'relative_strength_continuation',
    lineage             TEXT NOT NULL,
    signal_close        NUMERIC(12,4) NOT NULL,
    ret_5d              NUMERIC(10,6),
    ret_20d             NUMERIC(10,6),
    ret_60d             NUMERIC(10,6),
    ret_20d_rank        NUMERIC(6,4),
    ret_60d_rank        NUMERIC(6,4),
    close_above_ma50    BOOLEAN,
    outcome_window      INTEGER NOT NULL DEFAULT 10,
    outcome_status      TEXT NOT NULL DEFAULT 'PENDING',  -- PENDING | RESOLVED (in observation ledger, architectural)
    outcome_return      NUMERIC(10,6),
    outcome_timestamp   TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    sent_to_broker      BOOLEAN NOT NULL DEFAULT FALSE,
    broker_order_id     TEXT,

    -- Constraints
    CONSTRAINT chk_outcome_status CHECK (
        outcome_status IN ('PENDING', 'RESOLVED', 'PENDING_NO_OHLCV', 'PENDING_OHLCV_ERROR')
    ),
    CONSTRAINT chk_sent_to_broker_false CHECK (sent_to_broker = FALSE),
    CONSTRAINT chk_broker_order_id_null CHECK (broker_order_id IS NULL)
);

CREATE INDEX idx_observations_symbol ON observations(symbol);
CREATE INDEX idx_observations_signal_ts ON observations(signal_timestamp DESC);
CREATE INDEX idx_observations_status ON observations(outcome_status);
CREATE INDEX idx_observations_created ON observations(created_at DESC);
```

### 2.2 `outcomes`

Corresponds to `relative_strength_continuation_outcome_ledger.csv`.

```sql
CREATE TABLE outcomes (
    id                  BIGSERIAL PRIMARY KEY,
    observation_id      TEXT UNIQUE NOT NULL REFERENCES observations(observation_id),
    signal_timestamp    TIMESTAMPTZ NOT NULL,
    symbol              TEXT NOT NULL,
    signal_close        NUMERIC(12,4) NOT NULL,
    outcome_window      INTEGER NOT NULL DEFAULT 10,
    outcome_status      TEXT NOT NULL DEFAULT 'PENDING',
    outcome_return      NUMERIC(10,6),
    outcome_timestamp   TIMESTAMPTZ,
    outcome_close       NUMERIC(12,4),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_outcome_status_resolved CHECK (
        outcome_status IN ('PENDING', 'RESOLVED', 'PENDING_NO_OHLCV', 'PENDING_OHLCV_ERROR')
    )
);

CREATE INDEX idx_outcomes_status ON outcomes(outcome_status);
CREATE INDEX idx_outcomes_signal_ts ON outcomes(signal_timestamp DESC);
CREATE INDEX idx_outcomes_symbol ON outcomes(symbol);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_outcomes_updated_at
    BEFORE UPDATE ON outcomes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

### 2.3 `ghost_ledger`

Corresponds to `data/trust_calibration/ghost_ledger.csv`.

```sql
CREATE TABLE ghost_ledger (
    id                      BIGSERIAL PRIMARY KEY,
    ghost_id                TEXT UNIQUE NOT NULL,       -- SHA256[:24] deterministic
    source_observation_id   TEXT DEFAULT '',
    symbol                  TEXT NOT NULL,
    strategy_id             TEXT NOT NULL,
    setup_type              TEXT NOT NULL DEFAULT 'swing',
    signal_date             TIMESTAMPTZ NOT NULL,
    rejection_reason        TEXT NOT NULL,              -- e.g. '20d_momentum_too_weak'
    failed_gate             TEXT NOT NULL,              -- e.g. 'ret_20d_rank'
    score_if_available      TEXT DEFAULT '',
    price_at_signal         NUMERIC(12,4) DEFAULT 0,
    market_weather          TEXT DEFAULT '',
    published_status        TEXT NOT NULL DEFAULT 'GHOST_ONLY',
    reason_not_published    TEXT DEFAULT '',
    outcome_5d              TEXT DEFAULT '',
    outcome_10d             TEXT DEFAULT '',
    outcome_20d             TEXT DEFAULT '',
    outcome_30d             TEXT DEFAULT '',
    max_favorable_move      TEXT DEFAULT '',
    max_adverse_move        TEXT DEFAULT '',
    setup_broke             TEXT DEFAULT '',
    data_status             TEXT NOT NULL DEFAULT 'PENDING',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ghost_symbol ON ghost_ledger(symbol);
CREATE INDEX idx_ghost_signal_date ON ghost_ledger(signal_date DESC);
CREATE INDEX idx_ghost_rejection ON ghost_ledger(rejection_reason);
CREATE INDEX idx_ghost_data_status ON ghost_ledger(data_status);
```

### 2.4 `edge_sheets`

Tracks generated and approved edge sheets for the admin approval workflow.

```sql
CREATE TYPE edge_sheet_status AS ENUM ('generated', 'reviewed', 'approved', 'published', 'rolled_back');

CREATE TABLE edge_sheets (
    id                  BIGSERIAL PRIMARY KEY,
    sheet_date          DATE NOT NULL,
    status              edge_sheet_status NOT NULL DEFAULT 'generated',
    grade               TEXT,                           -- A/B/C/D/F
    market_weather      TEXT,
    maturity_classification TEXT,
    active_lineage      TEXT,
    json_content        JSONB NOT NULL,                  -- full edge sheet payload
    md_content          TEXT NOT NULL,                   -- full markdown content
    observations_count  INTEGER NOT NULL DEFAULT 0,
    outcomes_count      INTEGER NOT NULL DEFAULT 0,
    pending_cards_count INTEGER NOT NULL DEFAULT 0,
    generated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at         TIMESTAMPTZ,
    reviewed_by         TEXT,
    approved_at         TIMESTAMPTZ,
    approved_by         TEXT,
    published_at        TIMESTAMPTZ,
    rolled_back_at      TIMESTAMPTZ,
    rollback_reason     TEXT,

    CONSTRAINT uq_sheet_date UNIQUE (sheet_date)
);

CREATE INDEX idx_edge_sheets_date ON edge_sheets(sheet_date DESC);
CREATE INDEX idx_edge_sheets_status ON edge_sheets(status);

-- Only one published sheet at a time (the latest approved one)
CREATE UNIQUE INDEX idx_edge_sheets_one_published
    ON edge_sheets (status)
    WHERE status = 'published';
```

### 2.5 `audit_log`

Tracks every mutation and approval action.

```sql
CREATE TYPE audit_action AS ENUM (
    'observation_cycle_run',
    'outcome_resolved',
    'ghost_recorded',
    'edge_sheet_generated',
    'edge_sheet_reviewed',
    'edge_sheet_approved',
    'edge_sheet_published',
    'edge_sheet_rolled_back',
    'ohlcv_refreshed',
    'healthcheck_run',
    'admin_login'
);

CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    action          audit_action NOT NULL,
    actor           TEXT NOT NULL DEFAULT 'system',     -- 'system' or admin email
    detail          JSONB,                               -- action-specific metadata
    ledger_hash_before  TEXT,                            -- SHA256 before mutation
    ledger_hash_after   TEXT,                            -- SHA256 after mutation
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
```

### 2.6 `subscriptions` (future)

For Stripe integration.

```sql
CREATE TYPE subscription_status AS ENUM (
    'active', 'past_due', 'canceled', 'trialing', 'incomplete'
);

CREATE TABLE subscriptions (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             UUID NOT NULL REFERENCES auth.users(id),
    stripe_customer_id  TEXT UNIQUE,
    stripe_subscription_id TEXT UNIQUE,
    status              subscription_status NOT NULL DEFAULT 'incomplete',
    plan                TEXT NOT NULL DEFAULT 'monthly',
    current_period_start TIMESTAMPTZ,
    current_period_end  TIMESTAMPTZ,
    canceled_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

### 2.7 `email_delivery_log` (future)

For Resend / SendGrid integration.

```sql
CREATE TYPE email_delivery_status AS ENUM (
    'queued', 'sent', 'delivered', 'bounced', 'complained', 'opened'
);

CREATE TABLE email_delivery_log (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID REFERENCES auth.users(id),
    email_type      TEXT NOT NULL,                       -- 'daily_edge_sheet', 'weekly_summary'
    recipient_email TEXT NOT NULL,
    status          email_delivery_status NOT NULL DEFAULT 'queued',
    sent_at         TIMESTAMPTZ,
    delivered_at    TIMESTAMPTZ,
    opened_at       TIMESTAMPTZ,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_email_delivery_user ON email_delivery_log(user_id);
CREATE INDEX idx_email_delivery_status ON email_delivery_log(status);
```

---

## 3. Row-Level Security (RLS)

All data is read-only for subscribers. Only the `service_role` can write.

```sql
-- Enable RLS on all tables
ALTER TABLE observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE ghost_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE edge_sheets ENABLE ROW LEVEL SECURITY;

-- Subscribers can READ all tables
CREATE POLICY "Subscribers can read observations"
    ON observations FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Subscribers can read outcomes"
    ON outcomes FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Subscribers can read ghost_ledger"
    ON ghost_ledger FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Subscribers can read published edge sheets"
    ON edge_sheets FOR SELECT
    TO authenticated
    USING (status = 'published');

-- Public (anon) can only read the latest published edge sheet
CREATE POLICY "Public can read published edge sheets"
    ON edge_sheets FOR SELECT
    TO anon
    USING (status = 'published');

-- Only service_role can INSERT/UPDATE
-- (service_role bypasses RLS by default in Supabase)
```

---

## 4. Migration Strategy

### 4.1 Source → Target Mapping

| CSV File | PG Table | Key Column |
|---|---|---|
| `relative_strength_continuation_observation_ledger.csv` | `observations` | `observation_id` |
| `relative_strength_continuation_outcome_ledger.csv` | `outcomes` | `observation_id` |
| `ghost_ledger.csv` | `ghost_ledger` | `ghost_id` |
| `golden_edge_sheet.json` | `edge_sheets` | `sheet_date` |

### 4.2 Migration Script Pattern

```python
# migrate_csv_to_pg.py (planned)
import csv
import psycopg2

def migrate_observations(csv_path, conn):
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    with conn.cursor() as cur:
        for row in rows:
            cur.execute("""
                INSERT INTO observations (observation_id, signal_timestamp, ...)
                VALUES (%s, %s, ...)
                ON CONFLICT (observation_id) DO NOTHING
            """, (row['observation_id'], row['signal_timestamp'], ...))
    conn.commit()
```

### 4.3 Validation After Migration

| Check | Method |
|---|---|
| Row counts match | `SELECT COUNT(*)` vs `wc -l` CSV |
| Observation IDs match | `SELECT observation_id` vs CSV column |
| No sent_to_broker=True | `SELECT COUNT(*) WHERE sent_to_broker = TRUE` → must be 0 |
| No broker_order_id | `SELECT COUNT(*) WHERE broker_order_id IS NOT NULL` → must be 0 |
| Full test suite still passes | `PYTHONPATH=/opt/data pytest tests/` after migration |

---

## 5. Field Constraints Summary

| Table | Constraint | Reason |
|---|---|---|
| `observations` | `sent_to_broker = FALSE` (CHECK) | Safety — no broker execution |
| `observations` | `broker_order_id IS NULL` (CHECK) | Safety — no broker execution |
| `observations` | `observation_id` UNIQUE | No duplicate observations |
| `outcomes` | `observation_id` UNIQUE + FK → `observations` | 1:1 relationship |
| `ghost_ledger` | `ghost_id` UNIQUE | Idempotent appends |
| `edge_sheets` | Only one `published` at a time | Partial unique index |
| `edge_sheets` | `sheet_date` UNIQUE | One sheet per calendar date |

---

## 6. Supabase Project Structure (planned)

```
Project: strategy-factory
├── Database: PostgreSQL 15
│   ├── public.observations
│   ├── public.outcomes
│   ├── public.ghost_ledger
│   ├── public.edge_sheets
│   ├── public.audit_log
│   ├── public.subscriptions
│   └── public.email_delivery_log
├── Auth: Supabase Auth
│   ├── Email/password
│   ├── Magic link
│   └── OAuth (Google, GitHub)
├── Storage: (not used for research data)
├── Edge Functions: (optional — for email webhooks)
└── API: Auto-generated PostgREST + RLS
```