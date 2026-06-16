"""Logging configuration."""

import logging
from loguru import logger


def setup_logging():
    """Configure loguru logging."""
    logger.enable("app")
    logger.add(
        "logs/beatforge.log",
        rotation="500 MB",
        retention="7 days",
        level="INFO",
    )
