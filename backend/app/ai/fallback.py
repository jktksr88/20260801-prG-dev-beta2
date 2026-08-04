from __future__ import annotations
from typing import Any

from app.ai.base import AIService
from app.core.config import settings


class DisabledAIService(AIService):
    async def explain_diary(self, context: dict[str, Any], question: str, language: str) -> str | None:
        return None


def get_ai_service() -> AIService:
    # The AI layer is optional. Deterministic diary guidance remains available
    # when a provider or key is absent or temporarily unavailable.
    if settings.ai_provider.lower() == "openai" and settings.ai_api_key:
        from app.ai.openai_provider import OpenAIDiaryService

        return OpenAIDiaryService()
    return DisabledAIService()
