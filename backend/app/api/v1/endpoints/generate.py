"""Beatmap generation endpoint."""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from app.services.mapping_service import MappingService

router = APIRouter()


class GenerationRequest(BaseModel):
    """Beatmap generation request."""
    file_id: str
    difficulty: str  # Easy, Normal, Hard, Insane, Expert+
    mapping_style: str  # Technical Stream, Jump, Hybrid, Aim, Stream Practice
    target_star_rating: float  # 2.0 to 9.0


class GenerationResponse(BaseModel):
    """Beatmap generation response."""
    job_id: str
    status: str
    message: str


@router.post("/", response_model=GenerationResponse)
async def generate_beatmap(request: GenerationRequest):
    """Start beatmap generation job.
    
    Args:
        request: Generation parameters
        
    Returns:
        Job information with job_id for tracking
    """
    # Validate difficulty
    valid_difficulties = ["Easy", "Normal", "Hard", "Insane", "Expert+"]
    if request.difficulty not in valid_difficulties:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty. Must be one of: {valid_difficulties}")

    # Validate mapping style
    valid_styles = ["Technical Stream", "Jump", "Hybrid", "Aim", "Stream Practice"]
    if request.mapping_style not in valid_styles:
        raise HTTPException(status_code=400, detail=f"Invalid mapping style. Must be one of: {valid_styles}")

    # Validate star rating
    if not (2.0 <= request.target_star_rating <= 9.0):
        raise HTTPException(status_code=400, detail="Target star rating must be between 2.0 and 9.0")

    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Start async mapping task
        # TODO: Integrate with Celery for background processing
        mapping_service = MappingService()
        
        logger.info(f"Generation job started: {job_id}")
        logger.info(f"File ID: {request.file_id}")
        logger.info(f"Difficulty: {request.difficulty}")
        logger.info(f"Style: {request.mapping_style}")
        logger.info(f"Target SR: {request.target_star_rating}")

        return GenerationResponse(
            job_id=job_id,
            status="queued",
            message="Beatmap generation started. Use job_id to track progress."
        )

    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start beatmap generation")
