"""Job status tracking endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class JobStatus(BaseModel):
    """Job status information."""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: int  # 0-100
    current_step: str
    message: str


@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get status of a beatmap generation job.
    
    Args:
        job_id: Job ID from generation request
        
    Returns:
        Current job status and progress
    """
    # TODO: Fetch from database/cache
    return JobStatus(
        job_id=job_id,
        status="processing",
        progress=50,
        current_step="Generating patterns",
        message="Mapping engine is generating patterns based on audio analysis"
    )
