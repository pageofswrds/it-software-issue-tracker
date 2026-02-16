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
