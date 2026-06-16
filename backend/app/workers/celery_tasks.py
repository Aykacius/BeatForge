"""Celery task definitions."""

import logging
from uuid import UUID

from celery import Celery

from app.config import settings
from app.models.enums import DifficultyEnum, MappingStyleEnum
from app.services.generation_service import GenerationService

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "beatforge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
)


@celery_app.task(bind=True, name="generate_beatmap")
def generate_beatmap_task(
    self,
    song_id: str,
    audio_file_path: str,
    difficulty: str,
    mapping_style: str,
    target_star_rating: float,
):
    """Celery task for beatmap generation.

    Args:
        self: Celery task self reference
        song_id: Song ID
        audio_file_path: Path to audio file
        difficulty: Difficulty level
        mapping_style: Mapping style
        target_star_rating: Target difficulty in stars
    """
    try:
        logger.info(
            f"Beatmap generation task started: job_id={self.request.id}, "
            f"song_id={song_id}, difficulty={difficulty}"
        )

        # Initialize service
        service = GenerationService()

        # Generate beatmap
        result = service.generate_beatmap(
            song_id=UUID(song_id),
            audio_file_path=audio_file_path,
            difficulty=DifficultyEnum(difficulty),
            mapping_style=MappingStyleEnum(mapping_style),
            target_star_rating=target_star_rating,
            output_dir=settings.OUTPUT_PATH,
        )

        logger.info(f"Beatmap generation completed: {self.request.id}")
        return result

    except Exception as e:
        logger.error(f"Beatmap generation failed: {str(e)}", exc_info=e)
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
