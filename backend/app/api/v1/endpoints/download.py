"""Download endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, FileResponse, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{job_id}")
async def download_beatmap(job_id: UUID):
    """Download generated beatmap.

    Args:
        job_id: Job ID

    Returns:
        OSZ file download
    """
    logger.info(f"Download request for job: {job_id}")

    # TODO: Return actual OSZ file
    raise HTTPException(status_code=404, detail="Beatmap not found")
