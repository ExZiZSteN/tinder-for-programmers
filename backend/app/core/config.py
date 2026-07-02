from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Путь к корню проекта (4 уровня вверх от config.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",  # Игнорировать неизвестные переменные
    )

    APP_ENV: str = "development"
    SECRET_KEY: str = "1oVW5BOR4Ckn2MNhih-ukghniMvcOcuqzoIy4rqyh3R9JBQcC9S11KxikeX2AyGj7-7hrZuvNHgSCenRAXBg0Q"
    API_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"


    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "tinder_devs"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tinder_devs"


    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""

    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "uploads"
    MINIO_USE_SSL: bool = False
    MINIO_EXTERNAL_ENDPOINT: str = "localhost:9000"


    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM: int = 384
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DEVICE: str = "cpu"

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ============================================================
    # LOGGING
    # ============================================================
    LOG_LEVEL: str = "INFO"

    # ============================================================
    # SENTRY
    # ============================================================
    SENTRY_DSN: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            if not v:
                return []
            # Поддержка и JSON, и comma-separated
            if v.startswith("["):
                import json
                return json.loads(v)
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


settings = Settings()