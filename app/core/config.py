# app/core/config.py
# Minimal two-environment config with dotenv auto-load in dev

import os
from dataclasses import dataclass

try:
    # Load .env automatically in development if present
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; skip if not installed
    pass

def getenv_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")

@dataclass
class Settings:
    APP_NAME: str = "Torque"
    ENV: str = os.getenv("APP_ENV", "dev").strip().lower()  # "dev" or "prod"
    DEBUG: bool = getenv_bool("APP_DEBUG", default=(os.getenv("APP_ENV", "dev").strip().lower() == "dev"))
    API_PREFIX: str = os.getenv("API_PREFIX", "/v1")

    # Dev uses SQLite, Prod requires Postgres
    sqlite_url: str = os.getenv("SQLITE_URL", "sqlite:///./Torque.db")
    postgres_url: str = os.getenv("POSTGRES_URL", "")

    # CORS
    CORS_ALLOW_ORIGINS: str = os.getenv("CORS_ALLOW_ORIGINS", "")  # comma-separated
    cors_allow_credentials: bool = getenv_bool("CORS_ALLOW_CREDENTIALS", False)
    cors_allow_methods: str = os.getenv("CORS_ALLOW_METHODS", "GET,POST,OPTIONS")
    cors_allow_headers: str = os.getenv("CORS_ALLOW_HEADERS", "Content-Type,Authorization")

    # Resolved DB URL
    database_url: str = ""

    def __post_init__(self):
        if self.ENV == "prod":
            if not self.postgres_url:
                raise RuntimeError("POSTGRES_URL is required when APP_ENV=prod")
            self.database_url = self.postgres_url
        else:
            self.database_url = self.sqlite_url

    def cors_origins_list(self):
        # Split comma-separated origins; trim blanks
        origins = [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]
        # If none provided and in dev, default to localhost ports commonly used
        if not origins and self.env == "dev":
            return [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ]
        return origins

settings = Settings()
