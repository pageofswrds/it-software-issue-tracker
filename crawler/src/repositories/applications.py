from typing import Any
from src.db import Database


class ApplicationRepository:
    def __init__(self, db: Database):
        self.db = db

    def list_all(self) -> list[dict[str, Any]]:
        return self.db.execute("""
            SELECT id, name, vendor, keywords, created_at
            FROM applications
            ORDER BY name
        """)

    def get_by_id(self, app_id: str) -> dict[str, Any] | None:
        results = self.db.execute(
            "SELECT id, name, vendor, keywords, created_at FROM applications WHERE id = %s",
            (app_id,)
        )
        return results[0] if results else None

    def create(self, name: str, vendor: str | None, keywords: list[str]) -> dict[str, Any]:
        results = self.db.execute(
            """
            INSERT INTO applications (name, vendor, keywords)
            VALUES (%s, %s, %s)
            RETURNING id, name, vendor, keywords, created_at
            """,
            (name, vendor, keywords)
        )
        self.db.commit()
        return results[0]
