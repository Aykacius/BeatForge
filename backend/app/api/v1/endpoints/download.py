"""Beatmap download endpoint."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/{job_id}")
async def download_beatmap(job_id: str):
    """Download generated beatmap (.osz file).
    
    Args:
        job_id: Job ID from generation request
        
    Returns:
        .osz file for download
    """
    # TODO: Fetch from output directory and verify completion
    raise HTTPException(status_code=404, detail="Beatmap not found or still processing")
