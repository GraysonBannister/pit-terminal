import asyncio
import logging

logger = logging.getLogger(__name__)

_running = False
_tasks = []


async def _loop_ingest_polymarket():
    from ingestion.polymarket import ingest_polymarket
    while _running:
        try:
            logger.info("Running Polymarket ingestion...")
            await ingest_polymarket()
            logger.info("Polymarket ingestion complete")
        except Exception as e:
            logger.error(f"Polymarket ingestion failed: {e}")
        await asyncio.sleep(180)


async def _loop_ingest_news():
    from ingestion.news import ingest_news
    while _running:
        try:
            logger.info("Running news ingestion...")
            await ingest_news()
            logger.info("News ingestion complete")
        except Exception as e:
            logger.error(f"News ingestion failed: {e}")
        # NewsAPI free tier = 100 req/day. With 5 queries per run, that's 20 runs/day max.
        # 3600s = hourly is safe (24 runs/day × 5 queries = 120 requests — slightly over).
        # 7200s = every 2 hours is comfortably under limit.
        await asyncio.sleep(7200)


async def _loop_opportunity_engine():
    from ai.opportunity_engine import run_opportunity_engine
    while _running:
        try:
            logger.info("Running opportunity engine...")
            await run_opportunity_engine()
            logger.info("Opportunity engine complete")
        except Exception as e:
            logger.error(f"Opportunity engine failed: {e}")
        await asyncio.sleep(300)


def start_scheduler():
    global _running, _tasks
    if _running:
        return
    _running = True
    loop = asyncio.get_running_loop()
    _tasks = [
        loop.create_task(_loop_ingest_polymarket()),
        loop.create_task(_loop_ingest_news()),
        loop.create_task(_loop_opportunity_engine()),
    ]
    logger.info("Scheduler started")


def stop_scheduler():
    global _running, _tasks
    _running = False
    for t in _tasks:
        t.cancel()
    _tasks.clear()
    logger.info("Scheduler stopped")
