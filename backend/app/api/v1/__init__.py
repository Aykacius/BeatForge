"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1.endpoints import upload, generate, jobs, download

router = APIRouter()

router.include_router(upload.router, prefix="/upload", tags=["upload"])
router.include_router(generate.router, prefix="/generate", tags=["generate"])
router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
router.include_router(download.router, prefix="/download", tags=["download"])


@router.get("/")
async def root():
    """API v1 root endpoint."""
    return {"message": "BeatForge API v1", "endpoints": ["upload", "generate", "jobs", "download"]}
