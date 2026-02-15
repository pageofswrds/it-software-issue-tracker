# IT Software Issue Tracker Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a tool for enterprise IT teams to assess software update risk by crawling public forums for reported issues and classifying them by severity.

**Architecture:** Python crawler writes directly to PostgreSQL (with pgvector). Node.js/Express API serves data to React frontend. All components run locally via Docker Compose.

**Tech Stack:** Python 3.11+, Node.js 20+, React 18, PostgreSQL 16 + pgvector, Docker

---

## Phase 1: Infrastructure Setup

### Task 1.1: Database Schema Setup

**Files:**
- Create: `database/schema.sql`
- Create: `database/seed.sql`

**Step 1: Create schema file**

```sql
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
CREATE INDEX idx_issues_embedding ON issues USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_issues_app_severity ON issues (application_id, severity);
CREATE INDEX idx_issues_version ON issues (version_id);
CREATE INDEX idx_issues_fulltext ON issues USING gin (to_tsvector('english', title || ' ' || summary));
CREATE INDEX idx_issues_source_url ON issues (source_url);
```

**Step 2: Create seed file with sample applications**

```sql
-- database/seed.sql
-- Sample applications to monitor
INSERT INTO applications (name, vendor, keywords) VALUES
    ('Adobe Acrobat', 'Adobe', ARRAY['adobe acrobat', 'acrobat reader', 'acrobat dc', 'pdf reader']),
    ('Microsoft Teams', 'Microsoft', ARRAY['microsoft teams', 'ms teams', 'teams app']),
    ('Zoom', 'Zoom', ARRAY['zoom', 'zoom client', 'zoom app']),
    ('Slack', 'Salesforce', ARRAY['slack', 'slack app', 'slack desktop']);
```

**Step 3: Update docker-compose.yml to run schema on startup**

Read current docker-compose.yml first, then update it.

**Step 4: Test database setup**

Run: `docker-compose up -d`
Run: `docker exec -it it-tracker-db psql -U postgres -d it_tracker -c "\dt"`
Expected: Tables `applications`, `versions`, `issues` listed

**Step 5: Commit**

```bash
git add database/
git commit -m "feat: add database schema and seed data"
```

---

### Task 1.2: Python Crawler Project Setup

**Files:**
- Create: `crawler/requirements.txt`
- Create: `crawler/pyproject.toml`
- Create: `crawler/src/__init__.py`
- Create: `crawler/tests/__init__.py`

**Step 1: Create requirements.txt**

```
# crawler/requirements.txt
httpx==0.27.0
beautifulsoup4==4.12.3
psycopg[binary]==3.1.18
anthropic==0.25.0
openai==1.30.0
python-dotenv==1.0.1
click==8.1.7
praw==7.7.1
pytest==8.2.0
pytest-asyncio==0.23.6
```

**Step 2: Create pyproject.toml**

```toml
# crawler/pyproject.toml
[project]
name = "it-issue-crawler"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

**Step 3: Create package init files**

```python
# crawler/src/__init__.py
```

```python
# crawler/tests/__init__.py
```

**Step 4: Create virtual environment and install dependencies**

Run: `cd crawler && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
Expected: All packages installed successfully

**Step 5: Verify pytest works**

Run: `cd crawler && source .venv/bin/activate && pytest --collect-only`
Expected: "no tests ran" (empty collection is fine)

**Step 6: Commit**

```bash
git add crawler/
git commit -m "feat: scaffold Python crawler project"
```

---

### Task 1.3: Node.js API Project Setup

**Files:**
- Create: `api/package.json`
- Create: `api/src/index.js`
- Create: `api/.env.example`

**Step 1: Create package.json**

```json
{
  "name": "it-issue-tracker-api",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "node --watch src/index.js",
    "start": "node src/index.js",
    "test": "node --test tests/"
  },
  "dependencies": {
    "express": "^4.19.2",
    "pg": "^8.11.5",
    "pgvector": "^0.2.0",
    "cors": "^2.8.5",
    "dotenv": "^16.4.5"
  }
}
```

**Step 2: Create basic Express server**

```javascript
// api/src/index.js
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`);
});
```

**Step 3: Create .env.example**

```
# api/.env.example
PORT=3001
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/it_tracker
```

**Step 4: Install dependencies**

Run: `cd api && npm install`
Expected: node_modules created, no errors

**Step 5: Test server starts**

Run: `cd api && npm run dev &`
Run: `curl http://localhost:3001/api/health`
Expected: `{"status":"ok"}`
Run: `pkill -f "node.*src/index.js"` (stop the server)

**Step 6: Commit**

```bash
git add api/
git commit -m "feat: scaffold Node.js API project"
```

---

### Task 1.4: React Frontend Project Setup

**Files:**
- Create: `web/package.json`
- Create: `web/vite.config.js`
- Create: `web/index.html`
- Create: `web/src/main.jsx`
- Create: `web/src/App.jsx`
- Create: `web/src/App.css`

**Step 1: Create package.json**

```json
{
  "name": "it-issue-tracker-web",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.2.12"
  }
}
```

**Step 2: Create vite.config.js**

```javascript
// web/vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  }
});
```

**Step 3: Create index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>IT Issue Tracker</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

**Step 4: Create main.jsx**

```jsx
// web/src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**Step 5: Create App.jsx**

```jsx
// web/src/App.jsx
function App() {
  return (
    <div className="app">
      <header>
        <h1>IT Issue Tracker</h1>
      </header>
      <main>
        <p>Dashboard coming soon...</p>
      </main>
    </div>
  );
}

export default App;
```

**Step 6: Create App.css**

```css
/* web/src/App.css */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
  color: #333;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  margin-bottom: 24px;
}

header h1 {
  font-size: 24px;
  font-weight: 600;
}
```

**Step 7: Install dependencies and test**

Run: `cd web && npm install`
Run: `cd web && npm run dev &`
Run: `curl -s http://localhost:3000 | head -20`
Expected: HTML with "IT Issue Tracker" title
Run: `pkill -f vite` (stop the server)

**Step 8: Commit**

```bash
git add web/
git commit -m "feat: scaffold React frontend project"
```

---

## Phase 2: Crawler Database Layer

### Task 2.1: Database Connection Module

**Files:**
- Create: `crawler/src/db.py`
- Create: `crawler/tests/test_db.py`
- Create: `crawler/.env.example`

**Step 1: Write failing test for database connection**

```python
# crawler/tests/test_db.py
import pytest
from src.db import Database

def test_database_connects():
    db = Database()
    assert db.is_connected() == True
    db.close()

def test_database_can_query():
    db = Database()
    result = db.execute("SELECT 1 as num")
    assert result[0]['num'] == 1
    db.close()
```

**Step 2: Run test to verify it fails**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_db.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.db'"

**Step 3: Create .env.example**

```
# crawler/.env.example
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/it_tracker
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
```

**Step 4: Write database module**

```python
# crawler/src/db.py
import os
from typing import Any
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not set")
        self.conn = psycopg.connect(self.database_url, row_factory=dict_row)

    def is_connected(self) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception:
            return False

    def execute(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                return cur.fetchall()
            return []

    def execute_many(self, query: str, params_list: list[tuple]) -> None:
        with self.conn.cursor() as cur:
            cur.executemany(query, params_list)
        self.conn.commit()

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
```

**Step 5: Create .env file for testing**

Run: `cd crawler && cp .env.example .env`
Then edit `.env` to set: `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/it_tracker`

**Step 6: Run test to verify it passes**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_db.py -v`
Expected: PASS (2 tests)

**Step 7: Commit**

```bash
git add crawler/src/db.py crawler/tests/test_db.py crawler/.env.example
git commit -m "feat: add database connection module"
```

---

### Task 2.2: Application Repository

**Files:**
- Create: `crawler/src/repositories/__init__.py`
- Create: `crawler/src/repositories/applications.py`
- Create: `crawler/tests/test_applications.py`

**Step 1: Write failing test**

```python
# crawler/tests/test_applications.py
import pytest
from src.db import Database
from src.repositories.applications import ApplicationRepository

@pytest.fixture
def db():
    database = Database()
    yield database
    database.close()

def test_list_applications(db):
    repo = ApplicationRepository(db)
    apps = repo.list_all()
    assert isinstance(apps, list)
    # Seed data should have at least Adobe Acrobat
    assert len(apps) >= 1

def test_get_application_by_id(db):
    repo = ApplicationRepository(db)
    apps = repo.list_all()
    if apps:
        app = repo.get_by_id(apps[0]['id'])
        assert app is not None
        assert 'name' in app
        assert 'keywords' in app
```

**Step 2: Run test to verify it fails**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_applications.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write implementation**

```python
# crawler/src/repositories/__init__.py
from .applications import ApplicationRepository

__all__ = ['ApplicationRepository']
```

```python
# crawler/src/repositories/applications.py
from typing import Any
from src.db import Database

class ApplicationRepository:
    def __init__(self, db: Database):
        self.db = db

    def list_all(self) -> list[dict[str, Any]]:
        return self.db.execute("""
            SELECT id, name, vendor, keywords, created_at
            FROM applications
            ORDER BY name
        """)

    def get_by_id(self, app_id: str) -> dict[str, Any] | None:
        results = self.db.execute(
            "SELECT id, name, vendor, keywords, created_at FROM applications WHERE id = %s",
            (app_id,)
        )
        return results[0] if results else None

    def create(self, name: str, vendor: str | None, keywords: list[str]) -> dict[str, Any]:
        results = self.db.execute(
            """
            INSERT INTO applications (name, vendor, keywords)
            VALUES (%s, %s, %s)
            RETURNING id, name, vendor, keywords, created_at
            """,
            (name, vendor, keywords)
        )
        self.db.commit()
        return results[0]
```

**Step 4: Run test to verify it passes**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_applications.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add crawler/src/repositories/ crawler/tests/test_applications.py
git commit -m "feat: add application repository"
```

---

### Task 2.3: Issue Repository

**Files:**
- Create: `crawler/src/repositories/issues.py`
- Create: `crawler/tests/test_issues.py`

**Step 1: Write failing test**

```python
# crawler/tests/test_issues.py
import pytest
from src.db import Database
from src.repositories.applications import ApplicationRepository
from src.repositories.issues import IssueRepository

@pytest.fixture
def db():
    database = Database()
    yield database
    database.close()

@pytest.fixture
def app_id(db):
    repo = ApplicationRepository(db)
    apps = repo.list_all()
    return apps[0]['id']

def test_create_issue(db, app_id):
    repo = IssueRepository(db)
    issue = repo.create(
        application_id=app_id,
        title="Test crash issue",
        summary="App crashes on startup",
        raw_content="Full content here...",
        source_type="reddit",
        source_url="https://reddit.com/r/test/123",
        severity="critical",
        issue_type="crash",
        upvotes=50,
        comment_count=10
    )
    assert issue['id'] is not None
    assert issue['title'] == "Test crash issue"
    assert issue['severity'] == "critical"

    # Cleanup
    db.execute("DELETE FROM issues WHERE id = %s", (issue['id'],))
    db.commit()

def test_list_issues_by_application(db, app_id):
    repo = IssueRepository(db)
    issues = repo.list_by_application(app_id)
    assert isinstance(issues, list)

def test_issue_exists_by_url(db, app_id):
    repo = IssueRepository(db)
    unique_url = "https://reddit.com/unique/test/456"

    # Should not exist initially
    assert repo.exists_by_url(unique_url) == False

    # Create issue
    issue = repo.create(
        application_id=app_id,
        title="Test",
        summary="Test",
        raw_content="Test",
        source_type="reddit",
        source_url=unique_url,
        severity="minor"
    )

    # Now should exist
    assert repo.exists_by_url(unique_url) == True

    # Cleanup
    db.execute("DELETE FROM issues WHERE id = %s", (issue['id'],))
    db.commit()
```

**Step 2: Run test to verify it fails**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_issues.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# crawler/src/repositories/issues.py
from typing import Any
from datetime import datetime
from src.db import Database

class IssueRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(
        self,
        application_id: str,
        title: str,
        summary: str,
        source_type: str,
        source_url: str,
        severity: str,
        raw_content: str | None = None,
        version_id: str | None = None,
        issue_type: str | None = None,
        upvotes: int = 0,
        comment_count: int = 0,
        source_date: datetime | None = None,
        embedding: list[float] | None = None
    ) -> dict[str, Any]:
        results = self.db.execute(
            """
            INSERT INTO issues (
                application_id, version_id, title, summary, raw_content,
                source_type, source_url, severity, issue_type,
                upvotes, comment_count, source_date, embedding
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                application_id, version_id, title, summary, raw_content,
                source_type, source_url, severity, issue_type,
                upvotes, comment_count, source_date, embedding
            )
        )
        self.db.commit()
        return results[0]

    def list_by_application(
        self,
        application_id: str,
        severity: str | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM issues
            WHERE application_id = %s
        """
        params = [application_id]

        if severity:
            query += " AND severity = %s"
            params.append(severity)

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        return self.db.execute(query, tuple(params))

    def get_by_id(self, issue_id: str) -> dict[str, Any] | None:
        results = self.db.execute(
            "SELECT * FROM issues WHERE id = %s",
            (issue_id,)
        )
        return results[0] if results else None

    def exists_by_url(self, source_url: str) -> bool:
        results = self.db.execute(
            "SELECT 1 FROM issues WHERE source_url = %s LIMIT 1",
            (source_url,)
        )
        return len(results) > 0

    def count_by_severity(self, application_id: str) -> dict[str, int]:
        results = self.db.execute(
            """
            SELECT severity, COUNT(*) as count
            FROM issues
            WHERE application_id = %s
            GROUP BY severity
            """,
            (application_id,)
        )
        return {r['severity']: r['count'] for r in results}
```

**Step 4: Update repositories __init__.py**

```python
# crawler/src/repositories/__init__.py
from .applications import ApplicationRepository
from .issues import IssueRepository

__all__ = ['ApplicationRepository', 'IssueRepository']
```

**Step 5: Run test to verify it passes**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_issues.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add crawler/src/repositories/ crawler/tests/test_issues.py
git commit -m "feat: add issue repository"
```

---

## Phase 3: LLM Integration

### Task 3.1: LLM Interface

**Files:**
- Create: `crawler/src/llm/__init__.py`
- Create: `crawler/src/llm/interface.py`
- Create: `crawler/src/llm/anthropic_provider.py`
- Create: `crawler/tests/test_llm.py`

**Step 1: Write failing test**

```python
# crawler/tests/test_llm.py
import pytest
from src.llm import get_llm_provider
from src.llm.interface import LLMProvider, IssueAnalysis

def test_llm_provider_interface():
    # Test that interface defines required methods
    assert hasattr(LLMProvider, 'analyze_issue')

def test_issue_analysis_structure():
    analysis = IssueAnalysis(
        title="Test Issue",
        summary="This is a test",
        severity="critical",
        issue_type="crash",
        version_mentioned="1.0.0",
        has_workaround=False
    )
    assert analysis.title == "Test Issue"
    assert analysis.severity == "critical"

def test_get_llm_provider_returns_anthropic():
    provider = get_llm_provider("anthropic")
    assert provider is not None
```

**Step 2: Run test to verify it fails**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_llm.py -v`
Expected: FAIL

**Step 3: Write interface**

```python
# crawler/src/llm/interface.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class IssueAnalysis:
    title: str
    summary: str
    severity: str  # 'critical', 'major', 'minor'
    issue_type: str | None = None  # 'crash', 'performance', 'install', 'security', etc.
    version_mentioned: str | None = None
    has_workaround: bool = False

class LLMProvider(ABC):
    @abstractmethod
    def analyze_issue(self, raw_content: str, application_name: str) -> IssueAnalysis:
        """Analyze raw content and extract structured issue information."""
        pass
```

**Step 4: Write Anthropic provider**

```python
# crawler/src/llm/anthropic_provider.py
import os
import json
import anthropic
from .interface import LLMProvider, IssueAnalysis

ANALYSIS_PROMPT = """Analyze this IT support forum post about {application_name} and extract structured information.

Post content:
{content}

Respond with ONLY a JSON object (no markdown, no explanation) with these fields:
- title: A concise title for this issue (max 100 chars)
- summary: A 2-3 sentence summary of the problem and any solutions mentioned
- severity: "critical" (crashes, data loss, security), "major" (significant functionality broken), or "minor" (cosmetic, workarounds exist)
- issue_type: One of "crash", "performance", "install", "security", "compatibility", "ui", "other"
- version_mentioned: The software version mentioned, or null if not specified
- has_workaround: true if a workaround is mentioned, false otherwise

JSON response:"""

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

    def analyze_issue(self, raw_content: str, application_name: str) -> IssueAnalysis:
        prompt = ANALYSIS_PROMPT.format(
            application_name=application_name,
            content=raw_content[:4000]  # Truncate to avoid token limits
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()
        data = json.loads(response_text)

        return IssueAnalysis(
            title=data.get("title", "Unknown Issue"),
            summary=data.get("summary", ""),
            severity=data.get("severity", "minor"),
            issue_type=data.get("issue_type"),
            version_mentioned=data.get("version_mentioned"),
            has_workaround=data.get("has_workaround", False)
        )
```

**Step 5: Write __init__.py**

```python
# crawler/src/llm/__init__.py
from .interface import LLMProvider, IssueAnalysis
from .anthropic_provider import AnthropicProvider

def get_llm_provider(provider_name: str = "anthropic") -> LLMProvider:
    if provider_name == "anthropic":
        return AnthropicProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")

__all__ = ['LLMProvider', 'IssueAnalysis', 'get_llm_provider', 'AnthropicProvider']
```

**Step 6: Run test to verify it passes**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_llm.py -v`
Expected: PASS (note: the integration test will need API key to run fully)

**Step 7: Commit**

```bash
git add crawler/src/llm/ crawler/tests/test_llm.py
git commit -m "feat: add LLM interface and Anthropic provider"
```

---

### Task 3.2: Embeddings Module

**Files:**
- Create: `crawler/src/embeddings.py`
- Create: `crawler/tests/test_embeddings.py`

**Step 1: Write failing test**

```python
# crawler/tests/test_embeddings.py
import pytest
from src.embeddings import get_embedding, EMBEDDING_DIMENSION

def test_embedding_dimension_constant():
    assert EMBEDDING_DIMENSION == 1536

def test_get_embedding_returns_correct_dimension():
    # This test requires OPENAI_API_KEY
    # Skip if not available
    import os
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")

    embedding = get_embedding("This is a test sentence")
    assert len(embedding) == EMBEDDING_DIMENSION
    assert all(isinstance(x, float) for x in embedding)
```

**Step 2: Run test to verify it fails**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_embeddings.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# crawler/src/embeddings.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_DIMENSION = 1536
EMBEDDING_MODEL = "text-embedding-3-small"

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        _client = OpenAI(api_key=api_key)
    return _client

def get_embedding(text: str) -> list[float]:
    """Generate embedding for the given text using OpenAI's embedding model."""
    client = _get_client()

    # Truncate text if too long (max ~8000 tokens for this model)
    text = text[:30000]

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding
```

**Step 4: Run test (may skip if no API key)**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_embeddings.py -v`
Expected: PASS or SKIPPED

**Step 5: Commit**

```bash
git add crawler/src/embeddings.py crawler/tests/test_embeddings.py
git commit -m "feat: add embeddings module using OpenAI"
```

---

## Phase 4: Reddit Crawler

### Task 4.1: Reddit Source Module

**Files:**
- Create: `crawler/src/sources/__init__.py`
- Create: `crawler/src/sources/reddit.py`
- Create: `crawler/tests/test_reddit.py`

**Step 1: Write failing test**

```python
# crawler/tests/test_reddit.py
import pytest
from src.sources.reddit import RedditSource, RedditPost

def test_reddit_post_structure():
    post = RedditPost(
        id="abc123",
        title="Test Post",
        content="This is the content",
        url="https://reddit.com/r/sysadmin/abc123",
        subreddit="sysadmin",
        upvotes=100,
        comment_count=25,
        created_utc=1700000000.0
    )
    assert post.id == "abc123"
    assert post.upvotes == 100

def test_reddit_source_initialization():
    import os
    if not os.environ.get("REDDIT_CLIENT_ID"):
        pytest.skip("Reddit credentials not set")

    source = RedditSource()
    assert source is not None
```

**Step 2: Run test to verify it fails**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_reddit.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# crawler/src/sources/__init__.py
from .reddit import RedditSource, RedditPost

__all__ = ['RedditSource', 'RedditPost']
```

```python
# crawler/src/sources/reddit.py
import os
from dataclasses import dataclass
from datetime import datetime
import praw
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RedditPost:
    id: str
    title: str
    content: str
    url: str
    subreddit: str
    upvotes: int
    comment_count: int
    created_utc: float

    @property
    def created_at(self) -> datetime:
        return datetime.fromtimestamp(self.created_utc)

    @property
    def full_url(self) -> str:
        return f"https://reddit.com{self.url}"

class RedditSource:
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_agent: str = "IT-Issue-Tracker/0.1"
    ):
        self.client_id = client_id or os.environ.get("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("REDDIT_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError("Reddit credentials not set")

        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=user_agent
        )

    def search(
        self,
        keywords: list[str],
        subreddit: str = "sysadmin",
        time_filter: str = "week",
        limit: int = 25
    ) -> list[RedditPost]:
        """Search subreddit for posts matching keywords."""
        results = []
        seen_ids = set()

        subreddit_obj = self.reddit.subreddit(subreddit)

        for keyword in keywords:
            try:
                for submission in subreddit_obj.search(
                    keyword,
                    sort="relevance",
                    time_filter=time_filter,
                    limit=limit
                ):
                    if submission.id in seen_ids:
                        continue
                    seen_ids.add(submission.id)

                    # Combine title and selftext for content
                    content = f"{submission.title}\n\n{submission.selftext}"

                    results.append(RedditPost(
                        id=submission.id,
                        title=submission.title,
                        content=content,
                        url=submission.permalink,
                        subreddit=subreddit,
                        upvotes=submission.score,
                        comment_count=submission.num_comments,
                        created_utc=submission.created_utc
                    ))
            except Exception as e:
                print(f"Error searching for '{keyword}': {e}")
                continue

        return results
```

**Step 4: Run test**

Run: `cd crawler && source .venv/bin/activate && pytest tests/test_reddit.py -v`
Expected: PASS (first test passes, second may skip without credentials)

**Step 5: Commit**

```bash
git add crawler/src/sources/ crawler/tests/test_reddit.py
git commit -m "feat: add Reddit source module"
```

---

## Phase 5: CLI and Pipeline

### Task 5.1: CLI Entry Point

**Files:**
- Create: `crawler/main.py`
- Create: `crawler/src/crawler.py`

**Step 1: Write the crawler orchestrator**

```python
# crawler/src/crawler.py
from typing import Callable
from src.db import Database
from src.repositories import ApplicationRepository, IssueRepository
from src.sources.reddit import RedditSource, RedditPost
from src.llm import get_llm_provider, IssueAnalysis
from src.embeddings import get_embedding

class Crawler:
    def __init__(
        self,
        db: Database,
        llm_provider: str = "anthropic",
        on_progress: Callable[[str], None] | None = None
    ):
        self.db = db
        self.app_repo = ApplicationRepository(db)
        self.issue_repo = IssueRepository(db)
        self.llm = get_llm_provider(llm_provider)
        self.on_progress = on_progress or print

    def log(self, message: str) -> None:
        self.on_progress(message)

    def crawl_application(self, app_id: str) -> int:
        """Crawl all sources for a single application. Returns count of new issues."""
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ValueError(f"Application not found: {app_id}")

        self.log(f"Crawling: {app['name']}")
        keywords = app['keywords']
        new_count = 0

        # Crawl Reddit
        try:
            reddit = RedditSource()
            posts = reddit.search(keywords)
            self.log(f"  Found {len(posts)} Reddit posts")

            for post in posts:
                if self.issue_repo.exists_by_url(post.full_url):
                    continue

                try:
                    new_count += self._process_post(app, post)
                except Exception as e:
                    self.log(f"  Error processing {post.id}: {e}")
        except Exception as e:
            self.log(f"  Reddit error: {e}")

        self.log(f"  Added {new_count} new issues")
        return new_count

    def _process_post(self, app: dict, post: RedditPost) -> int:
        """Process a single post and store as issue. Returns 1 if stored, 0 if skipped."""
        self.log(f"  Processing: {post.title[:50]}...")

        # Analyze with LLM
        analysis = self.llm.analyze_issue(post.content, app['name'])

        # Skip if LLM thinks it's not relevant (very short summary)
        if len(analysis.summary) < 20:
            return 0

        # Generate embedding
        embedding = get_embedding(f"{analysis.title} {analysis.summary}")

        # Store issue
        self.issue_repo.create(
            application_id=app['id'],
            title=analysis.title,
            summary=analysis.summary,
            raw_content=post.content,
            source_type="reddit",
            source_url=post.full_url,
            severity=analysis.severity,
            issue_type=analysis.issue_type,
            upvotes=post.upvotes,
            comment_count=post.comment_count,
            source_date=post.created_at,
            embedding=embedding
        )

        return 1

    def crawl_all(self) -> int:
        """Crawl all applications. Returns total new issues."""
        apps = self.app_repo.list_all()
        total = 0
        for app in apps:
            total += self.crawl_application(app['id'])
        return total
```

**Step 2: Write CLI entry point**

```python
# crawler/main.py
import click
from src.db import Database
from src.repositories import ApplicationRepository
from src.crawler import Crawler

@click.group()
def cli():
    """IT Issue Tracker Crawler CLI"""
    pass

@cli.command()
@click.option('--app', 'app_name', help='Crawl specific application by name')
def crawl(app_name: str | None):
    """Crawl sources for IT issues."""
    db = Database()
    try:
        crawler = Crawler(db)

        if app_name:
            # Find app by name
            apps = ApplicationRepository(db).list_all()
            app = next((a for a in apps if a['name'].lower() == app_name.lower()), None)
            if not app:
                click.echo(f"Application not found: {app_name}")
                return
            count = crawler.crawl_application(app['id'])
        else:
            count = crawler.crawl_all()

        click.echo(f"\nDone! Added {count} new issues.")
    finally:
        db.close()

@cli.command('list-apps')
def list_apps():
    """List all monitored applications."""
    db = Database()
    try:
        repo = ApplicationRepository(db)
        apps = repo.list_all()

        if not apps:
            click.echo("No applications configured.")
            return

        click.echo("\nMonitored Applications:")
        click.echo("-" * 50)
        for app in apps:
            keywords = ", ".join(app['keywords'][:3])
            click.echo(f"  {app['name']} ({app['vendor'] or 'Unknown vendor'})")
            click.echo(f"    Keywords: {keywords}")
    finally:
        db.close()

@cli.command('add-app')
@click.option('--name', required=True, help='Application name')
@click.option('--vendor', help='Vendor name')
@click.option('--keywords', required=True, help='Comma-separated search keywords')
def add_app(name: str, vendor: str | None, keywords: str):
    """Add a new application to monitor."""
    db = Database()
    try:
        repo = ApplicationRepository(db)
        keyword_list = [k.strip() for k in keywords.split(',')]
        app = repo.create(name, vendor, keyword_list)
        click.echo(f"Added: {app['name']} (id: {app['id']})")
    finally:
        db.close()

if __name__ == '__main__':
    cli()
```

**Step 3: Test CLI**

Run: `cd crawler && source .venv/bin/activate && python main.py --help`
Expected: Shows help with crawl, list-apps, add-app commands

Run: `cd crawler && source .venv/bin/activate && python main.py list-apps`
Expected: Shows seeded applications (Adobe Acrobat, etc.)

**Step 4: Commit**

```bash
git add crawler/main.py crawler/src/crawler.py
git commit -m "feat: add CLI and crawler orchestration"
```

---

## Phase 6: Node.js API

### Task 6.1: Database Connection

**Files:**
- Create: `api/src/db.js`
- Create: `api/.env`

**Step 1: Create .env file**

```
PORT=3001
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/it_tracker
```

**Step 2: Write database module**

```javascript
// api/src/db.js
import pg from 'pg';
import pgvector from 'pgvector/pg';

const { Pool } = pg;

let pool = null;

export async function getPool() {
  if (!pool) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL
    });
    await pgvector.registerType(pool);
  }
  return pool;
}

export async function query(text, params) {
  const pool = await getPool();
  const result = await pool.query(text, params);
  return result.rows;
}

export async function queryOne(text, params) {
  const rows = await query(text, params);
  return rows[0] || null;
}
```

**Step 3: Commit**

```bash
git add api/src/db.js api/.env
git commit -m "feat: add API database connection"
```

---

### Task 6.2: Applications Routes

**Files:**
- Create: `api/src/routes/applications.js`
- Modify: `api/src/index.js`

**Step 1: Write applications routes**

```javascript
// api/src/routes/applications.js
import { Router } from 'express';
import { query, queryOne } from '../db.js';

const router = Router();

// List all applications with issue counts
router.get('/', async (req, res) => {
  try {
    const apps = await query(`
      SELECT
        a.*,
        COALESCE(SUM(CASE WHEN i.severity = 'critical' THEN 1 ELSE 0 END), 0)::int as critical_count,
        COALESCE(SUM(CASE WHEN i.severity = 'major' THEN 1 ELSE 0 END), 0)::int as major_count,
        COALESCE(SUM(CASE WHEN i.severity = 'minor' THEN 1 ELSE 0 END), 0)::int as minor_count,
        COUNT(i.id)::int as total_issues
      FROM applications a
      LEFT JOIN issues i ON i.application_id = a.id
      GROUP BY a.id
      ORDER BY a.name
    `);
    res.json(apps);
  } catch (err) {
    console.error('Error fetching applications:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get single application
router.get('/:id', async (req, res) => {
  try {
    const app = await queryOne(
      'SELECT * FROM applications WHERE id = $1',
      [req.params.id]
    );
    if (!app) {
      return res.status(404).json({ error: 'Application not found' });
    }
    res.json(app);
  } catch (err) {
    console.error('Error fetching application:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get issues for application
router.get('/:id/issues', async (req, res) => {
  try {
    const { severity } = req.query;
    let queryText = `
      SELECT * FROM issues
      WHERE application_id = $1
    `;
    const params = [req.params.id];

    if (severity) {
      queryText += ' AND severity = $2';
      params.push(severity);
    }

    queryText += ' ORDER BY created_at DESC LIMIT 100';

    const issues = await query(queryText, params);
    res.json(issues);
  } catch (err) {
    console.error('Error fetching issues:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
```

**Step 2: Update index.js to use routes**

```javascript
// api/src/index.js
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import applicationsRouter from './routes/applications.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/applications', applicationsRouter);

app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`);
});
```

**Step 3: Test the API**

Run: `cd api && npm run dev &`
Run: `curl http://localhost:3001/api/applications | jq`
Expected: JSON array of applications with issue counts

**Step 4: Commit**

```bash
git add api/src/
git commit -m "feat: add applications API routes"
```

---

### Task 6.3: Issues and Search Routes

**Files:**
- Create: `api/src/routes/issues.js`
- Create: `api/src/routes/search.js`
- Modify: `api/src/index.js`

**Step 1: Write issues routes**

```javascript
// api/src/routes/issues.js
import { Router } from 'express';
import { query, queryOne } from '../db.js';

const router = Router();

// Get single issue
router.get('/:id', async (req, res) => {
  try {
    const issue = await queryOne(
      `SELECT i.*, a.name as application_name, a.vendor
       FROM issues i
       JOIN applications a ON a.id = i.application_id
       WHERE i.id = $1`,
      [req.params.id]
    );
    if (!issue) {
      return res.status(404).json({ error: 'Issue not found' });
    }
    res.json(issue);
  } catch (err) {
    console.error('Error fetching issue:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
```

**Step 2: Write search routes**

```javascript
// api/src/routes/search.js
import { Router } from 'express';
import { query } from '../db.js';
import OpenAI from 'openai';

const router = Router();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Search issues (semantic + keyword)
router.get('/', async (req, res) => {
  try {
    const { q, limit = 20 } = req.query;

    if (!q) {
      return res.status(400).json({ error: 'Query parameter q is required' });
    }

    // Generate embedding for query
    const embeddingResponse = await openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: q
    });
    const queryEmbedding = embeddingResponse.data[0].embedding;

    // Semantic search with cosine similarity
    const issues = await query(`
      SELECT
        i.*,
        a.name as application_name,
        a.vendor,
        1 - (i.embedding <=> $1::vector) as similarity
      FROM issues i
      JOIN applications a ON a.id = i.application_id
      WHERE i.embedding IS NOT NULL
      ORDER BY i.embedding <=> $1::vector
      LIMIT $2
    `, [`[${queryEmbedding.join(',')}]`, parseInt(limit)]);

    res.json(issues);
  } catch (err) {
    console.error('Error searching:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
```

**Step 3: Update index.js**

```javascript
// api/src/index.js
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import applicationsRouter from './routes/applications.js';
import issuesRouter from './routes/issues.js';
import searchRouter from './routes/search.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/applications', applicationsRouter);
app.use('/api/issues', issuesRouter);
app.use('/api/search', searchRouter);

app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`);
});
```

**Step 4: Update package.json to add openai**

```json
{
  "name": "it-issue-tracker-api",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "node --watch src/index.js",
    "start": "node src/index.js",
    "test": "node --test tests/"
  },
  "dependencies": {
    "express": "^4.19.2",
    "pg": "^8.11.5",
    "pgvector": "^0.2.0",
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "openai": "^4.47.1"
  }
}
```

**Step 5: Install new dependency and test**

Run: `cd api && npm install`
Run: `cd api && npm run dev &`
Run: `curl "http://localhost:3001/api/issues" | jq`

**Step 6: Commit**

```bash
git add api/
git commit -m "feat: add issues and search API routes"
```

---

## Phase 7: React Frontend

### Task 7.1: Application List Page

**Files:**
- Create: `web/src/pages/ApplicationList.jsx`
- Create: `web/src/components/ApplicationCard.jsx`
- Modify: `web/src/App.jsx`

**Step 1: Create ApplicationCard component**

```jsx
// web/src/components/ApplicationCard.jsx
function ApplicationCard({ app, onClick }) {
  const totalIssues = app.critical_count + app.major_count + app.minor_count;

  let statusIcon = '✓';
  let statusClass = 'status-ok';

  if (app.critical_count > 0) {
    statusIcon = '🔴';
    statusClass = 'status-critical';
  } else if (app.major_count > 0) {
    statusIcon = '⚠️';
    statusClass = 'status-major';
  }

  return (
    <div className={`app-card ${statusClass}`} onClick={onClick}>
      <div className="app-card-header">
        <span className="status-icon">{statusIcon}</span>
        <h3>{app.name}</h3>
      </div>
      <p className="vendor">{app.vendor || 'Unknown vendor'}</p>
      <div className="issue-counts">
        <span className="critical">{app.critical_count} critical</span>
        <span className="major">{app.major_count} major</span>
        <span className="minor">{app.minor_count} minor</span>
      </div>
    </div>
  );
}

export default ApplicationCard;
```

**Step 2: Create ApplicationList page**

```jsx
// web/src/pages/ApplicationList.jsx
import { useState, useEffect } from 'react';
import ApplicationCard from '../components/ApplicationCard';

function ApplicationList({ onSelectApp }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/applications')
      .then(res => res.json())
      .then(data => {
        setApplications(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="application-list">
      <h2>Monitored Applications</h2>
      <div className="app-grid">
        {applications.map(app => (
          <ApplicationCard
            key={app.id}
            app={app}
            onClick={() => onSelectApp(app)}
          />
        ))}
      </div>
    </div>
  );
}

export default ApplicationList;
```

**Step 3: Update App.jsx**

```jsx
// web/src/App.jsx
import { useState } from 'react';
import ApplicationList from './pages/ApplicationList';

function App() {
  const [selectedApp, setSelectedApp] = useState(null);

  return (
    <div className="app">
      <header>
        <h1>IT Issue Tracker</h1>
        {selectedApp && (
          <button onClick={() => setSelectedApp(null)}>← Back</button>
        )}
      </header>
      <main>
        {!selectedApp ? (
          <ApplicationList onSelectApp={setSelectedApp} />
        ) : (
          <div>Application detail coming soon: {selectedApp.name}</div>
        )}
      </main>
    </div>
  );
}

export default App;
```

**Step 4: Update App.css**

```css
/* web/src/App.css */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
  color: #333;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

header h1 {
  font-size: 24px;
  font-weight: 600;
}

header button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.app-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.app-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  cursor: pointer;
  border-left: 4px solid #4caf50;
}

.app-card.status-critical {
  border-left-color: #f44336;
}

.app-card.status-major {
  border-left-color: #ff9800;
}

.app-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-card h3 {
  font-size: 18px;
  margin: 0;
}

.vendor {
  color: #666;
  font-size: 14px;
  margin: 4px 0 12px;
}

.issue-counts {
  display: flex;
  gap: 12px;
  font-size: 14px;
}

.issue-counts .critical { color: #f44336; }
.issue-counts .major { color: #ff9800; }
.issue-counts .minor { color: #666; }

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #f44336;
}
```

**Step 5: Test frontend**

Run: `cd web && npm run dev &`
Open: http://localhost:3000
Expected: Grid of application cards with issue counts

**Step 6: Commit**

```bash
git add web/
git commit -m "feat: add application list page"
```

---

### Task 7.2: Application Detail Page

**Files:**
- Create: `web/src/pages/ApplicationDetail.jsx`
- Create: `web/src/components/IssueCard.jsx`
- Modify: `web/src/App.jsx`

**Step 1: Create IssueCard component**

```jsx
// web/src/components/IssueCard.jsx
function IssueCard({ issue, onClick }) {
  const severityColors = {
    critical: '#f44336',
    major: '#ff9800',
    minor: '#666'
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString();
  };

  return (
    <div className="issue-card" onClick={onClick}>
      <div className="issue-header">
        <span
          className="severity-badge"
          style={{ backgroundColor: severityColors[issue.severity] }}
        >
          {issue.severity.toUpperCase()}
        </span>
        {issue.issue_type && (
          <span className="issue-type">{issue.issue_type}</span>
        )}
        <span className="issue-date">{formatDate(issue.source_date || issue.created_at)}</span>
      </div>
      <h4>{issue.title}</h4>
      <p className="issue-summary">{issue.summary}</p>
      <div className="issue-meta">
        <span>{issue.source_type}</span>
        <span>↑ {issue.upvotes}</span>
        <span>💬 {issue.comment_count}</span>
      </div>
    </div>
  );
}

export default IssueCard;
```

**Step 2: Create ApplicationDetail page**

```jsx
// web/src/pages/ApplicationDetail.jsx
import { useState, useEffect } from 'react';
import IssueCard from '../components/IssueCard';

function ApplicationDetail({ app, onSelectIssue }) {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('');

  useEffect(() => {
    const url = severityFilter
      ? `/api/applications/${app.id}/issues?severity=${severityFilter}`
      : `/api/applications/${app.id}/issues`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        setIssues(data);
        setLoading(false);
      });
  }, [app.id, severityFilter]);

  return (
    <div className="application-detail">
      <div className="detail-header">
        <h2>{app.name}</h2>
        <p className="vendor">{app.vendor || 'Unknown vendor'}</p>
      </div>

      <div className="filters">
        <label>Filter by severity:</label>
        <select
          value={severityFilter}
          onChange={e => setSeverityFilter(e.target.value)}
        >
          <option value="">All</option>
          <option value="critical">Critical</option>
          <option value="major">Major</option>
          <option value="minor">Minor</option>
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading issues...</div>
      ) : issues.length === 0 ? (
        <div className="no-issues">No issues found. Run the crawler to populate data.</div>
      ) : (
        <div className="issues-list">
          {issues.map(issue => (
            <IssueCard
              key={issue.id}
              issue={issue}
              onClick={() => onSelectIssue(issue)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default ApplicationDetail;
```

**Step 3: Update App.jsx**

```jsx
// web/src/App.jsx
import { useState } from 'react';
import ApplicationList from './pages/ApplicationList';
import ApplicationDetail from './pages/ApplicationDetail';

function App() {
  const [selectedApp, setSelectedApp] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);

  const handleBack = () => {
    if (selectedIssue) {
      setSelectedIssue(null);
    } else {
      setSelectedApp(null);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>IT Issue Tracker</h1>
        {(selectedApp || selectedIssue) && (
          <button onClick={handleBack}>← Back</button>
        )}
      </header>
      <main>
        {!selectedApp ? (
          <ApplicationList onSelectApp={setSelectedApp} />
        ) : !selectedIssue ? (
          <ApplicationDetail app={selectedApp} onSelectIssue={setSelectedIssue} />
        ) : (
          <div>Issue detail coming soon: {selectedIssue.title}</div>
        )}
      </main>
    </div>
  );
}

export default App;
```

**Step 4: Update App.css with new styles**

Add to the end of `web/src/App.css`:

```css
/* Application Detail */
.detail-header {
  margin-bottom: 24px;
}

.detail-header h2 {
  font-size: 24px;
  margin-bottom: 4px;
}

.filters {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.issue-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  cursor: pointer;
}

.issue-card:hover {
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.issue-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.severity-badge {
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.issue-type {
  background: #e0e0e0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.issue-date {
  margin-left: auto;
  color: #666;
  font-size: 12px;
}

.issue-card h4 {
  font-size: 16px;
  margin-bottom: 8px;
}

.issue-summary {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.issue-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
}

.no-issues {
  text-align: center;
  padding: 40px;
  color: #666;
}
```

**Step 5: Test**

Open: http://localhost:3000
Click on an application card
Expected: See issues list (empty until crawler runs)

**Step 6: Commit**

```bash
git add web/
git commit -m "feat: add application detail page with issues list"
```

---

### Task 7.3: Issue Detail Page

**Files:**
- Create: `web/src/pages/IssueDetail.jsx`
- Modify: `web/src/App.jsx`

**Step 1: Create IssueDetail page**

```jsx
// web/src/pages/IssueDetail.jsx
function IssueDetail({ issue }) {
  const severityColors = {
    critical: '#f44336',
    major: '#ff9800',
    minor: '#666'
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  return (
    <div className="issue-detail">
      <div className="issue-detail-header">
        <span
          className="severity-badge large"
          style={{ backgroundColor: severityColors[issue.severity] }}
        >
          {issue.severity.toUpperCase()}
        </span>
        <h2>{issue.title}</h2>
      </div>

      <div className="issue-detail-meta">
        <div className="meta-item">
          <label>Source</label>
          <span>{issue.source_type}</span>
        </div>
        <div className="meta-item">
          <label>Type</label>
          <span>{issue.issue_type || 'Unknown'}</span>
        </div>
        <div className="meta-item">
          <label>Reported</label>
          <span>{formatDate(issue.source_date)}</span>
        </div>
        <div className="meta-item">
          <label>Engagement</label>
          <span>↑ {issue.upvotes} · 💬 {issue.comment_count}</span>
        </div>
      </div>

      <div className="issue-section">
        <h3>Summary</h3>
        <p>{issue.summary}</p>
      </div>

      <div className="issue-section">
        <a
          href={issue.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="source-link"
        >
          View Original Source ↗
        </a>
      </div>

      {issue.raw_content && (
        <details className="raw-content">
          <summary>Show Raw Content</summary>
          <pre>{issue.raw_content}</pre>
        </details>
      )}
    </div>
  );
}

export default IssueDetail;
```

**Step 2: Update App.jsx**

```jsx
// web/src/App.jsx
import { useState } from 'react';
import ApplicationList from './pages/ApplicationList';
import ApplicationDetail from './pages/ApplicationDetail';
import IssueDetail from './pages/IssueDetail';

function App() {
  const [selectedApp, setSelectedApp] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);

  const handleBack = () => {
    if (selectedIssue) {
      setSelectedIssue(null);
    } else {
      setSelectedApp(null);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>IT Issue Tracker</h1>
        {(selectedApp || selectedIssue) && (
          <button onClick={handleBack}>← Back</button>
        )}
      </header>
      <main>
        {!selectedApp ? (
          <ApplicationList onSelectApp={setSelectedApp} />
        ) : !selectedIssue ? (
          <ApplicationDetail app={selectedApp} onSelectIssue={setSelectedIssue} />
        ) : (
          <IssueDetail issue={selectedIssue} />
        )}
      </main>
    </div>
  );
}

export default App;
```

**Step 3: Add styles to App.css**

Add to end of `web/src/App.css`:

```css
/* Issue Detail */
.issue-detail {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.issue-detail-header {
  margin-bottom: 24px;
}

.issue-detail-header h2 {
  margin-top: 12px;
  font-size: 24px;
}

.severity-badge.large {
  font-size: 14px;
  padding: 4px 12px;
}

.issue-detail-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 24px;
}

.meta-item label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.meta-item span {
  font-weight: 500;
}

.issue-section {
  margin-bottom: 24px;
}

.issue-section h3 {
  font-size: 16px;
  margin-bottom: 8px;
  color: #333;
}

.issue-section p {
  line-height: 1.6;
  color: #444;
}

.source-link {
  display: inline-block;
  padding: 12px 24px;
  background: #2196f3;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}

.source-link:hover {
  background: #1976d2;
}

.raw-content {
  margin-top: 24px;
}

.raw-content summary {
  cursor: pointer;
  color: #666;
  margin-bottom: 8px;
}

.raw-content pre {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
}
```

**Step 4: Test full flow**

Open: http://localhost:3000
Expected: Can navigate App List → App Detail → Issue Detail → Back

**Step 5: Commit**

```bash
git add web/
git commit -m "feat: add issue detail page"
```

---

## Phase 8: Integration Testing

### Task 8.1: End-to-End Test

**Step 1: Start all services**

Terminal 1: `docker-compose up -d`
Terminal 2: `cd api && npm run dev`
Terminal 3: `cd web && npm run dev`

**Step 2: Verify seed data**

Run: `curl http://localhost:3001/api/applications | jq`
Expected: Array with Adobe Acrobat, Microsoft Teams, Zoom, Slack

**Step 3: Run crawler (requires API keys)**

Set environment variables in crawler/.env:
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET

Run: `cd crawler && source .venv/bin/activate && python main.py crawl --app "Adobe Acrobat"`
Expected: Crawls Reddit, processes posts, stores issues

**Step 4: Verify issues in dashboard**

Open: http://localhost:3000
Click: Adobe Acrobat
Expected: See crawled issues with severity badges

**Step 5: Test search API**

Run: `curl "http://localhost:3001/api/search?q=crash" | jq`
Expected: Returns semantically similar issues

**Step 6: Final commit**

```bash
git add -A
git commit -m "chore: complete v1 implementation"
```

---

## Summary

**What was built:**
1. PostgreSQL database with pgvector for semantic search
2. Python crawler with Reddit source, LLM analysis, embeddings
3. Node.js API with applications, issues, and search endpoints
4. React dashboard with three views: App List, App Detail, Issue Detail

**To run locally:**
```bash
# Start database
docker-compose up -d

# Terminal 1: API
cd api && npm run dev

# Terminal 2: Frontend
cd web && npm run dev

# Terminal 3: Crawl (when needed)
cd crawler && source .venv/bin/activate && python main.py crawl
```

**Next steps (v2):**
- Add more sources (Server Fault, GitHub Issues, BleepingComputer)
- User-submitted issues
- Scheduled crawling
- Cloud deployment
