import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from api.markets import router as markets_router
from api.websockets import router as ws_router
from ingestion.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
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
    
    yield
    
    # Shutdown
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

# CORS — allow local dev AND production Netlify
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://pit-terminal.netlify.app",
    "https://*.netlify.app",
]

# Also allow any origin in production if env var is set
if os.getenv("ALLOW_ALL_ORIGINS"):
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(markets_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "pit-terminal-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
