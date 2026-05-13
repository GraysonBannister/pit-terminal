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
    logger.warning("OPENAI_API_KEY not set, AI sentiment analysis disabled")


SENTIMENT_SYSTEM_PROMPT = """You are a market sentiment analyst. Analyze news articles about a prediction market and output a JSON object with four scores (0.0 to 1.0):

- confidence: How confident/certain the overall narrative appears (1.0 = very confident, 0.0 = highly uncertain)
- uncertainty: How much doubt, ambiguity, or unknowns exist (1.0 = very uncertain, 0.0 = very clear)
- polarization: How divided opinions are (1.0 = extremely polarized, 0.0 = unanimous consensus)
- narrative_velocity: How fast the narrative is changing (1.0 = rapidly shifting, 0.0 = completely static)

Output ONLY valid JSON. No markdown, no explanations."""


async def analyze_sentiment(news_articles: list[dict]) -> dict[str, float]:
    if not client or not news_articles:
        return {
            "confidence": 0.5,
            "uncertainty": 0.5,
            "polarization": 0.5,
            "narrative_velocity": 0.5,
        }

    news_context = "\n".join(
        f"- [{n.get('source', 'Unknown')}] {n.get('headline', '')}: {n.get('summary', '')}"
        for n in news_articles[:8]
    )

    prompt = (
        f"Analyze the sentiment of these news articles for a prediction market:\n\n"
        f"{news_context}\n\n"
        f"Return ONLY a JSON object with keys: confidence, uncertainty, polarization, narrative_velocity."
    )

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SENTIMENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=200,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content.strip()
        result = json.loads(content)
        return {
            "confidence": float(result.get("confidence", 0.5)),
            "uncertainty": float(result.get("uncertainty", 0.5)),
            "polarization": float(result.get("polarization", 0.5)),
            "narrative_velocity": float(result.get("narrative_velocity", 0.5)),
        }
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return {
            "confidence": 0.5,
            "uncertainty": 0.5,
            "polarization": 0.5,
            "narrative_velocity": 0.5,
        }
