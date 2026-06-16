"""Celery configuration."""

from app.config import settings

class CeleryConfig:
    """Celery configuration."""

    broker_url = settings.CELERY_BROKER_URL
    result_backend = settings.CELERY_RESULT_BACKEND
    task_serializer = "json"
    accept_content = ["json"]
    result_serializer = "json"
    timezone = "UTC"
    enable_utc = True
    task_track_started = True
    task_time_limit = settings.CELERY_TASK_TIME_LIMIT
    task_soft_time_limit = settings.CELERY_TASK_SOFT_TIME_LIMIT


config = CeleryConfig()
