import os
from typing import Any
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not set")
        self.conn = psycopg.connect(self.database_url, row_factory=dict_row)

    def is_connected(self) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception:
            return False

    def execute(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                return cur.fetchall()
            return []

    def execute_many(self, query: str, params_list: list[tuple]) -> None:
        with self.conn.cursor() as cur:
            cur.executemany(query, params_list)
        self.conn.commit()

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
