-- database/schema.sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Monitored applications
CREATE TABLE applications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    vendor          TEXT,
    keywords        TEXT[],
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Specific versions
CREATE TABLE versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID REFERENCES applications(id) ON DELETE CASCADE,
    version_number  TEXT NOT NULL,
    release_date    DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Individual issues (crawled nuggets)
CREATE TABLE issues (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID REFERENCES applications(id) ON DELETE CASCADE,
    version_id      UUID REFERENCES versions(id) ON DELETE SET NULL,

    title           TEXT NOT NULL,
    summary         TEXT NOT NULL,
    raw_content     TEXT,
    source_type     TEXT NOT NULL,
    source_url      TEXT NOT NULL UNIQUE,

    severity        TEXT NOT NULL CHECK (severity IN ('critical', 'major', 'minor')),
    issue_type      TEXT,

    upvotes         INTEGER DEFAULT 0,
    comment_count   INTEGER DEFAULT 0,
    source_date     TIMESTAMP,

    embedding       vector(1536),

    created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_issues_embedding ON issues USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_issues_app_severity ON issues (application_id, severity);
CREATE INDEX idx_issues_version ON issues (version_id);
CREATE INDEX idx_issues_fulltext ON issues USING gin (to_tsvector('english', title || ' ' || summary));
CREATE INDEX idx_issues_source_url ON issues (source_url);
