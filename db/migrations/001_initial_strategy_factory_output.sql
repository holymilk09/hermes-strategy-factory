-- 001_initial_strategy_factory_output.sql
-- Phase 7B — PostgreSQL Output Store for Strategy Factory
-- Read-only published-output store. CSV ledgers remain source of truth.
-- Supabase PostgreSQL 15+ / standard PostgreSQL 14+.
-- All tables are APPEND-ONLY under service_role writes.
-- Subscribers have SELECT-only via Row-Level Security.

BEGIN;

-- ─────────────────────────────────────────────────────────
-- 1. system_runs — track every export / pipeline execution
-- ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS system_runs (
    id              BIGSERIAL PRIMARY KEY,
    run_id          TEXT UNIQUE NOT NULL,          -- deterministic: YYYYMMDD_HHMMSS + SHA256[:8]
    run_type        TEXT NOT NULL,                 -- 'export', 'migration', 'refresh'
    status          TEXT NOT NULL DEFAULT 'started', -- started | completed | failed | rolled_back
    ledgers_source  TEXT NOT NULL DEFAULT 'csv',   -- 'csv' until parity proven
    observation_count       INTEGER,
    resolved_count          INTEGER,
    pending_count           INTEGER,
    ghost_count             INTEGER,
    edge_audit_date         TEXT,
    export_rows_written     INTEGER DEFAULT 0,
    validation_passed       BOOLEAN,
    validation_errors       JSONB DEFAULT '[]'::jsonb,
    ledger_hash_observation TEXT,
    ledger_hash_outcome     TEXT,
    ledger_hash_ghost       TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_system_runs_status ON system_runs(status);
CREATE INDEX idx_system_runs_run_type ON system_runs(run_type);
CREATE INDEX idx_system_runs_started ON system_runs(started_at DESC);

-- ─────────────────────────────────────────────────────────
-- 2. setup_cards — per-observation setup context
-- ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS setup_cards (
    id                  BIGSERIAL PRIMARY KEY,
    observation_id      TEXT UNIQUE NOT NULL,
    symbol              TEXT NOT NULL,
    signal_date         TIMESTAMPTZ NOT NULL,
    signal_close        NUMERIC(12,4) NOT NULL,
    setup_label         TEXT NOT NULL,             -- e.g. 'Waiting for Stronger Proof'
    lineage             TEXT NOT NULL,             -- e.g. 'relative_strength_continuation_phase28a_weak_pass'
    strategy            TEXT NOT NULL DEFAULT 'relative_strength_continuation',
    status              TEXT NOT NULL DEFAULT 'PENDING', -- PENDING | RESOLVED
    maturity_bars       INTEGER NOT NULL DEFAULT 0, -- bars elapsed since signal
    maturity_window     INTEGER NOT NULL DEFAULT 10, -- required bars for maturity
    ret_5d              NUMERIC(10,6),
    ret_20d             NUMERIC(10,6),
    ret_60d             NUMERIC(10,6),
    ret_20d_rank        NUMERIC(6,4),
    ret_60d_rank        NUMERIC(6,4),
    close_above_ma50    BOOLEAN,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT chk_setup_label CHECK (setup_label <> ''),
    CONSTRAINT chk_maturity_window CHECK (maturity_window > 0)
);

CREATE INDEX idx_setup_cards_symbol ON setup_cards(symbol);
CREATE INDEX idx_setup_cards_signal_date ON setup_cards(signal_date DESC);
CREATE INDEX idx_setup_cards_status ON setup_cards(status);

-- ─────────────────────────────────────────────────────────
-- 3. maturity_results — resolved outcome data per observation
-- ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS maturity_results (
    id                          BIGSERIAL PRIMARY KEY,
    observation_id              TEXT UNIQUE NOT NULL REFERENCES setup_cards(observation_id),
    symbol                      TEXT NOT NULL,
    signal_date                 TIMESTAMPTZ NOT NULL,
    outcome_date                TIMESTAMPTZ,
    signal_close                NUMERIC(12,4) NOT NULL,
    outcome_close               NUMERIC(12,4),
    raw_return                  NUMERIC(12,6),     -- (outcome_close/signal_close - 1)
    spy_return                  NUMERIC(12,6),     -- SPY over same window
    qqq_return                  NUMERIC(12,6),     -- QQQ over same window
    benchmark_relative_return   NUMERIC(12,6),     -- raw_return - max(SPY, QQQ)
    cost_adjusted_return        NUMERIC(12,6),     -- from economic sanity
    delay_adjusted_return       NUMERIC(12,6),     -- from economic sanity
    drift_label                 TEXT,               -- from drift attribution
    sample_size_warning         BOOLEAN NOT NULL DEFAULT TRUE,
    concurrent_exposure_warning BOOLEAN NOT NULL DEFAULT FALSE,
    economic_sanity_status      TEXT,
    outcome_status              TEXT NOT NULL DEFAULT 'PENDING',
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_maturity_results_symbol ON maturity_results(symbol);
CREATE INDEX idx_maturity_results_signal_date ON maturity_results(signal_date DESC);
CREATE INDEX idx_maturity_results_drift_label ON maturity_results(drift_label);

-- ─────────────────────────────────────────────────────────
-- 4. edge_audit_results — per-observation audit detail
-- ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS edge_audit_results (
    id                      BIGSERIAL PRIMARY KEY,
    observation_id          TEXT NOT NULL REFERENCES setup_cards(observation_id),
    symbol                  TEXT NOT NULL,
    drift_label             TEXT,
    economic_sanity_status  TEXT,
    cost_status             TEXT,                   -- 'cost_fragile' | 'cost_resilient' | 'insufficient_data'
    delay_status            TEXT,                   -- 'delay_sensitive' | 'delay_resilient' | 'insufficient_data'
    filter_lift_status      TEXT,                   -- from filter quality audit
    stock_forward_return    NUMERIC(12,6),
    spy_forward_return      NUMERIC(12,6),
    qqq_forward_return      NUMERIC(12,6),
    cost_adjusted_return    NUMERIC(12,6),
    delay_adjusted_return    NUMERIC(12,6),
    compounding_artifact_warning BOOLEAN DEFAULT FALSE,
    concurrent_exposure_warning BOOLEAN DEFAULT FALSE,
    audit_run_id            TEXT NOT NULL,          -- which system_run generated this
    generated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_edge_audit_obs UNIQUE (observation_id, audit_run_id)
);

CREATE INDEX idx_edge_audit_obs_id ON edge_audit_results(observation_id);
CREATE INDEX idx_edge_audit_drift_label ON edge_audit_results(drift_label);
CREATE INDEX idx_edge_audit_run ON edge_audit_results(audit_run_id);

-- ─────────────────────────────────────────────────────────
-- 5. ghost_rejections — rejected candidates
-- ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS ghost_rejections (
    id                  BIGSERIAL PRIMARY KEY,
    ghost_id            TEXT UNIQUE NOT NULL,
    symbol              TEXT NOT NULL,
    rejection_date      TIMESTAMPTZ NOT NULL,       -- signal_date from ghost ledger
    rejection_reason    TEXT NOT NULL,               -- e.g. '20d_momentum_too_weak'
    failed_gate         TEXT NOT NULL,               -- e.g. 'ret_20d_rank'
    lineage             TEXT NOT NULL,               -- strategy lineage
    strategy_id         TEXT NOT NULL DEFAULT 'relative_strength_continuation',
    setup_type          TEXT DEFAULT 'swing',
    score_if_available  TEXT DEFAULT '',
    price_at_signal     NUMERIC(12,4) DEFAULT 0,
    outcome_5d          TEXT DEFAULT '',
    outcome_10d         TEXT DEFAULT '',
    outcome_20d         TEXT DEFAULT '',
    max_favorable_move  TEXT DEFAULT '',
    max_adverse_move    TEXT DEFAULT '',
    setup_broke         TEXT DEFAULT '',
    data_status         TEXT DEFAULT 'PENDING',
    audit_run_id        TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ghost_rej_symbol ON ghost_rejections(symbol);
CREATE INDEX idx_ghost_rej_date ON ghost_rejections(rejection_date DESC);
CREATE INDEX idx_ghost_rej_reason ON ghost_rejections(rejection_reason);
CREATE INDEX idx_ghost_rej_audit_run ON ghost_rejections(audit_run_id);

-- ─────────────────────────────────────────────────────────
-- 6. approved_publications — admin-approved edge sheet releases
-- ─────────────────────────────────────────────────────────

CREATE TYPE publication_status AS ENUM (
    'generated', 'reviewed', 'approved', 'published', 'rolled_back'
);

CREATE TABLE IF NOT EXISTS approved_publications (
    id                  BIGSERIAL PRIMARY KEY,
    publication_date    DATE NOT NULL,
    status              publication_status NOT NULL DEFAULT 'generated',
    audit_run_id        TEXT NOT NULL,
    grade               TEXT,
    market_weather      TEXT,
    observations_count  INTEGER NOT NULL DEFAULT 0,
    resolved_count      INTEGER NOT NULL DEFAULT 0,
    pending_count       INTEGER NOT NULL DEFAULT 0,
    reviewed_by         TEXT,
    reviewed_at         TIMESTAMPTZ,
    approved_by         TEXT,
    approved_at         TIMESTAMPTZ,
    published_at        TIMESTAMPTZ,
    rolled_back_at      TIMESTAMPTZ,
    rollback_reason     TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_publication_date UNIQUE (publication_date)
);

CREATE INDEX idx_approved_pub_date ON approved_publications(publication_date DESC);
CREATE INDEX idx_approved_pub_status ON approved_publications(status);

-- Only one published at a time
CREATE UNIQUE INDEX idx_approved_pub_one_published
    ON approved_publications (status)
    WHERE status = 'published';

-- ─────────────────────────────────────────────────────────
-- 7. user_ticker_selections — placeholder for future auth
-- ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS user_ticker_selections (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID,                           -- NULL placeholder — no auth yet
    symbol          TEXT NOT NULL,
    selected_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_user_ticker_symbol ON user_ticker_selections(symbol);

-- ─────────────────────────────────────────────────────────
-- Row-Level Security (Supabase-compatible)
-- ─────────────────────────────────────────────────────────

ALTER TABLE setup_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE maturity_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE edge_audit_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE ghost_rejections ENABLE ROW LEVEL SECURITY;
ALTER TABLE approved_publications ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_ticker_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_runs ENABLE ROW LEVEL SECURITY;

-- Authenticated subscribers can SELECT all tables
CREATE POLICY "Subscribers can read setup_cards"
    ON setup_cards FOR SELECT TO authenticated USING (true);

CREATE POLICY "Subscribers can read maturity_results"
    ON maturity_results FOR SELECT TO authenticated USING (true);

CREATE POLICY "Subscribers can read edge_audit_results"
    ON edge_audit_results FOR SELECT TO authenticated USING (true);

CREATE POLICY "Subscribers can read ghost_rejections"
    ON ghost_rejections FOR SELECT TO authenticated USING (true);

CREATE POLICY "Subscribers can read published"
    ON approved_publications FOR SELECT TO authenticated
    USING (status = 'published');

-- Anon (public) can read only published edge-sheet data
CREATE POLICY "Public can read published"
    ON approved_publications FOR SELECT TO anon
    USING (status = 'published');

-- service_role bypasses RLS (Supabase default)

COMMIT;