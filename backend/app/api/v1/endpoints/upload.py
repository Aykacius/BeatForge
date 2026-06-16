"""File upload endpoints."""

import logging
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.config import settings
from app.models.schemas import UploadResponse
from app.utils.exceptions import InvalidFileError, FileTooLargeError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload MP3 file for beatmap generation.

    Args:
        file: MP3 file to upload

    Returns:
        Upload response with song ID
    """
    logger.info(f"File upload started: {file.filename}")

    # Validate file type
    if not file.content_type.startswith("audio/"):
        logger.warning(f"Invalid file type: {file.content_type}")
        raise InvalidFileError("File must be an audio file (MP3, WAV, OGG)")

    # Validate file size
    content = await file.read()
    file_size = len(content)

    if file_size > settings.MAX_FILE_SIZE:
        logger.warning(f"File too large: {file_size} > {settings.MAX_FILE_SIZE}")
        raise FileTooLargeError(
            f"File too large. Maximum size is {settings.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
        )

    # Save file
    song_id = uuid4()
    upload_path = Path(settings.UPLOAD_TEMP_PATH) / f"{song_id}.mp3"
    upload_path.parent.mkdir(parents=True, exist_ok=True)

    with open(upload_path, "wb") as f:
        f.write(content)

    logger.info(f"File uploaded successfully: {song_id} ({file_size} bytes)")

    return UploadResponse(
        song_id=song_id,
        filename=file.filename,
        duration=0.0,  # TODO: Calculate from audio
        file_size=file_size,
    )
