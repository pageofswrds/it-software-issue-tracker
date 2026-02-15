import pytest
from src.sources.reddit import RedditSource, RedditPost

def test_reddit_post_structure():
    post = RedditPost(
        id="abc123",
        title="Test Post",
        content="This is the content",
        url="https://reddit.com/r/sysadmin/abc123",
        subreddit="sysadmin",
        upvotes=100,
        comment_count=25,
        created_utc=1700000000.0
    )
    assert post.id == "abc123"
    assert post.upvotes == 100

def test_reddit_source_initialization():
    import os
    if not os.environ.get("REDDIT_CLIENT_ID"):
        pytest.skip("Reddit credentials not set")

    source = RedditSource()
    assert source is not None
