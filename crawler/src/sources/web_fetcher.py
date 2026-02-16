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
