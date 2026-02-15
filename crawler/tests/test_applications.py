# crawler/tests/test_applications.py
import pytest
from src.db import Database
from src.repositories.applications import ApplicationRepository

@pytest.fixture
def db():
    database = Database()
    yield database
    database.close()

def test_list_applications(db):
    repo = ApplicationRepository(db)
    apps = repo.list_all()
    assert isinstance(apps, list)
    # Seed data should have at least Adobe Acrobat
    assert len(apps) >= 1

def test_get_application_by_id(db):
    repo = ApplicationRepository(db)
    apps = repo.list_all()
    if apps:
        app = repo.get_by_id(apps[0]['id'])
        assert app is not None
        assert 'name' in app
        assert 'keywords' in app
