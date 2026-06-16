"""Database initialization and migrations."""

from loguru import logger
from app.models.database import engine, Base


def init_db():
    """Initialize database tables."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


if __name__ == "__main__":
    init_db()
