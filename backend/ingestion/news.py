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
    "reddit": 0.55,
    "hackernews": 0.75,
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
        logger.info("NEWSAPI_KEY not set, skipping NewsAPI")
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


async def fetch_reddit() -> list[dict]:
    """Fetch hot posts from relevant subreddits — no API key needed."""
    subreddits = [
        ("politics", "politics"),
        ("worldnews", "worldnews"),
        ("Bitcoin", "crypto"),
        ("ethereum", "crypto"),
        ("artificial", "ai"),
        ("technology", "tech"),
        ("economy", "macro"),
        ("wallstreetbets", "macro"),
    ]

    articles = []
    async with httpx.AsyncClient(timeout=15.0, headers={"User-Agent": "PIT-Terminal/1.0"}) as client:
        for subreddit, default_tag in subreddits:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=15"
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    title = post.get("title", "")
                    permalink = post.get("permalink", "")
                    if not title or not permalink:
                        continue
                    articles.append({
                        "title": title,
                        "url": f"https://reddit.com{permalink}",
                        "description": post.get("selftext", "")[:300],
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "source": {"name": "Reddit"},
                        "tags": _extract_tags(title),
                    })
            except Exception as e:
                logger.warning(f"Reddit fetch failed for r/{subreddit}: {e}")

    return articles


async def fetch_hackernews() -> list[dict]:
    """Fetch top stories from Hacker News — no API key needed."""
    articles = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            top_resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            top_ids = top_resp.json()[:30]
            for story_id in top_ids:
                try:
                    item_resp = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
                    item = item_resp.json()
                    if not item or item.get("type") != "story":
                        continue
                    title = item.get("title", "")
                    url = item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                    articles.append({
                        "title": title,
                        "url": url,
                        "description": "",
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "source": {"name": "HackerNews"},
                        "tags": _extract_tags(title),
                    })
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"HackerNews fetch failed: {e}")

    return articles


async def ingest_news():
    logger.info("Fetching news from all sources...")

    # Try all sources in parallel
    newsapi_articles = await fetch_newsapi()
    reddit_articles = await fetch_reddit()
    hn_articles = await fetch_hackernews()

    all_articles = newsapi_articles + reddit_articles + hn_articles
    logger.info(f"Fetched {len(all_articles)} articles total")

    async with AsyncSessionLocal() as session:
        seen = set()
        for art in all_articles:
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
            art_tags = art.get("tags", [])

            # Parse published date
            try:
                pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            except Exception:
                pub_dt = datetime.now(timezone.utc)

            tags = art_tags if art_tags else _extract_tags(headline + " " + description)
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
