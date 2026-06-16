"""Celery worker configuration."""

from celery import Celery
from loguru import logger

from app.config import settings

app = Celery(
    "beatforge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
)


@app.task(bind=True)
def generate_beatmap_task(
    self,
    job_id: str,
    file_path: str,
    difficulty: str,
    mapping_style: str,
    target_star_rating: float,
):
    """Async task for beatmap generation.
    
    Args:
        job_id: Unique job identifier
        file_path: Path to uploaded audio file
        difficulty: Difficulty level
        mapping_style: Mapping style
        target_star_rating: Target star rating
    """
    try:
        logger.info(f"Starting Celery task for job {job_id}")
        
        # Import here to avoid circular imports
        import asyncio
        from app.services.mapping_service import MappingService
        
        mapping_service = MappingService()
        
        # Update progress
        self.update_state(state="PROGRESS", meta={"progress": 10, "step": "Analyzing audio..."})
        
        # Generate beatmap
        result = asyncio.run(mapping_service.generate_beatmap(
            file_path=file_path,
            difficulty=difficulty,
            mapping_style=mapping_style,
            target_star_rating=target_star_rating,
        ))
        
        self.update_state(state="PROGRESS", meta={"progress": 100, "step": "Complete"})
        
        logger.info(f"Job {job_id} completed successfully")
        
        return {
            "status": "success",
            "job_id": job_id,
            "result": result,
        }
    
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
