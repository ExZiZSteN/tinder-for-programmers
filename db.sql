--============================================================
-- EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- ENUMS
-- ============================================================

CREATE TYPE user_role AS ENUM ('user', 'admin');

CREATE TYPE project_format AS ENUM (
    'remote',
    'office',
    'hybrid'
);

CREATE TYPE payment_type AS ENUM (
    'volunteer',
    'paid',
    'equity'
);

CREATE TYPE project_status AS ENUM (
    'draft',
    'open',
    'closed',
    'completed',
    'archived'
);

CREATE TYPE swipe_status AS ENUM (
    'pending',
    'approved',
    'rejected',
    'withdrawn'
);

CREATE TYPE match_status AS ENUM (
    'active',
    'completed',
    'closed'
);

CREATE TYPE notification_type AS ENUM (
    'new_swipe',
    'swipe_approved',
    'swipe_rejected',
    'match_created',
    'new_message',
    'system'
);

-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,

    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    role user_role NOT NULL DEFAULT 'user',

    full_name VARCHAR(150) NOT NULL,
    bio TEXT,

    github_url VARCHAR(255),
    linkedin_url VARCHAR(255),
    portfolio_url VARCHAR(255),

    experience_years SMALLINT DEFAULT 0
        CHECK (experience_years BETWEEN 0 AND 50),

    avatar_file_id BIGINT,
    resume_file_id BIGINT,

    embedding vector(384),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_banned BOOLEAN NOT NULL DEFAULT FALSE,

    last_login_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email
ON users(email);

CREATE INDEX idx_users_embedding
ON users
USING hnsw (embedding vector_cosine_ops);

-- ============================================================
-- SKILLS
-- ============================================================

CREATE TABLE skills (
    id BIGSERIAL PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_skills_name
ON skills(name);

-- ============================================================
-- USER SKILLS
-- ============================================================

CREATE TABLE user_skills (
    user_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    skill_id BIGINT NOT NULL
        REFERENCES skills(id)
        ON DELETE CASCADE,

    PRIMARY KEY (user_id, skill_id)
);

-- ============================================================
-- PROJECTS
-- ============================================================

CREATE TABLE projects (
    id BIGSERIAL PRIMARY KEY,

    owner_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE RESTRICT,

    title VARCHAR(200) NOT NULL,

    description TEXT NOT NULL,

    format project_format NOT NULL DEFAULT 'remote',

    payment_type payment_type NOT NULL DEFAULT 'volunteer',

    status project_status NOT NULL DEFAULT 'draft',

    embedding vector(384),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_projects_owner
ON projects(owner_id);

CREATE INDEX idx_projects_status
ON projects(status);

CREATE INDEX idx_projects_title_trgm
ON projects
USING gin(title gin_trgm_ops);

CREATE INDEX idx_projects_embedding
ON projects
USING hnsw (embedding vector_cosine_ops);

-- ============================================================
-- PROJECT SKILLS
-- ============================================================

CREATE TABLE project_skills (
    project_id BIGINT NOT NULL
        REFERENCES projects(id)
        ON DELETE CASCADE,

    skill_id BIGINT NOT NULL
        REFERENCES skills(id)
        ON DELETE CASCADE,

    PRIMARY KEY (project_id, skill_id)
);

-- ============================================================
-- FILES
-- ============================================================

CREATE TABLE files (
    id BIGSERIAL PRIMARY KEY,

    owner_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,

    path VARCHAR(500) NOT NULL,

    size_bytes BIGINT NOT NULL
        CHECK (size_bytes >= 0),

    mime_type VARCHAR(100) NOT NULL,

    bucket VARCHAR(100) NOT NULL DEFAULT 'uploads',

    is_public BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_files_owner
ON files(owner_id);

ALTER TABLE users
ADD CONSTRAINT fk_users_avatar
FOREIGN KEY (avatar_file_id)
REFERENCES files(id)
ON DELETE SET NULL;

ALTER TABLE users
ADD CONSTRAINT fk_users_resume
FOREIGN KEY (resume_file_id)
REFERENCES files(id)
ON DELETE SET NULL;

-- ============================================================
-- SWIPES
-- ============================================================

CREATE TABLE swipes (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    project_id BIGINT NOT NULL
        REFERENCES projects(id)
        ON DELETE CASCADE,

    message TEXT,

    status swipe_status NOT NULL DEFAULT 'pending',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    reviewed_at TIMESTAMPTZ,

    CONSTRAINT uq_swipe_per_project
        UNIQUE(user_id, project_id)
);

CREATE INDEX idx_swipes_user
ON swipes(user_id);

CREATE INDEX idx_swipes_project_pending
ON swipes(project_id, created_at DESC)
WHERE status = 'pending';

-- ============================================================
-- MATCHES
-- ============================================================

CREATE TABLE matches (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    project_id BIGINT NOT NULL
        REFERENCES projects(id)
        ON DELETE RESTRICT,

    swipe_id BIGINT NOT NULL UNIQUE
        REFERENCES swipes(id)
        ON DELETE CASCADE,

    status match_status NOT NULL DEFAULT 'active',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    closed_at TIMESTAMPTZ,

    CONSTRAINT uq_match_pair
        UNIQUE(user_id, project_id)
);

CREATE INDEX idx_matches_user
ON matches(user_id);

CREATE INDEX idx_matches_project
ON matches(project_id);

-- ============================================================
-- PROJECT MEMBERS
-- ============================================================

CREATE TYPE member_role AS ENUM (
    'developer',
    'teamlead',
    'owner'
);

CREATE TABLE project_members (
    id BIGSERIAL PRIMARY KEY,

    project_id BIGINT NOT NULL
        REFERENCES projects(id)
        ON DELETE CASCADE,

    user_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    role member_role NOT NULL DEFAULT 'developer',

    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    left_at TIMESTAMPTZ,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_project_member
        UNIQUE(project_id, user_id)
);

CREATE INDEX idx_project_members_project
ON project_members(project_id);

CREATE INDEX idx_project_members_user
ON project_members(user_id);

CREATE INDEX idx_project_members_active
ON project_members(project_id, is_active)
WHERE is_active = TRUE;

-- ============================================================
-- MESSAGES
-- ============================================================

CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,

    match_id BIGINT NOT NULL
        REFERENCES matches(id)
        ON DELETE CASCADE,

    sender_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE RESTRICT,

    content TEXT NOT NULL,

    is_read BOOLEAN NOT NULL DEFAULT FALSE,

    read_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_message_content
        CHECK(char_length(content) BETWEEN 1 AND 4000)
);

CREATE INDEX idx_messages_match_created
ON messages(match_id, created_at);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================

CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    type notification_type NOT NULL,

    title VARCHAR(200) NOT NULL,

    body TEXT,

    payload JSONB NOT NULL DEFAULT '{}',

    is_read BOOLEAN NOT NULL DEFAULT FALSE,

    read_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_unread
ON notifications(user_id, created_at DESC)
WHERE is_read = FALSE;

-- ============================================================
-- REFRESH TOKENS
-- ============================================================

CREATE TABLE refresh_tokens (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    token_hash VARCHAR(64) NOT NULL UNIQUE,

    family_id UUID NOT NULL,

    expires_at TIMESTAMPTZ NOT NULL,

    revoked BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user
ON refresh_tokens(user_id);

-- ============================================================
-- UPDATED_AT TRIGGERS
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_projects_updated_at
BEFORE UPDATE ON projects
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();