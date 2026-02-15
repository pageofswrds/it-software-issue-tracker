from typing import Any
from datetime import datetime
from src.db import Database


class IssueRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(
        self,
        application_id: str,
        title: str,
        summary: str,
        source_type: str,
        source_url: str,
        severity: str,
        raw_content: str | None = None,
        version_id: str | None = None,
        issue_type: str | None = None,
        upvotes: int = 0,
        comment_count: int = 0,
        source_date: datetime | None = None,
        embedding: list[float] | None = None
    ) -> dict[str, Any]:
        results = self.db.execute(
            """
            INSERT INTO issues (
                application_id, version_id, title, summary, raw_content,
                source_type, source_url, severity, issue_type,
                upvotes, comment_count, source_date, embedding
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                application_id, version_id, title, summary, raw_content,
                source_type, source_url, severity, issue_type,
                upvotes, comment_count, source_date, embedding
            )
        )
        self.db.commit()
        return results[0]

    def list_by_application(
        self,
        application_id: str,
        severity: str | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM issues
            WHERE application_id = %s
        """
        params = [application_id]

        if severity:
            query += " AND severity = %s"
            params.append(severity)

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        return self.db.execute(query, tuple(params))

    def get_by_id(self, issue_id: str) -> dict[str, Any] | None:
        results = self.db.execute(
            "SELECT * FROM issues WHERE id = %s",
            (issue_id,)
        )
        return results[0] if results else None

    def exists_by_url(self, source_url: str) -> bool:
        results = self.db.execute(
            "SELECT 1 FROM issues WHERE source_url = %s LIMIT 1",
            (source_url,)
        )
        return len(results) > 0

    def count_by_severity(self, application_id: str) -> dict[str, int]:
        results = self.db.execute(
            """
            SELECT severity, COUNT(*) as count
            FROM issues
            WHERE application_id = %s
            GROUP BY severity
            """,
            (application_id,)
        )
        return {r['severity']: r['count'] for r in results}
