# IT Issue Tracker Design

## Overview

A tool for enterprise IT teams to assess risk before rolling out software updates. The system crawls public forums and communities ("watering holes") where IT professionals report issues with third-party software, then summarizes and classifies these issues for easy review.

**Use case:** Before rolling out Adobe Acrobat 2024.001 to 10,000 employees, an IT admin checks the dashboard to see: "3 critical issues, 8 major, 12 minor — recommend: WAIT."

## Rev1 Scope

**In scope:**
- Predefined list of applications to monitor
- Manual-trigger crawler (Python)
- LLM summarization + severity classification
- Semantic + keyword search
- Dashboard: application list → issues by version
- Local-only deployment

**Deferred to rev2:**
- User-submitted issues
- Scheduled/automated crawling
- Cloud deployment
- Additional data sources

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Crawler   │────▶│  PostgreSQL │◀────│   Node API  │◀────│  React App  │
│  (Python)   │     │  + pgvector │     │  (Express)  │     │   (Vite)    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

- **Direct DB access:** Crawler writes directly to PostgreSQL (simplest for local dev)
- **Monorepo:** Single repository containing all components

## Repository Structure

```
it-software-issue-tracker/
├── crawler/
│   ├── src/
│   │   ├── sources/
│   │   │   ├── reddit.py
│   │   │   ├── serverfault.py
│   │   │   ├── github_issues.py
│   │   │   └── bleepingcomputer.py
│   │   ├── llm/
│   │   │   ├── interface.py
│   │   │   ├── anthropic.py
│   │   │   └── openai.py
│   │   ├── summarizer.py
│   │   ├── embeddings.py
│   │   └── db.py
│   ├── requirements.txt
│   └── main.py
├── api/
│   ├── src/
│   │   ├── routes/
│   │   │   ├── applications.js
│   │   │   ├── issues.js
│   │   │   └── search.js
│   │   ├── services/
│   │   │   └── search.js
│   │   └── db.js
│   ├── package.json
│   └── index.js
├── web/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## Database Schema

```sql
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
    application_id  UUID REFERENCES applications(id),
    version_number  TEXT NOT NULL,
    release_date    DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Individual issues (crawled nuggets)
CREATE TABLE issues (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id  UUID REFERENCES applications(id),
    version_id      UUID REFERENCES versions(id),

    title           TEXT NOT NULL,
    summary         TEXT NOT NULL,
    raw_content     TEXT,
    source_type     TEXT NOT NULL,
    source_url      TEXT NOT NULL UNIQUE,

    severity        TEXT NOT NULL,
    issue_type      TEXT,

    upvotes         INTEGER DEFAULT 0,
    comment_count   INTEGER DEFAULT 0,
    source_date     TIMESTAMP,

    embedding       vector(1536),

    created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX ON issues USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON issues (application_id, severity);
CREATE INDEX ON issues (version_id);
CREATE INDEX ON issues USING gin (to_tsvector('english', title || ' ' || summary));
```

## Data Sources (v1)

### Tier 1: API-based

| Source | Method | Content |
|--------|--------|---------|
| Reddit (r/sysadmin) | Reddit API | Enterprise IT discussion, fast "is anyone else seeing this?" posts |
| Server Fault | Stack Exchange API | Structured Q&A, production impact troubleshooting |
| GitHub Issues | GitHub API | Vendor repo issues (e.g., microsoft/*, adobe/*) |

### Tier 2: Scrape-based (1 source to prove approach)

| Source | Method | Content |
|--------|--------|---------|
| BleepingComputer | HTML scrape | Windows update/install failures, recovery threads |

### Deferred to v2

- Spiceworks (login required)
- Microsoft Tech Community (JS-rendered)
- PatchManagement.org (mailing list)
- AskWoody
- Vendor communities (Cisco, VMware, Okta, etc.)

## Crawler Pipeline

```
For each application in database:
    keywords = application.keywords

    For each source (Reddit, ServerFault, GitHub, BleepingComputer):
        results = search(source, keywords, since=last_crawl_date)

        For each result:
            - Skip if source_url already in database
            - Fetch full content
            - Extract metadata (upvotes, date, comments)
            - Send to LLM for summarization + classification
            - Generate embedding
            - Save to database
```

### LLM Processing

**Input:** Raw forum post / issue / article

**Output:**
```json
{
  "title": "Adobe Acrobat crashes when printing PDFs with embedded fonts",
  "summary": "Users report Acrobat 2024.001 crashes during print jobs when...",
  "severity": "critical",
  "issue_type": "crash",
  "version_mentioned": "2024.001.20604",
  "affected_platforms": ["Windows 11"],
  "has_workaround": false
}
```

### Severity Classification

**Heuristics (from source):**
- Upvotes, reactions, comment count
- Number of "me too" replies
- Recency

**LLM (from content):**
- Impact keywords: "crash", "data loss", "won't start", "security" → Critical
- Scope keywords: "affects all users", "enterprise only", "edge case"
- Workaround presence lowers urgency

### CLI Commands

```bash
# Crawl all applications
python main.py crawl

# Crawl specific app
python main.py crawl --app "Adobe Acrobat"

# Add a new application to monitor
python main.py add-app --name "Adobe Acrobat" --vendor "Adobe" --keywords "acrobat,adobe reader,pdf"

# List monitored applications
python main.py list-apps
```

## API Endpoints

```
GET  /api/applications           - List all monitored applications with issue counts
GET  /api/applications/:id       - Get application details
POST /api/applications           - Add new application to monitor

GET  /api/applications/:id/issues - List issues for an application
GET  /api/issues/:id             - Get issue details
GET  /api/issues/search?q=       - Semantic + keyword search

GET  /api/versions               - List versions (filterable by application)
```

## Dashboard Views

### View 1: Application List (Home)

Primary view showing all monitored applications with severity rollup.

- Application name
- Issue counts by severity (critical/major/minor)
- Visual indicator (red/yellow/green)
- Last crawl timestamp

### View 2: Application Detail

Issues for a specific application, filterable by version and severity.

- Version selector
- Severity filter
- Issue cards showing: severity, type, title, source, engagement metrics
- Sorted by severity then recency

### View 3: Issue Detail

Full details for a single issue.

- Severity badge
- Title and summary
- Application and version
- Source link and metadata (upvotes, comments, date)
- Expandable raw content

## Tech Stack

| Component | Technology |
|-----------|------------|
| Crawler | Python 3.11+, requests/httpx, BeautifulSoup |
| LLM | Pluggable (Anthropic Claude / OpenAI GPT) |
| Embeddings | OpenAI text-embedding-3-small (1536 dimensions) |
| Database | PostgreSQL 16 + pgvector |
| API | Node.js, Express |
| Frontend | React 18, Vite |
| Local Dev | Docker Compose (PostgreSQL) |

## LLM Integration

```python
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def summarize_issue(raw_content: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{
            "role": "user",
            "content": PROMPT_TEMPLATE.format(content=raw_content)
        }]
    )
    return parse_json(response.content)
```

**Cost estimate:** Claude Haiku or GPT-4o-mini at ~$0.25/1M tokens. Processing 1,000 issues costs a few cents.

## Local Development Setup

```bash
# Start PostgreSQL with pgvector
docker-compose up -d

# Set up crawler
cd crawler && pip install -r requirements.txt

# Set up API
cd api && npm install

# Set up frontend
cd web && npm install

# Configure environment
export ANTHROPIC_API_KEY="sk-..."
export DATABASE_URL="postgresql://localhost:5432/it_tracker"
```

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Direct DB vs API-mediated | Direct DB | Simplest for local v1; refactor to API-mediated for cloud deployment |
| Monorepo vs multi-repo | Monorepo | Easier coordination for v1, single place to run everything |
| ORM vs raw SQL | Raw SQL | Fewer dependencies, full control, pgvector works better with raw queries |
| UI library | Plain CSS | Keep focus on functionality; add component library in v2 if needed |
| LLM provider | Pluggable | Start with one (Claude or OpenAI), interface allows swapping |
