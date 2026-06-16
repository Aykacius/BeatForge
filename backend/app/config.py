"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Application
    APP_NAME: str = "BeatForge"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_RELOAD: bool = True

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/beatforge"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TASK_TIME_LIMIT: int = 3600  # 1 hour
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3300  # 55 minutes

    # Storage
    STORAGE_PATH: str = "/tmp/beatforge"
    MAX_FILE_SIZE: int = 52428800  # 50MB
    UPLOAD_TEMP_PATH: str = "/tmp/beatforge/uploads"
    OUTPUT_PATH: str = "/tmp/beatforge/output"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or standard

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Audio Processing
    AUDIO_SR: int = 22050  # Sample rate
    AUDIO_HOP_LENGTH: int = 512
    AUDIO_N_FFT: int = 2048

    # Mapping
    PLAYFIELD_WIDTH: int = 512
    PLAYFIELD_HEIGHT: int = 384
    DEFAULT_COMBO_COLORS: list[list[int]] = [
        [255, 0, 0],
        [0, 255, 0],
        [0, 0, 255],
        [255, 255, 0],
    ]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_UPLOADS_PER_HOUR: int = 100
    RATE_LIMIT_GENERATIONS_PER_HOUR: int = 50

    # Feature Flags
    ENABLE_ML_MODELS: bool = False
    ENABLE_USER_AUTH: bool = False
    ENABLE_BATCH_PROCESSING: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
