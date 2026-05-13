from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from database import get_db
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
