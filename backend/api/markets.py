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
    """Run live ingestion instead of inserting hardcoded demo data."""
    from ingestion.polymarket import ingest_polymarket
    from ingestion.news import ingest_news
    from ai.opportunity_engine import run_opportunity_engine
    await ingest_polymarket()
    await ingest_news()
    await run_opportunity_engine()
    return {"ok": True, "message": "Live ingestion complete. No demo data was inserted."}


@router.post("/clear-seed")
async def clear_seed_data():
    """Remove old hardcoded seed data that looks like mock data."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import delete
        # Delete old seeded markets (the 8 hardcoded ones from the original seed)
        old_market_ids = [
            "will-trump-win-2024", "fed-rate-cut-july", "btc-above-100k-2024",
            "openai-ipo-2024", "olympics-usa-gold", "ukraine-ceasefire-2024",
            "japan-ldp-election", "eth-etf-approved"
        ]
        await session.execute(delete(Market).where(Market.id.in_(old_market_ids)))
        await session.execute(delete(PricePoint).where(PricePoint.market_id.in_(old_market_ids)))

        # Delete old seeded opportunities
        old_opp_ids = [
            "opp-will-trump-win-2024", "opp-fed-rate-cut-july",
            "opp-btc-above-100k-2024", "opp-openai-ipo-2024"
        ]
        await session.execute(delete(Opportunity).where(Opportunity.id.in_(old_opp_ids)))

        # Delete old seeded narratives
        old_nar_ids = [
            "nar-japan-election", "nar-fed-rates", "nar-btc-adoption",
            "nar-ukraine-war", "nar-ai-releases"
        ]
        await session.execute(delete(NarrativeShift).where(NarrativeShift.id.in_(old_nar_ids)))

        # Delete old seeded news
        old_news_ids = ["news-001", "news-002", "news-003", "news-004", "news-005"]
        await session.execute(delete(NewsItem).where(NewsItem.id.in_(old_news_ids)))

        await session.commit()
    return {"ok": True, "message": "Old seed data cleared. Live data will repopulate on next ingestion cycle."}


@router.get("/cross-market")
async def list_cross_market(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Market).order_by(desc(Market.volume)).limit(100))
        markets = result.scalars().all()

        # Find related markets by keyword overlap in titles
        def _keywords(title: str) -> set[str]:
            words = title.lower().replace("?", "").replace(".", "").split()
            # Filter out common stop words
            stops = {"will", "the", "a", "an", "in", "on", "at", "by", "to", "of", "for", "be", "is", "are", "before", "end", "year", "2024", "2025", "2026", "2027", "2028"}
            return {w for w in words if len(w) > 2 and w not in stops}

        def _relatedness(m1: Market, m2: Market) -> float:
            k1 = _keywords(m1.title)
            k2 = _keywords(m2.title)
            if not k1 or not k2:
                return 0.0
            intersection = k1 & k2
            union = k1 | k2
            return len(intersection) / len(union) if union else 0.0

        # Build clusters of related markets
        clusters = []
        used = set()
        for i, m1 in enumerate(markets):
            if m1.id in used:
                continue
            cluster = [m1]
            used.add(m1.id)
            for m2 in markets[i + 1:]:
                if m2.id in used:
                    continue
                if _relatedness(m1, m2) >= 0.3:  # At least 30% keyword overlap
                    cluster.append(m2)
                    used.add(m2.id)
            if len(cluster) >= 2:
                clusters.append(cluster)

        comparisons = []
        for cluster in clusters[:10]:
            max_prob = max(m.probability for m in cluster)
            min_prob = min(m.probability for m in cluster)
            disagreement = abs(max_prob - min_prob)

            # Generate event title from common keywords
            common = _keywords(cluster[0].title)
            for m in cluster[1:]:
                common &= _keywords(m.title)
            event_title = " ".join(sorted(common)).title() if common else cluster[0].title[:60]

            comparisons.append({
                "event_title": event_title,
                "markets": [
                    {
                        "source": m.source,
                        "probability": m.probability,
                        "volume": m.volume,
                        "updated_at": m.updated_at.isoformat() if m.updated_at else datetime.now(timezone.utc).isoformat(),
                    }
                    for m in sorted(cluster, key=lambda x: x.volume, reverse=True)[:4]
                ],
                "disagreement_score": round(disagreement, 3),
                "arbitrage_hint": f"Related markets diverge by {(disagreement * 100):.0f}pts" if disagreement > 0.05 else None,
            })

        # Fallback: category-based groupings if no keyword clusters found
        if not comparisons:
            from collections import defaultdict
            by_category = defaultdict(list)
            for m in markets:
                by_category[m.category].append(m)
            for cat, cat_markets in by_category.items():
                if len(cat_markets) < 2:
                    continue
                selected = cat_markets[:3]
                max_prob = max(m.probability for m in selected)
                min_prob = min(m.probability for m in selected)
                disagreement = abs(max_prob - min_prob)
                comparisons.append({
                    "event_title": f"{cat.title()} markets",
                    "markets": [
                        {"source": m.source, "probability": m.probability, "volume": m.volume, "updated_at": m.updated_at.isoformat() if m.updated_at else datetime.now(timezone.utc).isoformat()}
                        for m in selected
                    ],
                    "disagreement_score": round(disagreement, 3),
                    "arbitrage_hint": f"{len(selected)} markets in {cat}" if disagreement > 0.05 else None,
                })

        return comparisons
    except Exception:
        return []


@router.get("/debug/network")
async def debug_network():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=1")
            return {"ok": True, "status": resp.status_code, "has_data": len(resp.json()) > 0 if resp.status_code == 200 else False}
    except Exception as e:
        return {"ok": False, "error": str(e)}
