"""Job status endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.models.schemas import JobStatusResponse
from app.models.enums import JobStatusEnum

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: UUID):
    """Get status of a generation job.

    Args:
        job_id: Job ID

    Returns:
        Job status information
    """
    logger.info(f"Status query for job: {job_id}")

    # TODO: Query from database
    return JobStatusResponse(
        job_id=job_id,
        status=JobStatusEnum.COMPLETED,
        progress=100,
        current_stage="Completed",
        estimated_time_remaining=None,
        result={"beatmap_id": str(job_id)},
        error_message=None,
    )
