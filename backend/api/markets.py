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

        # Seed markets
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

        # Seed news items
        news_items = [
            NewsItem(id="news-001", headline="Japan LDP faction leaders hold emergency meeting on election timing", source="Nikkei", credibility=0.92, published_at=now, tags=["japan", "politics", "election"], summary="Senior LDP members discussed snap election scenarios as approval ratings drop.", market_impact="Elevates probability of snap election call"),
            NewsItem(id="news-002", headline="US Core PCE rises 0.2% month-over-month, slightly above expectations", source="Bloomberg", credibility=0.94, published_at=now, tags=["usa", "macro", "inflation", "fed"], summary="The Fed's preferred inflation gauge showed sticky price pressures.", market_impact="May reduce likelihood of aggressive rate cuts"),
            NewsItem(id="news-003", headline="OpenAI unveils o1 reasoning model, says GPT-5 not on 2024 roadmap", source="The Verge", credibility=0.88, published_at=now, tags=["tech", "openai", "ai"], summary="CEO Sam Altman emphasized focus on reasoning capabilities.", market_impact="Strong signal against GPT-5 in 2024"),
            NewsItem(id="news-004", headline="Bitcoin ETF weekly inflows hit $1.2B, largest since launch", source="Reuters", credibility=0.91, published_at=now, tags=["crypto", "bitcoin", "etf"], summary="Institutional demand for spot Bitcoin ETFs surged.", market_impact="Supports bullish Bitcoin price trajectory"),
            NewsItem(id="news-005", headline="Ukraine-Russia prisoner exchange falls through after ceasefire talks stall", source="AP", credibility=0.93, published_at=now, tags=["ukraine", "russia", "war"], summary="Diplomatic channels remain strained.", market_impact="Reduces near-term ceasefire probability"),
        ]
        for n in news_items:
            stmt = insert(NewsItem).values(
                id=n.id, headline=n.headline, source=n.source, credibility=n.credibility,
                published_at=n.published_at, tags=n.tags, summary=n.summary, market_impact=n.market_impact,
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "headline": n.headline, "source": n.source, "credibility": n.credibility,
                    "published_at": n.published_at, "tags": n.tags, "summary": n.summary,
                    "market_impact": n.market_impact,
                },
            )
            await session.execute(stmt)

        # Seed opportunities
        opportunities = [
            Opportunity(
                id="opp-will-trump-win-2024", market_id="will-trump-win-2024",
                market_title="Will Trump win the 2024 US Presidential Election?",
                category="politics", market_probability=0.52,
                ai_estimated_low=0.48, ai_estimated_high=0.62,
                confidence_score=65.0, divergence_type="undervalued",
                signals=[{"type": "news", "label": "Polling Shift", "description": "Swing state polls tightening", "strength": 0.82, "source": "CNN"},
                         {"type": "sentiment", "label": "Narrative Velocity", "description": "Political discourse accelerating", "strength": 0.71}],
            ),
            Opportunity(
                id="opp-fed-rate-cut-july", market_id="fed-rate-cut-july",
                market_title="Will the Fed cut rates in July 2024?",
                category="macro", market_probability=0.78,
                ai_estimated_low=0.55, ai_estimated_high=0.68,
                confidence_score=58.0, divergence_type="overvalued",
                signals=[{"type": "news", "label": "Contradictory Signal", "description": "Core PCE reaccelerated slightly", "strength": 0.68, "source": "Bloomberg"},
                         {"type": "cross_market", "label": "SOFR Disagreement", "description": "Futures implying lower odds", "strength": 0.71}],
            ),
            Opportunity(
                id="opp-btc-above-100k-2024", market_id="btc-above-100k-2024",
                market_title="Will Bitcoin close above $100K in 2024?",
                category="crypto", market_probability=0.35,
                ai_estimated_low=0.38, ai_estimated_high=0.52,
                confidence_score=72.0, divergence_type="undervalued",
                signals=[{"type": "cross_market", "label": "Options Skew", "description": "Deribit calls pricing higher probability", "strength": 0.74},
                         {"type": "sentiment", "label": "Institutional Inflows", "description": "ETF weekly inflows at record highs", "strength": 0.69}],
            ),
            Opportunity(
                id="opp-openai-ipo-2024", market_id="openai-ipo-2024",
                market_title="Will OpenAI IPO in 2024?",
                category="tech", market_probability=0.18,
                ai_estimated_low=0.08, ai_estimated_high=0.15,
                confidence_score=68.0, divergence_type="overvalued",
                signals=[{"type": "news", "label": "Direct Statement", "description": "Altman explicitly ruled out IPO in 2024", "strength": 0.91, "source": "The Verge"},
                         {"type": "narrative", "label": "Hype Decay", "description": "Social volume on OpenAI IPO declining", "strength": 0.63}],
            ),
        ]
        for o in opportunities:
            stmt = insert(Opportunity).values(
                id=o.id, market_id=o.market_id, market_title=o.market_title, category=o.category,
                market_probability=o.market_probability, ai_estimated_low=o.ai_estimated_low,
                ai_estimated_high=o.ai_estimated_high, confidence_score=o.confidence_score,
                divergence_type=o.divergence_type, signals=o.signals, created_at=now,
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "market_title": o.market_title, "category": o.category,
                    "market_probability": o.market_probability, "ai_estimated_low": o.ai_estimated_low,
                    "ai_estimated_high": o.ai_estimated_high, "confidence_score": o.confidence_score,
                    "divergence_type": o.divergence_type, "signals": o.signals, "created_at": now,
                },
            )
            await session.execute(stmt)

        # Seed narrative shifts
        narratives = [
            NarrativeShift(
                id="nar-japan-election", topic="Japan Snap Election", category="politics",
                previous_sentiment=0.28, current_sentiment=0.54, velocity=0.82,
                attention_spike=3.4, sources=14, last_updated=now,
                markets_affected=["japan-ldp-election"],
            ),
            NarrativeShift(
                id="nar-fed-rates", topic="Fed Rate Cut Consensus", category="macro",
                previous_sentiment=0.62, current_sentiment=0.71, velocity=0.45,
                attention_spike=1.2, sources=38, last_updated=now,
                markets_affected=["fed-rate-cut-july"],
            ),
            NarrativeShift(
                id="nar-btc-adoption", topic="Bitcoin Institutional Adoption", category="crypto",
                previous_sentiment=0.48, current_sentiment=0.63, velocity=0.71,
                attention_spike=2.8, sources=27, last_updated=now,
                markets_affected=["btc-above-100k-2024"],
            ),
            NarrativeShift(
                id="nar-ukraine-war", topic="Ukraine War Fatigue", category="politics",
                previous_sentiment=0.41, current_sentiment=0.33, velocity=0.38,
                attention_spike=0.9, sources=22, last_updated=now,
                markets_affected=["ukraine-ceasefire-2024"],
            ),
            NarrativeShift(
                id="nar-ai-releases", topic="AI Model Release Cycle", category="tech",
                previous_sentiment=0.58, current_sentiment=0.44, velocity=0.67,
                attention_spike=2.1, sources=19, last_updated=now,
                markets_affected=["openai-ipo-2024"],
            ),
        ]
        for n in narratives:
            stmt = insert(NarrativeShift).values(
                id=n.id, topic=n.topic, category=n.category,
                previous_sentiment=n.previous_sentiment, current_sentiment=n.current_sentiment,
                velocity=n.velocity, attention_spike=n.attention_spike, sources=n.sources,
                last_updated=n.last_updated, markets_affected=n.markets_affected,
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "topic": n.topic, "category": n.category,
                    "previous_sentiment": n.previous_sentiment, "current_sentiment": n.current_sentiment,
                    "velocity": n.velocity, "attention_spike": n.attention_spike,
                    "sources": n.sources, "last_updated": n.last_updated,
                },
            )
            await session.execute(stmt)

        await session.commit()
    return {"ok": True, "seeded_markets": len(markets), "seeded_news": len(news_items), "seeded_opportunities": len(opportunities), "seeded_narratives": len(narratives)}


@router.get("/cross-market")
async def list_cross_market(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Market).order_by(desc(Market.volume)).limit(50))
        markets = result.scalars().all()

        # Group markets by category for synthetic cross-market comparisons
        from collections import defaultdict
        by_category = defaultdict(list)
        for m in markets:
            by_category[m.category].append(m)

        comparisons = []
        for cat, cat_markets in by_category.items():
            if len(cat_markets) < 2:
                continue
            # Pick top 2-3 markets in category
            selected = cat_markets[:3]
            max_prob = max(m.probability for m in selected)
            min_prob = min(m.probability for m in selected)
            disagreement = abs(max_prob - min_prob)

            comparisons.append({
                "event_title": f"{cat.title()} markets",
                "markets": [
                    {
                        "source": m.source,
                        "probability": m.probability,
                        "volume": m.volume,
                        "updated_at": m.updated_at.isoformat() if m.updated_at else datetime.now(timezone.utc).isoformat(),
                    }
                    for m in selected
                ],
                "disagreement_score": round(disagreement, 3),
                "arbitrage_hint": f"{len(selected)} active markets in {cat}" if disagreement > 0.1 else None,
            })

        # Also add a hardcoded-style comparison for popular events if we have the data
        trump_markets = [m for m in markets if "trump" in m.title.lower()]
        if len(trump_markets) >= 1:
            comparisons.insert(0, {
                "event_title": "Trump-related prediction markets",
                "markets": [
                    {"source": m.source, "probability": m.probability, "volume": m.volume, "updated_at": m.updated_at.isoformat() if m.updated_at else datetime.now(timezone.utc).isoformat()}
                    for m in trump_markets[:3]
                ],
                "disagreement_score": round(abs(max(m.probability for m in trump_markets) - min(m.probability for m in trump_markets)), 3) if len(trump_markets) > 1 else 0.05,
                "arbitrage_hint": "Multiple Trump events tracked" if len(trump_markets) > 1 else None,
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
