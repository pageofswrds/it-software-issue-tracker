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
