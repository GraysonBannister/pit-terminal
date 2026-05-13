import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database import AsyncSessionLocal
from models import NewsItem

logger = logging.getLogger(__name__)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_URL = "https://newsapi.org/v2/everything"

SOURCE_CREDIBILITY = {
    "reuters": 0.92,
    "associated press": 0.93,
    "bloomberg": 0.94,
    "nikkei": 0.88,
    "kyodo": 0.85,
    "the verge": 0.88,
    "techcrunch": 0.82,
    "coindesk": 0.80,
    "cnn": 0.78,
    "bbc": 0.85,
    "politico": 0.83,
    "axios": 0.84,
}

KEYWORD_TAGS = {
    "japan": ["japan", "japanese", "tokyo", "ldp", "snap election"],
    "usa": ["usa", "us", "america", "american", "trump", "biden", "election"],
    "ukraine": ["ukraine", "russia", "putin", "zelensky", "ceasefire", "war"],
    "fed": ["fed", "federal reserve", "rate cut", "interest rate", "inflation", "cpi"],
    "crypto": ["bitcoin", "btc", "crypto", "cryptocurrency", "ethereum", "etf"],
    "ai": ["openai", "gpt", "ai", "artificial intelligence", "llm"],
    "tech": ["apple", "vision pro", "meta", "google", "microsoft"],
}


def _extract_tags(text: str) -> list[str]:
    text_lower = text.lower()
    tags = set()
    for tag, keywords in KEYWORD_TAGS.items():
        if any(kw in text_lower for kw in keywords):
            tags.add(tag)
    return list(tags)


def _get_credibility(source_name: str) -> float:
    return SOURCE_CREDIBILITY.get(source_name.lower(), 0.70)


def _hash_url(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:32]


async def fetch_newsapi() -> list[dict]:
    if not NEWSAPI_KEY:
        logger.warning("NEWSAPI_KEY not set, skipping NewsAPI ingestion")
        return []

    queries = [
        "prediction market OR polymarket",
        "election OR trump OR biden",
        "fed OR inflation OR rate cut OR recession",
        "bitcoin OR crypto OR ethereum",
        "openai OR AI OR gpt",
    ]

    articles = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for q in queries:
            params = {
                "q": q,
                "sortBy": "publishedAt",
                "pageSize": 20,
                "language": "en",
                "apiKey": NEWSAPI_KEY,
            }
            try:
                resp = await client.get(NEWSAPI_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                if data.get("status") == "ok":
                    articles.extend(data.get("articles", []))
            except Exception as e:
                logger.error(f"NewsAPI fetch failed for query '{q}': {e}")

    return articles


async def ingest_news():
    logger.info("Fetching news...")
    articles = await fetch_newsapi()
    logger.info(f"Fetched {len(articles)} articles")

    async with AsyncSessionLocal() as session:
        seen = set()
        for art in articles:
            url = art.get("url", "")
            if not url:
                continue

            art_id = _hash_url(url)
            if art_id in seen:
                continue
            seen.add(art_id)

            # Deduplicate against DB
            existing = await session.execute(
                select(NewsItem).where(NewsItem.id == art_id)
            )
            if existing.scalar_one_or_none():
                continue

            source_name = art.get("source", {}).get("name", "Unknown")
            headline = art.get("title", "")
            description = art.get("description", "")
            published = art.get("publishedAt")
            content = art.get("content", "")

            # Parse published date
            try:
                pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            except Exception:
                pub_dt = datetime.now(timezone.utc)

            tags = _extract_tags(headline + " " + description)
            credibility = _get_credibility(source_name)

            news_item = NewsItem(
                id=art_id,
                headline=headline,
                source=source_name,
                credibility=credibility,
                published_at=pub_dt,
                tags=tags,
                summary=description or content,
            )
            session.add(news_item)

        await session.commit()
    logger.info("News ingestion complete")
