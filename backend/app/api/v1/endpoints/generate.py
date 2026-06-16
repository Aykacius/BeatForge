"""Beatmap generation endpoints."""

import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.models.schemas import GenerateRequest, GenerateResponse
from app.models.enums import JobStatusEnum

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=GenerateResponse)
async def start_generation(request: GenerateRequest):
    """Start beatmap generation job.

    Args:
        request: Generation request parameters

    Returns:
        Generation response with job ID
    """
    logger.info(
        f"Generation request: song_id={request.song_id}, difficulty={request.difficulty}"
    )

    # TODO: Queue Celery task
    job_id = uuid4()

    return GenerateResponse(
        job_id=job_id,
        status=JobStatusEnum.QUEUED,
        created_at="2024-01-01T00:00:00Z",
    )
