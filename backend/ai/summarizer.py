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
    logger.warning("OPENAI_API_KEY not set, AI summarization disabled")


SYSTEM_PROMPT = """You are a prediction market intelligence analyst. Your job is to synthesize recent news and market data into a concise, factual 2-3 sentence summary.

Rules:
- Be objective and factual. Do not make predictions.
- Highlight information that could shift market-implied probability.
- Mention source credibility when relevant.
- Avoid hype, speculation, or gambling language.
- Output plain text only, no markdown.
"""


async def generate_market_summary(
    market_title: str,
    recent_news: list[dict],
    current_probability: float,
    recent_movement: float,
) -> str:
    if not client:
        return ""

    news_context = "\n".join(
        f"- [{n.get('source', 'Unknown')}] {n.get('headline', '')}"
        for n in recent_news[:5]
    )

    prompt = (
        f"Market: {market_title}\n"
        f"Current implied probability: {current_probability:.0%}\n"
        f"Recent movement: {recent_movement:+.1%}\n\n"
        f"Recent news:\n{news_context}\n\n"
        f"Provide a concise 2-3 sentence summary of what this information means for the market."
    )

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return ""
