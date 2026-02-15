from typing import Callable
from src.db import Database
from src.repositories import ApplicationRepository, IssueRepository
from src.sources.reddit import RedditSource, RedditPost
from src.llm import get_llm_provider, IssueAnalysis
from src.embeddings import get_embedding

class Crawler:
    def __init__(
        self,
        db: Database,
        llm_provider: str = "anthropic",
        on_progress: Callable[[str], None] | None = None
    ):
        self.db = db
        self.app_repo = ApplicationRepository(db)
        self.issue_repo = IssueRepository(db)
        self.llm = get_llm_provider(llm_provider)
        self.on_progress = on_progress or print

    def log(self, message: str) -> None:
        self.on_progress(message)

    def crawl_application(self, app_id: str) -> int:
        """Crawl all sources for a single application. Returns count of new issues."""
        app = self.app_repo.get_by_id(app_id)
        if not app:
            raise ValueError(f"Application not found: {app_id}")

        self.log(f"Crawling: {app['name']}")
        keywords = app['keywords']
        new_count = 0

        # Crawl Reddit
        try:
            reddit = RedditSource()
            posts = reddit.search(keywords)
            self.log(f"  Found {len(posts)} Reddit posts")

            for post in posts:
                if self.issue_repo.exists_by_url(post.full_url):
                    continue

                try:
                    new_count += self._process_post(app, post)
                except Exception as e:
                    self.log(f"  Error processing {post.id}: {e}")
        except Exception as e:
            self.log(f"  Reddit error: {e}")

        self.log(f"  Added {new_count} new issues")
        return new_count

    def _process_post(self, app: dict, post: RedditPost) -> int:
        """Process a single post and store as issue. Returns 1 if stored, 0 if skipped."""
        self.log(f"  Processing: {post.title[:50]}...")

        # Analyze with LLM
        analysis = self.llm.analyze_issue(post.content, app['name'])

        # Skip if LLM thinks it's not relevant (very short summary)
        if len(analysis.summary) < 20:
            return 0

        # Generate embedding
        embedding = get_embedding(f"{analysis.title} {analysis.summary}")

        # Store issue
        self.issue_repo.create(
            application_id=app['id'],
            title=analysis.title,
            summary=analysis.summary,
            raw_content=post.content,
            source_type="reddit",
            source_url=post.full_url,
            severity=analysis.severity,
            issue_type=analysis.issue_type,
            upvotes=post.upvotes,
            comment_count=post.comment_count,
            source_date=post.created_at,
            embedding=embedding
        )

        return 1

    def crawl_all(self) -> int:
        """Crawl all applications. Returns total new issues."""
        apps = self.app_repo.list_all()
        total = 0
        for app in apps:
            total += self.crawl_application(app['id'])
        return total
