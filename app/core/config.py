# app/core/config.py
import os
from pydantic import BaseModel, Field, SecretStr

class Settings(BaseModel):
    # Environment: dev | uat | prod
    ENV: str = Field(default=os.getenv("ENV", "dev"))
    DEBUG: bool = Field(default=os.getenv("DEBUG", "false").lower() == "true")
    APP_NAME: str = Field(default=os.getenv("APP_NAME", "My FastAPI App"))

    # Database settings
    SQLITE_PATH: str = Field(default=os.getenv("SQLITE_PATH", "dev.db"))  # used when ENV=dev
    POSTGRES_DSN: str | None = Field(default=os.getenv("POSTGRES_DSN"))   # used when ENV in {uat, prod}

    # Security (no user auth, but useful for signing internal tokens if needed)
    SECRET_KEY: SecretStr = Field(default=SecretStr(os.getenv("SECRET_KEY", "please-change")))
    JWT_ALGORITHM: str = Field(default=os.getenv("JWT_ALGORITHM", "HS256"))

    # CORS
    CORS_ALLOW_ORIGINS: list[str] = Field(
        default_factory=lambda: [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")]
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true")
    CORS_ALLOW_METHODS: list[str] = Field(
        default_factory=lambda: [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")]
    )
    CORS_ALLOW_HEADERS: list[str] = Field(
        default_factory=lambda: [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "Content-Type").split(",")]
    )

    # Runtime limits
    REQUEST_BODY_MAX_BYTES: int = Field(default=int(os.getenv("REQUEST_BODY_MAX_BYTES", "1048576")))  # 1 MiB
    READ_TIMEOUT_SECONDS: int = Field(default=int(os.getenv("READ_TIMEOUT_SECONDS", "30")))
    WRITE_TIMEOUT_SECONDS: int = Field(default=int(os.getenv("WRITE_TIMEOUT_SECONDS", "30")))

    # Helpers
    @property
    def is_sqlite(self) -> bool:
        return self.ENV == "dev"

    @property
    def is_postgres(self) -> bool:
        return self.ENV in ("uat", "prod")

settings = Settings()
