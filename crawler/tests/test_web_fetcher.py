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
