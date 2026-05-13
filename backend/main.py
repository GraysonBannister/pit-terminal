import os
import logging
import sys
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine, Base
from api.markets import router as markets_router
from api.websockets import router as ws_router
from ingestion.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database init failed (app will still start): {e}")

    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"Scheduler start failed: {e}")

    # Run ingestion once at startup so data appears immediately
    try:
        from ingestion.polymarket import ingest_polymarket
        from ingestion.news import ingest_news
        from ai.opportunity_engine import run_opportunity_engine
        logger.info("Running startup ingestion...")
        await ingest_polymarket()
        await ingest_news()
        await run_opportunity_engine()
        logger.info("Startup ingestion complete")
    except Exception as e:
        logger.error(f"Startup ingestion failed: {e}")

    yield

    try:
        stop_scheduler()
    except Exception:
        pass
    try:
        await engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title="PIT Terminal API",
    description="Prediction Intelligence Terminal backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow everything. The frontend handles auth/fallbacks.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler — ensures CORS headers on errors too
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "ok": False},
    )


app.include_router(markets_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")


@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "pit-terminal-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
