"""Pydantic schemas for request/response validation."""

from datetime import datetime
from uuid import UUID
from typing import Optional, Any

from pydantic import BaseModel, Field

from app.models.enums import DifficultyEnum, MappingStyleEnum, JobStatusEnum


class UploadResponse(BaseModel):
    """Response for file upload."""

    song_id: UUID
    filename: str
    duration: float
    file_size: int


class GenerateRequest(BaseModel):
    """Request for beatmap generation."""

    song_id: UUID
    difficulty: DifficultyEnum
    mapping_style: MappingStyleEnum
    target_star_rating: float = Field(ge=2.0, le=9.0)


class GenerateResponse(BaseModel):
    """Response for generation start."""

    job_id: UUID
    status: JobStatusEnum
    created_at: datetime


class JobStatusResponse(BaseModel):
    """Response for job status query."""

    job_id: UUID
    status: JobStatusEnum
    progress: int = Field(ge=0, le=100)
    current_stage: Optional[str]
    estimated_time_remaining: Optional[int]
    result: Optional[dict[str, Any]]
    error_message: Optional[str]


class BeatmapMetadata(BaseModel):
    """Beatmap metadata."""

    title: str
    artist: str
    creator: str = "BeatForge AI"
    version: str
    bpm: float
    drain_time: float
    total_time: float
    estimated_star_rating: float
    object_count: int
    circle_count: int
    slider_count: int
    spinner_count: int
