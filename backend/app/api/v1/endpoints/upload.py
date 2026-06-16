"""File upload endpoint."""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger

from app.config import settings

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """Upload an MP3 file for beatmap generation.
    
    Args:
        file: MP3 audio file (max 100MB)
        
    Returns:
        Upload information including file_id
    """
    # Validate file type
    if not file.filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Only MP3 files are supported")

    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Generate unique file ID
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.mp3")

    try:
        # Save uploaded file
        contents = await file.read()
        
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )

        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"File uploaded: {file_id} ({len(contents)} bytes)")

        return {
            "file_id": file_id,
            "filename": file.filename,
            "size_bytes": len(contents),
            "message": "File uploaded successfully"
        }

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload file")
