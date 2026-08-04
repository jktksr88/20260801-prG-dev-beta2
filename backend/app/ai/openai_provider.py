from __future__ import annotations

import json
from typing import Any

import httpx

from app.ai.base import AIService
from app.core.config import settings


class OpenAIDiaryService(AIService):
    """Small provider adapter for the Responses API.

    The structured agronomy and layout data remain the source of truth. The
    model only turns that context into cautious beginner-friendly language.
    """

    def _prompt(self, context: dict[str, Any], question: str, language: str) -> str:
        language_name = "Bahasa Indonesia" if language == "id" else "English"
        safe_context = json.dumps(context, ensure_ascii=False, default=str)[:14000]
        return f"""
You are GROE Diary, a cautious home-gardening assistant for beginners in Indonesia.
Reply in {language_name}. Use only the supplied plan, crop, weather and diary context.
Do not claim a definitive diagnosis. Do not invent measurements, pesticides, diseases,
or crop facts. Start with the most likely low-risk checks. Clearly state uncertainty.
Keep the answer under 170 words and include: possible issue, what to check now,
low-risk next action, and warning signs that need local expert help.

CONTEXT:
{safe_context}

USER NOTE OR QUESTION:
{question}
""".strip()

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str | None:
        for item in payload.get("output", []):
            if item.get("type") != "message":
                continue
            for part in item.get("content", []):
                if part.get("type") == "output_text" and part.get("text"):
                    return str(part["text"]).strip()
        return None

    async def explain_diary(self, context: dict[str, Any], question: str, language: str) -> str | None:
        if not settings.ai_api_key:
            return None
        try:
            async with httpx.AsyncClient(timeout=25) as client:
                response = await client.post(
                    f"{settings.openai_base_url}/responses",
                    headers={
                        "Authorization": f"Bearer {settings.ai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.openai_model,
                        "input": self._prompt(context, question, language),
                        "max_output_tokens": 320,
                    },
                )
                response.raise_for_status()
                return self._extract_text(response.json())
        except (httpx.HTTPError, ValueError, TypeError):
            return None
