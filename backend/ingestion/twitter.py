import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx
import feedparser
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database import AsyncSessionLocal
from models import NewsItem

logger = logging.getLogger(__name__)

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Nitter instances for RSS fallback (these are often unreliable)
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.it",
]

KEYWORD_QUERIES = [
    "polymarket prediction market",
    "election trump biden harris",
    "fed rate cut inflation",
    "bitcoin crypto ethereum",
    "openai gpt ai",
    "ukraine russia war",
    "japan election ldp",
]


def _hash_content(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:32]


def _extract_tags(text: str) -> list[str]:
    text_lower = text.lower()
    tags = set()
    keyword_tags = {
        "japan": ["japan", "japanese", "tokyo", "ldp"],
        "usa": ["usa", " us ", "america", "american", "trump", "biden", "harris"],
        "ukraine": ["ukraine", "russia", "putin", "zelenskyy", "war"],
        "china": ["china", "chinese", "beijing", "xi jinping"],
        "politics": ["election", "president", "vote", "senator", "campaign"],
        "crypto": ["bitcoin", "btc", "crypto", "ethereum", "eth"],
        "tech": ["openai", "gpt", "ai ", "apple", "google"],
        "macro": ["fed", "rate cut", "inflation", "recession"],
    }
    for tag, keywords in keyword_tags.items():
        if any(kw in text_lower for kw in keywords):
            tags.add(tag)
    return list(tags) if tags else ["general"]


async def _fetch_twitter_api(query: str, max_results: int = 10) -> list[dict]:
    """Fetch tweets using Twitter API v2 (requires Bearer token)."""
    if not TWITTER_BEARER_TOKEN:
        return []

    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": query,
        "max_results": min(max_results, 25),  # Free tier limit
        "tweet.fields": "created_at,public_metrics,author_id,lang",
        "expansions": "author_id",
        "user.fields": "username,public_metrics",
    }
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 401:
                logger.warning("[Twitter API] Invalid Bearer token")
                return []
            if resp.status_code == 429:
                logger.warning("[Twitter API] Rate limited")
                return []
            if resp.status_code != 200:
                logger.warning(f"[Twitter API] HTTP {resp.status_code}: {resp.text[:200]}")
                return []

            data = resp.json()
            tweets = data.get("data", [])
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}

            results = []
            for tweet in tweets:
                author = users.get(tweet.get("author_id", ""), {})
                metrics = tweet.get("public_metrics", {})
                results.append({
                    "id": tweet["id"],
                    "text": tweet["text"],
                    "author": author.get("username", "unknown"),
                    "author_followers": author.get("public_metrics", {}).get("followers_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "likes": metrics.get("like_count", 0),
                    "created_at": tweet.get("created_at", ""),
                })
            return results

        except Exception as e:
            logger.warning(f"[Twitter API] Error: {e}")
            return []


async def _fetch_nitter_rss(query: str) -> list[dict]:
    """Fetch tweets via Nitter RSS as fallback."""
    # Nitter search RSS: /search?f=tweets&q=QUERY
    # RSS feed: /search/rss?f=tweets&q=QUERY
    encoded_query = query.replace(" ", "%20")
    results = []

    for instance in NITTER_INSTANCES:
        try:
            url = f"{instance}/search/rss?f=tweets&q={encoded_query}"
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue

                parsed = feedparser.parse(resp.text)
                for entry in parsed.entries[:10]:
                    title = entry.get("title", "").strip()
                    if not title:
                        continue
                    results.append({
                        "id": _hash_content(title),
                        "text": title,
                        "author": entry.get("author", "unknown"),
                        "author_followers": 0,
                        "retweets": 0,
                        "likes": 0,
                        "created_at": entry.get("published", datetime.now(timezone.utc).isoformat()),
                    })
                if results:
                    logger.info(f"[Nitter] {instance}: {len(results)} tweets for '{query[:30]}'")
                    return results
        except Exception as e:
            logger.debug(f"[Nitter] {instance} failed: {e}")

    return []


def _calculate_social_credibility(tweet: dict) -> float:
    """Calculate credibility score based on engagement and followers."""
    followers = tweet.get("author_followers", 0)
    retweets = tweet.get("retweets", 0)
    likes = tweet.get("likes", 0)

    # Base credibility
    cred = 0.35

    # Follower boost (diminishing returns)
    if followers > 100_000:
        cred += 0.25
    elif followers > 10_000:
        cred += 0.15
    elif followers > 1_000:
        cred += 0.05

    # Engagement boost
    engagement = retweets + likes
    if engagement > 1_000:
        cred += 0.20
    elif engagement > 100:
        cred += 0.10
    elif engagement > 10:
        cred += 0.05

    return min(0.90, max(0.20, cred))


async def ingest_twitter():
    """Main Twitter ingestion with API + fallback."""
    logger.info("=" * 60)
    logger.info("TWITTER INGESTION START")
    logger.info("=" * 60)

    all_tweets = []

    for query in KEYWORD_QUERIES:
        # Try Twitter API first
        tweets = await _fetch_twitter_api(query, max_results=10)
        if tweets:
            logger.info(f"[Twitter API] '{query[:30]}...': {len(tweets)} tweets")
            all_tweets.extend(tweets)
        else:
            # Fallback to Nitter
            tweets = await _fetch_nitter_rss(query)
            if tweets:
                logger.info(f"[Nitter RSS] '{query[:30]}...': {len(tweets)} tweets")
                all_tweets.extend(tweets)

    if not all_tweets:
        logger.warning("No tweets fetched. Set TWITTER_BEARER_TOKEN for Twitter API access.")
        logger.info("=" * 60)
        return

    # Deduplicate and store
    async with AsyncSessionLocal() as session:
        seen = set()
        new_count = 0

        for tweet in all_tweets:
            text = tweet.get("text", "").strip()
            if not text:
                continue

            art_id = f"tw-{tweet.get('id', _hash_content(text))}"
            if art_id in seen:
                continue
            seen.add(art_id)

            # Deduplicate against DB
            existing = await session.execute(
                select(NewsItem).where(NewsItem.id == art_id)
            )
            if existing.scalar_one_or_none():
                continue

            # Parse date
            created = tweet.get("created_at", "")
            try:
                if created:
                    pub_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                else:
                    pub_dt = datetime.now(timezone.utc)
            except Exception:
                pub_dt = datetime.now(timezone.utc)

            author = tweet.get("author", "unknown")
            followers = tweet.get("author_followers", 0)
            retweets = tweet.get("retweets", 0)
            likes = tweet.get("likes", 0)
            credibility = _calculate_social_credibility(tweet)
            tags = _extract_tags(text)

            # Build summary with engagement metrics
            summary = f"@{author} ({followers:,} followers) | {retweets} RT | {likes} likes"

            news_item = NewsItem(
                id=art_id,
                headline=text[:280],
                source="Twitter/X",
                credibility=credibility,
                published_at=pub_dt,
                tags=tags,
                summary=summary,
            )
            session.add(news_item)
            new_count += 1

        await session.commit()

        logger.info("=" * 60)
        logger.info("TWITTER INGESTION COMPLETE")
        logger.info(f"  Total tweets: {len(all_tweets)}")
        logger.info(f"  New tweets stored: {new_count}")
        logger.info("=" * 60)
