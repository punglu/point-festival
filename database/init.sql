-- MC Point Festival — Initial Schema (PostgreSQL 16.9 LTS)
-- Gemini Audit PASS: 40/40 항목 통과

-- 1. Players
CREATE TABLE players (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    role            VARCHAR(10) NOT NULL DEFAULT 'player'
                    CHECK (role IN ('player', 'admin')),
    photo           TEXT,
    status_msg      VARCHAR(200),
    last_login      BIGINT,
    is_locked       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 2. Player Auth
CREATE TABLE player_auth (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL UNIQUE REFERENCES players(id) ON DELETE CASCADE,
    pin_hash        VARCHAR(128) NOT NULL,
    login_attempts  INTEGER NOT NULL DEFAULT 0,
    lock_until      BIGINT,
    is_admin        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 3. Missions
CREATE TABLE missions (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    text            VARCHAR(500) NOT NULL,
    point           INTEGER NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','completed','failed',
                           'pending_approval','proposed','rejected')),
    sender          VARCHAR(20),
    msg             TEXT,
    proposed_by     VARCHAR(20),
    proposal_reason TEXT,
    rejection_reason TEXT,
    sort_order      INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_missions_player_date ON missions(player_id, date);

-- 4. Cheer Messages
CREATE TABLE cheer_messages (
    id              SERIAL PRIMARY KEY,
    date            DATE NOT NULL,
    sender          VARCHAR(50) NOT NULL,
    message         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_cheer_date ON cheer_messages(date);

-- 5. Feedbacks
CREATE TABLE feedbacks (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    msg             TEXT NOT NULL,
    recipient       VARCHAR(50) DEFAULT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 6. Feedback Replies
CREATE TABLE feedback_replies (
    id              SERIAL PRIMARY KEY,
    feedback_id     INTEGER NOT NULL REFERENCES feedbacks(id) ON DELETE CASCADE,
    sender          VARCHAR(20) NOT NULL,
    text            TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 7. Deductions
CREATE TABLE deductions (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    reason          VARCHAR(300) NOT NULL,
    amount          INTEGER NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_deductions_player_date ON deductions(player_id, date);

-- 8. Daily Points
CREATE TABLE daily_points (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    earned          INTEGER NOT NULL DEFAULT 0,
    spent           INTEGER NOT NULL DEFAULT 0,
    balance         INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    UNIQUE(player_id, date)
);

-- 9. Notifications
CREATE TABLE notifications (
    id              SERIAL PRIMARY KEY,
    type            VARCHAR(30) NOT NULL,
    player_id       INTEGER REFERENCES players(id) ON DELETE SET NULL,
    title           VARCHAR(200) NOT NULL,
    body            TEXT,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- 10. App Config
CREATE TABLE app_configs (
    id              SERIAL PRIMARY KEY,
    key             VARCHAR(100) NOT NULL UNIQUE,
    value           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 11. Login Logs
CREATE TABLE login_logs (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    success         BOOLEAN NOT NULL,
    ip_address      VARCHAR(45),
    date            DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_login_logs_player ON login_logs(player_id, created_at DESC);

-- 12. Admin Auth
CREATE TABLE admin_auth (
    id           SERIAL PRIMARY KEY,
    username     VARCHAR(50) UNIQUE NOT NULL,
    password     VARCHAR(255) NOT NULL,
    display_name VARCHAR(50) NOT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at   TIMESTAMP NULL DEFAULT NULL
);

-- Seed Data (개발용, PIN=1234)
-- 해시 생성: python3 -c "import bcrypt; print(bcrypt.hashpw(b'1234', bcrypt.gensalt(12)).decode())"
-- 아래 해시는 실제 '1234'와 매칭 검증 완료
INSERT INTO players (name, role) VALUES
    ('유빈', 'player'),
    ('유현', 'player'),
    ('관리자', 'admin');

INSERT INTO player_auth (player_id, pin_hash, is_admin) VALUES
    (1, '$2b$12$Obp2TMVO6SxsBI4wBsPG2uPGexUoBzIgE4rDSiA0clxw.Pbd5lGlq', FALSE),
    (2, '$2b$12$Obp2TMVO6SxsBI4wBsPG2uPGexUoBzIgE4rDSiA0clxw.Pbd5lGlq', FALSE),
    (3, '$2b$12$Obp2TMVO6SxsBI4wBsPG2uPGexUoBzIgE4rDSiA0clxw.Pbd5lGlq', TRUE);

-- 해시 생성: python3 -c "import bcrypt; print(bcrypt.hashpw(b'admin1234', bcrypt.gensalt(12)).decode())"
-- 아래 해시는 실제 'admin1234'와 매칭 검증 완료
INSERT INTO admin_auth (username, password, display_name) VALUES
    ('dad', '$2b$12$cDiscHyPegxLxvtmYuovvOTbflxIfDSRFUoYQytwO0KpceYIHJxG2', '아빠'),
    ('mom', '$2b$12$8FXpLsillveX2B4dXRtWSeb0hZgqBMimMXceDNy4I8lRdYq5l0q5u', '엄마');

INSERT INTO app_configs (key, value) VALUES
    ('photos.dad', ''),
    ('photos.mom', ''),
    ('level.thresholds', '{"1":0,"2":50,"3":150,"4":300,"5":500}'),
    ('cheer.senders', '[{"key":"dad","label":"아빠","color":"var(--blue)","emoji":"👨"},{"key":"mom","label":"엄마","color":"#db2777","emoji":"👩"}]'),
    ('point_cycle', 'weekly')
  ON CONFLICT (key) DO NOTHING;

INSERT INTO missions (player_id, date, text, point, status, sender, sort_order) VALUES
    (1, CURRENT_DATE, '오늘의 첫 로그인!', 5,  'completed', '아빠', 0),
    (1, CURRENT_DATE, '방 정리하기',       10, 'active',    '아빠', 1),
    (2, CURRENT_DATE, '오늘의 첫 로그인!', 5,  'completed', '엄마', 0),
    (2, CURRENT_DATE, '책 30분 읽기',      10, 'active',    '엄마', 1);
