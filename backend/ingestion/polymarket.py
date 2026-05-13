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

GAMMA_API = "https://gamma-api.polymarket.com"

CATEGORY_MAP = {
    "politics": ["politics", "us politics", "elections", "world politics", "government", "trump", "biden", "presidential", "democratic", "republican", "nomination", "senate", "congress", "house", "vote", "pm", "minister"],
    "macro": ["economics", "finance", "markets", "fed", "recession", "inflation", "rates", "gdp", "unemployment", "cpi", "ppi"],
    "tech": ["technology", "ai", "artificial intelligence", "openai", "apple", "google", "microsoft", "gpt", "llm", "model"],
    "crypto": ["crypto", "bitcoin", "ethereum", "btc", "eth", "cryptocurrency", "blockchain", "etf", "solana"],
    "sports": ["sports", "world cup", "olympics", "nba", "nfl", "mlb", "soccer", "football", "basketball"],
}

TAG_KEYWORDS = {
    "usa": ["usa", "us ", "america", "american", "trump", "biden"],
    "japan": ["japan", "japanese", "tokyo"],
    "ukraine": ["ukraine", "russia", "putin"],
    "fed": ["fed", "federal reserve", "rate cut", "interest rate"],
    "crypto": ["bitcoin", "btc", "crypto", "ethereum"],
    "ai": ["openai", "gpt", "ai", "artificial intelligence", "llm"],
    "tech": ["apple", "google", "microsoft", "meta"],
    "sports": ["world cup", "olympics", "nba", "nfl"],
}


def _infer_tags(question: str) -> list[str]:
    text = question.lower()
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    return tags


def _infer_category(tags: list[str], question: str) -> str:
    text = " ".join(tags + [question]).lower()
    for cat, keywords in CATEGORY_MAP.items():
        if any(kw in text for kw in keywords):
            return cat
    return "other"


def _parse_probability(outcome_prices: Any) -> float:
    try:
        if isinstance(outcome_prices, str):
            prices = json.loads(outcome_prices)
        else:
            prices = outcome_prices
        if isinstance(prices, dict):
            yes_price = prices.get("Yes") or prices.get("yes")
            if yes_price is not None:
                return float(yes_price)
        if isinstance(prices, list) and len(prices) > 0:
            return float(prices[0])
    except Exception:
        pass
    return 0.5


def _parse_volume(vol: Any) -> float:
    try:
        return float(vol) if vol is not None else 0
    except (ValueError, TypeError):
        return 0


def _parse_liquidity(liq: Any) -> float:
    try:
        return float(liq) if liq is not None else 0
    except (ValueError, TypeError):
        return 0


def _parse_spread(best_bid: Any, best_ask: Any) -> float:
    try:
        bid = float(best_bid) if best_bid is not None else 0
        ask = float(best_ask) if best_ask is not None else 1
        return ask - bid if ask > bid else 0
    except (ValueError, TypeError):
        return 0


async def fetch_markets(limit: int = 100) -> list[dict]:
    url = f"{GAMMA_API}/markets"
    params = {"active": "true", "closed": "false", "limit": limit}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        # Gamma API sometimes returns dict with markets key, sometimes list
        if isinstance(data, dict):
            return data.get("markets", [])
        return data


async def ingest_polymarket():
    logger.info("Fetching Polymarket markets...")
    markets_data = await fetch_markets(limit=100)
    logger.info(f"Fetched {len(markets_data)} markets")

    async with AsyncSessionLocal() as session:
        for m in markets_data:
            slug = m.get("slug") or m.get("id")
            if not slug:
                continue

            question = m.get("question", "")
            api_tags = m.get("tags", []) or []
            tags = api_tags if api_tags else _infer_tags(question)
            category = _infer_category(tags, question)

            probability = _parse_probability(m.get("outcomePrices"))
            volume = _parse_volume(m.get("volume"))
            liquidity = _parse_liquidity(m.get("liquidity"))
            spread = _parse_spread(m.get("bestBid"), m.get("bestAsk"))
            resolution_date = m.get("endDate")

            # Calculate recent movement from previous price point
            prev_result = await session.execute(
                select(PricePoint)
                .where(PricePoint.market_id == slug)
                .order_by(PricePoint.timestamp.desc())
                .limit(1)
            )
            prev_point = prev_result.scalar_one_or_none()
            recent_movement = probability - prev_point.probability if prev_point else 0

            # Upsert market
            stmt = insert(Market).values(
                id=slug,
                title=question,
                category=category,
                probability=probability,
                volume=volume,
                liquidity=liquidity,
                spread=spread,
                recent_movement=recent_movement,
                resolution_date=resolution_date,
                source="Polymarket",
                tags=tags,
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "title": question,
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

            # Insert price point
            price_point = PricePoint(
                market_id=slug,
                probability=probability,
                volume=volume,
            )
            session.add(price_point)

        await session.commit()
    logger.info("Polymarket ingestion complete")
