import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, String, Float, DateTime, Integer, Text, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Market(Base):
    __tablename__ = "markets"

    id = Column(String, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    probability = Column(Float, nullable=False)
    volume = Column(Float, default=0)
    liquidity = Column(Float, default=0)
    spread = Column(Float, default=0)
    recent_movement = Column(Float, default=0)
    resolution_date = Column(String)
    source = Column(String, nullable=False)
    ai_summary = Column(Text)
    sentiment = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    __table_args__ = (
        Index("idx_markets_category", "category"),
        Index("idx_markets_source", "source"),
    )


class PricePoint(Base):
    __tablename__ = "price_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(String, ForeignKey("markets.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=now_utc, index=True)
    probability = Column(Float, nullable=False)
    volume = Column(Float, default=0)


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(String, primary_key=True, index=True)
    headline = Column(Text, nullable=False)
    source = Column(String, nullable=False, index=True)
    credibility = Column(Float, default=0.5)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    tags = Column(JSON, default=list)
    summary = Column(Text)
    market_impact = Column(Text)
    created_at = Column(DateTime(timezone=True), default=now_utc)


class NarrativeShift(Base):
    __tablename__ = "narrative_shifts"

    id = Column(String, primary_key=True, index=True)
    topic = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    previous_sentiment = Column(Float, default=0)
    current_sentiment = Column(Float, default=0)
    velocity = Column(Float, default=0)
    attention_spike = Column(Float, default=0)
    sources = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), default=now_utc)
    markets_affected = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=now_utc)


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String, primary_key=True, index=True)
    market_id = Column(String, ForeignKey("markets.id", ondelete="CASCADE"), nullable=False, index=True)
    market_title = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    market_probability = Column(Float, nullable=False)
    ai_estimated_low = Column(Float, nullable=False)
    ai_estimated_high = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False, index=True)
    divergence_type = Column(String, nullable=False, index=True)
    signals = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    __table_args__ = (
        Index("idx_opportunities_confidence", "confidence_score"),
        Index("idx_opportunities_divergence", "divergence_type"),
    )
