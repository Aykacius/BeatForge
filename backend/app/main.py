"""FastAPI application factory and setup."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.middleware.error_handler import error_exception_handler
from app.api.v1.router import api_router
from app.utils.logging import setup_logging

# Setup logging
logger = logging.getLogger(__name__)
setup_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"Redis: {settings.REDIS_URL}")

    yield

    # Shutdown
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Automatic osu!standard beatmap generation from MP3 files",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(GZIPMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Error handlers
    app.add_exception_handler(Exception, error_exception_handler)

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    # Health check
    @app.get("/api/v1/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/")
    async def root():
        """Root endpoint."""
        return JSONResponse(
            {
                "message": "Welcome to BeatForge API",
                "docs": "/docs",
                "redoc": "/redoc",
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.API_RELOAD,
    )
