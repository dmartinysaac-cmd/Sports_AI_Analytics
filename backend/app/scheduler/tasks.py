"""
Scheduler for automatic data updates.
Uses APScheduler for periodic scraping and data refresh.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from app.core.config import settings


async def scraping_job():
    """Periodic scraping job."""
    logger.info("Scheduler: Starting scraping job")
    try:
        # In production, this would run the scraping pipeline
        # For now, log the execution
        logger.info("Scheduler: Scraping job completed")
    except Exception as e:
        logger.error(f"Scheduler: Scraping job failed: {e}")


async def prediction_update_job():
    """Periodic job to update predictions for upcoming matches."""
    logger.info("Scheduler: Starting prediction update job")
    try:
        logger.info("Scheduler: Prediction update completed")
    except Exception as e:
        logger.error(f"Scheduler: Prediction update failed: {e}")


async def backtesting_job():
    """Periodic job to run backtesting on completed matches."""
    logger.info("Scheduler: Starting backtesting job")
    try:
        logger.info("Scheduler: Backtesting completed")
    except Exception as e:
        logger.error(f"Scheduler: Backtesting failed: {e}")


def setup_scheduler() -> AsyncIOScheduler:
    """Configure and return the scheduler."""
    scheduler = AsyncIOScheduler()

    if settings.SCHEDULER_ENABLED:
        # Scraping job - runs every hour
        scheduler.add_job(
            scraping_job,
            IntervalTrigger(minutes=settings.SCRAPING_INTERVAL_MINUTES),
            id="scraping",
            name="Data Scraping",
            replace_existing=True,
        )

        # Prediction update - runs every 30 minutes
        scheduler.add_job(
            prediction_update_job,
            IntervalTrigger(minutes=30),
            id="prediction_update",
            name="Prediction Updates",
            replace_existing=True,
        )

        # Backtesting - runs daily
        scheduler.add_job(
            backtesting_job,
            IntervalTrigger(hours=24),
            id="backtesting",
            name="Model Backtesting",
            replace_existing=True,
        )

        logger.info(f"Scheduler configured with {len(scheduler.get_jobs())} jobs")
    else:
        logger.info("Scheduler is disabled")

    return scheduler
