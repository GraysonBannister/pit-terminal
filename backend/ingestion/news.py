import hashlib
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
import feedparser
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
    "ap": 0.93,
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
    "financial times": 0.91,
    "ft": 0.91,
    "wall street journal": 0.90,
    "wsj": 0.90,
    "new york times": 0.88,
    "nyt": 0.88,
    "washington post": 0.87,
    "the guardian": 0.86,
    "economist": 0.90,
    "forbes": 0.80,
    "fortune": 0.82,
    "coinbase": 0.85,
    "messari": 0.84,
    "the block": 0.83,
    "decrypt": 0.78,
    "reddit": 0.55,
    "hackernews": 0.75,
    "substack": 0.70,
    "medium": 0.65,
    "twitter": 0.50,
    "x": 0.50,
}

KEYWORD_TAGS = {
    "japan": ["japan", "japanese", "tokyo", "ldp", "snap election", "kishida"],
    "usa": ["usa", " us ", "america", "american", "trump", "biden", "harris", "congress", "senate", "white house", "gop", "democrat", "republican"],
    "ukraine": ["ukraine", "russia", "putin", "zelenskyy", "zelensky", "ceasefire", "war", "invasion"],
    "fed": ["fed", "federal reserve", "rate cut", "interest rate", "inflation", "cpi", "ppi", "powell"],
    "crypto": ["bitcoin", "btc", "crypto", "cryptocurrency", "ethereum", "eth", "solana", "defi", "nft"],
    "ai": ["openai", "chatgpt", "gpt", "ai ", "artificial intelligence", "llm", "claude", "anthropic", "gemini"],
    "tech": ["apple", "google", "alphabet", "microsoft", "meta", "facebook", "amazon", "nvidia", "tesla", "elon"],
    "markets": ["stock market", "nasdaq", "s&p", "dow", "trading", "investor", "bull", "bear market"],
    "macro": ["gdp", "recession", "unemployment", "jobs report", "economic growth", "tariff", "trade war"],
}

# RSS feeds for major news sources
RSS_FEEDS = [
    # Crypto
    ("https://cointelegraph.com/rss", "CoinTelegraph", 0.82),
    ("https://coindesk.com/arc/outboundfeeds/rss/", "CoinDesk", 0.80),
    ("https://decrypt.co/feed", "Decrypt", 0.78),
    # Tech
    ("https://techcrunch.com/feed/", "TechCrunch", 0.82),
    ("https://www.theverge.com/rss/index.xml", "The Verge", 0.88),
    # Business/Finance
    ("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg", 0.94),
    ("https://www.reutersagency.com/feed/?taxonomy=markets&post_type=reuters-best", "Reuters", 0.92),
    ("https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "WSJ", 0.90),
    # Politics
    ("https://www.politico.com/rss/politics.xml", "Politico", 0.83),
    ("https://feeds.bbci.co.uk/news/world/rss.xml", "BBC", 0.85),
]


def _extract_tags(text: str) -> list[str]:
    text_lower = text.lower()
    tags = set()
    for tag, keywords in KEYWORD_TAGS.items():
        if any(kw in text_lower for kw in keywords):
            tags.add(tag)
    return list(tags) if tags else ["general"]


def _get_credibility(source_name: str) -> float:
    cred = SOURCE_CREDIBILITY.get(source_name.lower(), 0.70)
    logger.debug(f"Credibility for '{source_name}': {cred}")
    return cred


def _hash_url(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:32]


async def fetch_newsapi() -> list[dict]:
    """Fetch from NewsAPI with detailed logging."""
    if not NEWSAPI_KEY:
        logger.warning("NEWSAPI_KEY not set, skipping NewsAPI")
        return []

    queries = [
        "prediction market OR polymarket",
        "election OR trump OR biden OR harris",
        "fed OR inflation OR rate cut OR recession OR powell",
        "bitcoin OR crypto OR ethereum OR defi",
        "openai OR chatgpt OR AI OR artificial intelligence",
    ]

    articles = []
    rate_limited = False
    total_requests = 0
    
    logger.info(f"[NewsAPI] Starting fetch with {len(queries)} queries")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for q in queries:
            if rate_limited:
                logger.warning(f"[NewsAPI] Rate limited earlier, skipping remaining queries")
                break
            
            total_requests += 1
            params = {
                "q": q,
                "sortBy": "publishedAt",
                "pageSize": 20,
                "language": "en",
                "apiKey": NEWSAPI_KEY,
            }
            try:
                logger.debug(f"[NewsAPI] Query: '{q}'")
                resp = await client.get(NEWSAPI_URL, params=params)
                
                if resp.status_code == 429:
                    logger.error(f"[NewsAPI] RATE LIMITED (429) for query '{q}' - quota exceeded")
                    rate_limited = True
                    continue
                elif resp.status_code == 401:
                    logger.error(f"[NewsAPI] INVALID API KEY (401) - check NEWSAPI_KEY")
                    break
                elif resp.status_code != 200:
                    logger.error(f"[NewsAPI] HTTP {resp.status_code} for query '{q}': {resp.text[:200]}")
                    continue
                
                data = resp.json()
                if data.get("status") == "ok":
                    query_articles = data.get("articles", [])
                    logger.info(f"[NewsAPI] Query '{q[:30]}...' returned {len(query_articles)} articles")
                    articles.extend(query_articles)
                else:
                    logger.error(f"[NewsAPI] API error for query '{q}': {data.get('message', 'unknown')}")
                    
            except httpx.TimeoutException:
                logger.error(f"[NewsAPI] TIMEOUT for query '{q}'")
            except Exception as e:
                logger.error(f"[NewsAPI] Exception for query '{q}': {type(e).__name__}: {e}")

    logger.info(f"[NewsAPI] Completed: {len(articles)} articles from {total_requests} requests")
    return articles


async def fetch_rss_feeds() -> list[dict]:
    """Fetch from RSS feeds with detailed logging."""
    articles = []
    
    logger.info(f"[RSS] Starting fetch from {len(RSS_FEEDS)} feeds")
    
    for feed_url, source_name, default_cred in RSS_FEEDS:
        try:
            logger.debug(f"[RSS] Fetching {source_name} from {feed_url}")
            parsed = feedparser.parse(feed_url)
            
            if parsed.bozo:
                logger.warning(f"[RSS] {source_name}: Parse warning - {parsed.get('bozo_exception', 'unknown')}")
            
            feed_articles = []
            for entry in parsed.entries[:15]:  # Top 15 per feed
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", entry.get("description", ""))[:500]
                published = entry.get("published", entry.get("updated", ""))
                
                if not title or not link:
                    continue
                
                # Parse date
                pub_dt = datetime.now(timezone.utc)
                if published:
                    try:
                        pub_dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
                    except:
                        try:
                            pub_dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%S%z")
                        except:
                            pass
                
                feed_articles.append({
                    "title": title,
                    "url": link,
                    "description": summary,
                    "publishedAt": pub_dt.isoformat(),
                    "source": {"name": source_name},
                    "tags": _extract_tags(title + " " + summary),
                })
            
            logger.info(f"[RSS] {source_name}: {len(feed_articles)} articles")
            articles.extend(feed_articles)
            
        except Exception as e:
            logger.error(f"[RSS] {source_name} failed: {type(e).__name__}: {e}")
    
    logger.info(f"[RSS] Total: {len(articles)} articles from RSS feeds")
    return articles


async def fetch_reddit() -> list[dict]:
    """Fetch from Reddit with detailed logging."""
    subreddits = [
        ("politics", "politics"),
        ("worldnews", "worldnews"),
        ("news", "general"),
        ("technology", "tech"),
        ("Bitcoin", "crypto"),
        ("ethereum", "crypto"),
        ("CryptoCurrency", "crypto"),
        ("artificial", "ai"),
        ("MachineLearning", "ai"),
        ("economy", "macro"),
        ("wallstreetbets", "markets"),
        ("stocks", "markets"),
        ("investing", "markets"),
    ]

    articles = []
    logger.info(f"[Reddit] Starting fetch from {len(subreddits)} subreddits")
    
    async with httpx.AsyncClient(timeout=15.0, headers={"User-Agent": "PIT-Terminal/1.0"}) as client:
        for subreddit, default_tag in subreddits:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                resp = await client.get(url)
                
                if resp.status_code == 429:
                    logger.warning(f"[Reddit] r/{subreddit}: RATE LIMITED (429)")
                    continue
                elif resp.status_code == 403:
                    logger.warning(f"[Reddit] r/{subreddit}: FORBIDDEN (403) - may be private")
                    continue
                elif resp.status_code != 200:
                    logger.warning(f"[Reddit] r/{subreddit}: HTTP {resp.status_code}")
                    continue
                
                data = resp.json()
                children = data.get("data", {}).get("children", [])
                subreddit_articles = []
                
                for child in children:
                    post = child.get("data", {})
                    title = post.get("title", "").strip()
                    permalink = post.get("permalink", "")
                    
                    if not title or not permalink:
                        continue
                    
                    subreddit_articles.append({
                        "title": title,
                        "url": f"https://reddit.com{permalink}",
                        "description": post.get("selftext", "")[:300],
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "source": {"name": "Reddit"},
                        "tags": _extract_tags(title) or [default_tag],
                    })
                
                logger.debug(f"[Reddit] r/{subreddit}: {len(subreddit_articles)} posts")
                articles.extend(subreddit_articles)
                
            except Exception as e:
                logger.warning(f"[Reddit] r/{subreddit}: {type(e).__name__}: {e}")

    logger.info(f"[Reddit] Total: {len(articles)} posts")
    return articles


async def fetch_hackernews() -> list[dict]:
    """Fetch from Hacker News with detailed logging."""
    articles = []
    logger.info("[HackerNews] Starting fetch")
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            top_resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            if top_resp.status_code != 200:
                logger.error(f"[HackerNews] Failed to get top stories: HTTP {top_resp.status_code}")
                return articles
            
            top_ids = top_resp.json()[:25]
            logger.debug(f"[HackerNews] Fetching {len(top_ids)} stories")
            
            for story_id in top_ids:
                try:
                    item_resp = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
                    if item_resp.status_code != 200:
                        continue
                    
                    item = item_resp.json()
                    if not item or item.get("type") != "story":
                        continue
                    
                    title = item.get("title", "")
                    url = item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                    
                    if not title:
                        continue
                    
                    articles.append({
                        "title": title,
                        "url": url,
                        "description": "",
                        "publishedAt": datetime.now(timezone.utc).isoformat(),
                        "source": {"name": "HackerNews"},
                        "tags": _extract_tags(title),
                    })
                except Exception as e:
                    logger.debug(f"[HackerNews] Story {story_id} failed: {e}")
                    
        except Exception as e:
            logger.error(f"[HackerNews] Failed: {type(e).__name__}: {e}")

    logger.info(f"[HackerNews] Total: {len(articles)} stories")
    return articles


async def ingest_news():
    """Main ingestion with comprehensive logging."""
    logger.info("=" * 60)
    logger.info("NEWS INGESTION START")
    logger.info("=" * 60)
    
    start_time = datetime.now(timezone.utc)
    
    # Fetch all sources
    logger.info("Fetching from all sources in parallel...")
    
    newsapi_articles = await fetch_newsapi()
    rss_articles = await fetch_rss_feeds()
    reddit_articles = await fetch_reddit()
    hn_articles = await fetch_hackernews()
    
    all_articles = newsapi_articles + rss_articles + reddit_articles + hn_articles
    
    # Log source breakdown
    source_counts = {}
    for art in all_articles:
        src = art.get("source", {}).get("name", "Unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
    
    logger.info("-" * 60)
    logger.info("SOURCE BREAKDOWN:")
    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        logger.info(f"  {src}: {count} articles")
    logger.info("-" * 60)
    
    # Deduplicate and store
    async with AsyncSessionLocal() as session:
        seen = set()
        new_count = 0
        duplicate_count = 0
        
        logger.info("Processing articles for database storage...")
        
        for art in all_articles:
            url = art.get("url", "")
            if not url:
                continue
            
            art_id = _hash_url(url)
            if art_id in seen:
                duplicate_count += 1
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
            new_count += 1
        
        await session.commit()
        
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info("=" * 60)
        logger.info("NEWS INGESTION COMPLETE")
        logger.info(f"  Total fetched: {len(all_articles)} articles")
        logger.info(f"  Duplicates skipped: {duplicate_count}")
        logger.info(f"  New articles stored: {new_count}")
        logger.info(f"  Duration: {duration:.1f}s")
        logger.info("=" * 60)
