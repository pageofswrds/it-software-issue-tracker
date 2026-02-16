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
