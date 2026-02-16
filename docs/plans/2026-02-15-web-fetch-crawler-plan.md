# Web Fetch Crawler Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the PRAW-based Reddit crawler with a DuckDuckGo search + httpx + BeautifulSoup web fetch pipeline, eliminating Reddit API credentials and enabling multi-source crawling.

**Architecture:** Two-stage pipeline — DuckDuckGo discovers relevant URLs via keyword+suffix queries, then httpx fetches each page and BeautifulSoup extracts text content. The existing Claude classification and OpenAI embedding pipeline remain unchanged.

**Tech Stack:** Python 3.11+, duckduckgo-search, httpx (already installed), beautifulsoup4 (already installed), pytest

**Design doc:** `docs/plans/2026-02-15-web-fetch-crawler-design.md`

---

### Task 1: Update dependencies

**Files:**
- Modify: `crawler/requirements.txt`

**Step 1: Update requirements.txt**

Remove `praw==7.7.1` and add `duckduckgo-search==7.5.1`. `httpx` and `beautifulsoup4` are already present.

The new `requirements.txt` should be:

```
httpx==0.27.0
beautifulsoup4==4.12.3
psycopg[binary]==3.2.3
anthropic==0.25.0
openai==1.30.0
python-dotenv==1.0.1
click==8.1.7
duckduckgo-search==7.5.1
pytest==8.2.0
pytest-asyncio==0.23.6
```

**Step 2: Install updated dependencies**

Run from `crawler/` directory:

```bash
pip install -r requirements.txt
```

Expected: All packages install successfully. `duckduckgo-search` is new, `praw` is no longer listed.

**Step 3: Commit**

```bash
git add crawler/requirements.txt
git commit -m "chore: replace praw with duckduckgo-search in dependencies"
```

---

### Task 2: Create WebSearchResult and FetchedPage data models

**Files:**
- Create: `crawler/src/sources/models.py`
- Test: `crawler/tests/test_models.py`

**Step 1: Write the failing test**

Create `crawler/tests/test_models.py`:

```python
from src.sources.models import WebSearchResult, FetchedPage


def test_web_search_result_structure():
    result = WebSearchResult(
        url="https://reddit.com/r/sysadmin/abc123",
        title="Adobe Acrobat crashes on open",
        snippet="Having issues with Acrobat DC crashing...",
        source="reddit.com",
    )
    assert result.url == "https://reddit.com/r/sysadmin/abc123"
    assert result.title == "Adobe Acrobat crashes on open"
    assert result.snippet == "Having issues with Acrobat DC crashing..."
    assert result.source == "reddit.com"


def test_fetched_page_structure():
    page = FetchedPage(
        url="https://reddit.com/r/sysadmin/abc123",
        title="Adobe Acrobat crashes on open",
        content="Full text content of the page goes here...",
        source="reddit.com",
    )
    assert page.url == "https://reddit.com/r/sysadmin/abc123"
    assert page.content == "Full text content of the page goes here..."
    assert page.source == "reddit.com"
```

**Step 2: Run test to verify it fails**

Run: `cd crawler && python -m pytest tests/test_models.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'src.sources.models'`

**Step 3: Write minimal implementation**

Create `crawler/src/sources/models.py`:

```python
from dataclasses import dataclass


@dataclass
class WebSearchResult:
    url: str
    title: str
    snippet: str
    source: str


@dataclass
class FetchedPage:
    url: str
    title: str
    content: str
    source: str
```

**Step 4: Run test to verify it passes**

Run: `cd crawler && python -m pytest tests/test_models.py -v`

Expected: 2 passed

**Step 5: Commit**

```bash
git add crawler/src/sources/models.py crawler/tests/test_models.py
git commit -m "feat: add WebSearchResult and FetchedPage data models"
```

---

### Task 3: Create web search module

**Files:**
- Create: `crawler/src/sources/web_search.py`
- Test: `crawler/tests/test_web_search.py`

This module wraps `duckduckgo-search` to find relevant URLs. It builds queries from application keywords + issue suffixes and deduplicates results by URL.

**Step 1: Write the failing tests**

Create `crawler/tests/test_web_search.py`:

```python
from unittest.mock import patch, MagicMock
from src.sources.web_search import WebSearch, SEARCH_SUFFIXES
from src.sources.models import WebSearchResult


def test_search_suffixes_exist():
    assert len(SEARCH_SUFFIXES) > 0
    assert "issue" in SEARCH_SUFFIXES
    assert "bug" in SEARCH_SUFFIXES


def test_build_queries():
    ws = WebSearch()
    queries = ws.build_queries(["adobe acrobat", "acrobat dc"])
    # Should produce keyword x suffix combinations
    assert len(queries) == len(["adobe acrobat", "acrobat dc"]) * len(SEARCH_SUFFIXES)
    assert '"adobe acrobat" issue' in queries
    assert '"acrobat dc" bug' in queries


def test_search_deduplicates_by_url():
    ws = WebSearch()

    fake_results = [
        {"href": "https://example.com/page1", "title": "Page 1", "body": "Snippet 1"},
        {"href": "https://example.com/page1", "title": "Page 1 dup", "body": "Snippet dup"},
        {"href": "https://example.com/page2", "title": "Page 2", "body": "Snippet 2"},
    ]

    with patch.object(ws, "_search_single_query", return_value=fake_results):
        results = ws.search(["test keyword"])

    urls = [r.url for r in results]
    assert len(urls) == len(set(urls)), "Results should be deduplicated by URL"


def test_search_returns_web_search_results():
    ws = WebSearch()

    fake_results = [
        {"href": "https://example.com/page1", "title": "Page 1", "body": "Snippet 1"},
    ]

    with patch.object(ws, "_search_single_query", return_value=fake_results):
        results = ws.search(["test keyword"])

    assert len(results) >= 1
    assert isinstance(results[0], WebSearchResult)
    assert results[0].url == "https://example.com/page1"
    assert results[0].title == "Page 1"
    assert results[0].snippet == "Snippet 1"
```

**Step 2: Run test to verify it fails**

Run: `cd crawler && python -m pytest tests/test_web_search.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'src.sources.web_search'`

**Step 3: Write minimal implementation**

Create `crawler/src/sources/web_search.py`:

```python
from urllib.parse import urlparse
from duckduckgo_search import DDGS
from .models import WebSearchResult

SEARCH_SUFFIXES = ["issue", "bug", "problem", "crash", "not working"]


class WebSearch:
    def __init__(self, max_results_per_query: int = 10):
        self.max_results_per_query = max_results_per_query

    def build_queries(self, keywords: list[str]) -> list[str]:
        """Build search queries from keywords and issue-related suffixes."""
        queries = []
        for keyword in keywords:
            for suffix in SEARCH_SUFFIXES:
                queries.append(f'"{keyword}" {suffix}')
        return queries

    def _search_single_query(self, query: str) -> list[dict]:
        """Run a single DuckDuckGo search query. Returns raw result dicts."""
        try:
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=self.max_results_per_query))
        except Exception as e:
            print(f"Search error for '{query}': {e}")
            return []

    def search(self, keywords: list[str]) -> list[WebSearchResult]:
        """Search for issues related to the given keywords. Deduplicates by URL."""
        queries = self.build_queries(keywords)
        seen_urls = set()
        results = []

        for query in queries:
            raw_results = self._search_single_query(query)
            for item in raw_results:
                url = item.get("href", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                domain = urlparse(url).netloc
                results.append(WebSearchResult(
                    url=url,
                    title=item.get("title", ""),
                    snippet=item.get("body", ""),
                    source=domain,
                ))

        return results
```

**Step 4: Run test to verify it passes**

Run: `cd crawler && python -m pytest tests/test_web_search.py -v`

Expected: 4 passed

**Step 5: Commit**

```bash
git add crawler/src/sources/web_search.py crawler/tests/test_web_search.py
git commit -m "feat: add DuckDuckGo web search module"
```

---

### Task 4: Create web fetcher module

**Files:**
- Create: `crawler/src/sources/web_fetcher.py`
- Test: `crawler/tests/test_web_fetcher.py`

This module fetches a URL with httpx and extracts text content using BeautifulSoup. It strips navigation, scripts, styles, and other boilerplate, returning just the main text.

**Step 1: Write the failing tests**

Create `crawler/tests/test_web_fetcher.py`:

```python
import pytest
from src.sources.web_fetcher import WebFetcher
from src.sources.models import FetchedPage


def test_extract_text_from_html():
    fetcher = WebFetcher()

    html = """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <nav>Navigation stuff</nav>
        <script>var x = 1;</script>
        <style>.foo { color: red; }</style>
        <main>
            <h1>Issue Report</h1>
            <p>Adobe Acrobat crashes when opening large PDFs.</p>
            <p>Steps to reproduce: open a 500MB file.</p>
        </main>
        <footer>Footer stuff</footer>
    </body>
    </html>
    """

    text = fetcher.extract_text(html)

    assert "Adobe Acrobat crashes" in text
    assert "Steps to reproduce" in text
    # Script/style content should be removed
    assert "var x = 1" not in text
    assert ".foo" not in text


def test_extract_title_from_html():
    fetcher = WebFetcher()

    html = "<html><head><title>My Page Title</title></head><body><p>Content</p></body></html>"
    title = fetcher.extract_title(html)
    assert title == "My Page Title"


def test_extract_title_missing():
    fetcher = WebFetcher()

    html = "<html><body><p>No title here</p></body></html>"
    title = fetcher.extract_title(html)
    assert title == ""


def test_fetch_page_returns_fetched_page(httpx_mock):
    """Test the full fetch flow with a mocked HTTP response."""
    fetcher = WebFetcher()

    test_html = """
    <html>
    <head><title>Bug Report</title></head>
    <body><p>Teams crashes on startup after update.</p></body>
    </html>
    """

    httpx_mock.add_response(url="https://example.com/bug", text=test_html)

    page = fetcher.fetch("https://example.com/bug")

    assert page is not None
    assert isinstance(page, FetchedPage)
    assert page.url == "https://example.com/bug"
    assert page.title == "Bug Report"
    assert "Teams crashes on startup" in page.content
    assert page.source == "example.com"


def test_fetch_page_returns_none_on_error(httpx_mock):
    """Test that fetch returns None on HTTP errors."""
    fetcher = WebFetcher()

    httpx_mock.add_response(url="https://example.com/404", status_code=404)

    page = fetcher.fetch("https://example.com/404")
    assert page is None
```

Note: These tests use `pytest-httpx` for mocking HTTP calls. It needs to be added to requirements.

**Step 2: Add pytest-httpx to requirements and install**

Add `pytest-httpx==0.30.0` to `crawler/requirements.txt` and run:

```bash
pip install -r requirements.txt
```

**Step 3: Run test to verify it fails**

Run: `cd crawler && python -m pytest tests/test_web_fetcher.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'src.sources.web_fetcher'`

**Step 4: Write minimal implementation**

Create `crawler/src/sources/web_fetcher.py`:

```python
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from .models import FetchedPage

# Elements that contain boilerplate, not content
STRIP_TAGS = ["script", "style", "nav", "footer", "header", "aside", "form"]

# Default request headers to look like a regular browser
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; IT-Issue-Tracker/0.1)",
}


class WebFetcher:
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    def extract_text(self, html: str) -> str:
        """Extract readable text content from HTML, stripping boilerplate."""
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(STRIP_TAGS):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # Collapse multiple blank lines
        lines = [line for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def extract_title(self, html: str) -> str:
        """Extract the <title> tag content from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else ""

    def fetch(self, url: str) -> FetchedPage | None:
        """Fetch a URL and extract its text content. Returns None on failure."""
        try:
            response = httpx.get(
                url,
                headers=DEFAULT_HEADERS,
                timeout=self.timeout,
                follow_redirects=True,
            )
            response.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            print(f"Fetch error for {url}: {e}")
            return None

        html = response.text
        domain = urlparse(url).netloc

        return FetchedPage(
            url=url,
            title=self.extract_title(html),
            content=self.extract_text(html),
            source=domain,
        )
```

**Step 5: Run test to verify it passes**

Run: `cd crawler && python -m pytest tests/test_web_fetcher.py -v`

Expected: 5 passed

**Step 6: Commit**

```bash
git add crawler/src/sources/web_fetcher.py crawler/tests/test_web_fetcher.py crawler/requirements.txt
git commit -m "feat: add web fetcher module with HTML text extraction"
```

---

### Task 5: Update sources __init__.py

**Files:**
- Modify: `crawler/src/sources/__init__.py`

**Step 1: Update the exports**

Replace the contents of `crawler/src/sources/__init__.py` with:

```python
from .models import WebSearchResult, FetchedPage
from .web_search import WebSearch
from .web_fetcher import WebFetcher

__all__ = ['WebSearchResult', 'FetchedPage', 'WebSearch', 'WebFetcher']
```

This removes the `RedditSource`/`RedditPost` imports and exports the new classes.

**Step 2: Run all tests to verify nothing breaks**

Run: `cd crawler && python -m pytest tests/test_models.py tests/test_web_search.py tests/test_web_fetcher.py -v`

Expected: All pass

**Step 3: Commit**

```bash
git add crawler/src/sources/__init__.py
git commit -m "refactor: update sources __init__ to export new web fetch modules"
```

---

### Task 6: Update Crawler to use web fetch pipeline

**Files:**
- Modify: `crawler/src/crawler.py`
- Test: `crawler/tests/test_crawler_integration.py`

This is the core change — rewire `Crawler` to use `WebSearch` + `WebFetcher` instead of `RedditSource`.

**Step 1: Write the failing test**

Create `crawler/tests/test_crawler_integration.py`:

```python
from unittest.mock import patch, MagicMock
from src.crawler import Crawler
from src.sources.models import WebSearchResult, FetchedPage
from src.llm.interface import IssueAnalysis


def test_crawler_uses_web_search_and_fetcher():
    """Test that Crawler wires together search, fetch, classify, and store."""
    mock_db = MagicMock()

    crawler = Crawler(mock_db)

    # Mock app repo
    test_app = {
        "id": "app-123",
        "name": "Adobe Acrobat",
        "keywords": ["adobe acrobat"],
    }
    crawler.app_repo.get_by_id = MagicMock(return_value=test_app)

    # Mock web search to return one result
    mock_search_result = WebSearchResult(
        url="https://example.com/bug-report",
        title="Acrobat crash",
        snippet="Acrobat crashes on open",
        source="example.com",
    )
    crawler.search.search = MagicMock(return_value=[mock_search_result])

    # Mock dedup check — URL not seen before
    crawler.issue_repo.exists_by_url = MagicMock(return_value=False)

    # Mock fetcher
    mock_page = FetchedPage(
        url="https://example.com/bug-report",
        title="Acrobat crash",
        content="Adobe Acrobat DC crashes when opening large PDF files.",
        source="example.com",
    )
    crawler.fetcher.fetch = MagicMock(return_value=mock_page)

    # Mock LLM
    mock_analysis = IssueAnalysis(
        title="Acrobat DC crashes on large PDFs",
        summary="Adobe Acrobat DC crashes when users attempt to open PDF files larger than 100MB.",
        severity="major",
        issue_type="crash",
    )
    crawler.llm.analyze_issue = MagicMock(return_value=mock_analysis)

    # Mock embedding
    with patch("src.crawler.get_embedding", return_value=[0.1] * 1536):
        count = crawler.crawl_application("app-123")

    assert count == 1
    crawler.issue_repo.create.assert_called_once()

    call_kwargs = crawler.issue_repo.create.call_args
    assert call_kwargs[1]["source_type"] == "example.com"
    assert call_kwargs[1]["source_url"] == "https://example.com/bug-report"
    assert call_kwargs[1]["title"] == "Acrobat DC crashes on large PDFs"


def test_crawler_skips_already_seen_urls():
    """Test that Crawler skips URLs already in the database."""
    mock_db = MagicMock()
    crawler = Crawler(mock_db)

    test_app = {
        "id": "app-123",
        "name": "Adobe Acrobat",
        "keywords": ["adobe acrobat"],
    }
    crawler.app_repo.get_by_id = MagicMock(return_value=test_app)

    mock_search_result = WebSearchResult(
        url="https://example.com/already-seen",
        title="Old bug",
        snippet="Already tracked",
        source="example.com",
    )
    crawler.search.search = MagicMock(return_value=[mock_search_result])

    # URL already exists in DB
    crawler.issue_repo.exists_by_url = MagicMock(return_value=True)

    with patch("src.crawler.get_embedding", return_value=[0.1] * 1536):
        count = crawler.crawl_application("app-123")

    assert count == 0
    crawler.fetcher.fetch.assert_not_called()


def test_crawler_skips_failed_fetches():
    """Test that Crawler handles fetch failures gracefully."""
    mock_db = MagicMock()
    crawler = Crawler(mock_db)

    test_app = {
        "id": "app-123",
        "name": "Adobe Acrobat",
        "keywords": ["adobe acrobat"],
    }
    crawler.app_repo.get_by_id = MagicMock(return_value=test_app)

    mock_search_result = WebSearchResult(
        url="https://example.com/broken",
        title="Broken page",
        snippet="Cannot load",
        source="example.com",
    )
    crawler.search.search = MagicMock(return_value=[mock_search_result])
    crawler.issue_repo.exists_by_url = MagicMock(return_value=False)

    # Fetch returns None (failure)
    crawler.fetcher.fetch = MagicMock(return_value=None)

    with patch("src.crawler.get_embedding", return_value=[0.1] * 1536):
        count = crawler.crawl_application("app-123")

    assert count == 0
    crawler.llm.analyze_issue.assert_not_called()
```

**Step 2: Run test to verify it fails**

Run: `cd crawler && python -m pytest tests/test_crawler_integration.py -v`

Expected: FAIL because `Crawler` still imports `RedditSource` and doesn't have `search`/`fetcher` attributes.

**Step 3: Update the Crawler implementation**

Replace `crawler/src/crawler.py` with:

```python
from typing import Callable
from src.db import Database
from src.repositories import ApplicationRepository, IssueRepository
from src.sources.web_search import WebSearch
from src.sources.web_fetcher import WebFetcher
from src.sources.models import FetchedPage
from src.llm import get_llm_provider, IssueAnalysis
from src.embeddings import get_embedding


class Crawler:
    def __init__(
        self,
        db: Database,
        llm_provider: str = "anthropic",
        on_progress: Callable[[str], None] | None = None,
    ):
        self.db = db
        self.app_repo = ApplicationRepository(db)
        self.issue_repo = IssueRepository(db)
        self.llm = get_llm_provider(llm_provider)
        self.search = WebSearch()
        self.fetcher = WebFetcher()
        self.on_progress = on_progress or print

    def log(self, message: str) -> None:
        self.on_progress(message)

    def crawl_application(self, app_id: str) -> int:
        """Crawl web sources for a single application. Returns count of new issues."""
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ValueError(f"Application not found: {app_id}")

        self.log(f"Crawling: {app['name']}")
        keywords = app["keywords"]
        new_count = 0

        try:
            results = self.search.search(keywords)
            self.log(f"  Found {len(results)} search results")

            for result in results:
                if self.issue_repo.exists_by_url(result.url):
                    continue

                try:
                    new_count += self._process_result(app, result)
                except Exception as e:
                    self.log(f"  Error processing {result.url}: {e}")
        except Exception as e:
            self.log(f"  Search error: {e}")

        self.log(f"  Added {new_count} new issues")
        return new_count

    def _process_result(self, app: dict, result) -> int:
        """Fetch, classify, and store a single search result. Returns 1 if stored, 0 if skipped."""
        self.log(f"  Fetching: {result.title[:50]}...")

        page = self.fetcher.fetch(result.url)
        if page is None:
            return 0

        # Analyze with LLM
        analysis = self.llm.analyze_issue(page.content, app["name"])

        # Skip if LLM thinks it's not relevant
        if len(analysis.summary) < 20:
            return 0

        # Generate embedding
        embedding = get_embedding(f"{analysis.title} {analysis.summary}")

        # Store issue
        self.issue_repo.create(
            application_id=app["id"],
            title=analysis.title,
            summary=analysis.summary,
            raw_content=page.content,
            source_type=page.source,
            source_url=page.url,
            severity=analysis.severity,
            issue_type=analysis.issue_type,
            embedding=embedding,
        )

        return 1

    def crawl_all(self) -> int:
        """Crawl all applications. Returns total new issues."""
        apps = self.app_repo.list_all()
        total = 0
        for app in apps:
            total += self.crawl_application(app["id"])
        return total
```

**Step 4: Run test to verify it passes**

Run: `cd crawler && python -m pytest tests/test_crawler_integration.py -v`

Expected: 3 passed

**Step 5: Commit**

```bash
git add crawler/src/crawler.py crawler/tests/test_crawler_integration.py
git commit -m "feat: rewire Crawler to use web search + fetch pipeline"
```

---

### Task 7: Remove Reddit source and update tests

**Files:**
- Remove: `crawler/src/sources/reddit.py`
- Remove: `crawler/tests/test_reddit.py`

**Step 1: Delete the old Reddit files**

```bash
rm crawler/src/sources/reddit.py crawler/tests/test_reddit.py
```

**Step 2: Run all tests to verify nothing references the deleted files**

Run: `cd crawler && python -m pytest tests/ -v`

Expected: All tests pass. No import errors referencing `reddit.py`.

**Step 3: Commit**

```bash
git add -u crawler/src/sources/reddit.py crawler/tests/test_reddit.py
git commit -m "chore: remove PRAW-based Reddit source"
```

---

### Task 8: Remove Reddit env vars from .env.example

**Files:**
- Modify: `crawler/.env.example` (if it exists)

**Step 1: Check if .env.example exists and remove Reddit credentials**

Look for `crawler/.env.example` or similar files. Remove any lines referencing `REDDIT_CLIENT_ID` or `REDDIT_CLIENT_SECRET`. Leave `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `DATABASE_URL` entries intact.

**Step 2: Run full test suite one final time**

Run: `cd crawler && python -m pytest tests/ -v`

Expected: All tests pass.

**Step 3: Commit**

```bash
git add crawler/.env.example
git commit -m "chore: remove Reddit credentials from .env.example"
```

---

### Task 9: Verify end-to-end manually

This is a manual verification step — not automated.

**Step 1: Ensure the database is running**

```bash
docker-compose up -d
```

**Step 2: Run the crawler for one application**

```bash
cd crawler && python main.py crawl --app "Adobe Acrobat"
```

Expected: The crawler searches DuckDuckGo, fetches pages, classifies issues with Claude, and stores them in the database. Output should show search result counts and new issues added.

**Step 3: Check the API returns new issues**

```bash
curl http://localhost:3001/api/applications
```

Expected: Adobe Acrobat shows issue counts.
