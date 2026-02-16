import os
import time
from urllib.parse import urlparse
import httpx
from dotenv import load_dotenv
from .models import WebSearchResult

load_dotenv()

SEARCH_SUFFIXES = ["issue", "bug", "problem", "crash", "not working"]

BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"


class WebSearch:
    def __init__(self, api_key: str | None = None, max_results_per_query: int = 10):
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY not set")
        self.max_results_per_query = max_results_per_query

    def build_queries(self, keywords: list[str]) -> list[str]:
        """Build search queries from keywords and issue-related suffixes."""
        queries = []
        for keyword in keywords:
            for suffix in SEARCH_SUFFIXES:
                queries.append(f'"{keyword}" {suffix}')
        return queries

    def _search_single_query(self, query: str) -> list[dict]:
        """Run a single Brave Search API query. Returns raw result dicts."""
        try:
            response = httpx.get(
                BRAVE_API_URL,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": self.api_key,
                },
                params={
                    "q": query,
                    "count": self.max_results_per_query,
                },
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("web", {}).get("results", [])
        except Exception as e:
            print(f"Search error for '{query}': {e}")
            return []

    def search(self, keywords: list[str]) -> list[WebSearchResult]:
        """Search for issues related to the given keywords. Deduplicates by URL."""
        queries = self.build_queries(keywords)
        seen_urls = set()
        results = []

        for i, query in enumerate(queries):
            if i > 0:
                time.sleep(1)
            raw_results = self._search_single_query(query)
            for item in raw_results:
                url = item.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                domain = urlparse(url).netloc
                results.append(WebSearchResult(
                    url=url,
                    title=item.get("title", ""),
                    snippet=item.get("description", ""),
                    source=domain,
                ))

        return results
