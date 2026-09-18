"""
Logging configuration using loguru.
Separate log files for different modules.
"""
import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configure application logging with separate handlers."""
    logger.remove()  # Remove default handler

    # Console output
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | {message}",
    )

    # General log file
    logger.add(
        f"{settings.LOG_DIR}/app.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )

    # Scraping-specific log
    logger.add(
        f"{settings.LOG_DIR}/scraping.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        filter=lambda record: "scraping" in record["name"],
    )

    # Prediction-specific log
    logger.add(
        f"{settings.LOG_DIR}/prediction.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        filter=lambda record: "prediction" in record["name"] or "analytics" in record["name"],
    )

    # AI-specific log
    logger.add(
        f"{settings.LOG_DIR}/ai.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        filter=lambda record: "ai" in record["name"],
    )

    # Error log (all errors)
    logger.add(
        f"{settings.LOG_DIR}/errors.log",
        rotation="10 MB",
        retention="14 days",
        level="ERROR",
    )

    logger.info("Logging configured successfully")
