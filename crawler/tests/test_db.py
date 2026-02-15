import pytest
from src.db import Database

def test_database_connects():
    db = Database()
    assert db.is_connected() == True
    db.close()

def test_database_can_query():
    db = Database()
    result = db.execute("SELECT 1 as num")
    assert result[0]['num'] == 1
    db.close()
