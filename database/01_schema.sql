-- ============================================================
-- SMARTBANCS - DATABASE SCHEMA
-- ============================================================

-- Extensión para generar UUID automáticamente
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ============================================================
-- 1. CUENTAS
-- ============================================================

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    account_number VARCHAR(20) NOT NULL UNIQUE,

    customer_ref VARCHAR(50) NOT NULL,

    balance NUMERIC(18,2) NOT NULL DEFAULT 0,

    currency CHAR(3) NOT NULL DEFAULT 'USD',

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_accounts_balance
        CHECK (balance >= 0),

    CONSTRAINT chk_accounts_currency
        CHECK (currency = 'USD'),

    CONSTRAINT chk_accounts_status
        CHECK (status IN ('ACTIVE', 'BLOCKED', 'CLOSED'))
);


-- ============================================================
-- 2. TRANSACCIONES
-- ============================================================

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    idempotency_key VARCHAR(64) NOT NULL UNIQUE,

    source_account_id UUID NOT NULL,

    destination_account_id UUID NOT NULL,

    amount NUMERIC(18,2) NOT NULL,

    currency CHAR(3) NOT NULL DEFAULT 'USD',

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    completed_at TIMESTAMPTZ,

    CONSTRAINT fk_transactions_source
        FOREIGN KEY (source_account_id)
        REFERENCES accounts(id),

    CONSTRAINT fk_transactions_destination
        FOREIGN KEY (destination_account_id)
        REFERENCES accounts(id),

    CONSTRAINT chk_transactions_different_accounts
        CHECK (source_account_id <> destination_account_id),

    CONSTRAINT chk_transactions_amount
        CHECK (amount > 0),

    CONSTRAINT chk_transactions_currency
        CHECK (currency = 'USD'),

    CONSTRAINT chk_transactions_status
        CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED'))
);


-- ============================================================
-- 3. EVENTOS OUTBOX
-- ============================================================

CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    transaction_id UUID NOT NULL,

    event_type VARCHAR(50) NOT NULL,

    payload JSONB NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    attempts INTEGER NOT NULL DEFAULT 0,

    next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    last_error TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    processed_at TIMESTAMPTZ,

    CONSTRAINT fk_outbox_transaction
        FOREIGN KEY (transaction_id)
        REFERENCES transactions(id),

    CONSTRAINT chk_outbox_status
        CHECK (status IN ('PENDING', 'PROCESSING', 'PROCESSED', 'FAILED')),

    CONSTRAINT chk_outbox_attempts
        CHECK (attempts >= 0),

    CONSTRAINT uq_outbox_transaction_event
        UNIQUE (transaction_id, event_type)
);


-- ============================================================
-- 4. RECOMENDACIONES DE IA
-- ============================================================

CREATE TABLE ai_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    account_id UUID NOT NULL,

    recommendation TEXT,

    model VARCHAR(100) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_ai_account
        FOREIGN KEY (account_id)
        REFERENCES accounts(id),

    CONSTRAINT chk_ai_status
        CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED'))
);


-- ============================================================
-- 5. ÍNDICES
-- ============================================================

CREATE INDEX idx_accounts_status
    ON accounts(status);

CREATE INDEX idx_transactions_source_account
    ON transactions(source_account_id);

CREATE INDEX idx_transactions_destination_account
    ON transactions(destination_account_id);

CREATE INDEX idx_transactions_created_at
    ON transactions(created_at);

CREATE INDEX idx_transactions_status
    ON transactions(status);

CREATE INDEX idx_outbox_status_next_attempt
    ON outbox_events(status, next_attempt_at);

CREATE INDEX idx_outbox_transaction
    ON outbox_events(transaction_id);

CREATE INDEX idx_ai_recommendations_account
    ON ai_recommendations(account_id);

CREATE INDEX idx_ai_recommendations_status
    ON ai_recommendations(status);