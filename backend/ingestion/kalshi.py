import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database import AsyncSessionLocal
from models import Market, PricePoint

logger = logging.getLogger(__name__)

KALSHI_API = "https://external-api.kalshi.com/trade-api/v2"

# Map Kalshi categories to our taxonomy
CATEGORY_MAP = {
    "Elections": "politics",
    "Politics": "politics",
    "Financials": "macro",
    "Companies": "tech",
    "Science and Technology": "tech",
    "Climate and Weather": "macro",
    "World": "politics",
    "Social": "politics",
    "Sports": "sports",
    "Crypto": "crypto",
    "Economics": "macro",
    "Health": "other",
    "Entertainment": "other",
}

TAG_KEYWORDS = {
    "usa": ["usa", " us ", "america", "american", "trump", "biden", "harris",
            "congress", "senate", "white house", "gop", "democrat", "republican",
            "president", "presidential"],
    "europe": ["europe", "european", "eu ", "france", "germany", "spain", "uk",
               "britain", "italy", "netherlands", "romania"],
    "crypto": ["bitcoin", "btc", "crypto", "ethereum", "eth", "solana"],
    "ai": ["openai", "gpt", "ai ", "artificial intelligence", "llm", "anthropic"],
    "sports": ["world cup", "fifa", "nba", "nfl", "nhl", "olympics", "championship",
               "baseball", "basketball", "football", "soccer"],
    "fed": ["fed", "federal reserve", "rate cut", "interest rate", "inflation"],
    "tech": ["apple", "google", "microsoft", "meta", "amazon", "nvidia",
             "ipo", "spacex", "mars", "fusion"],
    "politics": ["election", "president", "nomination", "vote", "senator",
                 "prime minister", "netanyahu", "g7"],
    "japan": ["japan", "japanese", "tokyo"],
    "china": ["china", "chinese", "beijing", "xi jinping"],
}


def _kalshi_category_to_ours(kalshi_cat: str) -> str:
    return CATEGORY_MAP.get(kalshi_cat, "other")


def _infer_tags(title: str) -> list[str]:
    text = title.lower()
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    return tags or ["other"]


def _parse_probability(last_price: str | None, yes_bid: str | None) -> float:
    """Extract implied probability from Kalshi pricing."""
    try:
        if last_price:
            return float(last_price)
        if yes_bid:
            return float(yes_bid)
    except (ValueError, TypeError):
        pass
    return 0.5


def _parse_volume(vol: str | None) -> float:
    try:
        return float(vol) if vol is not None else 0
    except (ValueError, TypeError):
        return 0


def _parse_liquidity(open_interest: str | None) -> float:
    try:
        return float(open_interest) if open_interest is not None else 0
    except (ValueError, TypeError):
        return 0


def _parse_spread(yes_bid: str | None, yes_ask: str | None) -> float:
    try:
        bid = float(yes_bid) if yes_bid is not None else 0
        ask = float(yes_ask) if yes_ask is not None else 1
        return ask - bid if ask > bid else 0
    except (ValueError, TypeError):
        return 0


async def fetch_kalshi_events(limit: int = 100) -> list[dict]:
    """Fetch open events from Kalshi to get categories."""
    url = f"{KALSHI_API}/events"
    params = {"status": "open", "limit": limit}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("events", [])


async def fetch_kalshi_markets_for_event(event_ticker: str) -> list[dict]:
    """Fetch open markets for a specific Kalshi event."""
    url = f"{KALSHI_API}/markets"
    params = {"event_ticker": event_ticker, "status": "open", "limit": 50}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("markets", [])


def _is_interesting_market(m: dict) -> bool:
    """Filter out multivariate/combo markets and low-quality ones."""
    # Skip multivariate event markets (combo bets)
    if m.get("mve_collection_ticker"):
        return False
    # Skip markets with comma-separated titles (combo bets)
    title = m.get("title", "")
    if title.count(",") > 2:
        return False
    # Skip if no price data
    if not m.get("last_price_dollars") and not m.get("yes_bid_dollars"):
        return False
    return True


async def ingest_kalshi():
    logger.info("Fetching Kalshi events and markets...")

    # Fetch events first
    events = await fetch_kalshi_events(limit=200)
    logger.info(f"Fetched {len(events)} events from Kalshi API")

    # Filter to interesting categories (skip sports multivariate)
    interesting_events = []
    for evt in events:
        cat = evt.get("category", "")
        if cat in ("Sports",):
            continue
        interesting_events.append(evt)

    logger.info(f"Filtered to {len(interesting_events)} non-sports events")

    # Fetch markets for each event (with rate limiting)
    all_markets = []
    for i, evt in enumerate(interesting_events[:50]):  # Limit to avoid too many API calls
        try:
            markets = await fetch_kalshi_markets_for_event(evt.get("event_ticker", ""))
            for m in markets:
                m["_kalshi_category"] = evt.get("category", "")
            all_markets.extend(markets)
            # Rate limit: sleep 150ms between requests to stay under ~6 req/sec
            if i < len(interesting_events) - 1:
                await asyncio.sleep(0.15)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"[Kalshi] Rate limited on event {evt.get('event_ticker')}, backing off...")
                await asyncio.sleep(1.0)
            else:
                logger.debug(f"Failed to fetch markets for event {evt.get('event_ticker')}: {e}")
        except Exception as e:
            logger.debug(f"Failed to fetch markets for event {evt.get('event_ticker')}: {e}")

    logger.info(f"Fetched {len(all_markets)} total markets from events")

    # Filter interesting markets
    markets_data = [m for m in all_markets if _is_interesting_market(m)]
    logger.info(f"Filtered to {len(markets_data)} interesting markets")

    async with AsyncSessionLocal() as session:
        ingested = 0
        for m in markets_data:
            ticker = m.get("ticker")
            if not ticker:
                continue

            title = m.get("title", "")
            if not title:
                continue

            # Get category from parent event
            kalshi_cat = m.get("_kalshi_category", "")
            category = _kalshi_category_to_ours(kalshi_cat)

            # Override with title-based inference for better accuracy
            text = title.lower()
            for cat, keywords in [
                ("sports", ["nba", "nfl", "mlb", "nhl", "soccer", "football", "basketball",
                           "world cup", "olympics", "championship", "game", "points", "win"]),
                ("crypto", ["bitcoin", "btc", "crypto", "ethereum", "eth"]),
                ("macro", ["fed", "rate", "inflation", "recession", "gdp", "economy"]),
                ("tech", ["ai", "openai", "apple", "google", "ipo", "mars", "fusion"]),
                ("politics", ["election", "president", "trump", "biden", "vote",
                              "minister", "senate", "congress"]),
            ]:
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            tags = _infer_tags(title)

            probability = _parse_probability(
                m.get("last_price_dollars"),
                m.get("yes_bid_dollars")
            )
            volume = _parse_volume(m.get("volume_fp"))
            liquidity = _parse_liquidity(m.get("open_interest_fp"))
            spread = _parse_spread(m.get("yes_bid_dollars"), m.get("yes_ask_dollars"))
            resolution_date = m.get("expiration_time", "")

            # Calculate recent movement from previous price point
            prev_result = await session.execute(
                select(PricePoint)
                .where(PricePoint.market_id == f"kalshi-{ticker}")
                .order_by(PricePoint.timestamp.desc())
                .limit(1)
            )
            prev_point = prev_result.scalar_one_or_none()
            recent_movement = round(probability - prev_point.probability, 4) if prev_point else 0

            market_id = f"kalshi-{ticker}"

            stmt = insert(Market).values(
                id=market_id,
                title=title,
                category=category,
                probability=probability,
                volume=volume,
                liquidity=liquidity,
                spread=spread,
                recent_movement=recent_movement,
                resolution_date=resolution_date,
                source="Kalshi",
                tags=tags,
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "title": title,
                    "category": category,
                    "probability": probability,
                    "volume": volume,
                    "liquidity": liquidity,
                    "spread": spread,
                    "recent_movement": recent_movement,
                    "resolution_date": resolution_date,
                    "tags": tags,
                    "updated_at": datetime.now(timezone.utc),
                },
            )
            await session.execute(stmt)

            price_point = PricePoint(
                market_id=market_id,
                probability=probability,
                volume=volume,
            )
            session.add(price_point)
            ingested += 1

        await session.commit()
    logger.info(f"Kalshi ingestion complete: {ingested} markets upserted")
