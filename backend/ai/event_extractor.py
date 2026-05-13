import json
import logging
import os
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client: AsyncOpenAI | None = None
if OPENAI_API_KEY:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
else:
    logger.warning("OPENAI_API_KEY not set, event extraction disabled")


EVENT_EXTRACTION_PROMPT = """You are an event extraction system for a prediction market intelligence platform.

Analyze the following news headline and extract structured event information.

Output ONLY valid JSON with these fields:
- event_type: The category of event (political, economic, technological, geopolitical, legal, social, environmental, sports, entertainment)
- primary_entities: List of key people, organizations, or entities mentioned (max 5)
- location: Geographic location if mentioned, or null
- timeline: Timeframe mentioned (e.g., "2024", "Q3 2024", "before end of year", "immediate"), or null
- involved_parties: List of parties/groups involved in or affected by the event (max 5)
- impact_direction: Whether this news is "positive", "negative", "neutral", or "mixed" for the event's probability
- confidence: How certain the source seems (0.0 to 1.0)
- key_facts: List of 1-3 factual claims made in the headline

Rules:
- Be factual. Do not infer beyond what is stated.
- If the headline is vague, mark confidence low.
- Output ONLY JSON, no markdown, no explanations."""


CONTRADICTION_PROMPT = """You are a contradiction detection system for prediction market analysis.

Compare the following NEWS EVENT with a MARKET's current implied probability.

News Event:
- Headline: {headline}
- Event Type: {event_type}
- Impact Direction: {impact_direction}
- Key Facts: {key_facts}

Market:
- Title: {market_title}
- Current Probability: {probability:.1%}
- Recent Movement: {recent_movement:+.1%}

Analyze whether the news implies a probability HIGHER or LOWER than the market's current pricing.

Output ONLY valid JSON with:
- contradiction_detected: true/false (true if news and market pricing are significantly misaligned)
- implied_direction: "higher", "lower", or "neutral" (what probability direction the news suggests)
- divergence_magnitude: 0.0 to 1.0 (how large the gap appears between news-implied and market-implied probability)
- reasoning: One sentence explaining your analysis
- confidence: 0.0 to 1.0 (how confident you are in this assessment)

Rules:
- A contradiction exists when credible news strongly suggests a different probability than the market price.
- If the market has already moved in the direction the news suggests, contradiction is likely false.
- Output ONLY JSON."""


async def extract_event(headline: str, summary: str = "") -> dict[str, Any]:
    """Extract structured event data from a news headline."""
    if not client:
        return {
            "event_type": "unknown",
            "primary_entities": [],
            "location": None,
            "timeline": None,
            "involved_parties": [],
            "impact_direction": "neutral",
            "confidence": 0.5,
            "key_facts": [],
        }

    context = headline
    if summary:
        context += f"\n\nSummary: {summary}"

    prompt = f"News headline: {context}\n\nExtract structured event information."

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": EVENT_EXTRACTION_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=400,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content.strip()
        result = json.loads(content)

        return {
            "event_type": result.get("event_type", "unknown"),
            "primary_entities": result.get("primary_entities", [])[:5],
            "location": result.get("location"),
            "timeline": result.get("timeline"),
            "involved_parties": result.get("involved_parties", [])[:5],
            "impact_direction": result.get("impact_direction", "neutral"),
            "confidence": float(result.get("confidence", 0.5)),
            "key_facts": result.get("key_facts", [])[:3],
        }
    except Exception as e:
        logger.error(f"Event extraction failed: {e}")
        return {
            "event_type": "unknown",
            "primary_entities": [],
            "location": None,
            "timeline": None,
            "involved_parties": [],
            "impact_direction": "neutral",
            "confidence": 0.5,
            "key_facts": [],
        }


async def detect_contradiction(
    headline: str,
    event_data: dict,
    market_title: str,
    market_probability: float,
    recent_movement: float,
) -> dict[str, Any]:
    """Detect if news contradicts market pricing."""
    if not client:
        return {
            "contradiction_detected": False,
            "implied_direction": "neutral",
            "divergence_magnitude": 0.0,
            "reasoning": "AI analysis disabled",
            "confidence": 0.0,
        }

    prompt = CONTRADICTION_PROMPT.format(
        headline=headline,
        event_type=event_data.get("event_type", "unknown"),
        impact_direction=event_data.get("impact_direction", "neutral"),
        key_facts=json.dumps(event_data.get("key_facts", [])),
        market_title=market_title,
        probability=market_probability,
        recent_movement=recent_movement,
    )

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a contradiction detection analyst for prediction markets."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content.strip()
        result = json.loads(content)

        return {
            "contradiction_detected": bool(result.get("contradiction_detected", False)),
            "implied_direction": result.get("implied_direction", "neutral"),
            "divergence_magnitude": float(result.get("divergence_magnitude", 0.0)),
            "reasoning": result.get("reasoning", ""),
            "confidence": float(result.get("confidence", 0.0)),
        }
    except Exception as e:
        logger.error(f"Contradiction detection failed: {e}")
        return {
            "contradiction_detected": False,
            "implied_direction": "neutral",
            "divergence_magnitude": 0.0,
            "reasoning": "Analysis failed",
            "confidence": 0.0,
        }


async def batch_extract_events(news_items: list[dict]) -> list[dict]:
    """Extract events from multiple news items efficiently."""
    if not client or not news_items:
        return [{"event_type": "unknown"} for _ in news_items]

    results = []
    for item in news_items:
        event = await extract_event(
            headline=item.get("headline", ""),
            summary=item.get("summary", ""),
        )
        results.append(event)
    return results
