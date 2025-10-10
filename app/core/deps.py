# app/core/deps.py
from typing import Generator
import sqlite3
import psycopg
from app.core.config import settings

def get_conn() -> Generator[object, None, None]:
    if settings.ENV == "dev":
        conn = sqlite3.connect(settings.SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()
    else:
        if not settings.POSTGRES_DSN:
            raise RuntimeError("POSTGRES_DSN not configured")
        with psycopg.connect(settings.POSTGRES_DSN, autocommit=False) as conn:
            yield conn  # closed after request
