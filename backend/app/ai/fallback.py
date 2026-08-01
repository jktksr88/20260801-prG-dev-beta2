from __future__ import annotations
from typing import Any
from app.ai.base import AIService

class DisabledAIService(AIService):
    async def explain_diary(self, context: dict[str,Any], question: str, language: str) -> str | None:
        return None

def get_ai_service() -> AIService:
    # Provider-independent seam. Add a provider implementation without changing diary persistence or planning.
    return DisabledAIService()
