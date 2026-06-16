"""Application configuration and settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # App
    DEBUG: bool = True
    APP_NAME: str = "BeatForge"
    APP_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/beatforge"
    SQLALCHEMY_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # File Upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "/tmp/beatforge/uploads"
    OUTPUT_DIR: str = "/tmp/beatforge/output"

    # Audio Processing
    SAMPLE_RATE: int = 44100
    HOP_LENGTH: int = 512
    N_FFT: int = 2048

    # Mapping Engine
    MIN_CIRCLE_DISTANCE: float = 50.0
    MAX_CIRCLE_DISTANCE: float = 250.0
    PLAYFIELD_WIDTH: int = 512
    PLAYFIELD_HEIGHT: int = 384

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
