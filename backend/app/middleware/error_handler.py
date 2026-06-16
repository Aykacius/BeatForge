"""Global error handler middleware."""

import logging
from fastapi.responses import JSONResponse
from app.utils.exceptions import BeatForgeException

logger = logging.getLogger(__name__)


async def error_exception_handler(request, exc: Exception):
    """Handle exceptions and return proper error response."""
    if isinstance(exc, BeatForgeException):
        logger.warning(f"BeatForge error: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
