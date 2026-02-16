# Web Fetch Crawler Design

## Overview

Replace the current PRAW-based Reddit crawler with a simpler web fetch approach using DuckDuckGo search + httpx + BeautifulSoup. This eliminates the need for Reddit API credentials and enables crawling from any public website.

## Architecture

Two-stage pipeline:

```
[Discovery]                    [Fetching]                [Processing]
DuckDuckGo search    →    httpx fetch each URL    →    BeautifulSoup parse
by app keywords             (public pages)              extract text content
                                                              ↓
                                                    Claude classifies issue
                                                              ↓
                                                    OpenAI generates embedding
                                                              ↓
                                                    Store in PostgreSQL
```

## Search Strategy

For each application keyword, combine with hardcoded issue-related suffixes:

```python
SEARCH_SUFFIXES = ["issue", "bug", "problem", "crash", "not working"]
```

Example for Adobe Acrobat (keywords: `['adobe acrobat', 'acrobat reader', ...]`):
- `"adobe acrobat" issue`
- `"adobe acrobat" bug`
- `"acrobat reader" problem`
- etc.

Results are deduplicated by URL before fetching.

## Data Models

Replace `RedditPost` with two new models:

```python
@dataclass
class WebSearchResult:
    url: str           # Full URL of the page
    title: str         # Page/result title
    snippet: str       # Search result snippet
    source: str        # Domain name (e.g., "reddit.com")

@dataclass
class FetchedPage:
    url: str
    title: str
    content: str       # Extracted text from the page
    source: str        # Domain name
```

## File Changes

| File | Change |
|------|--------|
| `sources/reddit.py` | **Remove** |
| `sources/web_search.py` | **New** — DuckDuckGo search wrapper |
| `sources/web_fetcher.py` | **New** — HTTP fetch + HTML-to-text extraction |
| `crawler.py` | **Modify** — use new sources instead of `RedditSource` |
| `requirements.txt` | **Modify** — drop `praw`, add `duckduckgo-search`, `httpx` |

## What Stays the Same

- Database schema (no changes; `source_type` stores domain name instead of "reddit")
- CLI commands (`crawl`, `list-apps`, `add-app`)
- LLM classification (`AnthropicProvider`)
- Embeddings (`get_embedding()`)
- Repositories (`ApplicationRepository`, `IssueRepository`)
- API and frontend (completely unchanged)

## What We Lose (Intentionally)

- Reddit-specific metadata (`upvotes`, `comment_count`) — defaults to 0 for non-Reddit sources
- Subreddit-specific scoping — replaced by broader web search

## Dependencies

- `duckduckgo-search` — no API key, queries DuckDuckGo programmatically
- `httpx` — modern async-capable HTTP client
- `beautifulsoup4` — already a dependency, used for HTML parsing

## Decisions Made

- **No API keys** for data sourcing (Anthropic + OpenAI still needed for classification/embeddings)
- **Multiple sources** supported by design (any public URL)
- **Hardcoded suffixes** for search queries (simple, effective)
- **DuckDuckGo** for discovery (free, no API key)
