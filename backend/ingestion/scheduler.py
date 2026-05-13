import os
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def _ingest_polymarket():
    logger.info("Running Polymarket ingestion...")
    try:
        from ingestion.polymarket import ingest_polymarket
        import asyncio
        asyncio.run(ingest_polymarket())
    except Exception as e:
        logger.error(f"Polymarket ingestion failed: {e}")


def _ingest_news():
    logger.info("Running news ingestion...")
    try:
        from ingestion.news import ingest_news
        import asyncio
        asyncio.run(ingest_news())
    except Exception as e:
        logger.error(f"News ingestion failed: {e}")


def _run_opportunity_engine():
    logger.info("Running opportunity engine...")
    try:
        from ai.opportunity_engine import run_opportunity_engine
        import asyncio
        asyncio.run(run_opportunity_engine())
    except Exception as e:
        logger.error(f"Opportunity engine failed: {e}")


def start_scheduler():
    scheduler.add_job(
        _ingest_polymarket,
        trigger=IntervalTrigger(minutes=3),
        id="polymarket_ingest",
        replace_existing=True,
    )
    scheduler.add_job(
        _ingest_news,
        trigger=IntervalTrigger(minutes=10),
        id="news_ingest",
        replace_existing=True,
    )
    scheduler.add_job(
        _run_opportunity_engine,
        trigger=IntervalTrigger(minutes=5),
        id="opportunity_engine",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler stopped")
