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


    def _recognition_prompt(self, candidates: list[dict[str, Any]], note: str, language: str) -> str:
        compact = [
            {
                "slug": crop.get("slug"),
                "name_id": crop.get("name_id"),
                "name_en": crop.get("name_en"),
                "alternative_names_id": crop.get("alternative_names_id", []),
                "alternative_names_en": crop.get("alternative_names_en", []),
            }
            for crop in candidates
        ]
        return f"""
Identify which crop the user explicitly refers to in this bilingual English/Indonesian garden note.
Choose only one slug from CANDIDATES. Do not infer a crop merely because it was previously selected.
If the note names multiple crops or no crop can be identified, return null for slug.
Return JSON only: {{"slug": string|null, "confidence": number}}.

CANDIDATES:
{json.dumps(compact, ensure_ascii=False)}

NOTE:
{note}
""".strip()

    async def recognize_crop(
        self, candidates: list[dict[str, Any]], note: str, language: str
    ) -> dict[str, Any] | None:
        if not settings.ai_api_key or not candidates:
            return None
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"{settings.openai_base_url}/responses",
                    headers={
                        "Authorization": f"Bearer {settings.ai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.openai_model,
                        "input": self._recognition_prompt(candidates, note, language),
                        "max_output_tokens": 100,
                    },
                )
                response.raise_for_status()
                text = self._extract_text(response.json())
                if not text:
                    return None
                text = text.strip()
                if text.startswith("```"):
                    text = text.strip("`")
                    if text.lower().startswith("json"):
                        text = text[4:].strip()
                parsed = json.loads(text)
                return parsed if isinstance(parsed, dict) else None
        except (httpx.HTTPError, ValueError, TypeError, json.JSONDecodeError):
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
