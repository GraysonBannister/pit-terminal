import os
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

raw_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./pit_terminal.db")

# Supabase and most managed Postgres require SSL
if raw_url.startswith("postgresql") and "ssl" not in raw_url:
    if "?" in raw_url:
        DATABASE_URL = raw_url + "&ssl=require"
    else:
        DATABASE_URL = raw_url + "?ssl=require"
else:
    DATABASE_URL = raw_url

logger.info(f"Using database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
