"""API v1 router assembly."""

from fastapi import APIRouter

from app.api.v1.endpoints import upload, generate, jobs, download

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
api_router.include_router(generate.router, prefix="/generate", tags=["Generate"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(download.router, prefix="/download", tags=["Download"])
