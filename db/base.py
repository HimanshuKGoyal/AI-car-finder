from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
import os

class Base(DeclarativeBase):
    pass

def get_database_url() -> str:
    """
    Determine the database URL based on environment variables.

    Priority:
      1) DATABASE_URL (explicit override for any env)
      2) ENV=dev  -> sqlite file path (SQLITE_PATH or torque.db)
      3) ENV=uat/prod -> POSTGRES_DSN (required)
    """
    # Explicit override if set
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.strip():
        return db_url.strip()

    env = os.getenv("ENV", "dev").lower()

    if env == "dev":
        # Use SQLite in dev; allow override path via SQLITE_PATH
        sqlite_path = os.getenv("SQLITE_PATH", "torque.db")
        # Use file-based sqlite URL
        return f"sqlite:///{sqlite_path}"

    # For uat/prod: use Postgres DSN
    pg_dsn = os.getenv("POSTGRES_DSN", "").strip()
    if pg_dsn:
        return pg_dsn

    # As a final fallback, if DATABASE_URL wasn’t set and POSTGRES_DSN missing in uat/prod,
    # allow a safe default only for local usage; otherwise raise a helpful error.
    # You can choose to raise to prevent misconfiguration:
    raise RuntimeError(
        "POSTGRES_DSN not configured for ENV="
        + env
        + ". Set POSTGRES_DSN (e.g., postgresql://user:pass@host:5432/db) "
          "or provide DATABASE_URL to override."
    )

engine = create_engine(get_database_url(), 
    echo=True, 
    future=True
)

SessionLocal = sessionmaker(autocommit=False, 
    autoflush=False, 
    bind=engine,
    future=True
)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()