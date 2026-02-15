import os
from dataclasses import dataclass
from datetime import datetime
import praw
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RedditPost:
    id: str
    title: str
    content: str
    url: str
    subreddit: str
    upvotes: int
    comment_count: int
    created_utc: float

    @property
    def created_at(self) -> datetime:
        return datetime.fromtimestamp(self.created_utc)

    @property
    def full_url(self) -> str:
        return f"https://reddit.com{self.url}"


class RedditSource:
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_agent: str = "IT-Issue-Tracker/0.1"
    ):
        self.client_id = client_id or os.environ.get("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("REDDIT_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError("Reddit credentials not set")

        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=user_agent
        )

    def search(
        self,
        keywords: list[str],
        subreddit: str = "sysadmin",
        time_filter: str = "week",
        limit: int = 25
    ) -> list[RedditPost]:
        """Search subreddit for posts matching keywords."""
        results = []
        seen_ids = set()

        subreddit_obj = self.reddit.subreddit(subreddit)

        for keyword in keywords:
            try:
                for submission in subreddit_obj.search(
                    keyword,
                    sort="relevance",
                    time_filter=time_filter,
                    limit=limit
                ):
                    if submission.id in seen_ids:
                        continue
                    seen_ids.add(submission.id)

                    # Combine title and selftext for content
                    content = f"{submission.title}\n\n{submission.selftext}"

                    results.append(RedditPost(
                        id=submission.id,
                        title=submission.title,
                        content=content,
                        url=submission.permalink,
                        subreddit=subreddit,
                        upvotes=submission.score,
                        comment_count=submission.num_comments,
                        created_utc=submission.created_utc
                    ))
            except Exception as e:
                print(f"Error searching for '{keyword}': {e}")
                continue

        return results
