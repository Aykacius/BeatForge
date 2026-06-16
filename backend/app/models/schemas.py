"""SQLAlchemy ORM models."""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.models.database import Base


class Song(Base):
    """Uploaded song model."""
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    size_bytes = Column(Integer)
    duration = Column(Float)
    bpm = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class GenerationJob(Base):
    """Beatmap generation job model."""
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    song_id = Column(Integer, index=True)
    difficulty = Column(String)
    mapping_style = Column(String)
    target_star_rating = Column(Float)
    status = Column(String)  # queued, processing, completed, failed
    progress = Column(Integer, default=0)
    output_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)


class GeneratedBeatmap(Base):
    """Generated beatmap model."""
    __tablename__ = "generated_beatmaps"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    osu_file_path = Column(String)
    star_rating = Column(Float)
    object_count = Column(Integer)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
