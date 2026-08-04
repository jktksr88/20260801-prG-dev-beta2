from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class AIService(ABC):
    @abstractmethod
    async def explain_diary(self, context: dict[str, Any], question: str, language: str) -> str | None:
        raise NotImplementedError

    async def recognize_crops(
        self,
        candidates: list[dict[str, Any]],
        note: str,
        language: str,
    ) -> list[dict[str, Any]] | None:
        """Optionally identify crops from a verified candidate list.

        Providers may override this. The default keeps recognition fully
        deterministic when no conversational AI provider is configured.
        """
        return None

    async def recognize_crop(
        self,
        candidates: list[dict[str, Any]],
        note: str,
        language: str,
    ) -> dict[str, Any] | None:
        """Backward-compatible single-crop adapter."""
        results = await self.recognize_crops(candidates, note, language)
        return results[0] if results and len(results) == 1 else None
