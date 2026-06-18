-- Tech-Career Mentor Bot — Database Schema
-- Jalankan di Supabase SQL Editor

CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wa_number     VARCHAR(20) UNIQUE NOT NULL,
    name          VARCHAR(100),
    joined_at     TIMESTAMPTZ DEFAULT NOW(),
    active_path   VARCHAR(50),
    last_seen_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS enrollments (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
    path_id       VARCHAR(50) NOT NULL,
    enrolled_at   TIMESTAMPTZ DEFAULT NOW(),
    completed_at  TIMESTAMPTZ,
    is_active     BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS module_progress (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
    path_id       VARCHAR(50) NOT NULL,
    module_id     VARCHAR(100) NOT NULL,
    status        VARCHAR(20) DEFAULT 'locked',
    completed_at  TIMESTAMPTZ,
    UNIQUE (user_id, path_id, module_id)
);

CREATE TABLE IF NOT EXISTS daily_challenges (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
    path_id       VARCHAR(50) NOT NULL,
    challenge_day INT NOT NULL,
    status        VARCHAR(20) DEFAULT 'pending',
    sent_at       TIMESTAMPTZ DEFAULT NOW(),
    responded_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS conversation_state (
    wa_number     VARCHAR(20) PRIMARY KEY,
    current_state VARCHAR(100),
    context_data  JSONB DEFAULT '{}',
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
