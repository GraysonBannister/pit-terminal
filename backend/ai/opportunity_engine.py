import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select, desc, func
from sqlalchemy.dialects.postgresql import insert

from database import AsyncSessionLocal
from models import Market, NewsItem, Opportunity, NarrativeShift
from ai.summarizer import generate_market_summary
from ai.sentiment import analyze_sentiment

logger = logging.getLogger(__name__)

# Weights for opportunity scoring
WEIGHTS = {
    "divergence": 0.30,
    "narrative_acceleration": 0.20,
    "liquidity_weakness": 0.15,
    "spread_inefficiency": 0.15,
    "recent_movement": 0.10,
    "news_signal": 0.10,
}

MIN_CONFIDENCE_THRESHOLD = 20.0
MAX_OPPORTUNITIES = 20


def _normalize_liquidity(liquidity: float) -> float:
    return max(0.0, min(1.0, 1.0 - (liquidity / 500_000)))


def _normalize_spread(spread: float) -> float:
    return max(0.0, min(1.0, spread * 50))


def _calculate_news_signal(news_items: list[NewsItem]) -> float:
    if not news_items:
        return 0.0
    total = 0.0
    now = datetime.now(timezone.utc)
    for item in news_items:
        published = item.published_at
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        age_hours = (now - published).total_seconds() / 3600
        recency_weight = max(0.1, 1.0 - (age_hours / 48))
        total += item.credibility * recency_weight
    return max(0.0, min(1.0, total / len(news_items)))


def _adjusted_probability(market_prob: float, sentiment: dict) -> float:
    confidence = sentiment.get("confidence", 0.5)
    uncertainty = sentiment.get("uncertainty", 0.5)
    sentiment_factor = (confidence - uncertainty) * 0.15
    adjusted = market_prob + sentiment_factor
    return max(0.02, min(0.98, adjusted))


def _divergence_type(market_prob: float, adjusted_prob: float) -> str:
    diff = adjusted_prob - market_prob
    if diff > 0.05:
        return "undervalued"
    elif diff < -0.05:
        return "overvalued"
    return "disagreement"


def _build_signals(
    divergence_score: float,
    narrative_velocity: float,
    liquidity_weakness: float,
    spread_score: float,
    news_signal: float,
    recent_news: list[NewsItem],
) -> list[dict]:
    signals = []

    if divergence_score > 0.3:
        signals.append({
            "type": "sentiment",
            "label": "Sentiment Divergence",
            "description": "News sentiment direction differs from market pricing",
            "strength": min(1.0, divergence_score),
        })

    if narrative_velocity > 0.5:
        signals.append({
            "type": "narrative",
            "label": "Narrative Velocity Spike",
            "description": "Narrative shifting faster than baseline",
            "strength": narrative_velocity,
        })

    if liquidity_weakness > 0.5:
        signals.append({
            "type": "liquidity",
            "label": "Thin Liquidity",
            "description": "Low liquidity may suppress price discovery",
            "strength": liquidity_weakness,
        })

    if spread_score > 0.3:
        signals.append({
            "type": "cross_market",
            "label": "Wide Spread",
            "description": "Bid-ask spread indicates poor price discovery",
            "strength": spread_score,
        })

    # Add top news signal
    top_news = [n for n in recent_news if n.credibility > 0.8][:1]
    if top_news:
        signals.append({
            "type": "news",
            "label": "Credible Signal",
            "description": top_news[0].headline[:80],
            "strength": top_news[0].credibility,
            "source": top_news[0].source,
        })

    return signals


async def run_opportunity_engine():
    logger.info("Running opportunity engine...")

    async with AsyncSessionLocal() as session:
        # Fetch active markets with volume > 0
        result = await session.execute(
            select(Market)
            .where(Market.volume > 0)
            .order_by(desc(Market.volume))
            .limit(50)
        )
        markets = result.scalars().all()

        # Fetch recent news (last 48h) — but don't require it
        cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
        news_result = await session.execute(
            select(NewsItem)
            .where(NewsItem.published_at >= cutoff)
            .order_by(desc(NewsItem.published_at))
            .limit(100)
        )
        all_news = news_result.scalars().all()

        opportunities_created = 0

        for market in markets:
            market_tags = set(market.tags or [])
            news_items = [
                n for n in all_news
                if market_tags.intersection(set(n.tags or []))
            ][:10]

            # Fallback: match by category keywords in headline
            if not news_items:
                category_keywords = {
                    "politics": ["election", "trump", "biden", "vote", "president", "minister", "pm"],
                    "macro": ["fed", "rate", "inflation", "recession", "economy", "gdp"],
                    "tech": ["ai", "openai", "apple", "google", "gpt", "model"],
                    "crypto": ["bitcoin", "btc", "crypto", "ethereum", "etf"],
                    "sports": ["world cup", "olympics", "nba", "nfl", "soccer"],
                }
                keywords = category_keywords.get(market.category, [])
                news_items = [
                    n for n in all_news
                    if any(kw in (n.headline or "").lower() for kw in keywords)
                ][:10]

            # Run AI analysis if OpenAI key is available, else use heuristics
            news_dicts = [
                {"headline": n.headline, "source": n.source, "summary": n.summary}
                for n in news_items
            ]

            if news_dicts:
                sentiment = await analyze_sentiment(news_dicts)
                summary = await generate_market_summary(
                    market_title=market.title,
                    recent_news=news_dicts,
                    current_probability=market.probability,
                    recent_movement=market.recent_movement,
                )
            else:
                # Heuristic sentiment when no news available
                sentiment = {
                    "confidence": 0.5,
                    "uncertainty": 0.5,
                    "polarization": 0.5,
                    "narrative_velocity": 0.5,
                }
                summary = None

            # Update market with AI outputs
            market.ai_summary = summary or market.ai_summary
            market.sentiment = sentiment

            # Calculate scores
            adjusted_prob = _adjusted_probability(market.probability, sentiment)
            divergence = abs(adjusted_prob - market.probability)
            divergence_score = min(1.0, divergence * 3)

            narrative_velocity = sentiment.get("narrative_velocity", 0.5)
            liquidity_weakness = _normalize_liquidity(market.liquidity)
            spread_score = _normalize_spread(market.spread)
            news_signal = _calculate_news_signal(news_items)
            movement_score = min(1.0, abs(market.recent_movement) * 5)

            # Weighted confidence score (0-100)
            confidence = (
                divergence_score * WEIGHTS["divergence"] +
                narrative_velocity * WEIGHTS["narrative_acceleration"] +
                liquidity_weakness * WEIGHTS["liquidity_weakness"] +
                spread_score * WEIGHTS["spread_inefficiency"] +
                movement_score * WEIGHTS["recent_movement"] +
                news_signal * WEIGHTS["news_signal"]
            ) * 100

            # BOOST: if no news but market has interesting characteristics, still create opportunity
            if not news_items and confidence < MIN_CONFIDENCE_THRESHOLD:
                # Pure market-data-driven scoring
                pure_score = (
                    (liquidity_weakness * 0.3) +
                    (spread_score * 0.3) +
                    (movement_score * 0.25) +
                    (min(1.0, market.volume / 5_000_000) * 0.15)
                ) * 100
                if pure_score >= MIN_CONFIDENCE_THRESHOLD:
                    confidence = pure_score
                    divergence_score = 0.2
                    narrative_velocity = 0.3

            if confidence < MIN_CONFIDENCE_THRESHOLD:
                continue

            div_type = _divergence_type(market.probability, adjusted_prob)
            signals = _build_signals(
                divergence_score, narrative_velocity,
                liquidity_weakness, spread_score, news_signal, news_items,
            )

            # Build AI estimated range
            uncertainty = sentiment.get("uncertainty", 0.3)
            low = max(0.02, adjusted_prob - uncertainty * 0.3)
            high = min(0.98, adjusted_prob + uncertainty * 0.3)

            opp_id = f"opp-{market.id}"
            stmt = insert(Opportunity).values(
                id=opp_id,
                market_id=market.id,
                market_title=market.title,
                category=market.category,
                market_probability=market.probability,
                ai_estimated_low=low,
                ai_estimated_high=high,
                confidence_score=round(confidence, 1),
                divergence_type=div_type,
                signals=signals,
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "market_title": market.title,
                    "category": market.category,
                    "market_probability": market.probability,
                    "ai_estimated_low": low,
                    "ai_estimated_high": high,
                    "confidence_score": round(confidence, 1),
                    "divergence_type": div_type,
                    "signals": signals,
                    "created_at": datetime.now(timezone.utc),
                },
            )
            await session.execute(stmt)
            opportunities_created += 1

            # Update narrative shift record
            nar_id = f"nar-{market.id}"
            prev_sent = market.sentiment.get("current_sentiment", 0.5) if market.sentiment else 0.5
            curr_sent = sentiment.get("confidence", 0.5)
            nar_stmt = insert(NarrativeShift).values(
                id=nar_id,
                topic=market.title[:100],
                category=market.category,
                previous_sentiment=prev_sent,
                current_sentiment=curr_sent,
                velocity=narrative_velocity,
                attention_spike=1.0 + narrative_velocity,
                sources=len(news_items),
                last_updated=datetime.now(timezone.utc),
                markets_affected=[market.id],
            ).on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "previous_sentiment": NarrativeShift.current_sentiment,
                    "current_sentiment": curr_sent,
                    "velocity": narrative_velocity,
                    "attention_spike": 1.0 + narrative_velocity,
                    "sources": len(news_items),
                    "last_updated": datetime.now(timezone.utc),
                },
            )
            await session.execute(nar_stmt)

        await session.commit()

    logger.info(f"Opportunity engine complete. Created/updated {opportunities_created} opportunities.")
