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
    crawler.issue_repo.create = MagicMock(return_value={})

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

    # Mock fetcher so we can assert it was not called
    crawler.fetcher.fetch = MagicMock()

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

    # Mock LLM so we can assert it was not called
    crawler.llm.analyze_issue = MagicMock()

    with patch("src.crawler.get_embedding", return_value=[0.1] * 1536):
        count = crawler.crawl_application("app-123")

    assert count == 0
    crawler.llm.analyze_issue.assert_not_called()
