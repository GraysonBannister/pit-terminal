from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
import httpx

from database import AsyncSessionLocal, get_db
from models import Market, Opportunity, NarrativeShift, NewsItem, PricePoint

router = APIRouter()


def _serialize(obj) -> dict:
    """Serialize SQLAlchemy model instance to JSON-safe dict."""
    data = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        elif isinstance(val, UUID):
            val = str(val)
        data[col.name] = val
    return data


@router.get("/markets")
async def list_markets(
    category: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Market).order_by(desc(Market.volume))
        if category:
            query = query.where(Market.category == category)
        result = await db.execute(query.limit(limit))
        markets = result.scalars().all()
        return [_serialize(m) for m in markets]
    except Exception:
        return []


@router.get("/markets/{market_id}")
async def get_market(market_id: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Market).where(Market.id == market_id))
        market = result.scalar_one_or_none()
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        price_result = await db.execute(
            select(PricePoint)
            .where(PricePoint.market_id == market_id)
            .order_by(desc(PricePoint.timestamp))
            .limit(100)
        )
        prices = price_result.scalars().all()

        data = _serialize(market)
        data["price_history"] = [
            {
                "timestamp": p.timestamp.isoformat(),
                "probability": p.probability,
                "volume": p.volume,
            }
            for p in reversed(prices)
        ]
        return data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.get("/opportunities")
async def list_opportunities(
    category: Optional[str] = None,
    min_confidence: float = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(Opportunity).order_by(desc(Opportunity.confidence_score))
        if category:
            query = query.where(Opportunity.category == category)
        if min_confidence > 0:
            query = query.where(Opportunity.confidence_score >= min_confidence)
        result = await db.execute(query.limit(limit))
        ops = result.scalars().all()
        return [_serialize(o) for o in ops]
    except Exception:
        return []


@router.get("/narratives")
async def list_narratives(
    category: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(NarrativeShift).order_by(desc(NarrativeShift.velocity))
        if category:
            query = query.where(NarrativeShift.category == category)
        result = await db.execute(query.limit(limit))
        nar = result.scalars().all()
        return [_serialize(n) for n in nar]
    except Exception:
        return []


@router.get("/news")
async def list_news(
    tag: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(NewsItem).order_by(desc(NewsItem.published_at))
        result = await db.execute(query.limit(limit * 2))
        items = result.scalars().all()
        if tag:
            items = [i for i in items if tag in (i.tags or [])]
        return [_serialize(i) for i in items[:limit]]
    except Exception:
        return []


@router.post("/seed")
async def seed_data():
    async with AsyncSessionLocal() as session:
        now = datetime.now(timezone.utc)
        markets = [
            Market(id="will-trump-win-2024", title="Will Trump win the 2024 US Presidential Election?", category="politics", probability=0.52, volume=4500000, liquidity=1200000, spread=0.01, recent_movement=0.03, resolution_date="2024-11-05", source="Polymarket", tags=["usa", "politics", "trump"]),
            Market(id="fed-rate-cut-july", title="Will the Fed cut rates in July 2024?", category="macro", probability=0.78, volume=2100000, liquidity=800000, spread=0.02, recent_movement=-0.05, resolution_date="2024-07-31", source="Polymarket", tags=["fed", "macro", "usa"]),
            Market(id="btc-above-100k-2024", title="Will Bitcoin close above $100K in 2024?", category="crypto", probability=0.35, volume=3200000, liquidity=950000, spread=0.03, recent_movement=0.08, resolution_date="2024-12-31", source="Polymarket", tags=["crypto", "bitcoin"]),
            Market(id="openai-ipo-2024", title="Will OpenAI IPO in 2024?", category="tech", probability=0.18, volume=890000, liquidity=300000, spread=0.04, recent_movement=0.02, resolution_date="2024-12-31", source="Polymarket", tags=["ai", "tech", "openai"]),
            Market(id="olympics-usa-gold", title="Will USA win the most gold medals at Paris 2024?", category="sports", probability=0.62, volume=1200000, liquidity=400000, spread=0.02, recent_movement=-0.01, resolution_date="2024-08-11", source="Polymarket", tags=["sports", "usa"]),
            Market(id="ukraine-ceasefire-2024", title="Will there be a ceasefire in Ukraine by end of 2024?", category="politics", probability=0.28, volume=1500000, liquidity=500000, spread=0.03, recent_movement=-0.04, resolution_date="2024-12-31", source="Polymarket", tags=["ukraine", "politics"]),
            Market(id="japan-ldp-election", title="Will LDP lose majority in Japan snap election?", category="politics", probability=0.44, volume=600000, liquidity=200000, spread=0.03, recent_movement=0.06, resolution_date="2024-10-27", source="Polymarket", tags=["japan", "politics"]),
            Market(id="eth-etf-approved", title="Will Ethereum spot ETF be approved in 2024?", category="crypto", probability=0.71, volume=1800000, liquidity=700000, spread=0.02, recent_movement=0.01, resolution_date="2024-12-31", source="Polymarket", tags=["crypto", "ethereum"]),
        ]
        for m in markets:
            stmt = insert(Market).values(
                id=m.id, title=m.title, category=m.category, probability=m.probability,
                volume=m.volume, liquidity=m.liquidity, spread=m.spread,
                recent_movement=m.recent_movement, resolution_date=m.resolution_date,
                source=m.source, tags=m.tags,
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "title": m.title, "category": m.category, "probability": m.probability,
                    "volume": m.volume, "liquidity": m.liquidity, "spread": m.spread,
                    "recent_movement": m.recent_movement, "resolution_date": m.resolution_date,
                    "tags": m.tags, "updated_at": now,
                },
            )
            await session.execute(stmt)
            pp = PricePoint(market_id=m.id, probability=m.probability, volume=m.volume)
            session.add(pp)

        await session.commit()
    return {"ok": True, "seeded": len(markets)}


@router.get("/debug/network")
async def debug_network():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=1")
            return {"ok": True, "status": resp.status_code, "has_data": len(resp.json()) > 0 if resp.status_code == 200 else False}
    except Exception as e:
        return {"ok": False, "error": str(e)}
