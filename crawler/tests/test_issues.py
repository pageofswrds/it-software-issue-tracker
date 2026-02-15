# crawler/tests/test_issues.py
import pytest
from src.db import Database
from src.repositories.applications import ApplicationRepository
from src.repositories.issues import IssueRepository

@pytest.fixture
def db():
    database = Database()
    yield database
    database.close()

@pytest.fixture
def app_id(db):
    repo = ApplicationRepository(db)
    apps = repo.list_all()
    return apps[0]['id']

def test_create_issue(db, app_id):
    repo = IssueRepository(db)
    issue = repo.create(
        application_id=app_id,
        title="Test crash issue",
        summary="App crashes on startup",
        raw_content="Full content here...",
        source_type="reddit",
        source_url="https://reddit.com/r/test/123",
        severity="critical",
        issue_type="crash",
        upvotes=50,
        comment_count=10
    )
    assert issue['id'] is not None
    assert issue['title'] == "Test crash issue"
    assert issue['severity'] == "critical"

    # Cleanup
    db.execute("DELETE FROM issues WHERE id = %s", (issue['id'],))
    db.commit()

def test_list_issues_by_application(db, app_id):
    repo = IssueRepository(db)
    issues = repo.list_by_application(app_id)
    assert isinstance(issues, list)

def test_issue_exists_by_url(db, app_id):
    repo = IssueRepository(db)
    unique_url = "https://reddit.com/unique/test/456"

    # Should not exist initially
    assert repo.exists_by_url(unique_url) == False

    # Create issue
    issue = repo.create(
        application_id=app_id,
        title="Test",
        summary="Test",
        raw_content="Test",
        source_type="reddit",
        source_url=unique_url,
        severity="minor"
    )

    # Now should exist
    assert repo.exists_by_url(unique_url) == True

    # Cleanup
    db.execute("DELETE FROM issues WHERE id = %s", (issue['id'],))
    db.commit()
