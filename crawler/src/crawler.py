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
