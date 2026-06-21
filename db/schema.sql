-- Studio Foto Bot — Database Schema
-- Jalankan di Supabase SQL Editor

CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wa_number     VARCHAR(20) UNIQUE NOT NULL,
    name          VARCHAR(100),
    joined_at     TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS conversation_state (
    wa_number     VARCHAR(20) PRIMARY KEY,
    current_state VARCHAR(100),
    context_data  JSONB DEFAULT '{}',
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bookings (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wa_number     VARCHAR(20) NOT NULL,
    nama          VARCHAR(100),
    layanan       VARCHAR(100) NOT NULL,
    paket         VARCHAR(50) NOT NULL,
    tanggal       DATE NOT NULL,
    jam           VARCHAR(10) NOT NULL,
    status        VARCHAR(50) DEFAULT 'menunggu_konfirmasi',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS time_slots (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tanggal       DATE NOT NULL,
    jam           VARCHAR(10) NOT NULL,
    is_available  BOOLEAN DEFAULT TRUE,
    UNIQUE (tanggal, jam)
);
